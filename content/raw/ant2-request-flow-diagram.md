# Ant2 Proxy Security Manager — Full Request Flow Diagram

Source type: internal architecture documentation  
System: NGINX + OWASP CRS + ModSecurity + Node.js API + Redis + SQLite  
Version documented: v2.4.15  
Date: 2026-05-09

---

## Overview

Every inbound HTTP/HTTPS request passes through five enforcement layers before reaching a backend.
Blocked requests feed a detection pipeline that automatically jails repeat attackers.

---

## Layer 1 — TCP / Network

```
Client ──TCP SYN──► NGINX (port 80 / 443)
                         │
                    [TLS termination]
```

Rate limiting is applied at the connection level via `limit_req_zone` before any application logic runs.

---

## Full Request Flow

```mermaid
flowchart TD
    CLIENT([" Client / Attacker "])

    CLIENT -->|TCP + TLS| RL

    subgraph NGINX_PROC["NGINX — Request Processing (per request)"]
        direction TB

        RL["🚦 Rate Limit\nlimit_req_zone\nper IP / per second"]
        GEO["🌍 Geo Block Check\n\$ip_blocked == 1 ?"]
        MODSEC["🛡️ ModSecurity\nOWASP CRS Rules"]
        PROXY["→ proxy_pass\nUpstream Backend"]

        RL -->|Exceeded| R429["HTTP 429\nToo Many Requests"]
        RL -->|OK| GEO
        GEO -->|IP is jailed| R423["HTTP 423\nip-blocked.html\n⚡ No ModSecurity hit"]
        GEO -->|Not jailed| MODSEC
    end

    subgraph CRS["ModSecurity + OWASP CRS — Anomaly Scoring"]
        direction TB
        RULES["Rule Engine\nPL1–PL4"]
        SCORE["Anomaly Score Accumulator\nWARNING  → +3 pts\nCRITICAL → +5 pts"]
        THRESH{"Score ≥ threshold?\n(default: 5, tuned: 3)"}

        RULES --> SCORE --> THRESH
    end

    MODSEC --> RULES
    THRESH -->|YES — Block| R403["HTTP 403\nWAF Blocked\n(rule_ids logged)"]
    THRESH -->|NO — Pass| PROXY
    PROXY --> BACKEND([" Backend Service "])

    %% Log outputs
    R403 -->|audit entry| AUDITLOG[/"📄 ModSecurity\nAudit Log\n/data/logs/modsec_audit.log"/]
    R423 -->|access entry| ACCESSLOG[/"📄 NGINX\nAccess Log\n/data/logs/access.log\nstatus=423"/]
    R429 -->|access entry| ACCESSLOG
    PROXY -->|access entry| ACCESSLOG

    subgraph API["API Service — Auto-Jail Pipeline (background)"]
        direction TB

        INGEST["maybeIngestWafLogs()\nRate-limited: max 1× per 10s\nParses audit log → waf_events"]
        WAF_DB[("waf_events\nSQLite\nclient_ip · status · rule_ids\ncat_xss · cat_sqli · cat_rce …")]
        POLL["pollAttacks()\nScheduled every 10s\nCounts 403 + rule_ids per IP"]
        REDIS[("Redis\njail:cnt:{ip}\n7-day TTL counter")]
        THRESHOLD{"cnt ≥ jail_threshold?\n(default: 10 attacks)"}
        JAIL_DB[("ip_jail\nSQLite\nip · attack_count · expires_at\npost_jail_count · country")]
        POSTJAIL["countPostJailHits()\nReads access.log new bytes\nCounts status=423 per jailed IP\n(Redis watermark per file)"]
        RELEASE["releaseExpired()\nEvery 30s\nDELETE where expires_at ≤ now"]

        INGEST --> WAF_DB --> POLL --> REDIS --> THRESHOLD
        THRESHOLD -->|YES — Jail| JAIL_DB
        THRESHOLD -->|NO — Accumulate| REDIS
        POSTJAIL --> JAIL_DB
        RELEASE -->|Expired| JAIL_DB
    end

    AUDITLOG -->|"new bytes (watermark)"| INGEST
    ACCESSLOG -->|"new bytes (Redis pos watermark)"| POSTJAIL

    subgraph RELOAD["Config Rebuild + Nginx Reload"]
        WRITECONF["writeAllHostConfigs()\nBuilds ngx geo block:\ngeo \$ip_blocked {\n  default 0;\n  1.2.3.4 1;\n}"]
        NGINXRELOAD["nginx -s reload\n(graceful — no dropped conns)"]
        WRITECONF --> NGINXRELOAD
    end

    JAIL_DB -->|"new jail / release"| WRITECONF
    NGINXRELOAD -.->|"updated \$ip_blocked map"| GEO
```

---

## Attack Count Display (UI)

The IP Jail page shows a three-tier counter per jailed IP:

```
attack_count total           ← grows continuously (WAF events after jail still counted)
  +{N} WAF after jail        ← attack_count − jailed_at_count  (parsed from reason field)
  +{N} HTTP 423 blocked      ← post_jail_count  (from access log, no WAF involved)
```

`reason` field stores: `"Auto-jailed: 11 attacks"` — regex extracts the at-jail snapshot.

---

## Timing / Latency Budget

| Event | Interval | Notes |
|-------|----------|-------|
| `maybeIngestWafLogs` rate limit | 10 s | Min gap between audit log ingestions |
| `pollAttacks` | 10 s | Scans waf_events for new 403s |
| `releaseExpired` | 30 s | Checks expired jails |
| nginx reload after jail | ~0 s | Triggered immediately after INSERT |
| **Worst-case time to jail** | **~20 s** | ingest delay + poll delay |

An attacker firing continuously can land up to ~20 s of unblocked requests before the geo block activates.

---

## HTTP Status Code Reference

| Code | Meaning | Who Returns It | Counted in jail? |
|------|---------|----------------|-----------------|
| 200 | Pass | Backend | No |
| 301/302 | Redirect | NGINX | No |
| 403 | WAF Block | ModSecurity/CRS | **Yes** — feeds jail counter |
| 423 | Geo Block (Jailed) | NGINX geo module | No (already jailed) |
| 429 | Rate Limited | NGINX limit_req | No |

---

## Key Redis Keys

| Key | Purpose | TTL |
|-----|---------|-----|
| `jail:cnt:{ip}` | Pre-jail attack counter | 7 days |
| `jail:last_event_id` | waf_events watermark | none |
| `jail:access_pos:{filename}` | access.log byte offset | none |

---

## OWASP CRS Rule Categories

| Category | DB Column | Examples |
|----------|-----------|---------|
| XSS | `cat_xss` | `<script>`, event handlers |
| SQLi | `cat_sqli` | `' OR 1=1`, `--` comment |
| RCE | `cat_rce` | shell metacharacters |
| LFI | `cat_lfi` | `../../../etc/passwd` |
| RFI | `cat_rfi` | `http://evil.com/shell.php` |
| Protocol | `cat_proto` | malformed headers, methods |
| Other | `cat_other` | scanner signatures, bad UA |

---

## Paranoia Level vs Anomaly Threshold

| PL | Rule aggressiveness | Default threshold | Block on single WARNING? |
|----|---------------------|-------------------|--------------------------|
| PL1 | Low FP | 5 | No (WARNING=3 < 5) |
| PL1 (tuned) | Low FP | **3** | **Yes** (WARNING=3 ≥ 3) |
| PL2 | Medium | 5 | No |

SQLi comment bypass (`--`, rule 942110) is a WARNING-level rule.  
At threshold=5 it never blocks alone. At threshold=3 it does.
