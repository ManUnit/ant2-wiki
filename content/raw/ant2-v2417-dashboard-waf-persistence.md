# Ant2 v2.4.17 — Dashboard WAF Card, SelectBox Drop-Up, WAF Persistence Fix

**Date:** 2026-05-10  
**Version:** v2.4.17 (continued iteration)  
**Files changed:**
- `web/src/pages/Dashboard.jsx`
- `web/src/pages/Settings.jsx`
- `web/src/pages/IpJail.jsx` (SelectBox drop-up)
- `api/src/routes/dashboard.js`

---

## 1. Dashboard WAF Detections Card — 3-Metric Layout

### Problem
The WAF Detections StatCard showed a single number (`ws.total`) with "N blocked" subtitle. With large totals (e.g. 12M), a single number gives no sense of current attack rate.

### Change
Replaced `<StatCard>` with a custom inline card showing three metrics:

```jsx
// Derived from existing ws.hourly data — no new API endpoint needed
const wafPerDay  = chartData.reduce((s, x) => s + x.count, 0)   // sum last 24 hours
const wafPerHour = chartData.length > 0 ? chartData[chartData.length - 1].count : 0  // latest hour
```

Card layout (same `stat-orange` gradient as before):
```
WAF Detections                 [icon]
12,290,034
total all time
┌──────────┬──────────┐
│   900    │  34,900  │
│  / hr    │  / day   │
└──────────┴──────────┘
```

Key: reused existing `chartData` useMemo — `wafPerDay`/`wafPerHour` are derived values, not new state. No API changes needed for this feature.

---

## 2. SelectBox Drop-Up — Automatic Direction Flip

### Problem
When the SelectBox trigger button is near the bottom of the viewport (e.g. pagination "Per page" selector when viewing a long jailed-IPs table), the dropdown list opened downward below the viewport and couldn't be clicked.

### Solution
Calculate available space in both directions at click time; use `bottom` (CSS fixed) instead of `top` when flipping up:

```js
const handleToggle = () => {
  if (!open && btnRef.current) {
    const r     = btnRef.current.getBoundingClientRect()
    const gap   = 4
    const itemH = small ? 28 : 36           // estimated height per option
    const estH  = options.length * itemH    // estimated total dropdown height
    const below = window.innerHeight - r.bottom - gap
    const above = r.top - gap
    const up    = estH > below && above > below   // flip if not enough room below

    setDropPos({
      left:   r.left,
      top:    up ? undefined : r.bottom + gap,
      bottom: up ? window.innerHeight - r.top + gap : undefined,
      maxH:   Math.min(estH + 8, up ? above : below),  // cap height to available space
      up,
    })
  }
  setOpen(v => !v)
}
```

Portal div uses both `top` and `bottom` in style — only one is defined at a time:
```jsx
style={{
  position: 'fixed',
  left:      dropPos.left,
  top:       dropPos.top,       // undefined when flipped up
  bottom:    dropPos.bottom,    // undefined when flipped down
  maxHeight: dropPos.maxH,
  overflowY: 'auto',
  zIndex:    9999,
}}
```

Key: `position: fixed` with `bottom` = distance from viewport bottom to bottom of dropdown. `window.innerHeight - r.top + gap` positions the dropdown to end exactly at the trigger button's top edge (gap above).

`maxHeight` + `overflowY: auto` ensures the dropdown never overflows even when space is limited in both directions.

---

## 3. WAF Detection Total — Persistence Bug and Fix

### Problem
On every container restart (including version updates via `docker compose up -d --build`), the WAF Detections total on the Dashboard reset to 0 (or a small number from the current log file window).

### Root Cause
`readWafStats()` in `dashboard.js` computed `total` by scanning WAF log files:
```js
for (const raw of tailFile(path.join(wafDir, file), 1000)) {
  const e = parseLine(raw)
  if (!e) continue
  stats.total++
  if (...) stats.blocked++
}
```

This reads at most **1000 lines per log file**. On container restart, log files may be rotated, or the log directory may start fresh — losing history.

### The `waf_events` SQLite Table
There is already a persistent SQLite table `waf_events` (schema in `database.js:69–91`) that stores all ingested WAF events. This table lives on a Docker volume mounted at `/data` — it is NOT affected by container rebuilds or restarts.

```sql
CREATE TABLE waf_events (
  unique_id    TEXT PRIMARY KEY,
  host_id      INTEGER,
  ts           INTEGER,      -- Unix timestamp
  status_code  INTEGER,
  client_ip    TEXT,
  ...
  rule_ids     TEXT,         -- JSON array
  action       TEXT,
  country_code TEXT,
  country_name TEXT
)
```

### Fix
Override `total` and `blocked` in `buildPayload()` with SQLite counts:

```js
// WAF log stats for recent hourly/top_rules (cached 10s, from log files)
const wafLogStats = readWafStats();

// Persistent totals — from waf_events SQLite table (survives restarts & updates)
const wafTotal   = db.prepare('SELECT COUNT(*) as c FROM waf_events').get().c;
const wafBlocked = db.prepare('SELECT COUNT(*) as c FROM waf_events WHERE status_code >= 400').get().c;
const wafStats   = { ...wafLogStats, total: wafTotal, blocked: wafBlocked };
```

`hourly` and `top_rules` remain log-file derived (they show recent activity, not all-time history — this is correct behavior for a 24h chart).

### Architectural Principle
> **Log files = recent/live data. SQLite = historical/persistent data.**  
> Never use log file scanning for totals shown on a dashboard — logs rotate and get truncated.

---

## 4. Settings — Clear WAF Detections

### Feature
Added "WAF Detection History" section to `Settings → Logging` tab. The "Clear WAF Detections" button:
- Confirms before clearing
- Calls `DELETE /api/dashboard/waf-stats`
- Shows "Cleared N records at [timestamp]" confirmation
- Raw log files are NOT affected (only `waf_events` SQLite table is cleared)

### API Endpoint
```js
// DELETE /api/dashboard/waf-stats
router.delete('/waf-stats', (req, res) => {
  try {
    const db = getDb();
    const { changes } = db.prepare('DELETE FROM waf_events').run();
    // Invalidate log-file cache so next fetch shows zeroes immediately
    _wafCache.ts   = 0;
    _wafCache.data = null;
    res.json({ cleared: changes });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
```

Key: must also invalidate `_wafCache` after delete, otherwise the 10-second cached value from log files would still show non-zero counts until the next cache expiry.

### UX
Button is styled as a warning (rose border/bg) rather than full `btn-danger` — destructive but not system-critical. Inline confirmation message shows exact row count cleared and timestamp.

---

## Summary of Changes

| File | Change |
|------|--------|
| `Dashboard.jsx` | WAF Detections card: total + /hr + /day three-metric layout |
| `Dashboard.jsx` | Added `wafPerDay`, `wafPerHour` derived from existing `chartData` |
| `IpJail.jsx` | SelectBox: drop-up logic — calculates space above/below, flips with `bottom` CSS |
| `IpJail.jsx` | SelectBox: `maxHeight` + `overflowY: auto` to cap dropdown in limited space |
| `dashboard.js` (API) | `buildPayload()`: `total`/`blocked` now from `waf_events` SQLite COUNT(*) |
| `dashboard.js` (API) | Added `DELETE /api/dashboard/waf-stats` endpoint + cache invalidation |
| `Settings.jsx` | Added Clear WAF Detections section in LoggingTab |

All 3 servers (172.20.20.181, 172.20.20.180, 192.168.0.238) deployed.
