---
title: "ModSecurity"
type: entity
tags: [modsecurity, waf, engine, nginx, open-source]
sources: [2026-05-05-owasp-crs-owasp-foundation, 2026-05-05-ant2-progress, 2026-05-07-ant2-v242-v243-session]
created: 2026-05-05
updated: 2026-05-07
---

# ModSecurity

ModSecurity is the open-source WAF engine that runs [[OWASP-CRS]] rules. It is the engine layer in the engine/rule-set separation — CRS provides the rules, ModSecurity enforces them.

## Versions

- **ModSecurity v2**: Original version, Apache-native. Processes requests in-process before redirect decisions — payloads over HTTP always reach the WAF regardless of redirect rules. CRS v2.2.x with threshold 10 achieved >95% block rate against Nikto scans.
- **ModSecurity v3 (libmodsecurity3)**: Current version, NGINX-native, used in [[Ant2-Proxy-Security-Manager]]. Built as a shared library loaded by NGINX. Benchmark: ~94.5% true-positive rate (TPR) with CRS v4, ~0.41% false-positive rate (FPR). ([[2026-05-07-ant2-v242-v243-session]])

## Role in Ant2

[[Ant2-Proxy-Security-Manager]] runs ModSecurity v3 inside the `nginx-waf` Docker container. The engine is loaded via the `nginx-module-modsecurity` module. OWASP CRS rules are loaded on top.

WAF mode is controlled per-host via `SecRuleEngine`:
- `Off` — WAF disabled entirely
- `DetectionOnly` — logs but does not block
- `On` — blocks matched requests

## Critical NGINX Interaction — WAF Scope per Server Block

> [!warning] `modsecurity on` must appear in **every server block that contains `proxy_pass`**. WAF activation does not inherit across server blocks for the same domain. A host with WAF on port 443 but missing `modsecurity on` on port 80 will silently pass uninspected traffic if port 80 is also proxying. ([[2026-05-07-ant2-v244-waf-port80-fix]])

See [[waf-proxy-pass-scope]] for the full pattern and checklist.

## Critical NGINX Interaction — Port 80 Redirect Bypass

> [!warning] NGINX `return 301 https://...` in the port 80 server block fires **before** ModSecurity phase 1. Any payload sent over HTTP never reaches the WAF engine, regardless of whether ModSecurity is enabled on the port 80 block. ([[2026-05-07-ant2-v242-v243-session]])

This means:
- WAF tests must use `https://` — HTTP-based tests always return 301 and never validate WAF behavior.
- If an attacker sends a malicious HTTP request (not following the redirect), the WAF will not inspect it.
- Mitigation: ensure legitimate traffic always uses HTTPS at the client level; HTTP-only attack scenarios are unlikely in practice but worth documenting.

## Alternative: Coraza

Coraza is a Go-based WAF engine that passes 100% of the CRS v4 test suite. It is a drop-in alternative to ModSecurity v3 for NGINX/Caddy deployments. Not currently used in [[Ant2-Proxy-Security-Manager]] but worth tracking as v3 missing operator support expands.

## Official Resources

- Website: https://modsecurity.org/
- GitHub (v3): https://github.com/owasp-modsecurity/ModSecurity

## See Also

- [[OWASP-CRS]]
- [[Ant2-Proxy-Security-Manager]]
- [[paranoia-levels]]
- [[waf-rule-sets]]
- [[crs-rule-scope]]
- [[custom-waf-rules]]
- [[waf-validation-testing]]
- [[2026-05-07-ant2-v242-v243-session]]
