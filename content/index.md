---
title: "Ant2Cloud — Private Cloud Appliance & WAF"
---

# Ant2Cloud 🇹🇭

## "เอา Cloud ยกกลับมาไว้ที่บ้าน"

**Ant2Cloud** คือ hardware appliance นวัตกรรมจากประเทศไทย — รวมทุกอย่างไว้ในกล่องเดียว ไม่ต้องพึ่งพา SaaS หรือ Global Cloud รายใหญ่ ใช้แค่ FTTX internet ก็สร้าง Private Cloud ได้เลย

🌐 **Website:** [ant2cloud.com](https://ant2cloud.com)

---

## All-in-One Box — ทุกอย่างในกล่องเดียว

```
GPON Fiber ──→ [ Ant2Cloud Box ] ──→ Private Cloud
                 │
                 ├── ONU/ONT built-in (ไม่ต้องซื้อแยก)
                 ├── Smart Router
                 ├── WAF — NGINX + OWASP CRS
                 ├── IP Phone / VOIP Server
                 ├── VLAN (IP Phone จาก ISP GPON)
                 ├── DDNS — อัปเดต DNS อัตโนมัติ 10–15s
                 └── 20 Virtual Machines
```

| Hardware | Spec |
|----------|------|
| CPU | 12-core / 24 vCPU |
| RAM | 64 GB |
| Storage | 2 TB |
| VM Capacity | 20 VMs |
| Form Factor | Router style — บางเบา |
| Price | **฿250,000 THB** |

---

## ทำไมต้อง Ant2Cloud?

### ❌ ปัญหาของ Global Cloud / SaaS

- Traffic ทั้งหมดผ่าน server ต่างประเทศ — **ข้อมูลรั่ว**
- ค่าบริการรายเดือนไม่มีวันจบ — **แพงระยะยาว**
- ต้องพึ่งพา Cloudflare, AWS, Azure — **ไม่มี sovereignty**
- Internet ล่ม → Cloud ล่ม → ธุรกิจหยุด

### ✅ Ant2Cloud แก้ปัญหาทั้งหมด

| | Global SaaS Cloud | Ant2Cloud |
|--|-------------------|-----------|
| Data | ผ่าน server ต่างชาติ | **อยู่ในกล่องที่บ้านคุณ** |
| ค่าใช้จ่าย | รายเดือนตลอดชีพ | **ซื้อครั้งเดียว** |
| Internet | ต้องการตลอด | **ทำงานได้ offline บางส่วน** |
| การควบคุม | vendor lock-in | **คุณเป็นเจ้าของ 100%** |
| GeoIP Filter | มักคิดเงินแยก | **มีในตัว — เลือกประเทศได้** |
| Static IP | ต้องซื้อจาก ISP | **ไม่ต้อง — DDNS built-in** |
| VOIP | ซื้อ PABX แยก | **มีในตัว** |
| Router | ซื้อแยก | **มีในตัว** |
| ONU/ONT | ซื้อแยก | **มีในตัว** |

---

## Ant2 WAF — Security ระดับ Enterprise

Ant2Cloud มาพร้อม **Ant2 WAF** ที่พัฒนาโดยทีมไทย บน NGINX + OWASP CRS มาตรฐานโลก

### 3 ชั้นป้องกัน ที่ไม่มีใครทำได้ในราคานี้

```
ชั้น 1 → GeoIP Block    ปิดประเทศที่ไม่ต้องการ
ชั้น 2 → IP Jail        จับ attacker อัตโนมัติ ภายใน 20 วินาที
ชั้น 3 → WAF Rules      OWASP CRS 4.26.0 — SQLi, XSS, RCE, LFI
```

### Cloudflare Shield + Real IP Extraction — ซ่อน IP เครื่อง แต่ block User ได้ถูกต้อง

```
User → Cloudflare CDN → [ Ant2Cloud Box ] → Website
         (IP เครื่องซ่อนอยู่)    ↑
                           ดึง real user IP
                           จาก CF-Connecting-IP header
```

**ทำไมต้องทำแบบนี้:**

- ✅ IP เครื่องไม่เปิดเผย — attacker ไม่รู้จะ DDoS ที่ไหน
- ✅ Ant2WAF อ่าน `CF-Connecting-IP` header → ได้ IP จริงของ user
- ✅ GeoIP lookup, IP Jail, และ Block ทำงานกับ **IP ต้นทางจริง** ไม่ใช่ IP ของ Cloudflare
- ✅ rate limiting / IP Jail ไม่ jail Cloudflare CDN node โดยไม่ตั้งใจ

**2-Stage IP Detection:**

| สถานการณ์ | IP ที่ใช้ |
|-----------|----------|
| Traffic ผ่าน Cloudflare | `CF-Connecting-IP` header (real user IP) |
| Traffic ตรง (non-CF) | `$remote_addr` (TCP source IP) |

Ant2WAF ตรวจสอบอัตโนมัติ — ไม่ต้องตั้งค่าเพิ่ม

### GeoIP Country Filter — เสิร์ฟเฉพาะประเทศที่ต้องการ

Ant2Cloud รองรับการตั้งค่า **Allow List** หรือ **Block List** ระดับประเทศ:

```
โหมด Allow List:  อนุญาต TH เท่านั้น → บล็อกทุกประเทศอื่น ✅
โหมด Block List:  บล็อก CN, RU, KP  → อนุญาตทุกประเทศอื่น ✅
```

- ระบุได้ทั้ง **รายโฮสต์** (per-host) และ **global** ทุก domain พร้อมกัน
- GeoIP lookup เร็วมาก — **latency < 1ms ต่อ request** ไม่ส่งผลต่อประสิทธิภาพ
- มีระบบ cache — request ซ้ำตอบสนองได้เร็วขึ้นอีก
- รองรับ **Cloudflare CDN** — แยก IP ต้นทาง user จาก CDN node ได้ถูกต้อง
- ใช้ร่วมกับ **IP Jail** ได้ทันที — บล็อกประเทศก่อน จับ attacker ที่เหลือ

### IP Jail — นวัตกรรมที่แตกต่าง

WAF ทั่วโลก block จาก **rate** (จำนวน request ต่อนาที)

**Ant2 block จาก WAF rule violation count** — จับ slow attack ที่คนอื่นพลาด:

> ผู้โจมตีส่ง payload อันตราย 1 request ทุก 30 วินาที → rate-based WAF ไม่ block → **Ant2 block หลัง 10 violations** ไม่ว่าจะช้าแค่ไหน

### เปรียบกับ WAF ชั้นนำของโลก

| | Ant2Cloud | Cloudflare Business | Imperva | FortiWeb |
|--|-----------|--------------------|---------| ---------|
| ราคา | **฿250,000 (ครั้งเดียว)** | ~$3,000/ปี | ~$20,000+/ปี | $10,000–$50,000 |
| GeoIP Block | ✅ | ✅ | ✅ | ✅ |
| Auto IP Jail | ✅ event-based | ✅ rate-based | ✅ behavioral | ✅ |
| Cloudflare Real IP | ✅ **CF-Connecting-IP** | N/A (IS CF) | ✅ | ✅ |
| Data Sovereignty | ✅ **100% on-premise** | ❌ ผ่าน CF | ❌ ผ่าน Imperva | ✅ |
| VOIP Server | ✅ **built-in** | ❌ | ❌ | ❌ |
| ONU/ONT | ✅ **built-in** | ❌ | ❌ | ❌ |
| VM Platform | ✅ **20 VMs** | ❌ | ❌ | ❌ |
| Smart Router | ✅ **built-in** | ❌ | ❌ | ❌ |

---

## สำหรับใคร?

- 🏢 **SME / Office** — ต้องการ Private Cloud + VOIP + Security ในงบเดียว
- 🏠 **Home Office** — FTTX internet + Ant2Cloud = Cloud ส่วนตัว
- 🏥 **Healthcare / Finance** — ข้อมูลต้องไม่ออกนอกองค์กร
- 🇹🇭 **องค์กรรัฐ** — Data sovereignty 100% ในประเทศ

---

## Knowledge Base

Wiki นี้รวบรวมความรู้ด้าน WAF, NGINX, OWASP CRS และ Security Operations

- [[Ant2-Proxy-Security-Manager]] — Ant2 WAF full documentation
- [[auto-jail-pipeline]] — IP Jail pipeline architecture
- [[geoip-country-blocking]] — GeoIP implementation
- [[request-flow-layers]] — 5-layer defense architecture
- [[OWASP-CRS]] — OWASP Core Rule Set
- [[2026-06-07-ant2-vs-world-waf-comparison]] — Ant2 vs World WAF comparison

---

> 🇹🇭 **Ant2Cloud — พัฒนาในประเทศไทย สำหรับโลก**
> 
> [ant2cloud.com](https://ant2cloud.com)
