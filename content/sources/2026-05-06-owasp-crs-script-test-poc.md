---
title: "OWASP CRS Script Test POC — owaps.ps1"
type: source
tags: [owasp-crs, waf-testing, powershell, sqli, xss, lfi, rce, nosql, validation]
sources: []
created: 2026-05-06
updated: 2026-05-06
---

## Abstract

A PowerShell WAF validation script (`owaps.ps1`) that fires 27 attack payloads against a target URL and reports which are blocked (HTTP 403/406/000) vs passed through. Includes actual test runs against `abpmart.com` (40.74% pass rate) and `kasikornbank.com` (85.19% pass rate) — both results are misleading due to methodology issues documented below.

## Key Takeaways

- **Script covers 7 OWASP CRS attack categories, 27 test cases** — SQLi (942xxx), XSS (941xxx), LFI/Path traversal (930xxx), RCE/CMD injection (932xxx), File upload (933xxx), HTTP injection/CRLF (921xxx), NoSQL (942290). Good baseline coverage of [[OWASP-CRS]] core rules.
- **abpmart.com 40.74% pass rate is not a real WAF failure** — most "NOT PASS" results are HTTP 301 redirects caused by testing `http://` instead of `https://`. The server redirects HTTP→HTTPS before the WAF can inspect the payload. The true blocking rate on HTTPS is much higher.
- **kasikornbank.com 85.19% is misleading — HTTP 000 is not WAF blocking** — every test returned 000 (curl connection refused / no response). This means the IP was blocked at network/CDN level (Cloudflare / firewall), not by the WAF inspecting payloads. A PASS against an unreachable host tells you nothing about WAF effectiveness.
- **NoSQL injection tests always fail due to PowerShell variable expansion** — payloads contain `$ne`, `$gt`, `$regex`, `$where` which PowerShell expands to empty strings in double-quoted strings. The actual requests sent have empty operator values, not valid NoSQL injection payloads.
- **Fix requirements for accurate results**: use `https://` prefix, single-quote NoSQL payloads (or escape `$`), consider following redirects (`-L` flag) to reach the actual application.

## Test Case Coverage

| Category | Rules | Tests | Description |
|----------|-------|-------|-------------|
| SQLi | 942100–942390 | 5 | Basic OR, UNION SELECT, comments, boolean, time-based |
| XSS | 941100–941180 | 5 | script tag, img onerror, svg onload, javascript:, URL-encoded |
| LFI / Path traversal | 930100–930120 | 3 | /etc/passwd, /proc/self/environ, Windows ..\..\ |
| RCE / CMD injection | 932100–932160 | 5+1 | semicolon, pipe, &&, backticks, Shellshock |
| File upload | 933110–933120 | 2 | .php extension, double extension .php.jpg |
| HTTP injection | 921110–921160 | 3 | open redirect, CRLF, Host header spoofing |
| NoSQL | 942290 | 4 | $ne, $gt, $regex, $where operators |

## Test Results Analysis

### abpmart.com (Ant2 WAF — [[Ant2-Proxy-Security-Manager]])

```
Total: 27 | PASS: 11 | NOT PASS: 16 | Rate: 40.74%
```

**Root cause of "NOT PASS"**: HTTP 301 redirect on every HTTP request. The test script calls `http://abpmart.com` (no scheme prefix), which the server redirects to `https://abpmart.com` — the WAF never inspects the payload.

Tests that genuinely PASS (403/000): SQLi Basic, SQLi UNION, SQLi Boolean, SQLi Time-based, XSS Script, XSS Encoded, LFI passwd, LFI proc, CMD Semicolon, Shellshock.

**True picture**: Re-running with `https://abpmart.com` would show far higher blocking rates.

### kasikornbank.com (External — reference baseline)

```
Total: 27 | PASS: 23 | NOT PASS: 4 | Rate: 85.19%
```

All 23 "PASS" results returned HTTP 000 — curl could not connect. The 4 "NOT PASS" are the broken NoSQL tests. This result says nothing about the kasikornbank WAF; it only shows that the test IP is blocked at network level.

## Script Bug: NoSQL Payloads

```powershell
# These payloads in double-quoted strings:
'?id[$ne]=1'     # PowerShell expands $ne → empty → sends "?id[]=1"
'?id[$gt]=0'     # same issue
```

Fix with single-quoted strings OR escape the dollar sign:
```powershell
Payload = '?id[$ne]=1'     # single-quote — literal, no expansion
Payload = "?id[`$ne]=1"   # backtick escapes $ in double-quote
```

## Notable Quotes

> `SQLi Comment | 942110 | REQUEST-942 | 301 | NOT PASS`
> `CMD Pipe | 932110 | REQUEST-932 | 301 | NOT PASS`

— All 301s are HTTP→HTTPS redirects, not bypasses. ([[2026-05-06-owasp-crs-script-test-poc]])

> `NoSQL Injection | 942290 | REQUEST-942 | | NOT PASS`

— Empty HTTP code = curl error, likely from broken payload due to `$` expansion. ([[2026-05-06-owasp-crs-script-test-poc]])

## Gaps / Unanswered Questions

- What is abpmart.com's true blocking rate when tested over HTTPS?
- Does the Ant2 WAF at abpmart.com have paranoia level set above PL1? Higher PL would catch more cases.
- No POST body injection tests — most real-world SQLi/XSS comes via POST, not GET params.
- No WAF evasion tests (double encoding, case variation, comment obfuscation) — basic payloads only.

## See Also

- [[waf-validation-testing]]
- [[OWASP-CRS]]
- [[Ant2-Proxy-Security-Manager]]
- [[false-positive-false-negative-tradeoff]]
- [[crs-rule-numbering]]
