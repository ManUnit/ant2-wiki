import re

# ── Patch 1: jailService.js ──────────────────────────────────────────
with open('/opt/ant2-proxy/api/src/services/jailService.js', 'r') as f:
    svc = f.read()

# Change the events query from GROUP BY client_ip  →  GROUP BY client_ip, host_id
# and add h.domain to SELECT, join hosts
old_query = """    // Count 403 WAF-rule events per IP in this batch
    const events = db.prepare(`
      SELECT client_ip, COUNT(*) AS cnt
      FROM   waf_events
      WHERE  id > ? AND id <= ?
        AND  status_code = 403
        AND  (cat_xss > 0 OR cat_sqli > 0 OR cat_rce > 0
              OR cat_lfi > 0 OR cat_rfi > 0 OR cat_proto > 0 OR cat_other > 0)
        AND  rule_ids != '[]'
        AND  client_ip != ''
      GROUP BY client_ip
    `).all(lastId, newMaxId);"""

new_query = """    // Count 403 WAF-rule events per IP+host in this batch (include domain for Redis cache)
    const rawEvents = db.prepare(`
      SELECT we.client_ip, we.host_id, h.domain, COUNT(*) AS cnt
      FROM   waf_events we
      LEFT JOIN hosts h ON h.id = we.host_id
      WHERE  we.id > ? AND we.id <= ?
        AND  we.status_code = 403
        AND  (we.cat_xss > 0 OR we.cat_sqli > 0 OR we.cat_rce > 0
              OR we.cat_lfi > 0 OR we.cat_rfi > 0 OR we.cat_proto > 0 OR we.cat_other > 0)
        AND  we.rule_ids != '[]'
        AND  we.client_ip != ''
      GROUP BY we.client_ip, we.host_id
    `).all(lastId, newMaxId);

    // Aggregate per IP (sum across hosts) and build domain map
    const ipDomains = {};
    const ipCounts  = {};
    for (const r of rawEvents) {
      ipCounts[r.client_ip]  = (ipCounts[r.client_ip] || 0) + r.cnt;
      if (!ipDomains[r.client_ip]) ipDomains[r.client_ip] = new Set();
      if (r.domain) ipDomains[r.client_ip].add(r.domain);
      else if (r.host_id) ipDomains[r.client_ip].add(`host_${r.host_id}`);
    }
    const events = Object.entries(ipCounts).map(([client_ip, cnt]) => ({ client_ip, cnt }));"""

if old_query in svc:
    svc = svc.replace(old_query, new_query)
    print('jailService: events query patched')
else:
    print('jailService: events query NOT found — check whitespace')

# After incrementing cntKey, store domains in jail:dom:<ip>
old_incr = """      const cntKey   = `jail:cnt:${ip}`;
      const newTotal = await redis.incrby(cntKey, ev.cnt);
      if (newTotal === ev.cnt) await redis.expire(cntKey, 7 * 24 * 3600);"""

new_incr = """      const cntKey   = `jail:cnt:${ip}`;
      const newTotal = await redis.incrby(cntKey, ev.cnt);
      if (newTotal === ev.cnt) await redis.expire(cntKey, 7 * 24 * 3600);

      // Persist domain so counters page still shows domain after waf_events purge
      if (ipDomains[ip] && ipDomains[ip].size > 0) {
        const domKey = `jail:dom:${ip}`;
        await redis.sadd(domKey, ...[...ipDomains[ip]]);
        await redis.expire(domKey, 7 * 24 * 3600);
      }"""

if old_incr in svc:
    svc = svc.replace(old_incr, new_incr)
    print('jailService: domain storage after incr patched')
else:
    print('jailService: incr block NOT found')

# Also delete jail:dom when IP gets auto-jailed
old_jailed_del = """          await redis.del(cntKey);
          jailChanged = true;
          console.log(`[Jail] Auto-jailed ${ip} (${newTotal} attacks)`);"""

new_jailed_del = """          await redis.del(cntKey);
          await redis.del(`jail:dom:${ip}`);
          jailChanged = true;
          console.log(`[Jail] Auto-jailed ${ip} (${newTotal} attacks)`);"""

if old_jailed_del in svc:
    svc = svc.replace(old_jailed_del, new_jailed_del)
    print('jailService: del dom on auto-jail patched')
else:
    print('jailService: del dom on auto-jail NOT found')

with open('/opt/ant2-proxy/api/src/services/jailService.js', 'w') as f:
    f.write(svc)

# ── Patch 2: jail.js counters route ─────────────────────────────────
with open('/opt/ant2-proxy/api/src/routes/jail.js', 'r') as f:
    route = f.read()

# Replace the domainsByIp lookup block in /counters to also fallback to jail:dom:* Redis keys
old_domain_lookup = """    // Single DB query for all IPs
    const placeholders = ips.map(() => '?').join(',');
    const attackedRows = db.prepare(`
      SELECT DISTINCT we.client_ip, we.host_id, h.domain
      FROM   waf_events we
      LEFT JOIN hosts h ON h.id = we.host_id
      WHERE  we.client_ip IN (${placeholders}) AND we.ts >= ?
    `).all(...ips, sevenDaysAgo);
    const hostsByIp = {};
    for (const r of attackedRows) {
      if (!hostsByIp[r.client_ip]) hostsByIp[r.client_ip] = [];
      hostsByIp[r.client_ip].push(r.domain || `host_${r.host_id}`);
    }"""

new_domain_lookup = """    // Single DB query for all IPs (waf_events may have been purged — Redis fallback below)
    const placeholders = ips.map(() => '?').join(',');
    const attackedRows = db.prepare(`
      SELECT DISTINCT we.client_ip, we.host_id, h.domain
      FROM   waf_events we
      LEFT JOIN hosts h ON h.id = we.host_id
      WHERE  we.client_ip IN (${placeholders}) AND we.ts >= ?
    `).all(...ips, sevenDaysAgo);
    const hostsByIp = {};
    for (const r of attackedRows) {
      if (!hostsByIp[r.client_ip]) hostsByIp[r.client_ip] = [];
      hostsByIp[r.client_ip].push(r.domain || `host_${r.host_id}`);
    }

    // Fallback: read jail:dom:<ip> from Redis for any IP whose waf_events were purged
    const missingDomainIps = ips.filter(ip => !hostsByIp[ip] || hostsByIp[ip].length === 0);
    if (missingDomainIps.length > 0) {
      await Promise.all(missingDomainIps.map(async ip => {
        try {
          const doms = await redis.smembers(`jail:dom:${ip}`);
          if (doms && doms.length > 0) hostsByIp[ip] = doms;
        } catch { /* best effort */ }
      }));
    }"""

if old_domain_lookup in route:
    route = route.replace(old_domain_lookup, new_domain_lookup)
    print('jail.js: counters domain fallback patched')
else:
    print('jail.js: counters domain lookup block NOT found')

# Also clean jail:dom when manually clearing counters (clearAll)
old_clear = """    for (const j of all) await redis.del(`jail:cnt:${j.ip_address}`);"""
new_clear = """    for (const j of all) {
      await redis.del(`jail:cnt:${j.ip_address}`);
      await redis.del(`jail:dom:${j.ip_address}`);
    }"""
if old_clear in route:
    route = route.replace(old_clear, new_clear)
    print('jail.js: clearAll dom del patched')
else:
    print('jail.js: clearAll NOT found')

# Clean jail:dom on single manual jail
old_single_del = """    await redis.del(`jail:cnt:${ip_address}`);"""
new_single_del = """    await redis.del(`jail:cnt:${ip_address}`);
    await redis.del(`jail:dom:${ip_address}`);"""
if old_single_del in route:
    route = route.replace(old_single_del, new_single_del, 1)
    print('jail.js: single jail dom del patched')
else:
    print('jail.js: single jail del NOT found')

with open('/opt/ant2-proxy/api/src/routes/jail.js', 'w') as f:
    f.write(route)

print('\nAll patches done.')
