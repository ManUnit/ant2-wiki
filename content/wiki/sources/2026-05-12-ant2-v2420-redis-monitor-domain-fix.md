---
title: "Ant2 v2.4.20 — Redis Monitor & Domain Fix"
type: source
tags: [ant2, redis, monitor, jail, domain-tracking, bug-fix]
sources: []
created: 2026-05-12
updated: 2026-05-12
---

# Ant2 v2.4.20 — Redis Monitor & Domain Fix

**Date:** 2026-05-12 · **Server:** `172.20.20.181` · **Package:** ant2ProxySecurityManager-v2.4.20.tar.gz (882 KB)

## Abstract

This session added a Redis monitoring panel to the `/monitor` page (SSE push) and fixed a critical bug where attack counters in the IP Jail view lost their domain association after `waf_events` was purged. A new `jail:dom:<ip>` Redis SET key pattern was introduced so domain data persists for the full 7-day TTL regardless of the 2-hour `waf_events` retention window. A partial backfill recovered 53% of existing domain associations from log files.

## Key Takeaways

- **`jail:dom:<ip>` must be written at ingestion time** — `waf_events` purges after 2h; any domain data not persisted to Redis at write time is permanently lost ([[redis-key-patterns]])
- **Redis as WAF log offset tracker** — `waf:offset:<filename>` enables incremental parsing; only new bytes are read on each poll, avoiding full re-reads
- **Redis Monitor panel** added to `/monitor` SSE stream: hit rate gauge, memory gauge, ops/sec, key count — see [[redis-key-patterns]]
- **Backfill is a one-shot partial fix** — 170/359 IPs recovered (53%); 189 IPs had attacks beyond log retention and are permanently unresolvable
- **allkeys-lru + no persistence** — container restart clears Redis entirely; offsets, counters, and GeoIP cache all lost on restart

## Notable Quotes

> "domain tracking must happen at event-ingestion time; cannot be recovered from purged DB tables"

> "allkeys-lru eviction — Redis has no persistence; a container restart clears all state"

## Redis Key Patterns Added (v2.4.20)

| Key | Description | TTL |
|-----|-------------|-----|
| `jail:dom:<ip>` | Redis SET of domains that triggered attacks from this IP | 7 days |

Full key map lives in [[redis-key-patterns]].

## Bug Fix Detail

### Root Cause

`jailService.js` polled `waf_events` grouped only by `client_ip` — no `host_id`/domain join. After the 2-hour retention purge, domain association was lost permanently.

### Fix

Query changed to join `hosts` table:
```sql
SELECT we.client_ip, we.host_id, h.domain, COUNT(*) as cnt
FROM waf_events we
LEFT JOIN hosts h ON h.id = we.host_id
WHERE we.id > ? AND we.ts > ?
GROUP BY we.client_ip, we.host_id
```

After incrementing `jail:cnt:<ip>`, write domain to the new SET:
```javascript
await redis.sadd(`jail:dom:${ip}`, ...domains);
await redis.expire(`jail:dom:${ip}`, 7 * 24 * 3600);
```

`/counters` route falls back to `redis.smembers('jail:dom:<ip>')` when `waf_events` returns no domain rows.

On jail release / clear-all: `redis.del('jail:dom:' + ip)` is called alongside `del(cntKey)`.

## Backfill

Script `backfill_waf_domains.js` scanned last 8 MB of each domain's WAF log (`/data/logs/waf/`). Result: **170 / 359 IPs** recovered. 189 IPs had attacks older than log retention — unrecoverable.

## Gaps / Unanswered Questions

- No automated log-rotation or size-based truncation policy documented — `waf_events` 2h purge relies on scheduled cleanup, not explicit file rotation
- Redis restart recovery: no documented procedure for reconstructing `waf:offset:*` after container restart (offsets reset → next poll re-reads from beginning → duplicate ingestion risk)

## See Also

- [[auto-jail-pipeline]]
- [[redis-key-patterns]]
- [[Ant2-Proxy-Security-Manager]]
- [[2026-05-09-ant2-v248-v2411-session]]
- [[2026-05-13-ant2-v2426-amnesty-session]]
