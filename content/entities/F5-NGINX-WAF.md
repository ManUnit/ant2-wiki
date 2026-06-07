---
title: "F5 WAF for NGINX"
type: entity
tags: [f5, nginx, waf, commercial, api-security, bot-protection]
sources: [2026-05-05-f5-waf-for-nginx]
created: 2026-05-05
updated: 2026-05-05
---

# F5 WAF for NGINX

F5's commercial WAF product for NGINX. Formerly known as **NGINX App Protect WAF**. A full security suite, not just a rule set.

## Identity

- **Current name**: F5 WAF for NGINX
- **Former name**: NGINX App Protect WAF (relevant for searching older docs/issues)
- **Docs**: https://docs.nginx.com/waf/
- **Vendor**: F5 (acquired NGINX in 2019)
- **License**: Commercial

## Feature Set

Bundles multiple security capabilities in one product:
- Web application firewall (WAF)
- Layer 7 DoS protection
- Bot protection
- API security
- Threat intelligence services

## Contrast with OWASP CRS Stack

| | F5 WAF for NGINX | OWASP CRS + ModSecurity |
|--|-----------------|------------------------|
| License | Commercial | Apache 2.0 (free) |
| Rule set | F5 proprietary | Open-source, community-maintained |
| Scope | WAF + DoS + Bot + API + ThreatIntel | WAF rules only |
| DevOps integration | Built-in | Manual |
| Used in [[Ant2-Proxy-Security-Manager]] | No | Yes |

## See Also

- [[OWASP-CRS]]
- [[ModSecurity]]
- [[waf-rule-sets]]
