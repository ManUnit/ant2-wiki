---
title: "Ant2Cloud — Private Cloud Appliance & WAF"
---

# Ant2Cloud 🇹🇭

## "Bring the Cloud Home"

**Ant2Cloud** is a hardware appliance innovation from Thailand — everything in one box, no dependency on SaaS or major global cloud providers. With just FTTX internet, you can run your own Private Cloud.

🌐 **Website:** [ant2cloud.com](https://ant2cloud.com)

---

## All-in-One Box — Everything in a Single Device

```
GPON Fiber ──→ [ Ant2Cloud Box ] ──→ Private Cloud
                 │
                 ├── ONU/ONT built-in (no separate device needed)
                 ├── Smart Router
                 ├── WAF — ANT2 Proxy Server
                 ├── IP Phone / VOIP Server
                 ├── VLAN (IP Phone from ISP GPON)
                 ├── DDNS — auto DNS update in 10–15s
                 └── 20 Virtual Machines
```

| Hardware | Spec |
|----------|------|
| CPU | 12-core / 24 vCPU |
| RAM | 64 GB |
| Storage | 2 TB |
| VM Capacity | 20 VMs |
| Form Factor | Router style — slim & lightweight |
| Price | **Cheaper Local price ** |

---

## Why Ant2Cloud?

### ❌ Problems with Global Cloud / SaaS

- All traffic passes through overseas servers — **data exposure risk**
- Monthly subscription fees that never end — **expensive long-term**
- Dependent on Cloudflare, AWS, Azure — **no data sovereignty**
- Internet outage → Cloud down → Business stops

### ✅ Ant2Cloud Solves Everything

| | Global SaaS Cloud | Ant2Cloud |
|--|-------------------|-----------|
| Data | Through foreign servers | **Stays in your box** |
| Cost | Monthly forever | **One-time purchase** |
| Internet | Required at all times | **Partially offline capable** |
| Control | Vendor lock-in | **100% yours** |
| GeoIP Filter | Usually paid separately | **Built-in — choose countries** |
| Static IP | Must buy from ISP | **Not needed — DDNS built-in** |
| VOIP | Buy PABX separately | **Built-in** |
| Router | Buy separately | **Built-in** |
| ONU/ONT | Buy separately | **Built-in** |

---

## Ant2 WAF — Enterprise-Grade Security

Ant2Cloud includes **Ant2 WAF** developed by Thai engineers — **ANT2 Proxy Server** meeting international standards.

### 3-Layer Defense — Unmatched at This Price

```
Layer 1 → GeoIP Block    Block unwanted countries
Layer 2 → IP Jail        Auto-capture attackers within 20 seconds
Layer 3 → WAF Rules      Auto-detect SQLi, XSS, RCE, LFI
```

### Real IP Detection — Always Identifies the True IP, Through Any Number of Layers

```
User → CDN / Proxy / Load Balancer → [ Ant2Cloud Box ] → Website
                                            ↑
                               Analyzes and identifies true source IP
                               automatically — always
```

**Ant2WAF always identifies the true IP of users or attackers, regardless of how many layers they go through** — whether CDN, reverse proxy, load balancer, or firewall in between, Ant2WAF correctly identifies the real source IP.

- ✅ Device IP hidden — attackers don't know what to target for DDoS
- ✅ GeoIP lookup works on **true source IP** — correct country even through proxy
- ✅ IP Jail captures **actual attacker** — doesn't accidentally jail CDN nodes
- ✅ Block/Unblock targets real attacker IP, not intermediaries
- ✅ Automatic — no additional configuration needed

### GeoIP Country Filter — Serve Only the Countries You Want

Ant2Cloud supports **Allow List** or **Block List** at country level:

```
Allow List mode:  Allow TH only → block all other countries ✅
Block List mode:  Block CN, RU, KP → allow all others ✅
```

- Configurable both **per-host** and **global** across all domains at once
- GeoIP lookup is extremely fast — **latency < 1ms per request** — no performance impact
- Second-layer cache — repeated requests respond even faster
- Supports **Cloudflare CDN** — correctly separates user source IP from CDN node
- Works with **IP Jail** immediately — block countries first, then jail remaining attackers

### IP Jail — The Innovation That Makes the Difference

Most WAFs worldwide block based on **rate** (requests per minute)

**Ant2 blocks based on WAF rule violation count** — catching what others miss:

> Attacker sends dangerous payload once every 30 seconds → rate-based WAF won't block → **Ant2 blocks after 10 violations** regardless of how slow the attack is

### Compare with World-Leading WAFs

| | Ant2Cloud | Cloudflare Business | Imperva | Huawei Cloud WAF | FortiWeb |
|--|-----------|--------------------|---------|-----------------| ---------|
| Price | **฿250,000 (one-time)** | ~$3,000/yr | ~$20,000+/yr | Pay-per-use | $10,000–$50,000 |
| GeoIP Block | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auto IP Jail | ✅ event-based | ✅ rate-based | ✅ behavioral | ✅ rate-based | ✅ |
| Real IP Detection | ✅ | N/A (IS CF) | ✅ | ✅ | ✅ |
| SSE / Streaming | ✅ | ⚠️ | ⚠️ | ❌ *(Mar 2026)* | ⚠️ |
| Data Sovereignty | ✅ **100% on-premise** | ❌ through CF | ❌ through Imperva | ❌ Huawei Cloud | ✅ |
| VOIP Server | ✅ **built-in** | ❌ | ❌ | ❌ | ❌ |
| ONU/ONT | ✅ **built-in** | ❌ | ❌ | ❌ | ❌ |
| VM Platform | ✅ **20 VMs** | ❌ | ❌ | ❌ | ❌ |
| Smart Router | ✅ **built-in** | ❌ | ❌ | ❌ | ❌ |

---

## Huawei Cloud WAF — SSE Streaming Issue *(issue detected Mar 2026)*

> **Huawei Cloud WAF** has issues with **SSE (Server-Sent Events)** — technology used in AI chat, live dashboards, and real-time notifications

**Root Cause:** Huawei WAF operates as a proxy that **buffers responses before forwarding** to clients — but SSE is a stream with no end. The WAF waits for buffering to complete → it never completes.

| Issue | Symptom |
|-------|---------|
| Response buffering | SSE events don't reach client in real-time — stuck waiting |
| Connection timeout | WAF cuts long-lived connections prematurely |
| Chunked transfer | Destroys streaming — events arrive in batches instead |

**Real-world Impact:**
- AI chat application → screen freezes, no character streaming
- Live dashboard → data doesn't update until forced reconnection
- Notification system → notifications arrive in delayed batches

| WAF | SSE Support |
|-----|------------|
| **Ant2Cloud** | ✅ Full support — designed for real-time streaming from the ground up |
| **Huawei Cloud WAF** | ❌ Buffering + timeout issues *(Mar 2026)* |
| Cloudflare | ⚠️ Depends on plan |
| AWS WAF | ⚠️ Depends on config |

---

## Who Is It For?

- 🏢 **SME / Office** — need Private Cloud + VOIP + Security in one budget
- 🏠 **Home Office** — FTTX internet + Ant2Cloud = your own private Cloud
- 🏥 **Healthcare / Finance** — data must not leave the organization
- 🇹🇭 **Government** — 100% in-country Data Sovereignty

---

## Knowledge Base

- [[entities/Ant2-Proxy-Security-Manager|Ant2 WAF — Full Documentation]]
- [[analyses/2026-06-07-ant2-vs-world-waf-comparison|Ant2 vs World WAF Comparison]]

---

> 🇹🇭 **Ant2Cloud — Built in Thailand, for the World**
>
> [ant2cloud.com](https://ant2cloud.com)
