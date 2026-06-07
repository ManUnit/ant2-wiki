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
| CPU | 12-core / 24 vCPU |
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

### Cloudflare Integration — ซ่อน IP เครื่อง + ดึง Real User IP

Ant2Cloud ทำงานร่วมกับ **Cloudflare** เพื่อความปลอดภัยสูงสุด:

```
User ──→ Cloudflare CDN ──→ Ant2Cloud Box ──→ Website
                              │
                    อ่าน CF-Connecting-IP header
                    ได้ real user IP ทันที
```

| ประโยชน์ | รายละเอียด |
|----------|-----------|
| **ซ่อน Origin IP** | IP เครื่อง Ant2Cloud ไม่เปิดเผยต่อ public — Cloudflare เป็น shield |
| **Real IP Extraction** | อ่าน `CF-Connecting-IP` header → ได้ IP ต้นทางจริงของ user |
| **GeoIP ถูกต้อง** | lookup ประเทศจาก real user IP ไม่ใช่ IP ของ Cloudflare node |
| **IP Jail ถูกต้อง** | jail real user IP — ไม่ jail Cloudflare CDN โดยไม่ตั้งใจ |
| **Block ถูกต้อง** | block/unblock กระทำกับ attacker จริง ไม่ใช่ intermediary |

ไม่ว่า traffic จะมาจาก Cloudflare หรือตรง — Ant2WAF ระบุ IP ต้นทางจริงได้เสมอ โดยอัตโนมัติ

### GeoIP Country Filter — เปิด/ปิดประเทศได้ทันที

Ant2Cloud ให้เว็บไซต์คุณ **บริการเฉพาะประเทศที่ต้องการ** ด้วย GeoIP ที่ทำงานเร็วมาก:

| ความสามารถ | รายละเอียด |
|------------|-----------|
| **Allow List Mode** | อนุญาตเฉพาะประเทศที่เลือก → บล็อกทุกประเทศอื่นอัตโนมัติ |
| **Block List Mode** | บล็อกประเทศที่ต้องการ → อนุญาตทุกประเทศที่เหลือ |
| **ตั้งค่าแบบ per-host** | แต่ละ domain มี GeoIP rule ของตัวเอง |
| **ตั้งค่าแบบ global** | บล็อก/อนุญาตพร้อมกันทุก domain |

**ความเร็วและความแม่นยำ:**

- GeoIP lookup เร็วมาก — **latency < 1ms ต่อ request** ไม่กระทบ performance
- มีระบบ cache ชั้นที่สอง — request ซ้ำตอบสนองได้เร็วขึ้นอีก
- รองรับ **Cloudflare CDN** — แยก IP ต้นทาง user ออกจาก CDN node ได้ถูกต้อง

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

## ความสามารถหลัก

- บริหาร Proxy Host หลาย domain ผ่าน GUI — ตั้งค่า HTTPS, HTTP/2, WebSocket, HSTS ได้ทันที
- WAF พร้อม dashboard วิเคราะห์การโจมตี real-time (XSS, SQLi, RCE, LFI, RFI)
- GeoIP country filter — Allow List / Block List ระดับประเทศ ต่อ domain หรือ global
- IP Jail อัตโนมัติ — จับ attacker ภายใน ~20 วินาที ไม่ว่าจะโจมตีเร็วหรือช้า
- Rate Limiting per domain — ป้องกัน brute force และ flood attack
- SSL อัตโนมัติ (Let's Encrypt) + อัปโหลด certificate เอง + แจ้งเตือนหมดอายุ
- Custom error page ออกแบบเองได้ทุก HTTP status code
- Dashboard Monitor วิเคราะห์ traffic, attack trend, และสถานะระบบ real-time

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
