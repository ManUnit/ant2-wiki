---
title: "Auto-Jail Pipeline"
type: concept
tags: [jail, auto-jail, waf, redis, ingestion, pipeline]
sources: [2026-05-09-ant2-v248-v2411-session, 2026-05-09-ant2-request-flow-diagram, 2026-05-13-ant2-v2426-amnesty-session, 2026-05-12-ant2-v2420-redis-monitor-domain-fix]
created: 2026-05-09
updated: 2026-05-12
---

# Auto-Jail Pipeline

The auto-jail pipeline in [[Ant2-Proxy-Security-Manager]] automatically blocks IPs that accumulate enough WAF attack events. Understanding the full pipeline is critical for diagnosing why auto-jail may silently fail.

## Full Pipeline

```
ModSecurity audit logs (/data/logs/waf/*.log)
  ↓ maybeIngestWafLogs() in logs.js  [rate-limited: 1× per 10s]
waf_events SQLite table
  ↓ pollAttacks() in jailService.js  [every 10s]
Redis jail:cnt:<ip> counters          [7-day TTL]
  ↓ threshold check (default: 10 attacks)
ip_jail SQLite table
  ↓ writeAllHostConfigs() + nginx -s reload
nginx geo block ($ip_blocked = 1)
  ↓ HTTP 423 response

NGINX access log (status=423)
  ↓ countPostJailHits()  [called at end of each pollAttacks]
ip_jail.post_jail_count  [Redis file-position watermark per log file]
```

## Key Coupling

`pollAttacks()` is the **consumer** of `waf_events`. `ingestWafLogs()` is the **producer**. These are in different files (`jailService.js` vs `logs.js`) and were originally decoupled — `ingestWafLogs()` was only triggered by WAF log UI routes.

**Critical bug (fixed in v2.4.11):** If the WAF logs UI page was never opened, `ingestWafLogs()` was never called, `waf_events` remained empty, and `pollAttacks()` found nothing — zero auto-jails despite real WAF blocks.

**Fix:** `pollAttacks()` now calls `maybeIngestWafLogs()` at the start of every poll cycle:
```js
async function pollAttacks() {
  try { require('../routes/logs').maybeIngestWafLogs(); } catch { /* ok */ }
  // ... rest of poll logic
}
```

`maybeIngestWafLogs()` has a **10-second rate limiter** matching the poll interval, so it's a no-op if called too soon. (Was 30 s prior to v2.4.11; reduced to match poll interval.)

## Redis Counter Keys

- `jail:cnt:<ip>` — accumulated attack count for an IP (7-day TTL set on first write)
- `jail:watermark` — last `waf_events.id` processed by `pollAttacks()` (prevents double-counting)
- `jail:dom:<ip>` — Redis SET of domains that triggered attacks from this IP (added v2.4.20, 7-day TTL) ([[redis-key-patterns]])

**Critical (v2.4.20+):** `jail:dom:<ip>` must be written at event-ingestion time alongside `jail:cnt:<ip>`. After `waf_events` is purged (2h TTL), domain attribution cannot be recovered from the DB — only from this Redis key or from log files (partial backfill: 53% recovery in practice). See [[2026-05-12-ant2-v2420-redis-monitor-domain-fix]].

## Jail Release

Jailed IPs are released in two ways:
1. **Expiry:** `releaseExpired()` runs every 60s, deletes from `ip_jail` where `expires_at <= now`
2. **Manual:** DELETE via `/api/jail/:id` or `/api/ipblock/global/:id`
3. **releaseExpired()** runs every **30 s** (was 60 s prior to v2.4.15)

When releasing via IP block delete, both `ip_jail` and `jail:cnt:<ip>` must be cleared — otherwise the jail entry blocks NGINX even if the block rule is gone ([[ant2-v248-v2411-session]]).

## Nginx Geo Block

Each virtual host gets a unique geo variable `$ip_blocked_<hostId>`. The default server uses `$ip_blocked_default`. Variables are defined at file top-level in `conf.d` includes, which is http context in nginx's parsing model.

Return code is HTTP **423** (Locked) rather than 403, to distinguish jail blocks from WAF rule blocks in logs and pentest scripts.

## Immediate Reload

After `writeAllHostConfigs()`, `reloadNginxNow()` calls:
```bash
docker exec ant2proxy-waf nginx -s reload
```
This bypasses inotify latency (which could accumulate multi-second delays with N+1 file writes). See [[inotify-write-order-pattern]].

## Amnesty List Bypass (v2.4.26+)

[[jail-amnesty-list]] adds a permanent exemption tier above the threshold check. Whitelisted IPs are intercepted at two points in the pipeline ([[2026-05-13-ant2-v2426-amnesty-session]]):

1. **`pollAttacks()`** — checked before "already jailed" logic. Match → `redis.del(jail:cnt:<ip>)` + `continue`. Counter never accumulates; IP never gets jailed.
2. **`applyThresholdToCounters()`** — checked after existing-jail guard. Belt-and-suspenders: clears any counter written before the IP was amnestied.

The pipeline with amnesty:

```
Redis jail:cnt:<ip> counters
  ↓ applyThresholdToCounters()
  → [amnesty check] → delete counter + skip if whitelisted
  ↓ threshold check
ip_jail table ...
```

## Diagnosing Silent Auto-Jail Failures

If attacks are firing but IPs are not being jailed:

1. Check `waf_events` row count is growing — if not, `ingestWafLogs()` is not running
2. Check Redis `jail:cnt:*` keys — if missing, `pollAttacks()` is not processing events
3. Check `jail:last_event_id` — if it's advancing but no jails, threshold may be too high
4. Check that `maybeIngestWafLogs()` export exists in `logs.js`

## See Also

- [[request-flow-layers]]
- [[Ant2-Proxy-Security-Manager]]
- [[jail-amnesty-list]]
- [[redis-key-patterns]]
- [[waf-validation-testing]]
- [[inotify-write-order-pattern]]
- [[geoip-country-blocking]]
