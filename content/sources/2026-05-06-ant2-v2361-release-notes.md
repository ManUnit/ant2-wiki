---
title: "Ant2 Proxy Security Manager — Release Notes v2.3.5 → v2.3.6-a1"
type: source
tags: [ant2, release-notes, nginx, waf, owasp-crs, wysiwyg, rate-limiting, server-header]
sources: []
created: 2026-05-06
updated: 2026-05-06
---

## Abstract

Cumulative release notes for three patch versions of [[Ant2-Proxy-Security-Manager]] shipped in May 2026. Covers infrastructure changes (headers-more module for server header suppression), WAF tuning (Magento preset, CSP removal), rate limiting format fixes, a new admin config editor, custom 429 error pages, and a complete rewrite of the error page WYSIWYG editor to render real page backgrounds.

## Key Takeaways

- **iframe designMode replaces contentEditable** — a `contentEditable` div inside the host app can never render a full HTML page's `<body>` CSS (gradients, backgrounds). The fix uses `<iframe sandbox="allow-same-origin">` with `document.designMode = 'on'`, rendering the complete error page as visitors see it.
- **`ngx_http_headers_more_filter_module` compiled from source** — built alongside geoip2 in a single `./configure --with-compat` pass in the nginx-waf Dockerfile. Enables `more_clear_headers 'Server'` to suppress the `Server: nginx` header globally.
- **Rate normalization (`100/m → 100r/m`)** — nginx `limit_req_zone` strictly requires the `r` prefix. Without it, nginx fails to reload with a Config Error. Fixed in both API route handlers and `nginxConfig.js`.
- **CSP at proxy level breaks CMS `unsafe-eval`** — any `Content-Security-Policy` header set by a reverse proxy will block CMSes (Magento, WordPress) that use `eval()` in their JS loaders. Removed from `block_exploits`.
- **Conditional `error_page 403`** — setting `error_page 403 /waf-blocked.html` even when WAF is off was silently replacing all upstream 403 responses with the WAF block page. Now only added when `wafActive = true`.

## Notable Details

### nginx-waf: headers-more module
- Added to `nginx-waf/Dockerfile`: `git clone https://github.com/openresty/headers-more-nginx-module.git` then built with `--add-dynamic-module=../headers-more-nginx-module`.
- `nginx.conf`: `load_module modules/ngx_http_headers_more_filter_module.so;` and `more_clear_headers 'Server';` in the `http` block after `server_tokens off`.
- `server_tokens off` hides the version number; `more_clear_headers 'Server'` removes the header entirely.

### Magento WAF Preset
- Excludes SQL injection rules (942xxx), XSS rules (941xxx), PHP injection rules (933xxx), and method enforcement (911100) to handle Magento's REST API, product description HTML, and layered navigation SQL-like filter params.
- Custom rules: `SecRuleUpdateTargetById 942100 "!ARGS:form_key"` and `!ARGS:product[description]` to exempt CSRF tokens and rich text fields.
- See [[platform-presets]].

### Ant2 Config Tab
- New Settings tab for editing `nginx-ant2-custom.conf` — a global include for http-level directives outside of virtual host configs (e.g., custom map blocks, global limits).
- **nginx -t button**: runs `docker exec ant2proxy-waf nginx -t` via Docker socket mounted at `/var/run/docker.sock:ro` in docker-compose.yml. Requires `docker-cli` in the API container.

### 429 Error Page
- Added to all error page systems. Previously rate-limited requests returned nginx's default bare 429 page with the "nginx" text visible.
- Rate limit status codes: `limit_conn_status 429` and `limit_req_status 429` were already set; the missing piece was the custom error page intercept.

### WYSIWYG Editor Technical Notes
- `overflow:hidden` on error page body was clipping content in the fixed-height editor iframe. Fixed by injecting `<style id="__ant2_editor_override">html,body{overflow:auto!important;}</style>` after `doc.write()`, then stripping it before serialization.
- Toolbar `execCommand` calls now target `iframe.contentDocument` and call `iframe.contentWindow.focus()` to restore focus before each command.
- `key={editing}` on the HtmlEditor component forces a clean React remount when switching between error pages, avoiding stale iframe state.

## Gaps / Unanswered Questions

- The Vite build produces a single 887 KB JS bundle — code splitting not yet implemented.
- `build-package.ps1` must be run on Windows before deploying (Node.js not available on the target server).
- `ngx_http_headers_more_filter_module` requires recompiling against each nginx version; Dockerfile auto-detects version via `nginx -v`.

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[rate-limiting-nginx]]
- [[platform-presets]]
- [[server-header-disclosure]]
- [[wysiwyg-iframe-editor]]
