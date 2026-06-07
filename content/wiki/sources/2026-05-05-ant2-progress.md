---
title: "Ant2 Proxy Security Manager — PROGRESS.md"
type: source
tags: [ant2, project, features, architecture, waf, geoip, rate-limiting, docker]
sources: []
created: 2026-05-05
updated: 2026-05-05
---

# Ant2 Proxy Security Manager — PROGRESS.md

Internal development tracker for the [[Ant2-Proxy-Security-Manager]] project. Covers feature status, DB schema, file structure, platform presets, bypass presets, and pending backlog.

**Source:** `raw/PROGRESS.md` (local project file)

## Abstract

PROGRESS.md is the authoritative feature status document for Ant2 Proxy Security Manager v2.3.3.1 — an NGINX reverse proxy GUI with integrated ModSecurity v3 + OWASP CRS, GeoIP country blocking (Cloudflare-aware), Redis caching, and per-host rate limiting. Stack: React 18 + Vite (frontend), Node.js/Express + SQLite (API), Docker Compose (4 services). Production server: `anan@192.168.0.238` → `/opt/nginx-gui/`.

## Key Takeaways

- **All core features are done**: proxy CRUD, SSL/TLS, WAF (mode/paranoia/presets/bypass), GeoIP, rate limiting, WAF Monitor with charts and audit log.
- **WAF implementation is 3-way**: Off / DetectionOnly / Block (`SecRuleEngine` setting), [[paranoia-levels]] 1–4 selectable per host.
- **17 [[platform-presets]]**: Injects `SecRuleRemoveById` exclusions per platform. Next.js preset (8 rules) covers `_next` params, API routes, server actions — directly relevant to intended Next.js integration.
- **10 [[bypass-presets]]**: `ctl:ruleEngine=Off` for known-safe paths — OAuth callbacks (Google, Facebook, GitHub, Microsoft, LINE), SAML SSO, Stripe/PayPal/GitHub webhooks.
- **Critical write-order rule**: WAF conf must be written before nginx conf — inotify race condition otherwise causes nginx reload failure. See [[inotify-write-order-pattern]].

## DB Schema Summary

| Table | Key columns |
|-------|-------------|
| `hosts` | domain, upstream, ssl, force_https, http2, websocket, rate_limit fields (v2.3) |
| `waf_settings` | host_id, mode, paranoia_level, thresholds, custom_rules, excluded_rules, bypass_presets, platform_preset |
| `waf_events` | unique_id, host_id, ts, client_ip, rule_ids, cat_xss/sqli/rce/lfi/rfi/proto, action |
| `ssl_certs` | domains, cert_path, key_path, expires_at, provider |
| `global_country_rules` | separate from `country_rules` to avoid FK constraint on `host_id=0` |

## Pending Backlog

| Feature | Priority |
|---------|----------|
| WAF Monitor: filter by attack category | High |
| WAF Monitor: export CSV | High |
| Backup & restore DB via UI | High (production) |
| Multi-user / RBAC | High (team use) |
| SSL: Let's Encrypt wildcard (DNS-01) | Medium |
| Proxy Hosts: drag-to-reorder | Low |
| Dark mode | Low |

## Gaps / Open Questions

- No Next.js frontend integration documented yet (planned).
- No backup/restore — data loss risk in current state on server failure.
- Multi-user RBAC design not yet specified.

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[OWASP-CRS]]
- [[ModSecurity]]
- [[paranoia-levels]]
- [[platform-presets]]
- [[bypass-presets]]
- [[geoip-country-blocking]]
- [[rate-limiting-nginx]]
- [[inotify-write-order-pattern]]
