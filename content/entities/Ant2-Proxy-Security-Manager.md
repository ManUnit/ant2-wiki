---
title: "Ant2 Proxy Security Manager"
type: entity
tags: [ant2, geoip, web-service]
sources: []
created: 2026-05-05
updated: 2026-05-12
---

# Ant2 Proxy Security Manager

**ANT2 Proxy Server** — ระบบ WAF และ reverse-proxy เต็มรูปแบบพร้อม GUI บริหารจัดการ รองรับ GeoIP country blocking, IP Jail, rate limiting ต่อ domain พัฒนาโดยทีมไทย 🇹🇭 มีจำหน่ายในรูปแบบ **commercial hardware appliance**.

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
| **Ant2 WAF** | ANT2 Proxy Server — GeoIP country filter, IP Jail, rate limiting |
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
                    วิเคราะห์ต้นทาง traffic
                    ระบุ IP ผู้ใช้จริงโดยอัตโนมัติ
```

| ประโยชน์ | รายละเอียด |
|----------|-----------|
| **ซ่อน Origin IP** | IP เครื่อง Ant2Cloud ไม่เปิดเผยต่อ public — Cloudflare เป็น shield |
| **ระบุ IP ต้นทาง** | วิเคราะห์ต้นทางจริงของ traffic ได้แม้ผ่านหลายชั้น |
| **GeoIP ถูกต้อง** | ตรวจสอบประเทศจาก IP ผู้ใช้จริง ไม่ใช่ IP ของ CDN node |
| **IP Jail ถูกต้อง** | Jail ผู้โจมตีจริง — ไม่ Jail Cloudflare CDN โดยไม่ตั้งใจ |
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
        ├── WAF (ANT2 Proxy Server)
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
- **Swarm Attack Protection** — ป้องกันการโจมตีแบบกระจาย หลาย IP พร้อมกัน
- **Attack Domain Identification** — ระบุได้ทันทีว่า domain ไหนกำลังถูกโจมตีอยู่

## Swarm Attack Protection — รับมือการโจมตีแบบกองทัพ

**Swarm Attack** คือการโจมตีแบบกระจายจากหลาย IP พร้อมกัน — แต่ละ IP ส่ง request ช้าพอที่จะไม่ติด rate limit แต่รวมกันแล้วทำให้ระบบล่ม WAF ทั่วไปที่ดูแค่ rate ต่อ IP จะไม่เห็นว่าเกิดอะไรขึ้น

```
IP-A  → 5 requests/min  ← ไม่ติด rate limit
IP-B  → 5 requests/min  ← ไม่ติด rate limit
IP-C  → 5 requests/min  ← ไม่ติด rate limit
...
IP-500 → 5 requests/min
─────────────────────────
รวม: 2,500 requests/min → server ล่ม
```

**Ant2Cloud รับมือ Swarm Attack ด้วย 3 กลไกพร้อมกัน:**

| กลไก | วิธีทำงาน |
|------|----------|
| **GeoIP Block** | ตัด IP ทั้ง subnet/ประเทศที่เป็นแหล่งของ swarm ได้ทันที |
| **WAF Event-based Jail** | แต่ละ IP ใน swarm ที่ส่ง payload อันตราย → ถูก jail อัตโนมัติเป็นรายตัว |
| **Rate Limiting Global** | จำกัด rate ระดับ global ต่อ domain — ป้องกัน flood แม้ IP แต่ละตัวดูเบา |

> ต่างจาก WAF ทั่วไป — Ant2 จับ attacker แต่ละตัวใน swarm ได้จาก **พฤติกรรม** (WAF violations) ไม่ใช่แค่ rate

## Attack Domain Identification — รู้ทันทีว่า domain ไหนโดนโจมตี

เมื่อถูกโจมตี สิ่งที่ต้องรู้เร็วที่สุดคือ: **โดนที่ domain ไหน?**

Ant2Cloud ระบุ domain เป้าหมายได้ทันทีแบบ real-time:

| ข้อมูล | รายละเอียด |
|--------|-----------|
| **Attack per domain** | Dashboard แสดงจำนวน WAF violations แยกต่อ domain |
| **Jailed IP → Domain** | ทุก IP ที่ถูก Jail บันทึกไว้ว่ากำลังโจมตี domain ใด |
| **Attack type per domain** | แยกประเภทการโจมตี (SQLi, XSS, RCE ฯลฯ) ต่อ domain |
| **Timeline** | เห็น pattern การโจมตีว่าเริ่มที่เมื่อไหร่ domain ไหนโดนก่อน |

**ประโยชน์ในการรับมือ:**
- รู้ว่าต้อง isolate หรือ lockdown domain ไหนก่อน
- เห็นว่า swarm กำลัง rotate เป้าหมายระหว่าง domain หรือไม่
- ตัดสินใจ apply GeoIP block หรือ custom rule ได้ตรงจุด

## See Also

- [[2026-06-07-ant2-vs-world-waf-comparison]]
- [[2026-05-06-ant2-v2361-release-notes]]
- [[2026-05-07-ant2-v242-v243-session]]
- [[2026-05-09-ant2-v248-v2411-session]]
- [[2026-05-09-ant2-v2412-v2415-session]]
- [[2026-05-13-ant2-v2426-amnesty-session]]
