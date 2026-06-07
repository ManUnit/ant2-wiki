---
title: "Platform Presets"
type: concept
tags: [crs, false-positives, presets, tuning, ant2]
sources: [2026-05-05-ant2-progress]
created: 2026-05-05
updated: 2026-05-06
---

# Platform Presets

Platform presets are pre-tuned sets of `SecRuleRemoveById` directives that eliminate known [[false-positive-false-negative-tradeoff|false positives]] for specific frameworks and languages. [[Ant2-Proxy-Security-Manager]] ships 17 platform presets, selectable per host via a dropdown.

## How They Work

When a platform preset is selected, Ant2 injects a set of `SecRuleRemoveById` statements into that host's ModSecurity config — disabling the specific [[OWASP-CRS]] rules known to fire on legitimate traffic for that platform.

## All 18 Presets

| Key           | Platform                      | Rules excluded                                         |
| ------------- | ----------------------------- | ------------------------------------------------------ |
| `wordpress`   | WordPress                     | 50+ — Gutenberg editor, WooCommerce, shortcodes        |
| `laravel`     | Laravel (PHP)                 | 15 — CSRF token, Eloquent ORM, signed URLs             |
| `php`         | PHP generic                   | 12 — PHP function names in form data                   |
| `php_fpm`     | PHP-FPM / FastCGI             | 14 — SCRIPT_FILENAME, PATH_INFO conflicts              |
| `nodejs`      | Node.js (Express/Fastify)     | 8 — application/json, REST methods                     |
| `python`      | Python (Django/Flask/FastAPI) | 9 — CSRF token, DRF content-type                       |
| `nextjs`      | **Next.js**                   | **8 — API routes, server actions, `_next` params**     |
| `spring_boot` | Java Spring Boot              | 13 — JSON, REST methods, Spring CSRF                   |
| `dotnet`      | .NET / ASP.NET Core           | 12 — ViewState, serialization, CSRF                    |
| `asp_classic` | ASP Classic (VBScript)        | 11 — VBScript triggers Perl detection                  |
| `java`        | Java (J2EE / Jakarta EE)      | 8 — Java serialization/deserialization                 |
| `tomcat`      | Apache Tomcat                 | 9 — Java rules + JSP EL expressions                    |
| `sap`         | SAP (NetWeaver/HANA/Fiori)    | 10 — Java serialization, OData                         |
| `perl`        | Perl (CGI/Dancer2/Mojo)       | 6 — Perl syntax misfires                               |
| `apache`      | Apache HTTP Server            | 1 — mod_rewrite request-line                           |
| `nginx_app`   | Nginx (as upstream)           | 0 — CRS is optimized for Nginx                         |
| `iis`         | IIS Windows                   | 11 — Windows paths, .asp/.aspx extension               |
| magento       | Magento (Adobe Commerce)      | 18 — CSRF/form_key, REST/GraphQL, EAV queries, cookies |

## Magento / Adobe Commerce Preset Detail (added v2.3.6)

The `magento` preset is the most aggressive — 18+ rule exclusions covering:
- SQL injection rules (942xxx): Magento's layered navigation uses SQL-like filter params in URLs
- XSS rules (941xxx): product description fields accept rich HTML
- PHP injection rules (933xxx): Magento admin generates PHP-like strings
- Method enforcement (911100): REST API uses PUT/PATCH/DELETE
- Custom rules exempt `form_key` (CSRF token) from injection checks and whitelist `product[description]` / `content` fields

> **Note**: CSP headers at the proxy level break Magento's RequireJS loader which uses `eval()`. The `block_exploits` feature no longer sets `Content-Security-Policy`. ([[2026-05-06-ant2-v2361-release-notes]])

## Next.js Preset Detail

The `nextjs` preset is directly relevant to the planned Next.js integration. It excludes 8 rules covering:
- `_next/` static asset paths
- Next.js API routes (JSON body patterns)
- Server actions
- `__NEXT_DATA__` inline script injection patterns

## Code Location

Defined in `api/src/wafPresets.js` in [[Ant2-Proxy-Security-Manager]]. Applied by `nginxConfig.js` when generating per-host ModSecurity config.

## See Also

- [[false-positive-false-negative-tradeoff]]
- [[bypass-presets]]
- [[paranoia-levels]]
- [[OWASP-CRS]]
- [[Ant2-Proxy-Security-Manager]]
