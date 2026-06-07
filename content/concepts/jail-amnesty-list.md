---
title: "Jail Amnesty List"
type: concept
tags: [jail, amnesty, whitelist, redis, sqlite, ant2, v2426]
sources: [2026-05-13-ant2-v2426-amnesty-session]
created: 2026-05-13
updated: 2026-05-13
---

# Jail Amnesty List

The Amnesty List is a permanent IP exemption mechanism in [[Ant2-Proxy-Security-Manager]] that prevents trusted IPs from being auto-jailed and clears their Redis attack counters at runtime. Introduced in v2.4.26.

## Naming Rationale

"Amnesty" was chosen as the UI-facing name because it is semantically opposite to "Jail" — granting amnesty means the IP is permanently exempt from imprisonment. All user-visible strings use this vocabulary: "Grant Amnesty", "Revoke", "Revoke amnesty for X?". The underlying DB table is named `jail_whitelist` for clarity in code ([[2026-05-13-ant2-v2426-amnesty-session]]).

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS jail_whitelist (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  ip_address TEXT    NOT NULL UNIQUE,
  note       TEXT    NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
);
```

`ip_address` has a UNIQUE constraint — inserting a duplicate returns HTTP 409 with a clear error message.

## API Routes

Three routes registered in `api/src/routes/jail.js` **before** the `/:id` catch-all to avoid Express path conflict:

| Method | Path | Action |
|--------|------|--------|
| GET | `/api/jail/whitelist` | List all amnesty entries |
| POST | `/api/jail/whitelist` | Add IP; body: `{ ip_address, note, release_if_jailed }` |
| DELETE | `/api/jail/whitelist/:id` | Revoke amnesty by DB id |

The `release_if_jailed` POST body flag (boolean): when true, deletes the IP from `ip_jail` and triggers `writeAllHostConfigs(true)` at add-time, immediately removing the nginx block. This handles the add-time case only — retroactive unblock (for IPs jailed before amnesty was granted) is **not** automatic (see Gaps).

## jailService Integration

Whitelisted IPs are checked at **two points** in [[auto-jail-pipeline]]:

### 1. `pollAttacks()` — before "already jailed" check

```js
// Skip whitelisted IPs entirely — clear any stale counter
if (db.prepare('SELECT id FROM jail_whitelist WHERE ip_address = ?').get(ip)) {
  await redis.del(`jail:cnt:${ip}`);
  continue;
}
```

Placed first so whitelisted IPs never accumulate counters and never get jailed on subsequent polls.

### 2. `applyThresholdToCounters()` — after existing jail check

```js
if (db.prepare('SELECT id FROM jail_whitelist WHERE ip_address = ?').get(ip)) {
  await redis.del(key);
  continue;
}
```

Belt-and-suspenders: catches any scenario where a whitelisted IP's counter was written before the IP was added to the amnesty list.

## UI (IpJail.jsx)

The Amnesty tab is the 3rd tab in the IP Jail page, using an emerald/green color theme (contrasting with the orange jail tabs). Features:

- Description bar explaining the purpose
- "Grant Amnesty" form: IP address field + optional note + "Also release if currently jailed" checkbox
- Table: IP | Note | Added At | Revoke button
- Confirm dialog before revoke: "Revoke amnesty for {ip}?"
- Toast notifications: "granted amnesty" / "Amnesty revoked for {ip}"

State: `whitelist`, `showWlForm`, `wlIp`, `wlNote`, `wlRelease`, `wlAdding`

## Gaps / Known Limitations

- **No retroactive nginx unblock**: an IP jailed before amnesty was granted remains in nginx geo block until `releaseExpired()` removes it naturally. The `release_if_jailed` flag only acts at add-time.
- **No localStorage persistence** for the Amnesty tab's `activeTab` state — page reload returns to default tab (unlike Jail and Counter tabs which persist).
- **No bulk import** — IPs must be added one at a time via the form.

## See Also

- [[auto-jail-pipeline]]
- [[Ant2-Proxy-Security-Manager]]
- [[2026-05-13-ant2-v2426-amnesty-session]]
