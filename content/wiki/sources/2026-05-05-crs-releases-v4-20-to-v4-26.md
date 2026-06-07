---
title: "CRS Releases v4.20–v4.26 (+ v3.3.8)"
type: source
tags: [owasp, crs, releases, changelog, cve, versions]
created: 2026-05-05
updated: 2026-05-05
---

# CRS Releases v4.20–v4.26 (+ v3.3.8)

GitHub releases page covering 6 months of CRS v4.x releases (Nov 2025–May 2026) plus a concurrent v3.x security patch.

**Source:** https://github.com/coreruleset/coreruleset/releases

## Abstract

OWASP CRS follows a monthly release cadence on the v4.x branch. This source covers v4.20.0 through v4.26.0, with v4.25.0 designated as LTS. The v3.x branch received one critical security patch (v3.3.8) during this period. Key themes: active attack-surface expansion (SSTI, AI paths, shell fork bomb), continuous [[false-positive-false-negative-tradeoff]] recalibration, one critical CVE, and an ongoing regex-assembly refactor.

## Key Takeaways

- **Version landscape**: v4.26.0 = current, v4.25.0 = LTS, v3.3.8 = legacy security-only. Two active branches.
- **Release cadence is monthly** — deployments that pin a version accumulate known gaps and FP regressions.
- **CVE-2026-33691 (critical, fixed v4.25.0 LTS)**: Whitespace padding bypass in PHP/JSP file upload rules — 933110, 933111, 944140, 932180. Attacker pads filename with whitespace to bypass upload blocking.
- **New attack surfaces added**: SSTI rule 934200 (v4.26.0), AI coding assistant artifact paths rule 930140 (v4.24.1), shell fork bomb rule 932390 (v4.25.0), Vite.js path traversal CVE-2025-30208 (v4.23.0), framework method overrides 920650 (v4.23.0).
- **False positive reduction is continuous**: Multiple FP fixes per release across SQLi (942xxx), file access (930xxx), Unix RCE (932xxx). The FP/FN balance is never permanently solved.
- **Regex Assembly (.ra) refactor**: Dozens of rules migrated to regex-assembly format per release. No behavior change — maintenance quality improvement only.

## Notable Rule IDs Referenced

| Rule range | Category |
|------------|----------|
| 913xxx | Scanner/recon detection |
| 920xxx | Protocol validation |
| 921xxx | HTTP request smuggling |
| 930xxx | LFI / file access |
| 931xxx | RFI / SSRF |
| 932xxx | RCE / Unix commands |
| 933xxx | PHP injection |
| 934xxx | Node.js / SSTI |
| 941xxx | XSS |
| 942xxx | SQL injection |
| 943xxx | Session fixation |
| 944xxx | Java / JSP |
| 951xxx | Data leakage (DB errors) |

## CVEs in This Period

| CVE | Fixed in | Affected rules | Attack |
|-----|----------|----------------|--------|
| CVE-2026-33691 | v4.25.0 LTS | 933110, 933111, 944140, 932180 | Whitespace padding bypass in file upload detection |
| CVE-2025-30208 | v4.23.0 | LFI rules | Vite.js path traversal |
| CVE-2025-55182 | v4.22.0 | 934100 | (details in advisory) |

## Gaps / Open Questions

- Source does not cover v4.19.x and earlier — need additional releases page for historical context.
- No detail on how to safely upgrade from v3.x to v4.x.

## See Also

- [[OWASP-CRS]]
- [[crs-rule-numbering]]
- [[false-positive-false-negative-tradeoff]]
- [[paranoia-levels]]
- [[platform-presets]]
