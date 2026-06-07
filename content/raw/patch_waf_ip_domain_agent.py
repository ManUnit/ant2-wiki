"""
Architecture:
  Tier 1 (permanent): ip_jail.domains  — written at jail time
  Tier 2 (permanent): waf_ip_summary   — updated by ingestWafLogsAsync(), never pruned, has 691 rows
  Tier 3 (ephemeral): Redis jail:dom + waf:ipdomain:<ip>  — speed cache

Changes:
  1. database.js   — ensure waf_ip_summary is updated in ingest (add upsert hook)
  2. logs.js       — in batchInsert transaction, also upsert waf_ip_summary
  3. jail.js       — GET /  uses waf_ip_summary as tier-2 fallback (not waf_events)
                  — on startup warmup: cache waf:ipdomain:<ip> from waf_ip_summary
  4. jailService.js — auto-jail reads domain from waf_ip_summary first, stores in ip_jail.domains
  5. Backfill       — update ip_jail.domains for 40 remaining IPs from waf_ip_summary
"""
import re

# ── 1. logs.js: add waf_ip_summary upsert inside batchInsert ─────────
logs_path = '/opt/ant2-proxy/api/src/routes/logs.js'
with open(logs_path) as f:
    src = f.read()

# Find the batchInsert transaction — add waf_ip_summary upsert
old_batch = """  const batchInsert = db.transaction((rows) => {
    for (const r of rows) stmt.run(...r);
  });"""

new_batch = """  const upsertIpDomain = db.prepare(`
    INSERT INTO waf_ip_summary (host_id, client_ip, country_code, country_name, last_seen_ts, total_count, block_count)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(host_id, client_ip) DO UPDATE SET
      last_seen_ts = MAX(waf_ip_summary.last_seen_ts, excluded.last_seen_ts),
      total_count  = waf_ip_summary.total_count + excluded.total_count,
      block_count  = waf_ip_summary.block_count + excluded.block_count,
      country_code = CASE WHEN waf_ip_summary.country_code = '' THEN excluded.country_code ELSE waf_ip_summary.country_code END,
      country_name = CASE WHEN waf_ip_summary.country_name = '' THEN excluded.country_name ELSE waf_ip_summary.country_name END
  `);

  const batchInsert = db.transaction((rows, hostId) => {
    const ipSeen = {};
    for (const r of rows) {
      stmt.run(...r);
      // r: [uid, hostId, ts, sc, ip, method, uri, ruleIds, ...cats, action, cc, cn]
      const ip = r[4], ts = r[2], sc = r[3], cc = r[16], cn = r[17];
      const hid = hostId ?? r[1];
      if (!ip || !hid) continue;
      const cnt = ipSeen[ip] || { total: 0, block: 0, ts: 0, cc: '', cn: '' };
      cnt.total++;
      if (sc >= 400) cnt.block++;
      if (ts > cnt.ts) { cnt.ts = ts; cnt.cc = cc || cnt.cc; cnt.cn = cn || cnt.cn; }
      ipSeen[ip] = cnt;
    }
    // Batch upsert waf_ip_summary
    for (const [ip, c] of Object.entries(ipSeen)) {
      try { upsertIpDomain.run(hostId ?? rows[0]?.[1], ip, c.cc, c.cn, c.ts, c.total, c.block); } catch {}
    }
  });"""

assert old_batch in src, 'batchInsert pattern not found'
src = src.replace(old_batch, new_batch, 1)

# Fix the batchInsert call: pass hostId
old_call = "      if (rows.length) { batchInsert(rows); total += rows.length; }"
new_call  = "      if (rows.length) { batchInsert(rows, hostId); total += rows.length; }"
assert old_call in src, 'batchInsert call pattern not found'
src = src.replace(old_call, new_call, 1)

with open(logs_path, 'w') as f:
    f.write(src)
print('logs.js patched OK')

# ── 2. jail.js: replace domain resolution block ──────────────────────
jail_route = '/opt/ant2-proxy/api/src/routes/jail.js'
with open(jail_route) as f:
    src = f.read()

old_domain_block = """    // Primary: use stored domains from ip_jail.domains (persisted at jail time)
    // Supplement: fill empty entries from waf_events (recent jails where column may be empty)
    const ipList = rows.map(j => j.ip_address);
    const storedDomains = {};
    for (const j of rows) {
      try { storedDomains[j.ip_address] = JSON.parse(j.domains || '[]'); } catch { storedDomains[j.ip_address] = []; }
    }
    const domainsByIp = { ...storedDomains };

    // For IPs with no stored domains (old rows before this fix), try waf_events
    const needsLookup = ipList.filter(ip => !domainsByIp[ip] || domainsByIp[ip].length === 0);
    if (needsLookup.length) {
      const placeholders = needsLookup.map(() => '?').join(',');
      const attacked = db.prepare(`
        SELECT DISTINCT we.client_ip, h.domain, we.host_id
        FROM   waf_events we
        LEFT JOIN hosts h ON h.id = we.host_id
        WHERE  we.client_ip IN (${placeholders}) AND we.ts >= ?
      `).all(...needsLookup, sevenDaysAgo);
      for (const r of attacked) {
        if (!domainsByIp[r.client_ip]) domainsByIp[r.client_ip] = [];
        const d = r.domain || `host_${r.host_id}`;
        if (!domainsByIp[r.client_ip].includes(d)) domainsByIp[r.client_ip].push(d);
      }
    }

    // Last resort: Redis jail:dom for truly old entries
    const stillEmpty = ipList.filter(ip => !domainsByIp[ip] || domainsByIp[ip].length === 0);
    if (stillEmpty.length) {
      const redis = getRedis();
      await Promise.all(stillEmpty.map(async ip => {
        try {
          const doms = await redis.smembers(`jail:dom:${ip}`);
          if (doms?.length) domainsByIp[ip] = doms;
        } catch {}
      }));
    }"""

new_domain_block = """    // Tier 1: ip_jail.domains — stored permanently at jail time
    const ipList = rows.map(j => j.ip_address);
    const domainsByIp = {};
    for (const j of rows) {
      try {
        const arr = JSON.parse(j.domains || '[]');
        if (arr.length) domainsByIp[j.ip_address] = arr;
      } catch {}
    }

    // Tier 2: waf_ip_summary — permanent lifetime fingerprint, never pruned
    const stillEmpty = ipList.filter(ip => !domainsByIp[ip]);
    if (stillEmpty.length) {
      const ph = stillEmpty.map(() => '?').join(',');
      const rows2 = db.prepare(`
        SELECT DISTINCT s.client_ip, h.domain
        FROM   waf_ip_summary s
        LEFT JOIN hosts h ON h.id = s.host_id
        WHERE  s.client_ip IN (${ph}) AND h.domain IS NOT NULL
      `).all(...stillEmpty);
      for (const r of rows2) {
        if (!domainsByIp[r.client_ip]) domainsByIp[r.client_ip] = [];
        if (!domainsByIp[r.client_ip].includes(r.domain)) domainsByIp[r.client_ip].push(r.domain);
      }
      // Write back to ip_jail.domains for future fast path
      for (const ip of stillEmpty) {
        if (domainsByIp[ip]?.length) {
          try { db.prepare('UPDATE ip_jail SET domains=? WHERE ip_address=?')
            .run(JSON.stringify(domainsByIp[ip]), ip); } catch {}
        }
      }
    }

    // Tier 3: Redis waf:ipdomain:<ip> — for entries not yet in waf_ip_summary
    const tier3 = ipList.filter(ip => !domainsByIp[ip]);
    if (tier3.length) {
      const redis = getRedis();
      await Promise.all(tier3.map(async ip => {
        try {
          const doms = await redis.smembers(`waf:ipdomain:${ip}`);
          if (doms?.length) {
            domainsByIp[ip] = doms;
            db.prepare('UPDATE ip_jail SET domains=? WHERE ip_address=?')
              .run(JSON.stringify(doms), ip);
          }
        } catch {}
      }));
    }"""

assert old_domain_block in src, 'domain block not found in jail.js'
src = src.replace(old_domain_block, new_domain_block, 1)

with open(jail_route, 'w') as f:
    f.write(src)
print('jail.js patched OK')

# ── 3. jailService.js: on auto-jail read domain from waf_ip_summary ──
jail_svc = '/opt/ant2-proxy/api/src/services/jailService.js'
with open(jail_svc) as f:
    src = f.read()

# When building ipDomains in pollAttacks, also check waf_ip_summary for already-known domains
# Currently it reads from waf_events JOIN hosts in the same batch query
# Add: after aggregation, also SADD to waf:ipdomain:<ip> (not just jail:dom:<ip>)
old_sadd = """      // Persist domain so counters page still shows domain after waf_events purge
      if (ipDomains[ip] && ipDomains[ip].size > 0) {
        const domKey = `jail:dom:${ip}`;
        await redis.sadd(domKey, ...[...ipDomains[ip]]);
        await redis.expire(domKey, 7 * 24 * 3600);
      }"""

new_sadd = """      // Persist domain — Redis speed cache + permanent waf_ip_summary (never pruned)
      if (ipDomains[ip] && ipDomains[ip].size > 0) {
        const doms = [...ipDomains[ip]];
        // jail:dom:<ip> — pre-jail counter page (TTL 7d)
        await redis.sadd(`jail:dom:${ip}`, ...doms);
        await redis.expire(`jail:dom:${ip}`, 7 * 24 * 3600);
        // waf:ipdomain:<ip> — permanent IP fingerprint cache (TTL 30d)
        await redis.sadd(`waf:ipdomain:${ip}`, ...doms);
        await redis.expire(`waf:ipdomain:${ip}`, 30 * 24 * 3600);
      }"""

assert old_sadd in src, 'sadd pattern not found in jailService.js'
src = src.replace(old_sadd, new_sadd, 1)

# When auto-jailing: read domain from waf_ip_summary if ipDomains is empty
old_jail_dom = """          const domainArr = ipDomains[ip] ? [...ipDomains[ip]] : [];
          db.prepare(`
            INSERT INTO ip_jail
              (ip_address, attack_count, reason, jailed_at, expires_at, auto_jailed, country_code, country_name, domains)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
          `).run(ip, newTotal, `Auto-jailed: ${newTotal} attacks`, now, expires, geo?.code || '', geo?.name || '', JSON.stringify(domainArr));"""

new_jail_dom = """          let domainArr = ipDomains[ip] ? [...ipDomains[ip]] : [];
          // Supplement from waf_ip_summary if empty (permanent fingerprint)
          if (!domainArr.length) {
            try {
              const rows = db.prepare(
                'SELECT DISTINCT h.domain FROM waf_ip_summary s LEFT JOIN hosts h ON h.id=s.host_id WHERE s.client_ip=? AND h.domain IS NOT NULL'
              ).all(ip);
              domainArr = rows.map(r => r.domain);
            } catch {}
          }
          db.prepare(`
            INSERT INTO ip_jail
              (ip_address, attack_count, reason, jailed_at, expires_at, auto_jailed, country_code, country_name, domains)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
          `).run(ip, newTotal, `Auto-jailed: ${newTotal} attacks`, now, expires, geo?.code || '', geo?.name || '', JSON.stringify(domainArr));"""

assert old_jail_dom in src, 'jail domain INSERT pattern not found'
src = src.replace(old_jail_dom, new_jail_dom, 1)

with open(jail_svc, 'w') as f:
    f.write(src)
print('jailService.js patched OK')

print('\nAll patches applied. Now run: docker compose up -d --build api')
