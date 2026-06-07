---
title: "Wiki Index"
updated: 2026-05-13
---

# Wiki Index

Master catalog of all pages. Updated after every ingest and every page-creating query.

---

## Sources

| Page | Summary | Date |
|------|---------|------|
| [[2026-05-05-owasp-crs-owasp-foundation]] | OWASP CRS official project page — identity, license, issue channels | 2026-05-05 |
| [[2026-05-05-f5-waf-for-nginx]] | F5 WAF for NGINX (fka NGINX App Protect WAF) — commercial suite overview | 2026-05-05 |
| [[2026-05-05-crs-releases-v4-20-to-v4-26]] | CRS GitHub releases v4.20–v4.26 + v3.3.8 — CVEs, new rules, FP fixes | 2026-05-05 |
| [[2026-05-05-ant2-progress]] | Ant2 PROGRESS.md — feature tracker, DB schema, platform/bypass presets | 2026-05-05 |
| [[2026-05-05-ant2-changelog]] | Ant2 CHANGELOG.md — v2.2–v2.3 root causes, fixes, architecture decisions | 2026-05-05 |
| [[2026-05-06-ant2-v2361-release-notes]] | v2.3.5→v2.3.6-a1 release notes — headers-more, Magento preset, WYSIWYG fix, 429 page | 2026-05-06 |
| [[2026-05-06-owasp-crs-script-test-poc]] | owaps.ps1 — 27-test WAF validation script + results on abpmart.com & kasikornbank.com | 2026-05-06 |
| [[2026-05-07-ant2-v242-v243-session]] | v2.4.1→v2.4.3 session: WAF test fixes, CRS scope analysis, custom rules 9500101–9500103, 3-server deploy | 2026-05-07 |
| [[2026-05-07-ant2-v244-waf-port80-fix]] | v2.4.4: silent WAF bypass on port 80 CF-safe block — modsecurity missing from force_https branch | 2026-05-07 |
| [[2026-05-09-ant2-v248-v2411-session]] | v2.4.8–v2.4.11: default-server gap, jail release coupling, row2host, immediate reload, lazy ingestion bug | 2026-05-09 |
| [[2026-05-09-ant2-v2412-v2415-session]] | v2.4.12–v2.4.15: post_jail_count, 3-tier counter, jail speed tuning, owaps.ps1 rewrite + .exe, block page wording | 2026-05-09 |
| [[2026-05-09-ant2-server-184-incident]] | Server 184: disk full (13GB logs), Docker network isolation, NPM password reset + bash $ hash corruption bug | 2026-05-09 |
| [[2026-05-09-ant2-request-flow-diagram]] | Full request flow diagram v2.4.15 — 5 enforcement layers, jail pipeline, timing budget, status code roles | 2026-05-09 |
| [[2026-05-10-custom-selectbox-portal-dropdown]] | Custom SelectBox component — portal dropdown pattern, debug trace, CSS pitfalls (w-full/fixed viewport bug) | 2026-05-10 |
| [[2026-05-13-compact-row-table-theme]] | Compact row table theme — React+Tailwind dense list, sticky header, accordion, lazy load, Docker bake pattern | 2026-05-13 |
| [[2026-05-13-ant2-v2426-amnesty-session]] | v2.4.25→v2.4.26: IP Jail Amnesty List (jail_whitelist table, CRUD, jailService skip, Amnesty tab) + GeoIP allow-list semantic fix | 2026-05-13 |
| [[2026-05-12-ant2-v2420-redis-monitor-domain-fix]] | v2.4.20: Redis Monitor panel (SSE) + jail:dom:<ip> key for persistent domain tracking past waf_events 2h purge | 2026-05-12 |

---

## Entities

| Page | Type | Summary |
|------|------|---------|
| [[OWASP-CRS]] | Rule set | Open-source WAF rule set for ModSecurity; v4.26.0 current, v4.25.0 LTS |
| [[ModSecurity]] | WAF engine | Open-source WAF engine (v3 used in Ant2); runs CRS rules inside NGINX |
| [[Ant2-Proxy-Security-Manager]] | Project | NGINX reverse-proxy GUI + WAF + GeoIP + rate limiting; v2.4.26 |
| [[F5-NGINX-WAF]] | Product | Commercial WAF suite by F5; formerly NGINX App Protect WAF |

---

## Concepts

| Page | Summary | Key Sources |
|------|---------|-------------|
| [[paranoia-levels]] | CRS PL1–4 system — rules active vs FP tradeoff | PROGRESS.md, CRS overview |
| [[false-positive-false-negative-tradeoff]] | Core WAF tension; FP reduction is continuous, never solved | CRS overview, CRS releases |
| [[platform-presets]] | 18 SecRuleRemoveById preset sets for frameworks (incl. Magento, Next.js) | PROGRESS.md, v2.3.6-a1 |
| [[bypass-presets]] | 10 ctl:ruleEngine=Off presets for OAuth/webhook paths | PROGRESS.md |
| [[crs-rule-numbering]] | Full 9xx xxx range reference + most-excluded rule IDs | CRS releases, PROGRESS.md |
| [[inotify-write-order-pattern]] | WAF conf must be written before nginx conf — inotify race fix | CHANGELOG.md |
| [[geoip-country-blocking]] | 2-stage Cloudflare-aware GeoIP map, HTTP 423, global vs per-host | PROGRESS.md, CHANGELOG.md |
| [[rate-limiting-nginx]] | limit_conn / limit_req / limit_rate — v2.3 impl + rate normalization fix | CHANGELOG.md, v2.3.6-a1 |
| [[server-header-disclosure]] | Suppress Server header via headers-more module + server_tokens off | v2.3.6-a1 |
| [[wysiwyg-iframe-editor]] | iframe designMode pattern for true WYSIWYG full-page HTML editing | v2.3.6-a1 |
| [[custom-dropdown-portal-pattern]] | React+Tailwind custom dropdown: createPortal, position:fixed, w-full/viewport pitfall, Windows combo-box style | custom-selectbox-portal-dropdown |
| [[compact-row-table-theme]] | Dense management list pattern: ~40px rows, sticky header, divide-y, max-height accordion, everOpen lazy render, eager/lazy API split | 2026-05-13-compact-row-table-theme |
| [[ant2-docker-deploy-pattern]] | Ant2 web container uses Dockerfile COPY dist — must `docker compose build web` before `up -d`; restart alone has no effect | 2026-05-13-compact-row-table-theme |
| [[waf-validation-testing]] | Methodology + pitfalls for WAF blackbox testing (HTTP 301, curl -g, rule scope mismatch) | owaps.ps1 POC, v2.4.x session |
| [[crs-rule-scope]] | What each CRS rule actually inspects — the 3 misunderstood rules (933110/933120/921110) | v2.4.x session |
| [[custom-waf-rules]] | Custom rule development in Ant2 — IDs 9500101–9500103, placement, namespace | v2.4.x session |
| [[waf-proxy-pass-scope]] | WAF must be active in every server block with proxy_pass — port 80 CF-safe bypass pattern | v2.4.4 fix |
| [[auto-jail-pipeline]] | Full WAF event → Redis counter → ip_jail → nginx geo block pipeline; lazy-ingestion bug and fix | v2.4.11 session |
| [[jail-amnesty-list]] | Permanent IP exemption from auto-jailing — jail_whitelist table, CRUD API, jailService skip logic, Amnesty UI tab | 2026-05-13-ant2-v2426-amnesty-session |
| [[redis-key-patterns]] | Full Ant2 Redis key map (geo, waf:offset, jail:cnt, jail:dom, jail:watermark); domain-tracking rule; Monitor panel fields; restart impact | 2026-05-12-ant2-v2420-redis-monitor-domain-fix |
| [[request-flow-layers]] | 5-layer request enforcement order (rate-limit → geo-block → CRS → proxy); timing budget; status code roles | request-flow diagram |

---

## Analyses

| Page | Question | Date |
|------|---------|------|
| [[2026-06-07-ant2-vs-world-waf-comparison]] | Which WAFs worldwide offer GeoIP + IP Jail? How does Ant2 (Thai-built) compare in features, speed, and robustness? | 2026-06-07 |
