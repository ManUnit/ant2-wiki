---
title: "Ant2 v2.4.26 — IP Jail Amnesty List + GeoIP Allow List Fix"
type: source
tags: [ant2, jail, amnesty, geoip, allow-list, react, sqlite, v2426]
created: 2026-05-13
updated: 2026-05-13
---

# Ant2 v2.4.26 — IP Jail Amnesty List + GeoIP Allow List Fix

Session notes: v2.4.25 → v2.4.26 development and deployment to `172.20.20.181`.

## Abstract

Two features shipped in this session: (1) an **Amnesty List** for IP Jail — trusted IPs that are permanently exempt from auto-jailing, with jailService integration that clears their Redis counters at runtime; (2) a **GeoIP Allow List semantic fix** where `toggleCountry()` was always storing `action: 'block'` regardless of the UI mode selected. Version bumped from 2.4.25 → 2.4.26 and deployed via SCP + Docker rebuild.

## Key Takeaways

- **Amnesty List** — new `jail_whitelist` SQLite table + `/api/jail/whitelist` CRUD + `jailService.js` skip logic + 3rd tab in IP Jail UI (emerald/green theme). Name chosen for semantic contrast with "Jail" — Amnesty = opposite of imprisonment.
- **jailService integration** — in both `pollAttacks()` and `applyThresholdToCounters()`, whitelisted IPs are skipped and their `jail:cnt:<ip>` Redis key is deleted, preventing counter accumulation.
- **GeoIP Allow List bug** — `toggleCountry()` in GeoIP.jsx always appended `{ action: 'block' }` regardless of current mode. Fixed to use `action: 'allow'` in Allow List mode. Backend config generator ignores the `action` field (uses `mode` only), so nginx output was unaffected — but DB semantics were wrong.
- **GeoIP Allow List functional gap** — user observed that TH could still access a site set to Allow List: AF only. Root cause not definitively confirmed; likely nginx failed to reload due to config test error or inotify issue — needs further investigation with `nginx -t` on the live server.
- **Naming: Whitelist → Amnesty** — UI renamed after deployment. All user-visible strings updated: tab "Amnesty", button "Grant Amnesty", action "Revoke", confirm "Revoke amnesty for X?", toast "granted amnesty / Amnesty revoked for X".
- **Deploy pattern (existing server)** — `api/src` + `web/dist` SCP'd to `/tmp/` then `sudo cp` (VERSION owned by root). `docker compose -p ant2proxy up -d --build api web` rebuilds both images; WAF + Redis containers untouched.

## Notable Quotes / Observations

> "ถ้าเราจะเปลี่ยน จาก white list เป็น อะไร ดี ที่ มันมีความหมายตรงข้าม กับ เข้าคุก" — user, choosing the Amnesty name

> "เราจะทดสอบว่า จะ block เราได้ไหม ผลคือเราเปิดได้" — user confirming GeoIP Allow List functional gap

## Files Changed

| File | Change |
|------|--------|
| `api/src/database.js` | Added `jail_whitelist` table (id, ip_address UNIQUE, note, created_at) |
| `api/src/routes/jail.js` | Added GET/POST/DELETE `/whitelist` routes before `/:id` catch-all |
| `api/src/services/jailService.js` | Whitelist check in `pollAttacks()` and `applyThresholdToCounters()` |
| `web/src/pages/IpJail.jsx` | Amnesty tab (3rd tab), form, table, CRUD functions |
| `web/src/pages/GeoIP.jsx` | `toggleCountry()` fix — action based on mode |
| `VERSION` | 2.4.25 → 2.4.26 |
| `api/package.json` | 2.4.17 → 2.4.26 |
| `web/package.json` | 2.4.17 → 2.4.26 |
| `build-package.sh` | VERSION string 2.4.17 → 2.4.26 |

## Gaps / Unanswered Questions

- GeoIP Allow List functional gap: does `$geoip2_data_country_code` resolve correctly for direct (non-CF) traffic in the ant2proxy-waf container? Needs `nginx -t` + log inspection on live server.
- Amnesty List does not yet integrate with nginx geo block — a jailed IP that is later granted amnesty is NOT automatically unblocked in nginx until `releaseExpired()` removes it. The `release_if_jailed` flag (POST body) handles this at add-time, but not retroactively.
- IpJail page: `activeTab` localStorage persistence not implemented for Amnesty tab (jail and counter tabs persist across sessions; amnesty resets to default).

## See Also

- [[jail-amnesty-list]]
- [[auto-jail-pipeline]]
- [[geoip-country-blocking]]
- [[Ant2-Proxy-Security-Manager]]
- [[2026-05-09-ant2-v2412-v2415-session]]
