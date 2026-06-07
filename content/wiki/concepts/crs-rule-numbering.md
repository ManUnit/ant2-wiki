---
title: "CRS Rule Numbering"
type: concept
tags: [crs, rules, rule-ids, reference]
sources: [2026-05-05-crs-releases-v4-20-to-v4-26, 2026-05-05-ant2-progress]
created: 2026-05-05
updated: 2026-05-05
---

# CRS Rule Numbering

[[OWASP-CRS]] uses a structured 6-digit rule ID system. Understanding the ranges makes it possible to interpret WAF logs, write targeted exclusions, and understand which attack category a block belongs to.

## Range Reference

| Range | Category | Notes |
|-------|----------|-------|
| 910xxx | IP reputation / blocklists | |
| 911xxx | Method enforcement | |
| 912xxx | DoS protection | |
| 913xxx | Scanner / recon detection | WhatWAF, ghauri, Nettacker, AWS security agent |
| 920xxx | Protocol validation | Content-Type, request-line, HTTP version |
| 921xxx | HTTP request smuggling | |
| 922xxx | Multipart form data | |
| 930xxx | LFI / local file access | OS files, restricted paths, AI artifact paths |
| 931xxx | RFI / SSRF | Remote file inclusion, localhost variants |
| 932xxx | RCE / Unix command injection | Shell commands, fork bomb (PL2+) |
| 933xxx | PHP injection | PHP functions, double-extension uploads |
| 934xxx | Node.js / SSTI | Server-side template injection (934200 added v4.26.0) |
| 941xxx | XSS | Cross-site scripting, HTTP headers |
| 942xxx | SQL injection | SQLi patterns, MongoDB operators |
| 943xxx | Session fixation | |
| 944xxx | Java / JSP | JSP file upload, Spring, Java serialization |
| 950xxx | Data leakage — general | |
| 951xxx | Data leakage — DB errors | MSSQL, MySQL, PostgreSQL, SQLite, etc. |
| 953xxx | Data leakage — source code | |
| 954xxx | Data leakage — IIS | |
| 955xxx | Data leakage — PHP | |
| 956xxx | Data leakage — JSP/ASP | |

## Frequently Referenced in Ant2 Presets

Rules most commonly excluded in [[platform-presets]] and [[bypass-presets]]:

| Rule ID | Description | Commonly excluded for |
|---------|-------------|----------------------|
| 920120 | Multiple Content-Type headers | OAuth callbacks |
| 920230 | Multiple URL encoding | OAuth state params, SAML |
| 932150 | Unix command in args | GitHub OAuth auth codes |
| 933100 | PHP opening tag detected | PHP platforms, Smarty templates |
| 933110 | PHP file upload — single ext | Needs v4.25.0+ for whitespace bypass fix |
| 933111 | PHP file upload — double ext | Needs v4.25.0+ for whitespace bypass fix |
| 941100 | XSS via libinjection | OAuth JWT tokens |
| 942100 | SQL injection via libinjection | OAuth tokens, payment fields |
| 944140 | JSP file upload | Needs v4.25.0+ for whitespace bypass fix |

## See Also

- [[OWASP-CRS]]
- [[platform-presets]]
- [[bypass-presets]]
- [[false-positive-false-negative-tradeoff]]
