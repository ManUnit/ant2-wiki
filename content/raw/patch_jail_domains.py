import re

path = '/opt/ant2-proxy/api/src/routes/jail.js'
with open(path, 'r') as f:
    src = f.read()

# 1. Make the GET / route async
old = "router.get('/', (_req, res) => {"
new = "router.get('/', async (_req, res) => {"
assert old in src, "pattern 1 not found"
src = src.replace(old, new, 1)

# 2. Add Redis fallback after the domainsByIp DB query block, before res.json
old2 = """    res.json(rows.map(j => ({
      ...j,
      expires_in: j.expires_at ? Math.max(0, j.expires_at - now) : null,
      is_expired: j.expires_at ? j.expires_at <= now : false,
      domains: domainsByIp[j.ip_address] || [],
    })));"""

new2 = """    // Fallback: read jail:dom:<ip> from Redis for IPs whose waf_events were purged
    const missingDomainIps = ipList.filter(ip => !domainsByIp[ip] || domainsByIp[ip].length === 0);
    if (missingDomainIps.length > 0) {
      const redis = getRedis();
      await Promise.all(missingDomainIps.map(async ip => {
        try {
          const doms = await redis.smembers(`jail:dom:${ip}`);
          if (doms && doms.length > 0) domainsByIp[ip] = doms;
        } catch { /* best effort */ }
      }));
    }

    res.json(rows.map(j => ({
      ...j,
      expires_in: j.expires_at ? Math.max(0, j.expires_at - now) : null,
      is_expired: j.expires_at ? j.expires_at <= now : false,
      domains: domainsByIp[j.ip_address] || [],
    })));"""

assert old2 in src, "pattern 2 not found"
src = src.replace(old2, new2, 1)

with open(path, 'w') as f:
    f.write(src)

print("Patch applied OK")
