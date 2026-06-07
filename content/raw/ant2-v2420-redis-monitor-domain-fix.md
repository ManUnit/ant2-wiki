# Ant2 Proxy Security Manager v2.4.20 — Redis Monitor & Domain Fix Session Notes

**Date:** 2026-05-12  
**Server explored:** anan@172.20.20.181  
**Package delivered:** ant2ProxySecurityManager-v2.4.20.tar.gz (882KB)

---

## Overview

This session explored Redis usage on server 172.20.20.181 (the most advanced ant2 deployment), used it as the blueprint for version 2.4.20, added a Redis monitoring panel to the `/monitor` page, and fixed a critical bug where attack counters lost their domain association after `waf_events` was purged.

---

## Redis Architecture on ant2 (service: ant2proxy-redis)

Redis 7-alpine, password-protected, `maxmemory 128mb allkeys-lru`, no persistence.  
Client: `ioredis` via `/api/src/services/redis.js` → exports `getRedis()`, `cacheGet(key, ttlSec, fn)`, `cacheDel(pattern)`.

### Key patterns discovered

| Redis Key Pattern | Description | TTL |
|---|---|---|
| `geo:<ip>` | MaxMind GeoIP lookup cache (country_code, country_name, JSON) | varies |
| `waf:offset:<filename>` | Last byte offset read from WAF log file per domain | persistent |
| `jail:cnt:<ip>` | Auto-jail attack event counter for an IP (incremented by jailService poller) | 7 days |
| `jail:watermark` | Last event ID processed by jailService poller (prevents double-counting) | persistent |
| `ipblock:<ip>` | IP block cache entry (JSON with reason, blocked_at) | varies |
| `jail:dom:<ip>` | NEW in v2.4.20: Redis SET of domains that attacked from this IP | 7 days |

---

## New Feature: Redis Monitoring Panel (/monitor page)

### Backend — `api/src/routes/monitor.js`

Added `getRedisStats()` function that calls `redis.info()` and `redis.info('keyspace')`:

```javascript
async function getRedisStats() {
  const redis = getRedis();
  const info = await redis.info();
  const keyspace = await redis.info('keyspace');
  // parse: connected_clients, used_memory, maxmemory, keyspace_hits,
  //        keyspace_misses, instantaneous_ops_per_sec, uptime_in_seconds,
  //        redis_version, keys count, expires count
  return {
    connected, version, usedMemoryHuman, usedMemoryBytes, maxMemoryBytes,
    usedMemoryPct, hitRate, hits, misses, keys, expires, opsPerSec,
    connectedClients, uptimeSec
  };
}
```

SSE push payload now includes: `redis: await getRedisStats()` alongside `hosts`.

### Frontend — `web/src/pages/Monitor.jsx`

New Redis Cache panel with:
- **Connection status badge** — CONNECTED (green) / OFFLINE (red) / — (gray)
- **Memory Gauge** — color-coded: green <60%, amber <85%, red ≥85%
- **Hit Rate Gauge** — color-coded: green ≥80%, amber ≥50%, red <50%
- **Stats grid**: Keys (with TTL count), Ops/sec (with connected clients), Version (with eviction policy), Uptime (human-readable)

---

## Bug Fix: Attack Counter Domain Tracking

### Problem

The `/api/jail/counters` API endpoint showed attack counts but no domain names after `waf_events` was purged (retention: 2 hours default). The `jail:cnt:<ip>` Redis counter survives 7 days, but the domain association lived only in SQLite `waf_events`.

### Root Cause

The original `jailService.js` polled:
```sql
SELECT client_ip, COUNT(*) FROM waf_events WHERE ... GROUP BY client_ip
```
No domain stored. After 2h, `waf_events` is purged → domain gone.

### Fix — Three-file patch

**1. `api/src/services/jailService.js` (3 sub-patches)**

Query changed to:
```sql
SELECT we.client_ip, we.host_id, h.domain, COUNT(*) as cnt
FROM waf_events we
LEFT JOIN hosts h ON h.id = we.host_id
WHERE we.id > ? AND we.ts > ?
GROUP BY we.client_ip, we.host_id
```
Builds `ipDomains[ip] = Set<domain>` and `ipCounts[ip]` from aggregated rows.

After `redis.incrby(cntKey, ev.cnt)`, added:
```javascript
const domains = [...(ipDomains[ip] || [])];
if (domains.length) {
  await redis.sadd(`jail:dom:${ip}`, ...domains);
  await redis.expire(`jail:dom:${ip}`, 7 * 24 * 3600);
}
```

On auto-jail cleanup: `await redis.del('jail:dom:' + ip)` added alongside `del(cntKey)`.

**2. `api/src/routes/jail.js` (3 sub-patches)**

`/counters` route: after DB query for domains, fallback to Redis if empty:
```javascript
const missingDomainIps = ips.filter(ip => !hostsByIp[ip] || !hostsByIp[ip].length);
await Promise.all(missingDomainIps.map(async ip => {
  const doms = await redis.smembers(`jail:dom:${ip}`);
  if (doms?.length) hostsByIp[ip] = doms;
}));
```

Clear-all and manual-jail routes also del `jail:dom:<ip>` keys for consistency.

### Backfill

Script `backfill_waf_domains.js` scanned last 8MB of each domain's WAF log files in `/data/logs/waf/` to extract IP→domain mappings. Result: **170/359 IPs backfilled** with domain data. 189 IPs had attacks older than log retention — unrecoverable (forward-only fix).

### Verification

After rebuild and backfill:
```
Total:359 | with_domain:170 | no_domain:189
  206.189.19.19 cnt=7 ["crm.thailandpages.com"]
  64.225.75.246 cnt=7 ["crm.thailandpages.com"]
  64.227.32.66  cnt=7 ["gproperty.asia"]
  157.230.19.140 cnt=7 ["southex-th.com"]
  ...
```

---

## Version Bump

- `/opt/ant2-proxy/VERSION` → `2.4.20`
- `/opt/ant2-proxy/api/VERSION` → `2.4.20` (baked into Docker image)
- `/opt/ant2-proxy/api/package.json` → `"version": "2.4.20"`

---

## Build Process

Web assets rebuilt via Docker:
```bash
sudo docker run --rm -v /opt/ant2-proxy/web:/app -w /app node:20-alpine sh -c "npm install && npm run build"
```
Output: `dist/assets/index-CC42Kryj.js` + `index-DJWIiT9q.css`

Docker Compose rebuild: `sudo docker compose up -d --build api web`

---

## Package Contents (ant2ProxySecurityManager-v2.4.20.tar.gz, 882KB)

```
ant2ProxySecurityManager/
├── .env.example
├── VERSION
├── docker-compose.yml
├── install.sh
├── uninstall.sh
├── coreruleset-4.26.0-minimal.tar.gz  (bundled CRS)
├── api/                               (Node.js API, no node_modules)
├── nginx-waf/                         (NGINX+ModSecurity configs)
└── web/
    ├── Dockerfile
    ├── nginx.conf
    └── dist/                          (pre-built React app)
```

---

## Key Insights

1. **Redis as WAF log offset tracker** — enables efficient incremental log parsing without re-reading full files on each poll cycle
2. **jail:dom:<ip> pattern** — domain tracking must happen at event-ingestion time; cannot be recovered from purged DB tables
3. **7-day counter TTL** — jail counters (and now domain keys) outlive the 2h waf_events retention window by design
4. **allkeys-lru eviction** — Redis has no persistence; a container restart clears all state (offsets, counters, GeoIP cache all lost)
5. **Backfill limitation** — 53% domain recovery possible from log files; 47% were beyond log retention horizon
