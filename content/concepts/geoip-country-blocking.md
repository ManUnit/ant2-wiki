---
title: "GeoIP Country Blocking"
type: concept
tags: [geoip, nginx, cloudflare, country-blocking, ant2, mmdb]
sources: [2026-05-05-ant2-progress, 2026-05-05-ant2-changelog, 2026-05-13-ant2-v2426-amnesty-session]
created: 2026-05-05
updated: 2026-05-13
---

# GeoIP Country Blocking

Per-host and global country-level traffic blocking in [[Ant2-Proxy-Security-Manager]], using MaxMind GeoLite2 (db-ip.com mmdb format) + NGINX `geoip2` module, with Cloudflare CDN awareness.

## Architecture

### 2-Stage Country Map

NGINX uses a 2-stage map to correctly identify country regardless of whether traffic is proxied through Cloudflare:

```nginx
# Stage 1: pick the right IP source
map $http_cf_connecting_ip $real_client_ip {
    ""      $remote_addr;        # No Cloudflare → use TCP source IP
    default $http_cf_connecting_ip;  # Behind Cloudflare → use CF header
}

# Stage 2: look up country from GeoIP2 DB
# geoip2 module reads GeoLite2-Country.mmdb
# → $geoip2_data_country_code

# Stage 3: block/allow decision
map $geoip2_data_country_code $country_blocked {
    TH  0;   # allow Thailand
    default 1;  # block everything else
}
```

### Why 2-Stage Matters

Single-stage maps using only `$http_cf_ipcountry` fail when hosts are set to "DNS Only" (not proxied) in Cloudflare — the CF header is absent and all traffic appears as the same country (or none).

## Block Response

Blocked requests return **HTTP 423 (Locked)**, not 451. Reason: browsers intercept 451 ("Unavailable for Legal Reasons") and render their own error page, overriding the custom HTML. 423 renders the custom `country-blocked.html` page correctly.

## Global vs Per-Host Rules

- **Per-host rules**: stored in `country_rules` table with FK to `hosts.id`
- **Global rules**: stored in separate `global_country_rules` table — no FK constraint, so `host_id=0` is valid
- Separation was required because `host_id=0` (global) violated the FK constraint on `country_rules`

## GeoIP Lookup (API / Redis)

- Country lookups for WAF log enrichment use `ip-api.com` free tier
- **Critical**: ip-api.com free tier is **HTTP only** — using `https.request()` returns `{"status":"fail"}` silently
- Lookup results are cached in Redis

## Allow List Mode — Semantic Bug (v2.4.26 fix)

`toggleCountry()` in `GeoIP.jsx` always appended `{ action: 'block' }` regardless of the current UI mode. In Allow List mode, the correct semantic is `action: 'allow'`. Fixed in v2.4.26 to pass `mode` as a parameter and derive action accordingly ([[2026-05-13-ant2-v2426-amnesty-session]]).

The backend `buildCountryBlockConf()` generates nginx config from `mode` (not from individual rule `action` fields), so nginx output was semantically correct even before the fix. The bug only caused incorrect DB values — but these would mislead any future feature that reads the `action` column directly.

## Allow List Mode — Functional Gap (unresolved)

A site configured as Allow List: AF-only was observed to remain accessible from Thailand. Root cause not definitively confirmed as of 2026-05-13. Possible causes:

1. **Config test failure** — nginx failed `-t` after reload, leaving the old config in place. Check with `docker exec ant2proxy-waf nginx -t`.
2. **`$geoip2_data_country_code` undefined** — if `geoip2` module is not loaded in the main `nginx.conf`, the variable resolves to empty string and the geo map default applies.
3. **inotify race** — WAF conf written first, nginx conf second; if inotify fires on the WAF conf write before the nginx conf is ready, the reload may fail silently.

> [!warning] Needs investigation with `nginx -t` + access log inspection on live server 172.20.20.181 for direct (non-Cloudflare) traffic.

## Module Setup

`nginx-module-geoip2` is not available as a pre-built package — compiled from source in the `nginx-waf` Dockerfile:
- Source: `github.com/leev/ngx_http_geoip2_module`
- Compiled dynamically against the matching NGINX version
- Installed to `/etc/nginx/modules/ngx_http_geoip2_module.so`

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[rate-limiting-nginx]]
- [[docker-compose-architecture]]
- [[2026-05-13-ant2-v2426-amnesty-session]]
