# Wiki Log

Append-only record of all wiki operations. Each entry starts with `## [YYYY-MM-DD] TYPE | Title` for grep-ability.

---

## [2026-06-07] update | Ant2Cloud website added — https://ant2cloud.com

- Pages updated: [[Ant2-Proxy-Security-Manager]], [[2026-06-07-ant2-vs-world-waf-comparison]]
- Contact/product website: https://ant2cloud.com

---

## [2026-06-07] update | Ant2Cloud Box Appliance — Commercial Product Added

- Pages updated:
  - [[Ant2-Proxy-Security-Manager]] — added Ant2Cloud Box Appliance section (฿250,000 THB, hardware, built-in WAF, one-time purchase)
  - [[2026-06-07-ant2-vs-world-waf-comparison]] — added Section 7 commercial appliance pricing table vs Cloudflare Business / Imperva / FortiWeb; open-source vs appliance tier table
- Key fact: Ant2 WAF ships as pre-installed turnkey hardware inside Ant2Cloud appliance at ฿250,000 (one-time, on-premise, full data sovereignty)

---

## [2026-06-07] query | Ant2 vs World WAF — GeoIP + IP Jail Comparison

- Question: WAF solutions worldwide with GeoIP + IP Block + Auto-Jail; how does Ant2 compare?
- Analysis page: wiki/analyses/2026-06-07-ant2-vs-world-waf-comparison.md
- Key findings:
  - Ant2 is the only free, self-hosted, GUI-managed WAF with all three features integrated
  - Ant2 jails on WAF-event-count (not rate) — catches slow targeted attacks that bypass rate-based jails
  - 5-layer defense: rate-limit → GeoIP → IP Jail (pre-ModSec) → CRS → backend
  - SIGQUIT drain eliminates keepalive bypass window to ~1s
  - Worst-case jail latency: ~20s; config reload: zero-downtime
  - Built by independent Thai 🇹🇭 developer; production-proven on 20+ domains

---

## [2026-06-07] ingest | Ant2 v2.4.20 — Redis Monitor & Domain Fix

- Source file: raw/ant2-v2420-redis-monitor-domain-fix.md
- Summary page: wiki/sources/2026-05-12-ant2-v2420-redis-monitor-domain-fix.md
- Pages created: [[redis-key-patterns]]
- Pages updated:
  - [[auto-jail-pipeline]] — added `jail:dom:<ip>` to Redis counter key table; added domain-tracking critical note with 2h/7d retention mismatch explanation
  - [[Ant2-Proxy-Security-Manager]] — version row added for v2.4.20, added [[redis-key-patterns]] to See Also
- Index updated: new source row, new concept row (redis-key-patterns)
- Key insights:
  - `jail:dom:<ip>` must be written at ingestion time — `waf_events` purges after 2h, Redis key lasts 7 days; gap was silent (counts visible, domain blank)
  - `waf:offset:<filename>` is the incremental log parsing anchor — lost on restart → duplicate ingestion risk
  - Backfill is forward-only: 53% recovery (170/359 IPs); 47% permanently unresolvable
  - allkeys-lru + no persistence: Redis restart nukes all WAF pipeline state

---

## [2026-05-13] ingest | Ant2 v2.4.25→v2.4.26 — IP Jail Amnesty List + GeoIP Allow List Fix

- Source file: wiki/sources/2026-05-13-ant2-v2426-amnesty-session.md (session notes, no raw file)
- Summary page: wiki/sources/2026-05-13-ant2-v2426-amnesty-session.md
- Pages created: [[jail-amnesty-list]]
- Pages updated:
  - [[Ant2-Proxy-Security-Manager]] — version v2.4.15 → v2.4.26, added v2.4.16–v2.4.26 changelog row, fleet status (181 deployed, 180/238 still v2.4.15), added jail-amnesty-list to See Also
  - [[auto-jail-pipeline]] — added Amnesty List Bypass section (two skip points in pollAttacks + applyThresholdToCounters)
  - [[geoip-country-blocking]] — added Allow List semantic bug section (toggleCountry fix) + unresolved functional gap (TH accessible on AF-only allow list)
- Index updated: new source row, new concept row (jail-amnesty-list), Ant2 entity version bumped to v2.4.26
- Key insights:
  - "Amnesty" chosen as opposite of "Jail" for UI naming; DB table remains `jail_whitelist`
  - Express route ordering: `/whitelist` and `/whitelist/:id` must be registered before `/:id` catch-all
  - jailService skip at two points: `pollAttacks()` (before "already jailed") + `applyThresholdToCounters()` (belt-and-suspenders)
  - GeoIP `toggleCountry()` always stored `action: 'block'` regardless of mode — fixed; backend ignores action field so nginx output was already correct
  - Docker web image bakes dist/ at build time — must `docker compose build web` before `up -d`; restart alone has no effect
  - GeoIP Allow List functional gap: Thailand could still access AF-only site — root cause unconfirmed, needs `nginx -t` on 181
  - Deploy pattern for v2.4.26: SCP api/src + web/dist to /tmp; sudo cp; `docker compose -p ant2proxy up -d --build api web`

---

## [2026-05-13] update | ant2-proxy v2.4.22 — Monitor dashboard layout

- Version bump: api 2.4.21 → 2.4.22, web 2.3.6 → 2.3.7
- Monitor.jsx changes:
  - Redis Cache panel: replaced large SVG gauge with 4 compact stat cards (text-2xl), added thin progress bars for Mem Used + Hit Rate
  - Panel order changed: System Health → Nginx cards → Traffic cards → Redis Cache → Traffic Trend → Per-host
- Pages touched: [[Ant2-Proxy-Security-Manager]]

---

## [2026-05-13] ingest | Compact Row Table Theme — React + Tailwind

- Source file: raw/2026-05-13-compact-row-table-theme.md
- Summary page: wiki/sources/2026-05-13-compact-row-table-theme.md
- Pages created: [[compact-row-table-theme]], [[ant2-docker-deploy-pattern]]
- Pages updated: [[Ant2-Proxy-Security-Manager]] (referenced via new concepts)
- Key insights:
  - sticky header ต้องแยกออกจาก list body (`rounded-t-xl` + `rounded-b-xl` sibling) เพราะ `overflow:hidden` บน container blocks sticky positioning
  - `divide-y divide-slate-100` บน container ดีกว่า `border-b` ต่อ row — ไม่มี double border บน row แรก
  - CSS transition ไม่รองรับ `height: auto` — ใช้ `max-height` transition แทน (ตั้งค่าสูงพอ 3200px)
  - `everOpen` flag สำหรับ lazy render accordion panel — panel ไม่ unmount เมื่อ collapse ทำให้ form state คงอยู่
  - Badge ต้องใช้ eager `useEffect` (ไม่ gate ด้วย everOpen) — ถ้า gate badge จะแสดง `—` จนกว่าจะ click
  - Ant2 web container ใช้ `COPY dist` ใน Dockerfile (bake pattern) — ต้อง `docker compose build web` ก่อน `up -d` ทุกครั้ง `restart` ไม่มีผล

---

## [2026-05-10] ingest | Custom SelectBox — Portal Dropdown Pattern

- Source file: raw/custom-selectbox-portal-dropdown.md
- Summary page: wiki/sources/2026-05-10-custom-selectbox-portal-dropdown.md
- Pages created: [[custom-dropdown-portal-pattern]]
- Pages updated: none (new standalone UI pattern, not cross-cutting WAF/NGINX domain)
- Key insights:
  - `w-full` inside `position: fixed` resolves to viewport width — the containing block for % widths in fixed elements is the viewport, not the nearest parent; fix is `block` + `whitespace-nowrap` (no `w-full`)
  - `createPortal(content, document.body)` is the only reliable z-index escape — even z-index:9999 fails when ancestors have stacking contexts via transform/opacity/overflow:hidden
  - `mousedown` not `click` for outside-close handler — `click` causes immediate re-open because trigger's own onClick fires after document click closes it
  - `w-max` on a fixed container with `w-full` children does NOT shrink to content — both interact to produce viewport width; remove both
  - 5-iteration debug trace: icon overlap → appearance-none → absolute hidden → w-max viewport-wide → final `block whitespace-nowrap` fix

---

## [2026-05-09] ingest | Ant2 v2.4.12–v2.4.15 Session

- Source file: raw/ant2-v2412-v2415-session.md
- Summary page: wiki/sources/2026-05-09-ant2-v2412-v2415-session.md
- Pages updated: [[Ant2-Proxy-Security-Manager]] (version v2.4.15, jail settings table, v2.4.12–v2.4.15 changes), [[waf-validation-testing]] (owaps.ps1 v2 SECURE/BROKEN/JAILED/REDIR categories + .exe), [[auto-jail-pipeline]] (intervals corrected, post_jail_count branch added)
- Key insights:
  - pollAttacks 10s + ingest 10s = ~20s worst-case jail latency
  - post_jail_count counts access log 423s via Redis byte-position watermark
  - `reason` field "Auto-jailed: N attacks" is snapshot for 3-tier counter
  - owaps.ps1 JAILED (423) excluded from pass rate — unverifiable
  - PS2EXE compiled to 33.5KB owaps.exe

---

## [2026-05-09] ingest | Server 184 Incident Response

- Source file: raw/ant2-server-184-incident.md
- Summary page: wiki/sources/2026-05-09-ant2-server-184-incident.md
- Pages updated: [[Ant2-Proxy-Security-Manager]] (server table)
- Key insights:
  - NPM logs unbounded → 13GB on 29GB disk → 100% full → MariaDB and Docker exec both fail
  - Docker network isolation: separate compose projects = separate networks = ETIMEDOUT
  - bcrypt hash `$2b$13$...` silently corrupted by bash `$` expansion in double-quoted `-e "..."` — pipe SQL via stdin
  - Always SELECT back and checkpw() before reporting password reset success

---

## [2026-05-09] ingest | Ant2 Request Flow Diagram — Full Pipeline

- Source file: raw/ant2-request-flow-diagram.md
- Summary page: wiki/sources/2026-05-09-ant2-request-flow-diagram.md
- Pages created: [[request-flow-layers]]
- Pages updated: [[auto-jail-pipeline]] (corrected intervals: poll 10s, ingest rate 10s, release 30s; default threshold 10; added post_jail_count branch and countPostJailHits)
- Key insights:
  - Geo block (layer 3, rewrite phase) fires before ModSecurity (layer 4, access phase) — post-jail requests never touch CRS
  - Worst-case time to jail = ~20 s (ingest 10s + poll 10s)
  - 429 rate-limit does NOT feed jail counter — only 403+rule_ids do
  - `$` in bcrypt hashes silently corrupted by bash double-quote expansion; SQL must be piped via stdin

---

## [2026-05-05] note | Wiki initialized

- Schema created: CLAUDE.md
- Index created: index.md
- Log created: log.md (this file)
- Folder structure: raw/, raw/assets/, wiki/sources/, wiki/entities/, wiki/concepts/, wiki/analyses/
- Domain: NGINX + OWASP CRS WAF — architecture, configuration, tuning, attack patterns, deployment, security operations
- Status: empty wiki, ready for first ingest

---

## [2026-05-05] ingest | OWASP CRS | OWASP Foundation

- Source file: raw/OWASP CRS  OWASP Foundation.md
- Summary page: wiki/sources/2026-05-05-owasp-crs-owasp-foundation.md
- Pages updated: [[OWASP-CRS]], [[false-positive-false-negative-tradeoff]]
- Pages created: [[OWASP-CRS]], [[waf-rule-sets]] (referenced, not yet a full page)
- Key insight: "minimum of false alerts" is a stated design priority, not just a goal

---

## [2026-05-05] ingest | F5 WAF for NGINX

- Source file: raw/F5 WAF for NGINX.md
- Summary page: wiki/sources/2026-05-05-f5-waf-for-nginx.md
- Pages created: [[F5-NGINX-WAF]]
- Key insight: product rebranded from "NGINX App Protect WAF" — search older docs under that name

---

## [2026-05-05] ingest | CRS Releases v4.20–v4.26

- Source file: raw/Releases · corerulesetcoreruleset.md
- Summary page: wiki/sources/2026-05-05-crs-releases-v4-20-to-v4-26.md
- Pages updated: [[OWASP-CRS]], [[crs-rule-numbering]], [[false-positive-false-negative-tradeoff]]
- Pages created: [[crs-rule-numbering]]
- Key insight: CVE-2026-33691 — whitespace padding bypass in PHP/JSP upload rules, fixed v4.25.0 LTS

---

## [2026-05-05] ingest | Ant2 Proxy Security Manager — PROGRESS.md

- Source file: raw/PROGRESS.md
- Summary page: wiki/sources/2026-05-05-ant2-progress.md
- Pages created: [[Ant2-Proxy-Security-Manager]], [[paranoia-levels]], [[platform-presets]], [[bypass-presets]], [[geoip-country-blocking]]
- Pages updated: [[OWASP-CRS]], [[ModSecurity]]
- Key insight: 17 platform presets + 10 bypass presets; Next.js preset (8 rules) directly relevant to planned integration

---

## [2026-05-05] ingest | Ant2 Proxy Security Manager — CHANGELOG.md

- Source file: raw/CHANGELOG.md
- Summary page: wiki/sources/2026-05-05-ant2-changelog.md
- Pages created: [[inotify-write-order-pattern]], [[rate-limiting-nginx]]
- Pages updated: [[Ant2-Proxy-Security-Manager]], [[geoip-country-blocking]]
- Key insight: WAF conf must be written before nginx conf (inotify race); ip-api.com free tier is HTTP-only

---

## [2026-05-06] ingest | Ant2 v2.3.5→v2.3.6-a1 Release Notes

- Source file: raw/v2.3.6-a1-release-notes.md
- Summary page: wiki/sources/2026-05-06-ant2-v2361-release-notes.md
- Pages updated: [[Ant2-Proxy-Security-Manager]] (version → 2.3.6-a1, features list), [[rate-limiting-nginx]] (normalizeRate fix, 429 page), [[platform-presets]] (Magento preset + CSP note)
- Pages created: [[server-header-disclosure]], [[wysiwyg-iframe-editor]]
- Package built: ant2ProxySecurityManager-v2.3.6-a1.tar.gz (852 KB)
- Key insight: contentEditable cannot render full-page CSS — iframe designMode is the correct pattern for editing complete HTML documents in-browser

---

## [2026-05-06] ingest | OWASP CRS Script Test POC — owaps.ps1

- Source file: raw/OWASP_SCRIPT_TEST_POC.md
- Summary page: wiki/sources/2026-05-06-owasp-crs-script-test-poc.md
- Pages created: [[waf-validation-testing]]
- Pages updated: none (no existing page covers WAF black-box testing methodology)
- Key insight: abpmart.com 40.74% pass rate is not a real WAF failure — all "NOT PASS" are HTTP 301 redirects from testing http:// instead of https://; kasikornbank.com 85.19% is IP-blocked at network level, not WAF-validated; NoSQL payloads broken by PowerShell $ expansion

---

## [2026-05-07] ingest | Ant2 v2.4.1→v2.4.3 Session Notes

- Source file: raw/2026-05-07-ant2-v242-v243-session-notes.md
- Summary page: wiki/sources/2026-05-07-ant2-v242-v243-session.md
- Pages created: [[crs-rule-scope]], [[custom-waf-rules]]
- Pages updated: [[waf-validation-testing]] (curl -g pitfall, CRS scope mismatch pitfall, 400 as PASS, NGINX 301 bypass detail), [[ModSecurity]] (NGINX redirect bypass, v3 vs v2 benchmark, Coraza note), [[Ant2-Proxy-Security-Manager]] (version → v2.4.3, deployment table, custom rules section)
- Index updated: new source row, 2 new concept rows, Ant2 version bumped
- Key insights:
  - CRS 933110/933120/921110 do not inspect GET ARGS for their respective payload types — gaps require custom rules
  - NGINX `return 301` fires before ModSecurity phase 1 — HTTP payloads bypass WAF entirely
  - curl URL globbing silently corrupts `[$ne]`/`[$gt]` NoSQL payloads without `-g` flag
  - install.sh had a 3-state CRS dir logic bug that left WAF broken on upgrade scenarios
  - Final test score: 27/27 = 100% on bitec-registor.thailandpages.com (PL4, block mode, threshold 2)

---

## [2026-05-09] ingest | Ant2 v2.4.8–v2.4.11 — Jail/Block Pipeline Fixes

- Source file: raw/ant2-v248-v2411-session.md
- Summary page: wiki/sources/2026-05-09-ant2-v248-v2411-session.md
- Pages created: [[auto-jail-pipeline]]
- Pages updated: [[Ant2-Proxy-Security-Manager]] (version → v2.4.11, all 3 servers), [[waf-validation-testing]] (new pitfall: testing while jailed, updated PASS code table with 423/JAILED)
- Index updated: new source row, new concept row (auto-jail-pipeline), Ant2 version bumped to v2.4.11
- Key insights:
  - Default server `_default_site.conf` had no geo block — null-Host requests bypassed all jail/IP block rules entirely
  - IP block deletion must also delete from `ip_jail` + clear Redis counter, otherwise jail entry keeps nginx blocking
  - `row2host()` wrapper was missing from `ipblock.js` — raw SQLite rows passed to `writeHostConfig()` caused silent malformed configs
  - `reloadNginxNow()` bypasses inotify debounce latency by calling `docker exec ant2proxy-waf nginx -s reload` directly
  - `ingestWafLogs()` was lazy (UI-triggered only) — `pollAttacks()` never had new rows in `waf_events` → zero auto-jails despite real WAF blocks. Fix: `pollAttacks()` now drives ingestion itself
  - Testing while IP is jailed (baseline 423) makes WAF rule verification impossible — script now tracks 423 as JAILED category, not PASS or NOT PASS

---

## [2026-05-07] ingest | Ant2 v2.4.4 — WAF Port 80 Bypass Fix

- Source file: raw/2026-05-07-ant2-v244-waf-port80-fix.md
- Summary page: wiki/sources/2026-05-07-ant2-v244-waf-port80-fix.md
- Pages created: [[waf-proxy-pass-scope]]
- Pages updated: [[Ant2-Proxy-Security-Manager]] (version → v2.4.4, server status table), [[ModSecurity]] (new warning: WAF scope per server block), [[waf-validation-testing]] (pitfall #8: WAF UI mode ≠ WAF active on all ports)
- Index updated: new source row, new concept row, Ant2 version bumped to v2.4.4
- Key insights:
  - `force_https=true` port 80 server block was missing `modsecurity on` — silent WAF bypass for all CF proxy traffic on port 80 across all servers
  - WAF UI "Block mode" gives false confidence — actual `modsecurity on` presence in each server block must be verified with `nginx -T`
  - Architectural rule established: WAF follows `proxy_pass`, not SSL — every server block with `proxy_pass` needs `modsecurity on`
  - Two-layer fix: code fix in `nginxConfig.js` + live patch on server 181 host_5; servers 180/238 still need rebuild
