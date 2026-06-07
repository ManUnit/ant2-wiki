---
title: "F5 WAF for NGINX"
type: source
tags: [f5, nginx, waf, commercial, devops, api-security]
created: 2026-05-05
updated: 2026-05-05
---

# F5 WAF for NGINX

Official F5/NGINX documentation landing page for their commercial WAF product.

**Source:** https://docs.nginx.com/waf/

## Abstract

[[F5-NGINX-WAF]] (formerly NGINX App Protect WAF) is a commercial software security suite that integrates into DevOps environments as a lightweight WAF, L7 DoS protection, bot protection, API security, and threat intelligence. It is F5's commercial offering on top of NGINX, contrasting with the open-source [[OWASP-CRS]] + [[ModSecurity]] stack.

## Key Takeaways

- **Rebranding**: Product was formerly called "NGINX App Protect WAF" — relevant when searching older docs, issues, and community threads.
- **Broader than a WAF**: Bundles L7 DoS protection, bot protection, API security, and threat intelligence in one product. Not a rule-set-only solution.
- **DevOps-first design**: Explicitly positioned as "lightweight" and designed for DevOps pipeline integration — architectural priority.
- **Commercial product**: Owned by F5 (which acquired NGINX). Contrasts with the open-source OWASP CRS approach.

## Gaps / Open Questions

- This source is a brief intro page only — no architecture detail, no config examples, no pricing.
- No comparison with OWASP CRS feature set.
- Need to ingest deeper F5 WAF docs for technical content.

## See Also

- [[F5-NGINX-WAF]]
- [[OWASP-CRS]]
- [[ModSecurity]]
- [[waf-rule-sets]]
