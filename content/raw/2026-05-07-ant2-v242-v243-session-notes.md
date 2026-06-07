# Ant2 v2.4.1→v2.4.3 Session Notes — 2026-05-07

## Context
Working session covering WAF test methodology fixes, CRS rule scope analysis, custom rule development, and multi-server deployment of v2.4.2 and v2.4.3.

---

## 1. WAF Test Script Fixes (owaps.ps1 / owaps-v2.ps1)

### Problems found in original owaps.ps1
- No https:// enforcement — http:// requests hit NGINX `return 301` redirect BEFORE ModSecurity sees the payload. All attack tests returned HTTP 301 = "NOT PASS" but WAF was never reached.
- `curl` without `-g` flag interprets `[$ne]`, `[$gt]` etc. in NoSQL URLs as glob patterns → URL malformed → empty HTTP code → blank result
- 3 payloads mapped to wrong CRS rules (see section 2)
- Host Header test used plain `Host: evil.com` (no CRLF) — correct rule 921160 requires CRLF injection: `Host: evil.com%0d%0aX-Injected:evil`
- HTTP 400 not counted as PASS (Host CRLF block returns 400, not 403)

### Fixes applied
- Added `https://` prefix enforcement (error + exit if http://)
- Added `-g` flag to all curl calls (disables URL globbing)
- Restored original payloads after WAF custom rules were added (see section 3)
- Fixed Host Header test to use CRLF injection
- Added 400 to PASS codes list

---

## 2. CRS Rule Scope Analysis — 3 Failing Tests

All three tests returned HTTP 200 (WAF allowed) with original payloads at PL4. Root causes:

### Rule 933110 — test payload `?file=shell.php`
- **CRS actual scope**: Checks `FILES|REQUEST_HEADERS:X-Filename|X_Filename|X.Filename|X-File-Name` — multipart file upload headers only
- **Why it fails**: GET ARGS (`?file=...`) are not in the checked targets
- **Fix**: Custom rule 9500101 — check ARGS for PHP extension pattern

### Rule 933120 — test payload `?file=shell.php.jpg`
- **CRS actual scope**: Checks ARGS for PHP *configuration directive names* (`allow_url_fopen`, `open_basedir`, `safe_mode`, etc.)
- **Why it fails**: `shell.php.jpg` contains no PHP config directive names — it's a filename pattern
- **Fix**: Custom rule 9500102 — check ARGS for PHP double extension pattern

### Rule 921110 — test payload `?redirect=https://evil.com`
- **CRS actual scope**: HTTP Request Smuggling — looks for embedded HTTP method patterns in ARGS/body (`GET /path HTTP/1.0`)
- **Why it fails**: `https://evil.com` is a plain URL, not an HTTP smuggling pattern. Open redirect is application-level, not WAF-level by default.
- **Fix**: Custom rule 9500103 — check ARGS for external URL in redirect-like parameter names

---

## 3. Custom WAF Rules Added

Added to `nginx-waf/modsecurity-engine.conf` (global — applies to ALL hosts on any server):

```
# PHP file extension in GET/POST ARGS (upload bypass via query param)
SecRule ARGS "@rx \.ph(?:p[0-9]?|tml|ar)(\s*$|%00)" \
    "id:9500101,phase:2,deny,status:403,log,..."

# PHP double extension in ARGS (e.g. shell.php.jpg)
SecRule ARGS "@rx \.ph(?:p[0-9]?|tml|ar)\.[a-z]{2,4}($|%00)" \
    "id:9500102,phase:2,deny,status:403,log,..."

# Open redirect — external URL in redirect/url/return/goto parameters
SecRule ARGS "@rx (?i)^https?://[^/]" \
    "id:9500103,phase:2,chain,deny,status:403,log,..."
  SecRule MATCHED_VAR_NAME "@rx (?i)(?:redirect|^url$|return|next|goto|target|dest(?:ination)?|forward)" ""
```

Rule IDs 9500101–9500103 are in the custom/local namespace (9xxxxx).

---

## 4. ModSecurity v3 (NGINX) vs v2 (Apache) Research Findings

- ModSec v2 (Apache mod_security2): processes request in-process before redirect decisions. CRS v2.2.x with threshold 10 blocked >95% of Nikto.
- ModSec v3 (NGINX connector libmodsecurity3): benchmark shows ~94.5% TPR with CRS v4, 0.41% FPR.
- NGINX `return 301 https://...` in port 80 server block fires BEFORE ModSecurity phase 1. HTTP payloads bypass WAF entirely unless ModSecurity is also enabled on port 80 block.
- Coraza (Go-based) passes 100% of CRS v4 test suite; alternative to ModSec v3.
- Missing operators in ModSec v3: some v2 operators not supported; most critical CRS operators work.

---

## 5. Version History — v2.4.1 to v2.4.3

### v2.4.1
- WAF UI: replaced duplicate Security Level UI (presets + PL buttons) with single 4-preset block: Standard (PL1), Balanced (PL2), Strict (PL3), Maximum (PL4/threshold 2)
- owaps-v2.ps1 created: 27 tests, https:// required, -g flag, correct payloads for 3 rules

### v2.4.2
- Added 3 custom rules to modsecurity-engine.conf (global, all hosts)
- Restored original test payloads in owaps.ps1 (WAF now actually blocks them)
- Deployed to: 172.20.20.180, 172.20.20.181 (fresh install), 192.168.0.238 (upgrade)

### v2.4.3
- Fixed install.sh bug: `elif` branch handles "CRS dir exists but crs-setup.conf missing" (upgrade scenario)
- Added post-deploy container safety net: after `docker compose up`, exec into WAF container to activate CRS and reload nginx if conf is missing

---

## 6. install.sh CRS Activation Bug (v2.4.2 → v2.4.3)

### Symptom
After upgrading 192.168.0.238 (had old `ngx-*` install), WAF showed "Config Error":
```
/etc/modsecurity.d/owasp-crs/crs-setup.conf: Not able to open file
```

### Root cause
`/opt/modruls_crs/` existed from old installation with `crs-setup.conf.example` but NOT `crs-setup.conf`. The install.sh logic only had two paths:
1. `crs-setup.conf` exists → skip (safe)
2. Directory doesn't exist → download + extract + activate

Missing path: directory exists, `crs-setup.conf.example` present, but `crs-setup.conf` absent.

### Fix (v2.4.3)
Added `elif` branch:
```bash
elif [ -f "${CRS_HOST_DIR}/crs-setup.conf.example" ]; then
  cp "${CRS_HOST_DIR}/crs-setup.conf.example" "${CRS_HOST_DIR}/crs-setup.conf"
  success "CRS activated from example"
fi
```
Plus post-deploy safety net that execs into the WAF container to fix and reload if still broken.

---

## 7. Multi-Server Deployment

| Server | Previous | After | Method |
|--------|----------|-------|--------|
| 172.20.20.180 | v2.4.1 | v2.4.2 | docker compose up --build (docker group) |
| 172.20.20.181 | none | v2.4.2 | sudo docker compose up --build (fresh) |
| 192.168.0.238 | ngx-* (old) | v2.4.2 → v2.4.3 fix | docker group, manual steps |

### Server 181 challenge
- anan not in docker group; sudoers broken (`NOPASWD` typo → should be `NOPASSWD`)
- User fixed sudoers manually via console access
- Deployed with `sudo docker compose up --build`

### Server 192.168.0.238 challenge
- Old install at `/opt/nginx-gui` with project name `ngx-*`
- Upgraded in-place: preserved `.env`, stopped old containers, replaced files, relaunched as `ant2proxy-*`
- Hit CRS activation bug (see section 6)

---

## 8. Final WAF Test Results

Target: `https://bitec-registor.thailandpages.com` (host_16, Block mode, PL4, threshold 2)

```
27/27 = 100% PASS
```

All attack categories blocked: SQLi, XSS, LFI, Path Traversal, RCE/CMD, PHP Upload, Open Redirect, CRLF, HTTP Smuggling, NoSQL injection.
