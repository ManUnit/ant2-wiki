---
title: "WAF Validation Testing"
type: concept
tags: [waf-testing, validation, owasp-crs, curl, false-negative, methodology]
sources: [2026-05-06-owasp-crs-script-test-poc, 2026-05-07-ant2-v242-v243-session, 2026-05-09-ant2-v248-v2411-session, 2026-05-09-ant2-v2412-v2415-session]
created: 2026-05-06
updated: 2026-05-09
---

# WAF Validation Testing

Methodology and pitfalls for testing whether a WAF correctly blocks [[OWASP-CRS]] attack categories. Based on analysis of `owaps.ps1` — a 27-test PowerShell validation script run against real targets.

## What "PASS" Actually Means

A WAF test PASS means the server returned a blocking status code for a known-malicious payload:

| HTTP Code | Meaning |
|-----------|---------|
| `403` | WAF blocked the request (ModSecurity default) |
| `406` | WAF blocked — Not Acceptable |
| `000` | curl: no response / connection refused |

A "PASS" from HTTP 000 is **ambiguous** — it could mean:
- The WAF dropped the connection (genuine block), OR
- The target IP is blocked by Cloudflare/firewall (network-level, not WAF)

## Common Testing Pitfalls

### 1. HTTP vs HTTPS — the 301 Problem

Testing `http://target.com` when the site forces HTTPS causes every request to return 301 — before the WAF can inspect the payload. All results appear as "NOT PASS" even if the WAF would have blocked them over HTTPS.

This is not just a test script issue — NGINX `return 301 https://...` in the port 80 server block fires *before* ModSecurity phase 1. Payloads sent over HTTP **never reach the WAF** even when ModSecurity is enabled on that server block. ([[2026-05-07-ant2-v242-v243-session]])

**Fix**: Always test with `https://`. Validate that the test script rejects `http://` at startup.

### 2. curl URL Globbing Corrupts NoSQL Payloads

curl treats `[...]` in URLs as glob patterns by default. NoSQL injection payloads like `?id[$ne]=1` are silently malformed — the `[$ne]` portion is consumed as a glob range — resulting in HTTP 000 or a completely different URL being sent.

**Fix**: Always pass `-g` (`--globoff`) to curl when testing NoSQL payloads. ([[2026-05-07-ant2-v242-v243-session]])

```powershell
# WRONG — curl treats [$ne] as glob range → malformed URL
& curl -s -o NUL -w "%{http_code}" "$url`?id[$ne]=1"

# CORRECT — -g disables URL globbing
& curl -g -s -o NUL -w "%{http_code}" "$url`?id[$ne]=1"
```

### 3. CRS Rule Scope Mismatch — False Confidence

A payload may return HTTP 200 (WAF bypass) not because the WAF is misconfigured, but because the claimed CRS rule inspects a *different collection* than where the payload lives. This is the most subtle and dangerous testing pitfall.

Three specific cases confirmed in [[2026-05-07-ant2-v242-v243-session]]:

| Test Payload | Claimed Rule | Why it NEVER fires |
|---|---|---|
| `?file=shell.php` | CRS 933110 | 933110 inspects `FILES`/`X-Filename` (multipart upload), not `ARGS` |
| `?file=shell.php.jpg` | CRS 933120 | 933120 checks `ARGS` for PHP *config directive names*, not filename patterns |
| `?redirect=https://evil.com` | CRS 921110 | 921110 is HTTP Request Smuggling detection, not open redirect |

**Fix**: Verify the rule's actual target collection in the CRS source file before assuming a test failure is a WAF gap. See [[crs-rule-scope]] for full analysis. Where a genuine gap exists, add a [[custom-waf-rules|custom rule]].

> [!warning] Never Change Payloads to Force a Pass
> The correct response to a false-negative is to either (a) verify the rule scope and find the right payload, or (b) add a custom WAF rule to cover the gap. Changing a test payload to trigger a *different* rule that happens to fire is not a valid fix — it defeats the purpose of the test.

### 4. Testing While IP is Jailed Contaminates All Results

If the test IP was auto-jailed by a previous pentest run, the baseline check returns HTTP 423. Subsequent attack tests also return 423 — but these are jail blocks, not WAF rule blocks. The script cannot determine whether specific WAF rules would have fired.

**Evidence** ([[2026-05-09-ant2-v248-v2411-session]]): a full 27-test pentest showed mixed 403/423/000 results. Tests that returned 423 were NOT verified WAF blocks — they were blocked by the jail geo directive before ModSecurity could run (or before nginx could respond with 403).

**Diagnosis**: If baseline ≠ HTTP 200, release the test IP from the management panel before re-running.

**Script behavior**: `owaps-v2.ps1` now:
- Prints a prominent warning if baseline is 423 ("IP is in jail")
- Tracks 423 responses as a separate `JAILED` category (purple/magenta), not PASS or NOT PASS
- Shows `NOTE: N test(s) returned 423 — release your IP and re-run` in the summary

**Prevention**: Whitelist the test IP in the proxy config (or set a very high jail threshold / disable auto-jail) before running automated pentests.

### 5. HTTP 000 ≠ WAF Block

If curl returns 000 for every single test case on a target, the IP is likely blocked at network level (CDN, Cloudflare firewall, IP reputation blacklist). The WAF is never reached.

**Diagnosis**: Test one benign URL first (`/`, `/robots.txt`). If it also returns 000, network-level blocking is the cause.

### 5. Shell Variable Expansion in Payloads

PowerShell (and bash) expand `$` in double-quoted strings. NoSQL payloads like `?id[$ne]=1` become `?id[]=1` — invalid and unable to trigger the rule.

```powershell
# WRONG — PowerShell expands $ne to empty
"?id[$ne]=1"

# CORRECT — single-quote is literal
'?id[$ne]=1'
```

### 6. GET-only Testing Misses Most Real Attacks

SQLi, XSS, and command injection most commonly arrive in POST bodies, JSON payloads, XML, or headers — not URL query strings. GET-based testing validates rule coverage but not deployment completeness.

**Better coverage**: Add POST tests with `Content-Type: application/json` and `application/x-www-form-urlencoded` bodies.

### 8. WAF UI Mode ≠ WAF Active on All Ports

The WAF mode shown in a proxy manager GUI ("Block mode", "Detection Only") reflects the *database setting* — not whether `modsecurity on` is present in every active server block. A host can show "Block mode" while port 80 traffic is entirely uninspected, because the GUI setting and the generated NGINX config are two separate things.

**Confirmed case** ([[2026-05-07-ant2-v244-waf-port80-fix]]): [[Ant2-Proxy-Security-Manager]] `force_https=true` hosts had WAF active on port 443 but missing on port 80. Cloudflare connects to origin on port 80 → proxy fires → no ModSecurity. GUI showed Block mode throughout.

**Validation**: To confirm WAF is active on a given port, check the actual generated NGINX config (`nginx -T | grep modsecurity`) for each server block that contains `proxy_pass`.

### 7. Basic Payloads Miss Evasion Techniques

The standard test payloads (`?id=1 UNION SELECT`, `<script>alert(1)</script>`) are caught by PL1 rules. More sophisticated attacks use:
- Double URL encoding: `%253Cscript%253E`
- Case mixing: `<ScRiPt>`
- Comment obfuscation: `1/**/UNION/**/SELECT`
- Unicode normalization: `＜script＞`

Only catching basic payloads does not mean the WAF is tuned against evasion.

## PASS Code Reference

| HTTP Code | Category | Meaning |
|-----------|----------|---------|
| `403` | PASS | WAF blocked — ModSecurity default deny |
| `406` | PASS | WAF blocked — Not Acceptable (some CRS configurations) |
| `400` | PASS | WAF blocked — Bad Request; returned by CRLF injection blocks (rule 921160) |
| `000` | PASS | curl: no response / connection dropped — ambiguous |
| `423` | JAILED | Blocked by IP jail or GeoIP — WAF rule NOT verified |
| `301/302` | REDIRECT | HTTP→HTTPS redirect — WAF not reached |
| `200` | NOT PASS | Request passed through — WAF rule did not fire |

> [!note] 400 is a valid PASS for CRS 921160 (Host CRLF injection). If 400 is not in the PASS list, this test case will always fail incorrectly. ([[2026-05-07-ant2-v242-v243-session]])

> [!note] 423 is distinct from 403. In [[Ant2-Proxy-Security-Manager]], 423 = jail/GeoIP block applied at nginx geo level before WAF processing. A 423 means the attacker IS blocked, but it does not confirm the specific WAF rule fired. ([[2026-05-09-ant2-v248-v2411-session]])

## Correct Interpretation of owaps.ps1 Results

| Result on abpmart.com | Actual meaning |
|-----------------------|----------------|
| `301 NOT PASS` | HTTP→HTTPS redirect; WAF not tested |
| `403 PASS` | WAF correctly blocked over HTTP |
| `400 PASS` | WAF blocked CRLF injection (rule 921160) |
| `000 PASS` | Likely blocked (no connection) — ambiguous |
| NoSQL empty NOT PASS | Broken payload (curl globbing without `-g` flag) |

## Minimum Reliable Test Setup

```powershell
# Use https://
$TargetUrl = "https://target.com"

# Single-quote all payloads containing $
@{ Payload = '?id[$ne]=1' }

# Follow redirects to reach the actual app
$StatusCode = & curl -k -s -L -o NUL -w "%{http_code}" "$Url"

# Verify the baseline first
$BaselineCode = & curl -k -s -o NUL -w "%{http_code}" "$TargetUrl/"
# If baseline = 000, all results are meaningless
```

## Attack Categories Covered by owaps.ps1

See [[crs-rule-numbering]] for full rule range reference.

| Category | CRS Group | Rules Tested |
|----------|-----------|-------------|
| SQL Injection | REQUEST-942 | 942100, 942110, 942150, 942200, 942290, 942390 |
| XSS | REQUEST-941 | 941100, 941120, 941130, 941160, 941180 |
| LFI / Path Traversal | REQUEST-930 | 930100, 930110, 930120 |
| RCE / CMD injection | REQUEST-932 | 932100, 932105, 932110, 932130, 932160 |
| File upload | REQUEST-933 | 933110, 933120 |
| HTTP injection | REQUEST-921 | 921110, 921150, 921160 |

## owaps.ps1 / owaps.exe — Result Categories (v2, 2026-05-09)

Rewritten pentest script with four explicit categories replacing raw HTTP codes:

| Badge | HTTP codes | Meaning |
|-------|-----------|---------|
| `[  SECURE  ]` | 400, 403, 406, 000 | WAF blocked — rule verified |
| `[  JAILED  ]` | 423 | Geo-blocked — WAF rule NOT verified |
| `[  REDIR   ]` | 301, 302 | Redirect — WAF not reached |
| `[!!BROKEN!!]` | 200, 500, other | Attack passed through |

**Rate calculation** excludes JAILED and REDIRECT from both numerator and denominator. Only SECURE and BROKEN count toward the pass rate.

**Baseline check**: if `GET /` returns 423, script prints red alarm ("IP IS IN JAIL") and marks all results JAILED.

**Compiled form**: `owaps.exe` (33.5 KB) — PS2EXE wrapper, runs on any Windows machine without PowerShell module requirements. Usage: `owaps.exe https://target.com`

**Banner**: `Ant2cloud OWASP WAF Pentester v2.4.15`

([[2026-05-09-ant2-v2412-v2415-session]])

## See Also

- [[crs-rule-scope]]
- [[custom-waf-rules]]
- [[request-flow-layers]]
- [[OWASP-CRS]]
- [[false-positive-false-negative-tradeoff]]
- [[crs-rule-numbering]]
- [[paranoia-levels]]
- [[Ant2-Proxy-Security-Manager]]
- [[2026-05-06-owasp-crs-script-test-poc]]
- [[2026-05-07-ant2-v242-v243-session]]
