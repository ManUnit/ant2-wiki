---
title: "Ant2 Proxy Security Manager"
type: entity
tags: [ant2, geoip, web-service]
sources: []
created: 2026-05-05
updated: 2026-06-07
---

# Ant2 Proxy Security Manager

**ANT2 Proxy Server** — a full-featured WAF and reverse-proxy system with GUI management. Supports GeoIP country blocking, IP Jail, and per-domain rate limiting. Developed by a Thai team 🇹🇭 and available as a **commercial hardware appliance**.

## Commercial Product — Ant2Cloud Box Appliance

> **"Bring the Cloud Home"** — Ant2Cloud is an innovation that doesn't require SaaS or major global cloud providers. With just FTTX home or office internet, you can build your own Private Cloud.

| Attribute | Detail |
|-----------|--------|
| Product name | **Ant2Cloud** |
| Website | **https://ant2cloud.com** |
| Form factor | Hardware box appliance — router style, slim & lightweight |
| Price | **฿250,000 THB** |
| Origin | Thailand 🇹🇭 — developed and manufactured in Thailand |

### Hardware Specifications

| Component | Spec |
|-----------|------|
| CPU | 12-core / 24 vCPU |
| RAM | 64 GB |
| Storage | 2 TB HDD |
| VM Capacity | Supports up to 20 VMs |
| Form Factor | Router style — slim, easy to install |

### Built-in Services (All-in-One)

| Feature | Detail |
|---------|--------|
| **Ant2 WAF** | ANT2 Proxy Server — GeoIP country filter, IP Jail, rate limiting |
| **Smart Router** | Built-in smart router |
| **ONU / ONT** | Built-in — plug GPON fiber directly, no separate ONU needed |
| **IP Phone Server** | Built-in VOIP server — supports IP Phones across the office |
| **VLAN Support** | Split VLAN from ISP (GPON) and connect directly to VOIP server |
| **DDNS** | Dynamic DNS built-in — detects IP change → updates DNS within **10–15 seconds** |
| **Custom Domain** | Use your own domain without buying a static IP from ISP |
| **Private Cloud** | Run 20 VMs on FTTX home/office internet |

### DDNS — Dynamic DNS (No Static IP Required)

Home ISPs typically assign dynamic IPs (can change at any time) — Ant2Cloud solves this with built-in DDNS:

```
IP changes (ISP assigns new IP)
  ↓ Ant2Cloud detects it immediately
  ↓ Updates DNS record automatically
  ↓ Within 10–15 seconds
Your domain is pointing correctly again ✅
```

| | Without DDNS | Ant2Cloud DDNS |
|--|-----------|----------------|
| IP changes | website goes down | **Auto-update in 10–15s** |
| Need Static IP | ✅ must purchase (~฿500/mo) | ❌ not needed |
| Use own domain | ❌ IP can change | ✅ works all the time |
| Downtime when IP changes | minutes to hours | **< 15 seconds** |

### Real IP Detection — Always Identifies True IP Through Any Number of Layers

**Ant2WAF always identifies the true IP of users or attackers, regardless of how many layers they go through** — CDN, reverse proxy, load balancer, or firewall — however many are in between.

```
User ──→ CDN / Proxy / Load Balancer ──→ Ant2Cloud Box ──→ Website
                                               │
                                  Analyzes and identifies true source IP
                                  automatically — always
```

| Benefit | Detail |
|---------|--------|
| **Hide Origin IP** | Ant2Cloud's IP is not exposed to the public — CDN acts as shield |
| **Identify True Source IP** | Detects correctly even through multiple proxy layers |
| **Accurate GeoIP** | Checks country from real user IP, not CDN node IP |
| **Accurate IP Jail** | Jails real attackers — doesn't accidentally jail CDN |
| **Correct Block** | Block/unblock targets actual attacker, not intermediary |
| **Automatic** | No extra configuration — supports any CDN and proxy |

### GeoIP Country Filter — Enable/Block Countries Instantly

Ant2Cloud lets your website **serve only the countries you want**, with extremely fast GeoIP:

| Capability | Detail |
|------------|--------|
| **Allow List Mode** | Allow only selected countries → auto-block all others |
| **Block List Mode** | Block selected countries → allow all others |
| **Per-host config** | Each domain has its own GeoIP rule |
| **Global config** | Block/allow across all domains at once |

**Speed and accuracy:**

- GeoIP lookup is extremely fast — **latency < 1ms per request**, no performance impact
- Second-layer cache system — repeated requests respond even faster
- Supports **Cloudflare CDN** — correctly separates user source IP from CDN node

> Example: Thai online store → Allow TH only → cuts 90%+ of foreign attacks before they reach the WAF

### Concept: Private Cloud at Home and Office

```
GPON Fiber (ISP)
  └── Ant2Cloud Box (ONU/ONT built-in)
        ├── Smart Router
        ├── VLAN → IP Phone / VOIP Server
        ├── WAF (ANT2 Proxy Server)
        ├── 20x Virtual Machines
        └── Private Cloud Services
```

No dependency on:
- ❌ AWS / Azure / GCP (SaaS global cloud)
- ❌ Cloudflare (traffic stays off third-party)
- ❌ Separate ONU/ONT
- ❌ Separate VOIP server
- ❌ Separate Router

Everything in one box at **฿250,000 THB**

## Key Capabilities

- Manage multiple domain proxy hosts via GUI — configure HTTPS, HTTP/2, WebSocket, HSTS instantly
- WAF with real-time attack analytics dashboard (XSS, SQLi, RCE, LFI, RFI)
- GeoIP country filter — Allow List / Block List at country level, per domain or global
- Auto IP Jail — captures attacker within ~20 seconds, regardless of attack speed
- Rate Limiting per domain — protection against brute force and flood attacks
- Automatic SSL (Let's Encrypt) + manual certificate upload + expiry alerts
- Custom error pages for every HTTP status code
- Dashboard Monitor for real-time traffic, attack trends, and system status
- **Swarm Attack Protection** — defends against distributed attacks from many simultaneous IPs
- **Attack Domain Identification** — instantly identifies which domain is under active attack

## Swarm Attack Protection — Defense Against Coordinated Attacks

**Swarm Attack** is a distributed attack from many IPs simultaneously — each IP sends requests slowly enough to avoid rate limits, but collectively overwhelms the system. Standard WAFs that only look at per-IP rate will miss this entirely.

```
IP-A  → 5 requests/min  ← below rate limit
IP-B  → 5 requests/min  ← below rate limit
IP-C  → 5 requests/min  ← below rate limit
...
IP-500 → 5 requests/min
─────────────────────────
Total: 2,500 requests/min → server down
```

**Ant2Cloud defends against Swarm Attacks with 3 simultaneous mechanisms:**

| Mechanism | How It Works |
|-----------|--------------|
| **GeoIP Block** | Instantly cut entire subnet/country that is the swarm source |
| **WAF Event-based Jail** | Each IP in the swarm sending dangerous payload → auto-jailed individually |
| **Global Rate Limiting** | Limit rate at global domain level — prevents flood even when individual IPs look light |

> Unlike ordinary WAFs — Ant2 catches each individual attacker in the swarm by **behavior** (WAF violations), not just rate

## Attack Domain Identification — Know Instantly Which Domain Is Under Attack

When under attack, the most critical question is: **which domain is being targeted?**

Ant2Cloud identifies the target domain in real-time instantly:

| Data | Detail |
|------|--------|
| **Attack per domain** | Dashboard shows WAF violation count separately per domain |
| **Jailed IP → Domain** | Every jailed IP is recorded with which domain it was attacking |
| **Attack type per domain** | Breaks down attack type (SQLi, XSS, RCE, etc.) per domain |
| **Timeline** | See attack pattern — which domain was hit first and when |

**Response benefits:**
- Know which domain to isolate or lock down first
- See if the swarm is rotating targets between domains
- Apply GeoIP block or custom rules with surgical precision

## See Also

- [[analyses/2026-06-07-ant2-vs-world-waf-comparison|Ant2 vs World WAF Comparison]]
