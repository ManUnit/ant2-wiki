---
title: "Ant2 Proxy Security Manager — CHANGELOG.md"
type: source
tags: [ant2, project, bugs, fixes, architecture, docker, ntp, geoip, rate-limiting]
created: 2026-05-05
updated: 2026-05-05
---

# Ant2 Proxy Security Manager — CHANGELOG.md

Session log of all changes made to [[Ant2-Proxy-Security-Manager]] during May 1–3, 2026 (v2.2–v2.3). Documents root causes, fixes, and architectural decisions made during active development.

**Source:** `raw/CHANGELOG.md` (local project file)

## Abstract

Development session covering v2.2 (bug fixes, brand rename, installer) and v2.3 (rate limiting full-stack feature). Rich in root-cause analysis and reusable bug patterns.

## Key Takeaways

- **v2.3 Rate Limiting**: 6 new `hosts` columns, `buildRateLimitZones()` + `buildRateLimitBlock()` in nginxConfig.js, rate limit monitor API, frontend in Hosts (Advanced tab) and Settings (Rate Limiting tab).
- **ip-api.com free tier is HTTP-only** — using `https.request()` returns `status:fail` silently. Fix: switch to `http.request()`. Pattern: always verify free-tier API transport protocol before assuming HTTPS.
- **NTP in Docker without binary**: Pure Node.js UDP socket on port 123 queries NTP directly. Requires `cap_add: SYS_TIME` in docker-compose for `date -s` to work inside container.
- **[[inotify-write-order-pattern]]**: WAF conf must be written before nginx conf — inotify triggers nginx reload on first write, which fails if WAF conf doesn't exist yet. Fix confirmed and documented.
- **GeoIP domain log ingest bug**: Log ingest filter `/^host_\d+\.log$/` missed domain-named log files (`english.th-ai-land.com.log`). Fix: accept all `.log` files, resolve `host_id` from domain-name map via DB lookup.
- **Docker Compose `version:` field**: Obsolete in modern Compose — remove it to eliminate warnings.
- **Installer system**: `install.sh` creates `.env`, builds containers, registers systemd service + `ant2-proxy` CLI. `build-package.sh` packages for deployment.

## Bug Pattern Reference

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| inotify race on nginx reload | nginx conf written before WAF conf; inotify triggers too early | Write WAF conf first, always |
| GeoIP lookup returns `status:fail` | ip-api.com free tier = HTTP only, not HTTPS | Use `http.request()` |
| Domain log files not ingested | Regex filter `/^host_\d+\.log$/` too narrow | Accept all `.log`, resolve host via domain map |
| NTP sync fails in container | `ntpdate` binary not present; container lacks `CAP_SYS_TIME` | Pure Node.js UDP query + `cap_add: SYS_TIME` |
| Country blocking breaks for global rules | `host_id=0` violates FK constraint on `country_rules` | Separate `global_country_rules` table without FK |

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[inotify-write-order-pattern]]
- [[geoip-country-blocking]]
- [[rate-limiting-nginx]]
- [[docker-compose-architecture]]
