---
title: "Paranoia Levels"
type: concept
tags: [crs, paranoia-level, tuning, false-positives]
sources: [2026-05-05-owasp-crs-owasp-foundation, 2026-05-05-ant2-progress]
created: 2026-05-05
updated: 2026-05-05
---

# Paranoia Levels (CRS)

The Paranoia Level (PL) system is [[OWASP-CRS]]'s mechanism for controlling how aggressively rules are applied. Higher PL = more rules active = better detection = more false positives.

## The Four Levels

| PL | Rules active | Typical use |
|----|-------------|-------------|
| PL1 | Core rules only — low FP rate | Production default, most apps |
| PL2 | Adds stricter rules | Apps with moderate security requirements |
| PL3 | Adds even stricter rules | High-security environments, expect some FPs |
| PL4 | Maximum rules — high FP rate | Highly controlled environments only |

## How It Works in CRS

Each rule is tagged with the PL at which it becomes active. Setting `tx.paranoia_level=2` enables all PL1 and PL2 rules. The `tx.executing_paranoia_level` variable controls which rules actually fire.

## In Ant2

[[Ant2-Proxy-Security-Manager]] exposes PL as a 4-button selector per host in the WAF settings UI. The value maps directly to `tx.paranoia_level` in the ModSecurity config generated per host.

PL is stored in the `waf_settings.paranoia_level` column in SQLite.

## Tuning Guidance

- Start at **PL1** for all new hosts.
- Move to PL2 only after resolving FPs at PL1.
- Use [[platform-presets]] to pre-exclude known FPs before raising PL.
- PL3/PL4 should only be used with extensive custom exclusions.

## See Also

- [[OWASP-CRS]]
- [[false-positive-false-negative-tradeoff]]
- [[platform-presets]]
- [[Ant2-Proxy-Security-Manager]]
