# NGINX GUI Proxy + WAF — Development Progress

> Last updated: 2026-05-03 — **v2.2 Released**

---

## 🚀 Version 2.2 Release — May 3, 2026

### Critical Bug Fixes
- 🔧 **HTTP 451 → 423** — Browser was intercepting HTTP 451 and showing its own error page
  - **Solution**: Changed to HTTP 423 (Locked) which browsers render as custom HTML
  - Uses `return 423` inside `if` block + `error_page 423 @country_blocked;`
  - Named location `@country_blocked` serves custom HTML with `rewrite ^ /country-blocked.html break;`

- 🔧 **Global Country Blocking Not Working** — FK constraint on `country_rules` table
  - **Problem**: `country_rules.host_id` references `hosts(id)` — `host_id=0` violates FK
  - **Solution**: Created separate `global_country_rules` table without FK dependency
  - Global mode now correctly applies to ALL domains without per-host setup

- 🔧 **Per-host "off" Ignoring Global Rules** — Logic short-circuited too early
  - **Problem**: `buildCountryBlockConf()` returned empty when host mode was 'off'
  - **Solution**: Check global mode + rules even when per-host is 'off'

- 🔧 **2-Stage Country Map** — Fixed detection for DNS Only (non-proxied) hosts
  - **Problem**: Single map using only `$http_cf_ipcountry` fails when no Cloudflare
  - **Solution**: Stage 1 picks CF header or GeoIP2 fallback; Stage 2 does block/allow

### UI Fixes
- 🔧 **Red Dot Indicator** — Now updates immediately after saving rules (no page reload)
- 🔧 **GeoIP.jsx** — `setHosts()` state updated inline after successful PUT

### Infrastructure
- 🔧 **Docker Volumes** — Added explicit `name: ant2proxy_*` to prevent data loss
- 🔧 **nginx.conf** — Removed debug variables (`$effective_country_1`) from log format

### Package
- 📦 **ant2ProxySecurityManager-v2.2.tar.gz** (285KB)
- Pre-compiled web frontend (no source code shipped)
- Includes all fixes above

---

## 🔧 Version 2.1 Hotfix — May 2, 2026

### Critical Bug Fixes
- 🔧 **Country Blocking Now Works Behind Cloudflare** — Fixed GeoIP detection
  - **Problem**: Country blocking read Cloudflare proxy IP instead of real client IP
  - **Solution**: Integrated nginx `geoip2` module to read country from `$http_cf_connecting_ip`
  - Added `nginx-module-geoip2` to nginx-waf Dockerfile
  - Updated nginx.conf to load geoip2 module and read GeoLite2-Country.mmdb
  - Changed country map from `$http_cf_ipcountry` to `$geoip2_data_country_code`
  - Mounted GeoIP database volume to nginx-waf container (read-only)
  - **Result**: Country blocking now correctly identifies client country even behind Cloudflare proxy

### Technical Changes
- `nginx-waf/Dockerfile`: Build geoip2 module from source (GitHub: leev/ngx_http_geoip2_module)
  - **Build Fix**: Package `nginx-module-geoip2` not available in repos
  - Compile dynamically against matching nginx version
  - Install to `/etc/nginx/modules/ngx_http_geoip2_module.so`
- `nginx-waf/nginx.conf`: Added geoip2 module load + database config
- `docker-compose.yml`: Mounted geoip_data volume to nginx-waf (read-only)
- `api/src/services/nginxConfig.js`: Changed map source to `$geoip2_data_country_code`

### Testing
- Verified country blocking works with real client IP (124.120.207.64 → Thailand)
- Tested block Thailand → correctly returns 403
- Tested block US → correctly blocks US traffic through Cloudflare

---

## 🎉 Version 2.0 Release — May 2, 2026

### New Features
- ✅ **Redis 7** caching layer with password auth (128MB LRU)
- ✅ **GeoIP Country Database** (db-ip.com mmdb) with Redis-cached lookups
- ✅ **Per-Host Country Blocking** — block/allow by country (global + per-host rules)
- ✅ **WAF IP Access Control** — bypass WAF or hard-deny by source IP/CIDR
- ✅ **Default Landing Page** — branded Ant2 page for unmatched domains
- ✅ **GeoIP Management UI** — full-page country selector with live lookup tool

### Critical Fixes (May 2, 2026)
- 🔧 **Let's Encrypt HTTP-01 Challenge** — Fixed ACME validation failures
  - Added `modsecurity off;` in ACME challenge location blocks
  - Added ACME location to default site config
  - Added fallback self-signed cert for hosts without SSL cert
  - Added fallback HTTPS (443) listener for Cloudflare Full SSL mode compatibility
  - **Why**: Cloudflare Full SSL mode connects to origin via port 443. Without a 443 listener, requests went to default site showing landing page instead of proxying to backend.

### Bug Fixes
- Fixed WAF blocking ACME challenge requests (ModSecurity intercept)
- Fixed missing HTTPS server blocks causing Cloudflare SSL errors
- Fixed default site not serving ACME challenges
- Fixed hosts without SSL cert showing landing page when accessed via HTTPS

---

## ✅ Completed Features

### Core Proxy
| Feature | Status | Notes |
|---|---|---|
| Proxy host CRUD | ✅ Done | Add / edit / delete reverse-proxy entries |
| Path rules | ✅ Done | Per-path proxy, redirect (301/302/307/308), static |
| Force HTTPS | ✅ Done | Cloudflare-safe double-variable pattern |
| HTTP/2 | ✅ Done | Toggleable per HTTPS host |
| WebSocket support | ✅ Done | Upgrade headers injected automatically |
| Block common exploits | ✅ Done | Security headers + CSP |
| HSTS | ✅ Done | `Strict-Transport-Security` per domain |
| Custom nginx directives | ✅ Done | Free-text block injected into server config |
| Auto-reload | ✅ Done | `inotifywait` → `nginx -t && nginx -s reload` |

### SSL / TLS
| Feature | Status | Notes |
|---|---|---|
| Manual PEM/CRT upload | ✅ Done | Stored in shared Docker volume |
| Let's Encrypt (ACME) | ✅ Done | `certbot` via API; `skipChallengeVerification: true` |
| Expiry tracking | ✅ Done | `expires_at` column; dashboard badge |

### WAF (ModSecurity + OWASP CRS)
| Feature | Status | Notes |
|---|---|---|
| Per-domain WAF toggle | ✅ Done | On/Off per host |
| 3-way mode: Off / Detect / Block | ✅ Done | `SecRuleEngine Off/DetectionOnly/On` |
| Paranoia Level 1–4 | ✅ Done | Clickable 4-button selector |
| Inbound / Outbound anomaly threshold | ✅ Done | Per domain |
| Custom SecRule directives | ✅ Done | Free-text textarea per domain |
| Manual rule exclusions (by ID) | ✅ Done | Comma-separated `SecRuleRemoveById` |
| **Platform Compatibility Presets** | ✅ Done | Dropdown — 17 platforms, auto-injects exclusions |
| **Bypass Rules (OAuth / Webhooks)** | ✅ Done | 10 checkboxes + custom path textarea |
| **Custom Bypass Paths** | ✅ Done | Per-line URI prefix, `ctl:ruleEngine=Off` |
| Custom 403 block page | ✅ Done | IP reveal, Request ID, rule grid |
| Ant² WAF branding | ✅ Done | Red alert shield, glow animation, sup² |

### WAF Monitor
| Feature | Status | Notes |
|---|---|---|
| Time-series charts | ✅ Done | 1H / 6H / 24H / 7D / 30D / 3M / 1Y ranges |
| Chart tabs | ✅ Done | "Requests" multi-line + "Attack Types" stacked bar |
| "By day" grouping | ✅ Done | Checkbox toggle for daily granularity |
| Stat cards | ✅ Done | Total blocked, detected, top rule, top IP |
| Top rules bar chart | ✅ Done | Horizontal bar, top 10 |
| Audit log table | ✅ Done | Newest-first, paginated |
| DB-backed history | ✅ Done | SQLite `waf_events` table, parsed on each API call |
| Attack categories | ✅ Done | XSS / SQLi / RCE / LFI / RFI / Proto |

### Infrastructure
| Feature | Status | Notes |
|---|---|---|
| Timezone Asia/Bangkok | ✅ Done | All containers `TZ=Asia/Bangkok` + tzdata |
| JSON access logs | ✅ Done | Per-host structured log format |
| WAF audit logs | ✅ Done | Per-host `/var/log/nginx/waf/host_N.log` |

---

## 🔧 Platform Compatibility Presets (17 platforms)

When selected, auto-injects `SecRuleRemoveById` rules to fix common CRS false positives:

| Key | Platform | Category | Rules Excluded |
|---|---|---|---|
| `wordpress` | WordPress | CMS | 50+ rules — Gutenberg editor, WooCommerce, shortcodes |
| `laravel` | Laravel (PHP) | Framework | 15 rules — CSRF token, Eloquent ORM, signed URLs |
| `php` | PHP generic | Language | 12 rules — PHP function names in form data |
| `php_fpm` | PHP-FPM / FastCGI | Language | 14 rules — SCRIPT_FILENAME, PATH_INFO conflicts |
| `nodejs` | Node.js (Express/Fastify) | Language | 8 rules — application/json, REST methods |
| `python` | Python (Django/Flask/FastAPI) | Language | 9 rules — CSRF token, DRF content-type |
| `nextjs` | Next.js (Vercel) | Framework | 8 rules — API routes, server actions, _next params |
| `spring_boot` | Java Spring Boot | Framework | 13 rules — JSON, REST methods, Spring CSRF |
| `dotnet` | .NET / ASP.NET Core | Framework | 12 rules — ViewState, serialization, CSRF |
| `asp_classic` | ASP Classic (VBScript) | Framework | 11 rules — VBScript triggers Perl detection |
| `java` | Java (J2EE / Jakarta EE) | Language | 8 rules — Java serialization/deserialization |
| `tomcat` | Apache Tomcat | App Server | 9 rules — Java rules + JSP EL expressions |
| `sap` | SAP (NetWeaver/HANA/Fiori) | Enterprise | 10 rules — Java serialization, OData |
| `perl` | Perl (CGI/Dancer2/Mojo) | Language | 6 rules — Perl syntax misfires |
| `apache` | Apache HTTP Server | Web Server | 1 rule — mod_rewrite request-line |
| `nginx_app` | Nginx (as upstream) | Web Server | 0 rules — CRS is optimized for Nginx |
| `iis` | IIS Windows | Web Server | 11 rules — Windows paths, .asp/.aspx extension |

---

## 🔓 Bypass Presets (10 presets)

Inserts `SecRule REQUEST_URI ... ctl:ruleEngine=Off` **before** CRS rules to prevent false blocks:

| Key | Use Case | Rules Fixed |
|---|---|---|
| `google_oauth` | Google Login / OAuth2 callback | 920120, 941100, 942100 (scope=googleapis.com in URL) |
| `nextauth` | NextAuth.js / Auth.js all providers | `/api/auth/*` — covers all NextAuth providers |
| `facebook_oauth` | Facebook OAuth2 callback | Long state/code params resemble SQLi |
| `github_oauth` | GitHub OAuth2 callback | auth code values trigger 932150 (RCE) |
| `microsoft_oauth` | Microsoft / Azure AD / OIDC | JWT id_token in POST triggers 941100/942100/920230 |
| `saml_sso` | SAML SSO Assertion POST | base64 SAMLResponse triggers 920230/941100 |
| `line_oauth` | LINE Login OAuth | Common in Thai/Asian web apps |
| `stripe_webhook` | Stripe Webhook delivery | Payment fields trigger SQLi/XSS rules |
| `github_webhook` | GitHub Webhook delivery | Code diff in payload triggers injection rules |
| `paypal_webhook` | PayPal IPN / REST Webhook | Payment notifications trigger injection rules |

---

## 🗂️ File Structure

```
nginx-gui/
├── docker-compose.yml          # 3 services: nginx-waf, api, web
├── .env.example                # JWT_SECRET, ADMIN_USER, ADMIN_PASSWORD
│
├── nginx-waf/                  # ModSecurity + OWASP CRS container
│   ├── Dockerfile
│   ├── entrypoint.sh           # inotifywait auto-reload watcher
│   └── waf-blocked.html        # Custom 403 page (Ant² WAF branding)
│
├── api/                        # Express 4 + better-sqlite3
│   └── src/
│       ├── index.js            # App entry, JWT auth middleware
│       ├── database.js         # SQLite init + migrations
│       ├── wafPresets.js       # Bypass + Platform preset definitions
│       └── routes/
│           ├── hosts.js
│           ├── waf.js          # WAF CRUD + presets endpoint
│           ├── logs.js         # WAF time-series + audit log
│           ├── ssl.js
│           └── letsencrypt.js
│       └── services/
│           ├── nginxConfig.js  # Generates host_N.conf + ModSec conf
│           └── letsencrypt.js
│
└── web/                        # React 18 + Vite + Tailwind CSS 3
    └── src/
        └── pages/
            ├── Dashboard.jsx
            ├── Hosts.jsx
            ├── WAF.jsx         # WAF settings: mode, paranoia, bypass, platform
            ├── WAFMonitor.jsx  # Time-series charts, log table
            ├── SSL.jsx
            ├── Settings.jsx
            └── Login.jsx
```

---

## 🗄️ Database Schema (SQLite)

### `hosts`
```sql
id, domain, upstream, ssl_enabled, ssl_cert_id, force_https, http2,
websocket_support, block_exploits, hsts_enabled, custom_nginx, paths,
enabled, created_at, updated_at
```

### `waf_settings`
```sql
id, host_id, enabled, paranoia_level, inbound_threshold, outbound_threshold,
custom_rules, excluded_rules, mode, bypass_presets, bypass_custom, platform_preset
```

### `waf_events`
```sql
id, unique_id, host_id, ts, status_code, client_ip, method, uri, rule_ids,
cat_xss, cat_sqli, cat_rce, cat_lfi, cat_rfi, cat_proto, cat_other, action
```

### `ssl_certs`
```sql
id, name, domains, cert_path, key_path, chain_path, expires_at, provider, created_at
```

---

## 🚀 Deployment

**Server:** `anan@192.168.0.238`  
**Path:** `/opt/nginx-gui/`  
**Command:**
```bash
sudo docker compose up -d --build
# or rebuild single service:
sudo docker compose up -d --build api
sudo docker compose up -d --build web
sudo docker compose up -d --build nginx-waf
```

---

## 📋 Pending / Future Ideas

- [ ] WAF Monitor: filter by attack category
- [ ] WAF Monitor: export CSV
- [ ] Proxy Hosts: drag-to-reorder
- [ ] SSL: Let's Encrypt wildcard (DNS-01 challenge)
- [ ] Multi-user / role-based access
- [ ] Backup & restore DB via UI
- [ ] Dark mode
