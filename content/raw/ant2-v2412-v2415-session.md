# Ant2 v2.4.12 → v2.4.15 Session Notes

Date: 2026-05-09  
Starting version: v2.4.11  
Final version: v2.4.15  
Servers deployed: 172.20.20.180, 172.20.20.181, 192.168.0.238

---

## v2.4.12 — post_jail_count: Count 423 blocks after jailing

### Problem
After an IP is jailed and nginx geo block activates (HTTP 423), ModSecurity never sees those requests (geo block fires at rewrite phase, before access phase). So `waf_events` has zero entries for post-jail attacks. The UI showed the original jail count but no indication of continued blocking.

### Solution: countPostJailHits()
New function in `jailService.js` reads nginx access logs directly:

- Reads `NGINX_LOG_DIR` (default `/data/logs`) for all `access.log` files
- Parses JSON lines, counts lines where `status === 423` and `client_ip` is in jailed set
- Uses Redis key `jail:access_pos:{filename}` as file byte-position watermark — reads only new bytes since last call
- On bootstrap: starts at `max(0, filesize - 512KB)` to avoid reading entire large log
- Handles log rotation: if `pos > filesize`, reset to 0
- Updates `ip_jail.post_jail_count += count` for each jailed IP

Called at end of every `pollAttacks()` cycle.

New DB column: `ALTER TABLE ip_jail ADD COLUMN post_jail_count INTEGER NOT NULL DEFAULT 0`

New Redis keys:
- `jail:access_pos:{filename}` — byte offset watermark per access log file

---

## v2.4.13 — Attack count continues after jail

### Problem
Once an IP was in `ip_jail`, `pollAttacks()` skipped it with `continue`. The `attack_count` froze at jail time. The UI couldn't show ongoing attack volume.

### Fix
Instead of `continue`, update attack_count for already-jailed IPs:
```js
const jailed = db.prepare('SELECT id FROM ip_jail WHERE ip_address = ?').get(ip);
if (jailed) {
  db.prepare('UPDATE ip_jail SET attack_count = attack_count + ? WHERE ip_address = ?')
    .run(ev.cnt, ip);
  continue;
}
```

### UI: 3-tier attack counter
IpJail.jsx renders three stacked values:
1. `attack_count` — total (grows continuously)
2. `+{N} WAF after jail` — `attack_count - jailed_at_count` (jailed_at parsed from `reason` field regex: `Auto-jailed: (\d+) attacks`)
3. `+{N} HTTP 423 blocked` — `post_jail_count`

`reason` field stores the snapshot: `"Auto-jailed: 11 attacks"` — used as the freeze point.

---

## v2.4.14 — ip-blocked.html wording overhaul

Old text implied manual admin action. New text reflects automated threat detection.

| Field | Before | After |
|-------|--------|-------|
| Title | Access Denied — IP Blocked | Access Denied — Security Block |
| Subtitle | IP Address Blocked — 423 Locked | Threat Detected — Connection Blocked |
| Message strong | Your IP address has been blocked by the security policy. | Harmful activity was detected from your IP address. |
| Body | This block was applied manually by the site administrator. | Our automated security system has flagged and blocked this connection due to suspicious or malicious request patterns. If you believe this is a mistake, please contact support. |

Requires WAF container rebuild + restart (nginx-waf Docker image contains the static HTML).

---

## Jail Speed Tuning (applied across v2.4.11–v2.4.15)

| Parameter | Before | After | File |
|-----------|--------|-------|------|
| `pollAttacks` interval | 30 s | **10 s** | jailService.js |
| `releaseExpired` interval | 60 s | **30 s** | jailService.js |
| `maybeIngestWafLogs` rate limit | 30 s | **10 s** | routes/logs.js |
| First poll stagger | 5 s | 5 s | unchanged |
| First release stagger | 8 s | 8 s | unchanged |
| Default `jail_threshold` seeded | 50 | **10** | jailService.js start() |

Worst-case time to jail after these changes: ~20 s (10s ingest wait + 10s poll wait).

---

## SQLi Comment Bypass Fix — abpmart.com threshold=3

CRS rule 942110 (`--` SQL comment detection) is WARNING level (+3 pts).  
At default `inbound_anomaly_score_threshold=5` (PL1), a single `--` hit never reaches block threshold.

Fix: lower threshold to 3 for abpmart.com (host_id=14) specifically via per-host setting.  
At threshold=3: WARNING (+3) ≥ 3 → block.  
This does NOT change the paranoia level — just the score cutoff.

---

## owaps.ps1 Complete Rewrite

### SECURE/BROKEN/JAILED/REDIRECT categories

Previous script showed raw HTTP codes. New script categorizes each test result:

| Badge | Codes | Meaning |
|-------|-------|---------|
| `[  SECURE  ]` | 400, 403, 406, 000 | WAF blocked the attack |
| `[  JAILED  ]` | 423 | IP is geo-blocked (cannot verify WAF rule) |
| `[  REDIR   ]` | 301, 302 | Redirect — cannot verify |
| `[!!BROKEN!!]` | anything else (200, 500…) | Attack passed through — WAF not working |

Baseline check at start: if `GET /` returns 423, prints red warning "YOUR IP IS IN JAIL" and marks all subsequent results as JAILED (unverifiable).

Rate calculated on verifiable tests only (excludes JAILED and REDIRECT from denominator).

Broken list printed at end with all failed test names.

Summary banner uses `Write-Host -BackgroundColor DarkRed` for BROKEN status.

All box-drawing characters replaced with plain ASCII (`-`, `=`) to fix Unicode garble in Windows PowerShell console (default code page doesn't render box-drawing chars).

### Banner added
```
=================================================
    Ant2cloud OWASP WAF Pentester  v2.4.15
=================================================
```

### Compiled to .exe
Tool: PS2EXE (downloaded from GitHub, not PSGallery due to non-interactive shell limitation).  
Command: `Invoke-ps2exe -InputFile owaps.ps1 -OutputFile owaps.exe`  
Location: `C:\Users\anan\owaps.exe` (33.5 KB)  
Usage: `owaps.exe https://target.com` (no PowerShell required on execution machine)

---

## v2.4.15 Deploy — 3-server

### Server 180 (172.20.20.180)
No passwordless sudo for `cp` → SCP to `/tmp/`, then `sudo cp` from there.

### Server 181 (172.20.20.181)
Docker compose service name is `nginx-waf` (not `waf`).  
Build command: `docker compose build nginx-waf api web`

### Server 238 (192.168.0.238)
No `waf` service in docker-compose. WAF container patched via `docker exec ant2proxy-waf bash -c "cat > /etc/nginx/html/ip-blocked.html"` with stdin redirect from local file.
