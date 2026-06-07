---
title: "False Positive / False Negative Tradeoff"
type: concept
tags: [waf, false-positive, false-negative, tuning, crs]
sources: [2026-05-05-owasp-crs-owasp-foundation, 2026-05-05-crs-releases-v4-20-to-v4-26]
created: 2026-05-05
updated: 2026-05-05
---

# False Positive / False Negative Tradeoff

The central operational tension in WAF management. Every rule that catches an attack also risks blocking a legitimate request.

## Definitions

- **False Positive (FP)**: Legitimate traffic blocked by a WAF rule. Causes user-facing errors, disrupts business.
- **False Negative (FN)**: Attack traffic that passes through undetected. Causes security incidents.

## Why This Matters for CRS

[[OWASP-CRS]] explicitly states "minimum of false alerts" as a design priority — it is baked into the project's public identity ([[2026-05-05-owasp-crs-owasp-foundation]]). This means:

- The project consciously trades some attack coverage for lower FP rates at lower [[paranoia-levels]].
- The CRS team treats FP reports (GitHub Issues) and FN/bypass reports (security disclosure) as fundamentally different issue types.
- FP reduction work ships in every release — it is never fully resolved ([[2026-05-05-crs-releases-v4-20-to-v4-26]]).

## Practical Tradeoffs

| Action | FP effect | FN effect |
|--------|-----------|-----------|
| Raise paranoia level | ↑ more FPs | ↓ fewer FNs |
| Lower paranoia level | ↓ fewer FPs | ↑ more FNs |
| Add rule exclusion | ↓ fewer FPs for that rule | ↑ potential blind spot |
| Add bypass for a path | ↓ FPs for that path | ↑ no WAF coverage for that path |
| Pin old CRS version | Stable FPs | ↑ accumulating FNs as new attacks emerge |

## In Ant2

[[Ant2-Proxy-Security-Manager]] addresses this tradeoff with:
- [[paranoia-levels]] selector (PL1–4 per host)
- [[platform-presets]] — pre-tuned exclusion sets for 17 platforms
- [[bypass-presets]] — WAF-off paths for known-safe OAuth/webhook flows
- Custom `SecRuleRemoveById` textarea per host
- 3-way mode: DetectionOnly lets you observe FPs before enabling Block mode

## See Also

- [[paranoia-levels]]
- [[platform-presets]]
- [[bypass-presets]]
- [[OWASP-CRS]]
