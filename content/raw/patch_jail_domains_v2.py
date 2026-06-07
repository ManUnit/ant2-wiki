"""
Fix: store domains in ip_jail table so the jail list always shows domain
regardless of waf_events purge or Redis restarts.

Patches:
  1. database.js  — add migration for ip_jail.domains column
  2. jailService.js — save domains in INSERT; don't del jail:dom on jail
  3. jail.js       — GET / reads jp_jail.domains first; async GET /
"""
import re

# ── 1. database.js migration ─────────────────────────────────────
db_path = '/opt/ant2-proxy/api/src/database.js'
with open(db_path) as f:
    src = f.read()

old = "    'ALTER TABLE ip_jail ADD COLUMN post_jail_count INTEGER NOT NULL DEFAULT 0',"
new = ("    'ALTER TABLE ip_jail ADD COLUMN post_jail_count INTEGER NOT NULL DEFAULT 0',\n"
       "    'ALTER TABLE ip_jail ADD COLUMN domains TEXT NOT NULL DEFAULT \"[]\"',")
assert old in src, f"migration anchor not found"
src = src.replace(old, new, 1)
with open(db_path, 'w') as f:
    f.write(src)
print('database.js patched OK')

# ── 2. jailService.js — auto-jail: include domains in INSERT ─────
jail_svc = '/opt/ant2-proxy/api/src/services/jailService.js'
with open(jail_svc) as f:
    src = f.read()

# 2a. pollAttacks INSERT: add domains column
old = (
    "          db.prepare(`\n"
    "            INSERT INTO ip_jail\n"
    "              (ip_address, attack_count, reason, jailed_at, expires_at, auto_jailed, country_code, country_name)\n"
    "            VALUES (?, ?, ?, ?, ?, 1, ?, ?)\n"
    "          `).run(ip, newTotal, `Auto-jailed: ${newTotal} attacks`, now, expires, geo?.code || '', geo?.name || '');"
)
new = (
    "          const domainArr = ipDomains[ip] ? [...ipDomains[ip]] : [];\n"
    "          db.prepare(`\n"
    "            INSERT INTO ip_jail\n"
    "              (ip_address, attack_count, reason, jailed_at, expires_at, auto_jailed, country_code, country_name, domains)\n"
    "            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)\n"
    "          `).run(ip, newTotal, `Auto-jailed: ${newTotal} attacks`, now, expires, geo?.code || '', geo?.name || '', JSON.stringify(domainArr));"
)
assert old in src, 'pollAttacks INSERT pattern not found'
src = src.replace(old, new, 1)

# 2b. pollAttacks: don't delete jail:dom on auto-jail (keep for history)
old2 = (
    "          await redis.del(cntKey);\n"
    "          await redis.del(`jail:dom:${ip}`);\n"
    "          jailChanged = true;"
)
new2 = (
    "          await redis.del(cntKey);\n"
    "          jailChanged = true;"
)
assert old2 in src, 'del jail:dom pattern not found'
src = src.replace(old2, new2, 1)

# 2c. applyThresholdToCounters INSERT: read jail:dom from Redis, include domains
old3 = (
    "    try {\n"
    "      db.prepare(`\n"
    "        INSERT INTO ip_jail\n"
    "          (ip_address, attack_count, reason, jailed_at, expires_at, auto_jailed, country_code, country_name)\n"
    "        VALUES (?, ?, ?, ?, ?, 1, ?, ?)\n"
    "      `).run(ip, count, `Auto-jailed: ${count} attacks`, now, expires, cc, cn);\n"
    "      await redis.del(key);\n"
    "      newlyJailed.push({ ip_address: ip, attack_count: count, country_code: cc, country_name: cn });"
)
new3 = (
    "    try {\n"
    "      let domArr = [];\n"
    "      try { const d = await redis.smembers(`jail:dom:${ip}`); if (d?.length) domArr = d; } catch {}\n"
    "      db.prepare(`\n"
    "        INSERT INTO ip_jail\n"
    "          (ip_address, attack_count, reason, jailed_at, expires_at, auto_jailed, country_code, country_name, domains)\n"
    "        VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)\n"
    "      `).run(ip, count, `Auto-jailed: ${count} attacks`, now, expires, cc, cn, JSON.stringify(domArr));\n"
    "      await redis.del(key);\n"
    "      newlyJailed.push({ ip_address: ip, attack_count: count, country_code: cc, country_name: cn });"
)
assert old3 in src, 'applyThreshold INSERT pattern not found'
src = src.replace(old3, new3, 1)

with open(jail_svc, 'w') as f:
    f.write(src)
print('jailService.js patched OK')

# ── 3. jail.js — GET / reads ip_jail.domains + async ────────────
jail_route = '/opt/ant2-proxy/api/src/routes/jail.js'
with open(jail_route) as f:
    src = f.read()

# 3a. Make GET / async
old = "router.get('/', async (_req, res) => {"
# already async from previous patch — check
if old not in src:
    old_sync = "router.get('/', (_req, res) => {"
    assert old_sync in src, 'GET / signature not found'
    src = src.replace(old_sync, "router.get('/', async (_req, res) => {", 1)
    print('GET / made async')

# 3b. Replace the full domain-resolution block: use ip_jail.domains first, waf_events as supplement
old_block = (
    "    // Single query: all (ip, domain) pairs for every jailed IP in the last 7d\n"
    "    const ipList = rows.map(j => j.ip_address);\n"
    "    const domainsByIp = {};\n"
    "    if (ipList.length) {\n"
    "      const placeholders = ipList.map(() => '?').join(',');\n"
    "      const attacked = db.prepare(`\n"
    "        SELECT DISTINCT we.client_ip, h.domain, we.host_id\n"
    "        FROM   waf_events we\n"
    "        LEFT JOIN hosts h ON h.id = we.host_id\n"
    "        WHERE  we.client_ip IN (${placeholders}) AND we.ts >= ?\n"
    "      `).all(...ipList, sevenDaysAgo);\n"
    "      for (const r of attacked) {\n"
    "        if (!domainsByIp[r.client_ip]) domainsByIp[r.client_ip] = [];\n"
    "        domainsByIp[r.client_ip].push(r.domain || `host_${r.host_id}`);\n"
    "      }\n"
    "    }\n"
    "\n"
    "    // Fallback: read jail:dom:<ip> from Redis for IPs whose waf_events were purged\n"
    "    const missingDomainIps = ipList.filter(ip => !domainsByIp[ip] || domainsByIp[ip].length === 0);\n"
    "    if (missingDomainIps.length > 0) {\n"
    "      const redis = getRedis();\n"
    "      await Promise.all(missingDomainIps.map(async ip => {\n"
    "        try {\n"
    "          const doms = await redis.smembers(`jail:dom:${ip}`);\n"
    "          if (doms && doms.length > 0) domainsByIp[ip] = doms;\n"
    "        } catch { /* best effort */ }\n"
    "      }));\n"
    "    }\n"
    "\n"
    "    res.json(rows.map(j => ({"
)
new_block = (
    "    // Primary: use stored domains from ip_jail.domains (persisted at jail time)\n"
    "    // Supplement: fill empty entries from waf_events (recent jails where column may be empty)\n"
    "    const ipList = rows.map(j => j.ip_address);\n"
    "    const storedDomains = {};\n"
    "    for (const j of rows) {\n"
    "      try { storedDomains[j.ip_address] = JSON.parse(j.domains || '[]'); } catch { storedDomains[j.ip_address] = []; }\n"
    "    }\n"
    "    const domainsByIp = { ...storedDomains };\n"
    "\n"
    "    // For IPs with no stored domains (old rows before this fix), try waf_events\n"
    "    const needsLookup = ipList.filter(ip => !domainsByIp[ip] || domainsByIp[ip].length === 0);\n"
    "    if (needsLookup.length) {\n"
    "      const placeholders = needsLookup.map(() => '?').join(',');\n"
    "      const attacked = db.prepare(`\n"
    "        SELECT DISTINCT we.client_ip, h.domain, we.host_id\n"
    "        FROM   waf_events we\n"
    "        LEFT JOIN hosts h ON h.id = we.host_id\n"
    "        WHERE  we.client_ip IN (${placeholders}) AND we.ts >= ?\n"
    "      `).all(...needsLookup, sevenDaysAgo);\n"
    "      for (const r of attacked) {\n"
    "        if (!domainsByIp[r.client_ip]) domainsByIp[r.client_ip] = [];\n"
    "        const d = r.domain || `host_${r.host_id}`;\n"
    "        if (!domainsByIp[r.client_ip].includes(d)) domainsByIp[r.client_ip].push(d);\n"
    "      }\n"
    "    }\n"
    "\n"
    "    // Last resort: Redis jail:dom for truly old entries\n"
    "    const stillEmpty = ipList.filter(ip => !domainsByIp[ip] || domainsByIp[ip].length === 0);\n"
    "    if (stillEmpty.length) {\n"
    "      const redis = getRedis();\n"
    "      await Promise.all(stillEmpty.map(async ip => {\n"
    "        try {\n"
    "          const doms = await redis.smembers(`jail:dom:${ip}`);\n"
    "          if (doms?.length) domainsByIp[ip] = doms;\n"
    "        } catch {}\n"
    "      }));\n"
    "    }\n"
    "\n"
    "    res.json(rows.map(j => ({"
)
assert old_block in src, 'GET / domain block not found'
src = src.replace(old_block, new_block, 1)

with open(jail_route, 'w') as f:
    f.write(src)
print('jail.js patched OK')

# Also backfill existing jailed IPs from waf_events + Redis into ip_jail.domains
print('All patches applied. Backfill existing rows next.')
