import re, sys

with open('/opt/ant2-proxy/api/src/routes/monitor.js', 'r') as f:
    src = f.read()

# 1. Add require for redis after the http require
src = src.replace(
    "const http = require('http');",
    "const http  = require('http');\nconst { getRedis } = require('../services/redis');"
)

# 2. Add getRedisStats() function before const RANGES
redis_fn = r"""
// ── Redis stats helper ───────────────────────────────────────────────
async function getRedisStats() {
  try {
    const redis = getRedis();
    const [infoAll, keyspaceRaw] = await Promise.all([
      redis.info(),
      redis.info('keyspace'),
    ]);

    const parse = (raw) => {
      const m = {};
      for (const line of raw.split('\r\n')) {
        const i = line.indexOf(':');
        if (i > 0) m[line.slice(0, i).trim()] = line.slice(i + 1).trim();
      }
      return m;
    };

    const info   = parse(infoAll);
    const ksInfo = parse(keyspaceRaw);

    const hits    = parseInt(info.keyspace_hits   || '0', 10);
    const misses  = parseInt(info.keyspace_misses || '0', 10);
    const total   = hits + misses;
    const hitRate = total > 0 ? +((hits / total) * 100).toFixed(1) : null;

    let keys = 0, expires = 0;
    for (const [, val] of Object.entries(ksInfo)) {
      if (!val.startsWith('keys=')) continue;
      const kv = {};
      for (const part of val.split(',')) {
        const eq = part.indexOf('=');
        if (eq > 0) kv[part.slice(0, eq)] = parseInt(part.slice(eq + 1), 10) || 0;
      }
      keys    += kv.keys    || 0;
      expires += kv.expires || 0;
    }

    const usedBytes = parseInt(info.used_memory || '0', 10);
    const maxBytes  = parseInt(info.maxmemory   || '0', 10);

    return {
      connected:         true,
      version:           info.redis_version        || '?',
      usedMemoryHuman:   info.used_memory_human     || '?',
      usedMemoryBytes:   usedBytes,
      maxMemoryBytes:    maxBytes,
      usedMemoryPct:     maxBytes > 0 ? +((usedBytes / maxBytes) * 100).toFixed(1) : null,
      hitRate,
      hits,
      misses,
      keys,
      expires,
      opsPerSec:         parseInt(info.instantaneous_ops_per_sec || '0', 10),
      connectedClients:  parseInt(info.connected_clients         || '0', 10),
      uptimeSec:         parseInt(info.uptime_in_seconds         || '0', 10),
    };
  } catch {
    return { connected: false };
  }
}

"""

if 'getRedisStats' not in src:
    src = src.replace('const RANGES = {', redis_fn + 'const RANGES = {')

# 3. Add redis to SSE payload (after system block, before hosts)
old_hosts = '        hosts: hostMetrics,'
new_hosts = '        redis: await getRedisStats(),\n        hosts: hostMetrics,'
if 'redis: await getRedisStats()' not in src:
    src = src.replace(old_hosts, new_hosts, 1)

with open('/opt/ant2-proxy/api/src/routes/monitor.js', 'w') as f:
    f.write(src)

print('DONE — getRedisStats occurrences:', src.count('getRedisStats'))
