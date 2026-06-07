---
title: "OWASP CRS | OWASP Foundation"
type: source
tags: [owasp, crs, waf, modsecurity, overview, license]
created: 2026-05-05
updated: 2026-05-05
---

# OWASP CRS | OWASP Foundation

Official OWASP project page for the Core Rule Set. High-level overview of scope, positioning, licensing, and support channels.

**Source:** https://owasp.org/www-project-modsecurity-core-rule-set/

## Abstract

[[OWASP-CRS]] is a set of generic, engine-agnostic attack detection rules designed to run on [[ModSecurity]] or any compatible WAF engine. Its stated design priority is broad attack coverage (including the [[OWASP-Top-Ten]]) with a minimum of false alerts. Free and open source under Apache 2.0. Official docs live at coreruleset.org, not owasp.org.

## Key Takeaways

- CRS is not a WAF — it is a rule set that requires a separate engine. The two are explicitly decoupled.
- Installation is a deliberate two-step process: choose and install an engine first, then install the rules.
- "Minimum of false alerts" is a **stated design priority** — the [[false-positive-false-negative-tradeoff]] is baked into the project's identity.
- License is Apache 2.0: free for commercial use; derivative works must use same or compatible license.
- Two separate issue paths: false positives → GitHub Issues; false negatives/bypasses → security disclosure policy (treated as a security matter, not a bug report).

## Notable Quotes

> "The OWASP CRS is a set of generic attack detection rules for use with ModSecurity or compatible web application firewalls. It aims to protect web applications from a wide range of attacks, including the OWASP Top Ten, with a minimum of false alerts."

## Gaps / Open Questions

- No version information — does not specify current CRS version or release cadence.
- No detail on which engines beyond ModSecurity are "compatible."
- No technical detail on rule structure, [[paranoia-levels]], or tuning.

## See Also

- [[OWASP-CRS]]
- [[ModSecurity]]
- [[OWASP-Top-Ten]]
- [[false-positive-false-negative-tradeoff]]
- [[waf-rule-sets]]
