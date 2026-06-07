# Ant2 Proxy Security Manager — Development Changelog

> Session: May 1–3, 2026 | Server: anan@192.168.0.238 → 172.20.20.180 | Target: /opt/ant2-proxy/

---

## v2.3 — Nginx Rate Limiting (May 3, 2026)

### New Feature: Per-Host Rate Limiting (limit_conn / limit_req / limit_rate)

Full-stack implementation of nginx rate limiting with GUI configuration and real-time monitoring.

### 1. Database — 6 New Columns on `hosts`
```sql
ALTER TABLE hosts ADD COLUMN limit_conn        INTEGER NOT NULL DEFAULT 0;
ALTER TABLE hosts ADD COLUMN limit_req_rate    TEXT    NOT NULL DEFAULT "";
ALTER TABLE hosts ADD COLUMN limit_req_burst   INTEGER NOT NULL DEFAULT 0;
ALTER TABLE hosts ADD COLUMN limit_req_nodelay INTEGER NOT NULL DEFAULT 0;
ALTER TABLE hosts ADD COLUMN limit_rate        TEXT    NOT NULL DEFAULT "";
ALTER TABLE hosts ADD COLUMN limit_rate_after  TEXT    NOT NULL DEFAULT "";
```

### 2. Nginx Config Generator — `api/src/services/nginxConfig.js`
```js
// New functions:
buildRateLimitZones(host)  // → limit_req_zone in http{} context (outside server blocks)
buildRateLimitBlock(host)  // → limit_conn, limit_req, limit_rate inside server{} blocks
```

- Zones generated per-host with unique name `req_${host.id}`
- Block inserted in HTTP, HTTPS, and fallback HTTPS server blocks
- 429 status code for all rate limit responses

### 3. Global nginx.conf — `nginx-waf/nginx.conf`
```nginx
# Added in http{} block:
limit_conn_zone $binary_remote_addr zone=perip:10m;
# Per-host request rate zones are generated in each host conf file
```

### 4. API CRUD — `api/src/routes/hosts.js`
- `row2host()`: maps 6 new DB columns to API response
- `POST /api/hosts`: accepts rate limit fields on create
- `PUT /api/hosts/:id`: accepts rate limit fields on update

### 5. Rate Limit Monitor API — `api/src/routes/logs.js`
```
GET /api/logs/rate-limit/stats?range=1h|6h|24h|7d
```
Response:
```json
{
  "hosts": [...],          // per-host config summary (has_rate_limit flag)
  "summary": { "totalLimitReq": 0, "totalLimitConn": 0, "total429": 0 },
  "topIps": [{"ip": "...", "count": N}],
  "perHost429": {"host_1": 5, ...},
  "timeseries": [{"ts": "...", "req": N, "conn": N}]
}
```
Parses:
- nginx error logs for "limiting requests" / "limiting connections" events
- JSON access logs for 429 status responses

### 6. Frontend — Hosts Advanced Tab (Rate Limiting Section)
`web/src/pages/Hosts.jsx` → `renderAdvanced()`:
- Connection Limit: number input (0 = unlimited)
- Request Rate: text input (e.g. `10r/s`, `60r/m`)
- Burst: number input
- Nodelay: checkbox toggle
- Bandwidth Limit: text input (e.g. `100k`, `1m`)
- Rate After: text input (e.g. `500k`)

### 7. Frontend — Rate Limiting Monitor Tab
`web/src/pages/Settings.jsx` → new "Rate Limiting" tab (Gauge icon):
- Range selector: 1h / 6h / 24h / 7d
- 3 summary cards: Request Limits Hit, Conn Limits Hit, 429 Responses
- Time-series bar chart of limiting events
- Top Rate-Limited IPs table (top 20)
- Per-Host 429 Response counts
- Full config overview table (all hosts with limit status)

### Package
```
ant2ProxySecurityManager-v2.3.tar.gz  ~117KB
```

---

## v2.2 — Bug Fixes & Improvements (May 2, 2026)

### 1. Geo IP Lookup Fix

### Error
```
total: 133  with_geo: 0
ip-api response: {"status":"fail","message":"SSL unavailable for this endpoint..."}
```

### Root Cause
`batchGeoLookup()` ใน `api/src/routes/logs.js` ใช้ `https.request()` แต่ **ip-api.com free tier รองรับแค่ HTTP** ไม่ใช่ HTTPS

### Fix — `api/src/routes/logs.js`
```js
// Before
const req = https.request(opts, ...)

// After
const http = require('http');
const req = http.request(opts, ...)  // ip-api.com free tier = HTTP only
```

### Additional Fix — Domain-named Log Files Not Ingested
`ingestWafLogs()` filter แค่ `host_*.log` ทำให้ `english.th-ai-land.com.log` ไม่ถูก ingest

```js
// Before
const files = fs.readdirSync(wafDir).filter(f => /^host_\d+\.log$/.test(f));

// After — include all .log files, resolve hostId from domain map
const files = fs.readdirSync(wafDir)
  .filter(f => f.endsWith('.log') && !f.includes('debug') && !f.includes('error'));
let domainMap = {};
const rows = db.prepare('SELECT id, domain FROM hosts').all();
rows.forEach(r => { domainMap[r.domain] = r.id; });
```

### Result
```
after backfill with_geo: 75
top countries: [
  {"country_code":"TH","country_name":"Thailand","c":70},
  {"country_code":"JP","country_name":"Japan","c":4},
  {"country_code":"NL","country_name":"Netherlands","c":1}
]
```

---

## 2. NTP Sync Fix (Real Clock Sync)

### Error
```
Note: ntpdate not available. Server: th.pool.ntp.org
```
NTP ไม่ได้ sync จริง — แค่แสดงเวลาปัจจุบันแทน

### Root Cause
- `ntpdate` binary ไม่ได้ติดตั้งใน container (มีแค่ `openntpd`)
- Container ไม่มี `CAP_SYS_TIME` → ตั้งนาฬิกาไม่ได้

### Fix 1 — `api/src/routes/settings.js`
เขียน NTP UDP query ด้วย Node.js โดยตรง (ไม่พึ่ง binary)

```js
const dgram = require('dgram');

function ntpQuery(server, timeoutMs = 8000) {
  return new Promise((resolve, reject) => {
    const NTP_DELTA = 2208988800;
    const buf = Buffer.alloc(48, 0);
    buf[0] = 0x1b; // LI=0, VN=3, Mode=3 (client)
    const t1 = Date.now();
    const client = dgram.createSocket('udp4');
    // ... query NTP server on UDP port 123
    // returns { serverTime, offset, delay, stratum }
  });
}
```

ใช้ `date -s` ตั้งนาฬิกาหลัง query สำเร็จ

### Fix 2 — `docker-compose.yml`
```yaml
api:
  cap_add:
    - SYS_TIME   # อนุญาตให้ container ตั้งนาฬิกา host
```

### Result
```
Server   : th.pool.ntp.org
Stratum  : 1
Offset   : +17 ms
Delay    : 51 ms
NTP time : 2026-05-01 13:19:02 UTC
Set to   : 2026-05-01T06:19:02.002Z
```

---

## 3. Brand Rename

### Change
เปลี่ยนจาก **NGINX GUI** เป็น **Ant2 Proxy Security Manager**

### Files Changed
| File | Change |
|------|--------|
| `web/src/components/Sidebar.jsx` | `NGINX GUI` → `Ant2`, `Proxy + WAF Manager` → `Proxy Security Manager` |
| `web/src/pages/Login.jsx` | `NGINX GUI` → `Ant2`, `Proxy Manager + WAF` → `Proxy Security Manager` |
| `web/index.html` | title → `Ant2 Proxy Security Manager` |

---

## 4. inotify Race Condition Fix (nginx WAF conf missing)

### Error
```
[watcher] nginx config test FAILED — skipping reload
"modsecurity_rules_file" directive Failed to open the file:
/etc/modsecurity.d/custom/host_1.conf
```

### Root Cause
**Race condition**: API เขียน nginx conf → inotify watcher detect → nginx reload ทันที → แต่ WAF conf ยังไม่ถูกเขียน

```
Timeline (before fix):
  1. writeFileSync(host_1.conf)     ← nginx conf written
  2. inotify triggers nginx test    ← nginx tries to reload
  3. writeFileSync(modsec conf)     ← too late! nginx already failed
```

### Fix — `api/src/services/nginxConfig.js`
เขียน WAF conf **ก่อน** nginx conf เสมอ

```js
// Before
fs.writeFileSync(hostConfPath(host.id), nginxConf);  // nginx first ← WRONG
if (waf?.enabled) {
  fs.writeFileSync(wafConfPath(host.id), wafConf);   // waf second ← TOO LATE
}

// After
if (waf && wafMode !== 'off') {
  fs.writeFileSync(wafConfPath(host.id), wafConf);   // WAF first ← CORRECT
}
fs.writeFileSync(hostConfPath(host.id), nginxConf);  // nginx after
```

---

## 5. Docker Compose `version` Warning Fix

### Error
```
WARN[0000] /opt/ant2-proxy/docker-compose.yml: the attribute `version`
is obsolete, it will be ignored, please remove it to avoid potential confusion
```

### Fix — `docker-compose.yml`
```yaml
# Before
version: '3.8'
services:

# After
services:
```

---

## 6. Docker Image & Container Rename

### Change
เปลี่ยนชื่อ image และ container จาก `ngx-*` เป็น `ant2proxy-*`

### `docker-compose.yml`
```yaml
# Before
nginx-waf:
  container_name: ngx-waf

api:
  container_name: ngx-api

web:
  container_name: ngx-web

# After
nginx-waf:
  image: ant2proxy-waf
  container_name: ant2proxy-waf

api:
  image: ant2proxy-api
  container_name: ant2proxy-api

web:
  image: ant2proxy-web
  container_name: ant2proxy-web
```

### Build Output (After)
```
✔ Image ant2proxy-waf   Built
✔ Image ant2proxy-api   Built
✔ Image ant2proxy-web   Built
Container ant2proxy-waf   Started
Container ant2proxy-api   Started
Container ant2proxy-web   Started
```

---

## 7. Package Installer

### Files Created
| File | Purpose |
|------|---------|
| `install.sh` | Interactive installer — ถาม config, สร้าง `.env`, build containers, ติดตั้ง systemd service + CLI |
| `build-package.sh` | สร้าง `ant2ProxySecurityManager.tar.gz` จาก source |

### Install Flow
```bash
# Deploy to target machine
scp ant2ProxySecurityManager.tar.gz user@TARGET:/tmp/
ssh user@TARGET
cd /tmp && tar -xzf ant2ProxySecurityManager.tar.gz
sudo bash ant2ProxySecurityManager/install.sh
```

### installer ทำอะไร
1. ✅ ตรวจสอบ Docker + Docker Compose
2. ✅ ถาม install dir, ports, admin user/password, timezone
3. ✅ Auto-generate `JWT_SECRET` แบบ random
4. ✅ Build + start containers ทั้ง 3 ตัว
5. ✅ ติดตั้ง systemd service (auto-start หลัง reboot)
6. ✅ ติดตั้ง CLI: `ant2-proxy {start|stop|restart|rebuild|logs|status}`

### Package Size
```
ant2ProxySecurityManager.tar.gz  ~82KB
```

---

## Summary — All Files Changed

| File | Changes |
|------|---------|
| `api/src/routes/logs.js` | http geo lookup, domain log ingest |
| `api/src/routes/settings.js` | NTP UDP query, `date -s` clock sync |
| `api/src/services/nginxConfig.js` | Write WAF conf before nginx conf (race fix) |
| `docker-compose.yml` | `cap_add: SYS_TIME`, image/container rename, remove `version:` |
| `web/src/components/Sidebar.jsx` | Brand rename |
| `web/src/pages/Login.jsx` | Brand rename |
| `web/index.html` | Browser tab title |
| `install.sh` | **NEW** — interactive installer |
| `build-package.sh` | **NEW** — package builder |
