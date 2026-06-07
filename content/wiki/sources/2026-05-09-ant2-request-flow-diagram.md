---
title: "Ant2 Request Flow Diagram — Full Pipeline"
type: source
tags: [ant2, nginx, owasp-crs, auto-jail, rate-limit, geo-block, architecture, diagram]
created: 2026-05-09
updated: 2026-05-09
---

# Ant2 Request Flow Diagram — Full Pipeline

Internal architecture diagram documenting the complete request lifecycle through Ant2 Proxy Security Manager v2.4.15 — from TCP connection to backend, including all enforcement layers and the background detection/jail pipeline.

## Abstract

Every inbound request traverses five enforcement layers in strict order: rate limit → geo block → ModSecurity/CRS → proxy_pass → backend. Blocked requests (403) feed an asynchronous pipeline that accumulates per-IP attack counts in Redis, auto-jails IPs that exceed a threshold, and hot-reloads nginx with updated geo block maps. Post-jail requests (423) never reach ModSecurity and are counted separately via nginx access log file-position watermarks stored in Redis.

## Key Takeaways

- **Geo block runs before ModSecurity** (rewrite phase vs access phase). Once an IP is jailed, it never touches CRS — audit log has zero post-jail entries. Post-jail hit counts come from nginx access log only.
- **Pipeline latency budget is ~20 seconds worst-case**: `maybeIngestWafLogs` rate-limiter (10 s) + `pollAttacks` poll interval (10 s). An attacker can fire unblocked for up to 20 s before geo block activates.
- **Redis is the counter bridge**: `jail:cnt:{ip}` accumulates 403+rule WAF events across multiple poll cycles until the threshold is reached, then a single INSERT jails the IP.
- **HTTP status codes have different roles**: 403 = WAF block (feeds jail counter), 423 = already jailed (never touches WAF), 429 = rate limited (does not feed jail counter).
- **`$` in bcrypt hashes causes silent corruption** when passed through bash double-quoted strings. SQL with hashes must be piped to MySQL stdin, not passed via `-e "..."` shell argument.
- **SQLi comment bypass (rule 942110) is WARNING-level** (+3 pts). At default threshold 5 it never blocks alone. Per-host threshold tuning to 3 fixes this without changing paranoia level.

## Notable Details

> "An attacker firing continuously can land up to ~20 s of unblocked requests before the geo block activates." — timing table, this source

> "Rate limit (429) and WAF block (403) are counted differently — 429 never enters waf_events and does not count toward jail threshold." — status code reference table, this source

## Gaps / Questions

- Does `limit_req_zone` apply before or after the geo block check? (Likely before — both are in the same server block but `limit_req` directive order matters.)
- Is there a way to reduce the 20 s latency further without increasing CPU load?
- What happens to `jail:cnt:{ip}` if the IP is manually jailed before the threshold? (Currently: DELETE jail deletes ip_jail row but does not clear Redis counter — counter will re-trigger jail after manual release if attacks continued.)

## See Also

- [[auto-jail-pipeline]]
- [[request-flow-layers]]
- [[geoip-country-blocking]]
- [[rate-limiting-nginx]]
- [[waf-validation-testing]]
- [[Ant2-Proxy-Security-Manager]]
