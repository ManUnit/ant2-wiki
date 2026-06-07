---
title: "Ant2 Proxy Security Manager"
type: entity
tags: [ant2, project, nginx, waf, modsecurity, crs, geoip, redis, docker, react, nodejs]
sources: [2026-05-05-ant2-progress, 2026-05-05-ant2-changelog, 2026-05-07-ant2-v242-v243-session, 2026-05-09-ant2-v248-v2411-session, 2026-05-09-ant2-v2412-v2415-session, 2026-05-13-ant2-v2426-amnesty-session, 2026-05-12-ant2-v2420-redis-monitor-domain-fix]
created: 2026-05-05
updated: 2026-05-12
---

# Ant2 Proxy Security Manager

Full-stack NGINX reverse-proxy GUI with integrated [[ModSecurity]] v3 + [[OWASP-CRS]], GeoIP country blocking, Redis caching, and per-host rate limiting. Built by an independent developer in Thailand 🇹🇭. Available as open-source software and as a **commercial hardware appliance**.

## Commercial Product — Ant2Cloud Box Appliance

> **"เอา Cloud ยกกลับมาไว้ที่บ้าน"** — Ant2Cloud คือ innovation ที่ไม่ต้องพึ่งพา SaaS หรือ Global Cloud รายใหญ่ ใช้แค่ FTTX internet บ้านหรือ office ก็สร้าง Private Cloud ได้เลย

| Attribute | Detail |
|-----------|--------|
| Product name | **Ant2Cloud** |
| Website | **https://ant2cloud.com** |
| Form factor | Hardware box appliance — router style, บางเบา |
| Price | **฿250,000 THB** |
| Origin | Thailand 🇹🇭 — พัฒนาและผลิตในประเทศไทย |

### Hardware Specifications

| Component | Spec |
|-----------|------|
| CPU / GPU | 24-core GPU |
| RAM | 64 GB |
| Storage | 2 TB HDD |
| VM Capacity | รองรับได้ 20 VMs |
| Form Factor | Router style — บางเบา ติดตั้งง่าย |

### Built-in Services (All-in-One)

| Feature | Detail |
|---------|--------|
| **Ant2 WAF** | NGINX + OWASP CRS — GeoIP country filter, IP Jail, rate limiting |
| **Smart Router** | Built-in smart router ในตัว |
| **ONU / ONT** | Built-in — เสียบสาย GPON fiber ได้ตรงเลย ไม่ต้องซื้อ ONU แยก |
| **IP Phone Server** | VOIP server ในตัว — รองรับ IP Phone ทั้ง office |
| **VLAN Support** | แบ่ง VLAN จาก ISP (GPON) เชื่อมเข้า VOIP server ได้ทันที |
| **DDNS** | Dynamic DNS built-in — ตรวจจับ IP เปลี่ยน → อัปเดต DNS ภายใน **10–15 วินาที** |
| **Custom Domain** | ใช้ domain ของตัวเองได้เลย ไม่ต้องซื้อ static IP จาก ISP |
| **Private Cloud** | รัน 20 VM บน FTTX internet บ้าน/office |

### DDNS — Dynamic DNS (ไม่ต้องซื้อ Static IP)

ISP บ้านทั่วไปให้ IP แบบ dynamic (เปลี่ยนได้ตลอด) — Ant2Cloud แก้ปัญหานี้ด้วย DDNS built-in:

```
IP เปลี่ยน (ISP assign ใหม่)
  ↓ Ant2Cloud ตรวจจับได้ทันที
  ↓ อัปเดต DNS record อัตโนมัติ
  ↓ ภายใน 10–15 วินาที
Domain ของคุณชี้มาถูกต้องแล้ว ✅
```

| | ไม่มี DDNS | Ant2Cloud DDNS |
|--|-----------|----------------|
| IP เปลี่ยน | website ล่ม | **อัปเดตอัตโนมัติ 10–15s** |
| ต้องการ Static IP | ✅ ต้องซื้อ (~฿500/เดือน) | ❌ ไม่ต้อง |
| ใช้ domain ของตัวเอง | ❌ IP เปลี่ยนได้ | ✅ ใช้ได้ตลอด |
| downtime เมื่อ IP เปลี่ยน | นาที–ชั่วโมง | **< 15 วินาที** |

### GeoIP Country Filter — เปิด/ปิดประเทศได้ทันที

Ant2Cloud ให้เว็บไซต์คุณ **บริการเฉพาะประเทศที่ต้องการ** ด้วย GeoIP ที่ทำงานเร็วมาก:

| ความสามารถ | รายละเอียด |
|------------|-----------|
| **Allow List Mode** | อนุญาตเฉพาะประเทศที่เลือก → บล็อกทุกประเทศอื่นอัตโนมัติ |
| **Block List Mode** | บล็อกประเทศที่ต้องการ → อนุญาตทุกประเทศที่เหลือ |
| **ตั้งค่าแบบ per-host** | แต่ละ domain มี GeoIP rule ของตัวเอง |
| **ตั้งค่าแบบ global** | บล็อก/อนุญาตพร้อมกันทุก domain |

**ฐานข้อมูลและความเร็ว:**

- ใช้ **MaxMind GeoLite2** (ฟอร์แมต `.mmdb`) — มาตรฐานอุตสาหกรรมระดับโลก
- NGINX อ่าน MMDB โดยตรงจาก **memory** — latency **< 1ms ต่อ request**
- ผลลัพธ์ cache เพิ่มใน **Redis** — request ซ้ำไม่ต้อง lookup ใหม่
- รองรับ **Cloudflare CDN** ด้วย 2-stage map (ตรวจ `CF-Connecting-IP` header)

```
Request มาถึง
  ↓ NGINX ตรวจ IP จาก Cloudflare header หรือ TCP source
  ↓ Lookup จาก GeoLite2.mmdb (< 1ms, in-memory)
  ↓ เทียบกับ allow/block list
  ↓ ถ้าบล็อก → HTTP 423 + custom block page
  ↓ ถ้าผ่าน → ต่อไปยัง WAF rules + IP Jail
```

> ตัวอย่างการใช้งาน: ร้านค้าออนไลน์ไทย → Allow TH เท่านั้น ตัดการโจมตีจากต่างประเทศได้ 90%+ ก่อนถึง WAF

### แนวคิด: Private Cloud ที่บ้านและ Office

```
GPON Fiber (ISP)
  └── Ant2Cloud Box (ONU/ONT built-in)
        ├── Smart Router
        ├── VLAN → IP Phone / VOIP Server
        ├── WAF (NGINX + OWASP CRS)
        ├── 20x Virtual Machines
        └── Private Cloud Services
```

ไม่ต้องพึ่ง:
- ❌ AWS / Azure / GCP (SaaS global cloud)
- ❌ Cloudflare (traffic ไม่ผ่าน third party)
- ❌ ONU/ONT แยก
- ❌ VOIP server แยก
- ❌ Router แยก

ทุกอย่างอยู่ในกล่องเดียว ราคา **฿250,000 THB**

## Current Version

**v2.4.29** (latest release)

## v2.4.16–v2.4.26 Changes

| Version | Change |
|---------|--------|
| v2.4.20 | Redis Monitor panel in `/monitor` SSE stream (hit rate, memory, ops/sec); `jail:dom:<ip>` Redis SET to persist domain attribution past `waf_events` 2h purge; `/counters` route fallback to Redis when DB empty |
| v2.4.16–v2.4.19, v2.4.21–v2.4.25 | (intermediate: UI improvements, compact row table theme, Monitor dashboard layout, SelectBox portal dropdown) |
| v2.4.26 | [[jail-amnesty-list]]: `jail_whitelist` table + `/api/jail/whitelist` CRUD + jailService skip logic + 3rd Amnesty tab (emerald); GeoIP `toggleCountry()` semantic fix — action now matches mode |

## v2.4.12–v2.4.15 Changes

| Version | Change |
|---------|--------|
| v2.4.12 | `countPostJailHits()` — count 423 blocks from nginx access log via Redis watermark; new `post_jail_count` DB column |
| v2.4.13 | Attack count continues growing after jail (was frozen at jail time); 3-tier UI counter |
| v2.4.14 | `ip-blocked.html` wording updated to automated threat detection language |
| v2.4.15 | Jail poll 10s, ingest rate 10s, release 30s; default threshold 10; 3-server deploy |

### Jail Pipeline Settings (v2.4.15)

| Parameter | Value |
|-----------|-------|
| `pollAttacks` interval | 10 s |
| `releaseExpired` interval | 30 s |
| `maybeIngestWafLogs` rate limit | 10 s |
| Default `jail_threshold` | 10 attacks |
| Worst-case time to jail | ~20 s |

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS 3 |
| API | Node.js / Express 4 + SQLite (better-sqlite3) |
| WAF engine | NGINX + ModSecurity v3 + OWASP CRS |
| Cache / GeoIP | Redis 7 (128MB LRU) |
| Containers | Docker Compose (4 services) |
| Auth | JWT (bcryptjs) |
| SSL | Let's Encrypt ACME + manual PEM/CRT upload |

## Services (Docker Compose)

| Service | Container | Role |
|---------|-----------|------|
| `nginx-waf` | `ant2proxy-waf` | NGINX + ModSecurity + CRS |
| `api` | `ant2proxy-api` | Express REST API |
| `web` | `ant2proxy-web` | React frontend (Vite build) |
| `redis` | `ant2proxy-redis` | Cache + GeoIP lookup cache |

## Production Deployment

- **Path**: `/opt/ant2proxy/` (post-v2.4.x; old installs at `/opt/nginx-gui/`)
- **Start**: `sudo docker compose up -d --build` (or `ant2-proxy rebuild`)
- **CLI**: `ant2-proxy {start|stop|restart|rebuild|logs|status}` (installed via `install.sh`)
- **Project name**: `ant2proxy` (containers: `ant2proxy-waf`, `ant2proxy-api`, `ant2proxy-web`, `ant2proxy-redis`)

## Custom WAF Rules

Three global custom rules ship in `nginx-waf/modsecurity-engine.conf` (included by every per-host config) since v2.4.2. They fill gaps where CRS does not inspect the `ARGS` collection for certain attack patterns — see [[crs-rule-scope]] and [[custom-waf-rules]].

| Rule ID | Attack | Pattern |
|---------|--------|---------|
| 9500101 | PHP extension in GET/POST ARGS | `.ph(p[0-9]?|tml|ar)` at end of value |
| 9500102 | PHP double extension in ARGS | `.php.jpg` style filenames |
| 9500103 | Open redirect in ARGS | External URL (`https?://`) in redirect/url/return/goto params |

> [!warning] Rule 9500103 will block OAuth callback flows that pass external URLs in `redirect=` parameters. Add a per-host bypass rule for known callback paths.

## Key Features

- Proxy host CRUD with path rules, force HTTPS, HTTP/2, WebSocket, HSTS
- WAF: 3-way mode, [[paranoia-levels]] 1–4, [[platform-presets]] (18 incl. Magento), [[bypass-presets]] (10)
- WAF Monitor: time-series charts, attack categories (XSS/SQLi/RCE/LFI/RFI/Proto), audit log
- [[geoip-country-blocking]]: per-host + global, Cloudflare-aware (2-stage map)
- [[rate-limiting-nginx]]: limit_conn / limit_req / limit_rate per host + monitor + custom 429 page
- SSL: Let's Encrypt + manual upload, expiry tracking
- Custom error pages (400/401/403/404/429/451/500/502/503/504/default) with [[wysiwyg-iframe-editor]]
- **Ant2 Config tab**: edit `nginx-ant2-custom.conf` + nginx -t test button
- **[[server-header-disclosure]]**: `more_clear_headers 'Server'` via headers-more module

## Critical Architectural Rule

> WAF conf must always be written **before** nginx conf. inotify triggers nginx reload on the first file write — if WAF conf doesn't exist yet, nginx test fails.

See [[inotify-write-order-pattern]].

## Pending Backlog

| Feature | Priority |
|---------|----------|
| WAF Monitor: filter by attack category | High |
| WAF Monitor: export CSV | High |
| Backup & restore DB via UI | High |
| Multi-user / RBAC | High |
| SSL wildcard via DNS-01 | Medium |
| Dark mode | Low |

## See Also

- [[OWASP-CRS]]
- [[ModSecurity]]
- [[request-flow-layers]]
- [[auto-jail-pipeline]]
- [[jail-amnesty-list]]
- [[redis-key-patterns]]
- [[custom-waf-rules]]
- [[crs-rule-scope]]
- [[waf-validation-testing]]
- [[platform-presets]]
- [[bypass-presets]]
- [[geoip-country-blocking]]
- [[rate-limiting-nginx]]
- [[inotify-write-order-pattern]]
- [[server-header-disclosure]]
- [[wysiwyg-iframe-editor]]
- [[2026-05-06-ant2-v2361-release-notes]]
- [[2026-05-07-ant2-v242-v243-session]]
- [[2026-05-09-ant2-v248-v2411-session]]
- [[2026-05-09-ant2-v2412-v2415-session]]
- [[2026-05-13-ant2-v2426-amnesty-session]]
