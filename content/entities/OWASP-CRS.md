---
title: "OWASP CRS"
type: entity
tags: [owasp, crs, waf, rules, open-source]
sources: [2026-05-05-owasp-crs-owasp-foundation, 2026-05-05-crs-releases-v4-20-to-v4-26]
created: 2026-05-05
updated: 2026-05-05
---

# OWASP CRS (Core Rule Set)

The OWASP Core Rule Set is the de facto open-source WAF rule set for [[ModSecurity]] and compatible engines. It is **not** a WAF — it is a rule set that runs inside a WAF engine.

## Identity

- **Full name**: OWASP ModSecurity Core Rule Set
- **Repo**: https://github.com/coreruleset/coreruleset
- **Docs**: https://coreruleset.org
- **License**: Apache 2.0 (free for commercial use)
- **OWASP page**: https://owasp.org/www-project-modsecurity-core-rule-set/

## Current Versions (as of 2026-05-05)

| Branch | Version | Status |
|--------|---------|--------|
| v4.x | **v4.26.0** | Current |
| v4.x | **v4.25.0** | LTS |
| v3.x | **v3.3.8** | Legacy — security patches only |

([[2026-05-05-crs-releases-v4-20-to-v4-26]])

## Design Philosophy

- **Minimum false alerts** is a stated design priority — not just a goal but part of the project's public identity ([[2026-05-05-owasp-crs-owasp-foundation]]).
- Attack coverage vs. false positive rate is a continuously recalibrated balance — multiple FP fixes ship in every monthly release.
- Separate issue paths: FPs → GitHub Issues; bypasses → security disclosure (treated as CVEs, not bugs).

## Rule Numbering

See [[crs-rule-numbering]] for the full 9xx xxx range breakdown.

Key ranges used in [[Ant2-Proxy-Security-Manager]] presets:

| Range | Category |
|-------|----------|
| 920xxx | Protocol validation |
| 930xxx | LFI / file access |
| 932xxx | RCE / Unix commands |
| 933xxx | PHP injection |
| 934xxx | Node.js / SSTI |
| 941xxx | XSS |
| 942xxx | SQL injection |
| 944xxx | Java / JSP |

## Paranoia Levels

See [[paranoia-levels]]. CRS rules are assigned to PL1–PL4. Higher PL = more rules active = more FPs.

## Known CVEs (recent)

| CVE | Fixed | Rules | Attack |
|-----|-------|-------|--------|
| CVE-2026-33691 | v4.25.0 | 933110, 933111, 944140, 932180 | Whitespace padding bypass in PHP/JSP file upload |
| CVE-2025-30208 | v4.23.0 | LFI rules | Vite.js path traversal |

## Compatibility with Ant2

[[Ant2-Proxy-Security-Manager]] runs CRS via ModSecurity v3. See [[platform-presets]] for the 17 platforms with pre-tuned exclusion sets, and [[bypass-presets]] for OAuth/webhook bypass rules.

## See Also

- [[ModSecurity]]
- [[paranoia-levels]]
- [[false-positive-false-negative-tradeoff]]
- [[crs-rule-numbering]]
- [[platform-presets]]
- [[bypass-presets]]
- [[Ant2-Proxy-Security-Manager]]
