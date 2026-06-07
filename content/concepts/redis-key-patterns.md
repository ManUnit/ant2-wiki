---
title: "Redis Key Patterns — Ant2"
type: concept
tags: [redis, caching, jail, geoip, waf, keys, ttl]
sources: [2026-05-12-ant2-v2420-redis-monitor-domain-fix]
created: 2026-05-12
updated: 2026-05-12
---

# Redis Key Patterns — Ant2

[[Ant2-Proxy-Security-Manager]] uses Redis 7-alpine as a shared in-process cache with `maxmemory 128mb allkeys-lru` and **no persistence**. All keys are lost on container restart.

## Full Key Map

| Key Pattern | Description | TTL |
|-------------|-------------|-----|
| `geo:<ip>` | MaxMind GeoIP lookup result (country_code, country_name, JSON) | varies |
| `waf:offset:<filename>` | Last byte-position read in a WAF log file — enables incremental parsing | persistent (no expire) |
| `jail:cnt:<ip>` | Accumulated attack event count for an IP (incremented by jailService poller) | 7 days |
| `jail:watermark` | Last `waf_events.id` processed by `pollAttacks()` — prevents double-counting | persistent |
| `jail:dom:<ip>` | Redis SET of domains that generated attacks from this IP (added v2.4.20) | 7 days |
| `ipblock:<ip>` | IP block cache entry — JSON with reason, blocked_at | varies |

## Design Principles

### Offset-Based Incremental Parsing

`waf:offset:<filename>` stores the last byte read from each WAF log file (`/data/logs/waf/*.log`). On each `maybeIngestWafLogs()` call:
1. `redis.get('waf:offset:<filename>')` → seek to that position
2. Read only new bytes
3. `redis.set('waf:offset:<filename>', newPosition)`

This avoids full re-reads of large log files on every 10-second poll cycle. **Risk:** if the Redis key is lost (container restart), the next poll re-reads from byte 0 → duplicate `waf_events` rows. Duplicate events inflate `jail:cnt:<ip>` counters.

### Domain Tracking Must Be Written at Ingestion Time

`jail:dom:<ip>` stores the domain(s) associated with attacks from an IP as a Redis SET with 7-day TTL — matching the `jail:cnt:<ip>` TTL. This is critical because:

- `waf_events` SQLite table is purged every **2 hours**
- `jail:cnt:<ip>` survives for **7 days**
- Without `jail:dom:<ip>`, the Jail UI shows counts with no domain attribution for any IP whose events have been purged

**Rule:** domain data that must outlive `waf_events` retention MUST be written to Redis at event-ingestion time. It cannot be reconstructed retroactively from purged tables. ([[2026-05-12-ant2-v2420-redis-monitor-domain-fix]])

### allkeys-lru Eviction Policy

Redis is configured with `allkeys-lru` — any key (including those without TTL) can be evicted under memory pressure. Persistent keys like `waf:offset:*` and `jail:watermark` can be evicted if Redis approaches 128 MB. Monitor memory usage to ensure this does not silently reset ingestion state.

## Redis Monitor Panel (v2.4.20+)

The `/monitor` SSE stream includes a `redis` field from `getRedisStats()`:

| Field | Source | Description |
|-------|--------|-------------|
| `connected` | `redis.info()` | Client connected flag |
| `version` | `redis.info()` | Redis server version |
| `usedMemoryPct` | `used_memory / maxmemory` | Memory utilization % |
| `hitRate` | `hits / (hits + misses)` | Cache effectiveness |
| `opsPerSec` | `instantaneous_ops_per_sec` | Current command rate |
| `keys` / `expires` | `redis.info('keyspace')` | Total keys, keys with TTL |
| `uptimeSec` | `uptime_in_seconds` | Redis uptime |

Frontend thresholds:
- Memory gauge: green < 60%, amber < 85%, red ≥ 85%
- Hit rate gauge: green ≥ 80%, amber ≥ 50%, red < 50%

## Container Restart Impact

On `docker compose restart redis` (or any full compose restart):

| Lost | Impact |
|------|--------|
| `waf:offset:*` | Next poll re-reads all logs from byte 0 → duplicate waf_events |
| `jail:cnt:*` | All IP attack counters reset to 0 → auto-jail resets |
| `jail:dom:*` | Domain attribution lost for all jailed/pending IPs |
| `jail:watermark` | Next poll may reprocess old events |
| `geo:*` | GeoIP cache cold — extra MaxMind lookups until warm |

## See Also

- [[auto-jail-pipeline]]
- [[Ant2-Proxy-Security-Manager]]
- [[2026-05-12-ant2-v2420-redis-monitor-domain-fix]]
- [[geoip-country-blocking]]
- [[request-flow-layers]]
