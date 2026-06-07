---
title: "WAF Scope Follows proxy_pass, Not SSL"
type: concept
tags: [modsecurity, nginx, port80, cloudflare, waf-bypass, proxy-pass, server-block]
sources: [2026-05-07-ant2-v244-waf-port80-fix]
created: 2026-05-07
updated: 2026-05-07
---

# WAF Scope Follows proxy_pass, Not SSL

A [[ModSecurity]] NGINX deployment must have `modsecurity on` in **every server block that contains a `proxy_pass` directive**. The WAF does not inherit activation from other server blocks on the same host — each server block is independent.

## The Mistaken Mental Model

It is tempting to think: "I have HTTPS with WAF enabled — that's the production path, port 80 just redirects." This was true in the original Ant2 port 80 design. It broke when the Cloudflare-safe proxy path was added.

## How the Bug Manifested in Ant2

### Original design (safe)

```
port 80 server block:
  return 301 https://...     ← no proxy_pass, no WAF needed
  
port 443 server block:
  modsecurity on;            ← WAF active
  proxy_pass ...             ← traffic flows here
```

### After CF-safe redirect was added (broken)

```
port 80 server block:
  if (X-Forwarded-Proto = https) → skip redirect
  proxy_pass ...             ← traffic NOW flows here (no WAF!)

port 443 server block:
  modsecurity on;
  proxy_pass ...
```

Cloudflare connects to origin on port 80 and sends `X-Forwarded-Proto: https`. The redirect is skipped; `proxy_pass` fires. But `modsecurity on` is absent from this server block — ModSecurity never runs. ([[2026-05-07-ant2-v244-waf-port80-fix]])

### Fixed design

```
port 80 server block:
  modsecurity on;            ← WAF active on port 80 too
  modsecurity_rules_file ...; 
  if (X-Forwarded-Proto = https) → skip redirect
  proxy_pass ...

port 443 server block:
  modsecurity on;
  proxy_pass ...
```

## Detection Difficulty

This class of bug is hard to notice because:

1. **UI shows correct mode** — The WAF mode setting (Block/Detection/Off) is stored in the database and reflected in the GUI. It does not reflect whether `modsecurity on` is actually present in each server block.
2. **HTTPS attacks are blocked** — Port 443 traffic is inspected normally, so manual testing (which typically uses `https://`) passes.
3. **No ModSecurity log gap** — ModSecurity only logs what it sees. Requests arriving via port 80 (uninspected) produce no WAF log entries — they look like clean traffic, not bypasses.
4. **Cloudflare masks the port** — Browser users always see `https://`. The fact that CF→origin traffic travels over port 80 HTTP is invisible at the application layer.

## Rule

> **Every NGINX server block with `proxy_pass` must have `modsecurity on` if WAF is enabled for that host.**

Checklist when adding a new proxy path to an existing host config:
- [ ] Does the new server block or location contain `proxy_pass`?
- [ ] Is WAF enabled for this host?
- [ ] If both yes: add `modsecurity on` + `modsecurity_rules_file` to that block.

## Cloudflare-Specific Pattern

When a site sits behind Cloudflare:

| CF mode | CF→origin port | WAF block needed |
|---------|---------------|-----------------|
| CF Proxy (orange cloud) | Usually port 80 HTTP | port 80 server block |
| CF Proxy with Full SSL | port 443 HTTPS | port 443 server block |
| CF DNS only (grey cloud) | Whatever client uses | all active server blocks |

In [[Ant2-Proxy-Security-Manager]]'s Cloudflare-safe configuration, CF Proxy uses port 80. The WAF must be active on the port 80 block.

## See Also

- [[ModSecurity]]
- [[Ant2-Proxy-Security-Manager]]
- [[waf-validation-testing]]
- [[2026-05-07-ant2-v244-waf-port80-fix]]
- [[2026-05-07-ant2-v242-v243-session]]
