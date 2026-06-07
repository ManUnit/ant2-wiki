---
title: "Custom WAF Rules in Ant2"
type: concept
tags: [custom-rules, modsecurity, secrule, ant2, 9500101, 9500102, 9500103]
sources: [2026-05-07-ant2-v242-v243-session]
created: 2026-05-07
updated: 2026-05-07
---

# Custom WAF Rules in Ant2

[[Ant2-Proxy-Security-Manager]] supports two levels of custom [[ModSecurity]] rules beyond the [[OWASP-CRS]] base set.

## Rule Placement

### Global (all hosts) — `modsecurity-engine.conf`

`nginx-waf/modsecurity-engine.conf` is baked into the Docker image and included by every per-host config file. Rules placed here apply to every domain on every server.

- Respect per-host `SecRuleEngine` mode: in `DetectionOnly` hosts they log but do not block.
- Reloaded on container rebuild / `nginx -s reload`.

### Per-host — `/etc/modsecurity.d/custom/host_N.conf`

The API writes per-host config files to the `ant2proxy_modsec_custom` named Docker volume. The `# ── Custom Rules` section at the end is the insertion point for host-specific rules.

- Managed by the API; manually edited rules survive container restarts (named volume) but are overwritten if the API regenerates the file.

## Rule ID Namespace

| Range | Owner |
|-------|-------|
| 1–99999 | ModSecurity reserved |
| 900000–999999 | OWASP CRS |
| 9000001–9099999 | Ant2 per-host bypass rules |
| 9500001–9599999 | Ant2 global custom rules |

## Active Global Custom Rules (v2.4.2+)

These three rules were added to `modsecurity-engine.conf` to cover attack patterns not addressed by CRS standard rules. See [[crs-rule-scope]] for why these gaps exist.

### 9500101 — PHP File Extension in ARGS

```apache
SecRule ARGS "@rx \.ph(?:p[0-9]?|tml|ar)(\s*$|%00)" \
    "id:9500101,phase:2,deny,status:403,log,\
     msg:'Custom: PHP file extension in ARGS',\
     tag:'language-php',tag:'attack-php-upload'"
```

**Blocks**: `?file=shell.php`, `?upload=backdoor.phtml`, `?path=evil.php5`  
**Covers gap**: CRS 933110 only checks `FILES`/`X-Filename` headers, not query params.

### 9500102 — PHP Double Extension in ARGS

```apache
SecRule ARGS "@rx \.ph(?:p[0-9]?|tml|ar)\.[a-z]{2,4}($|%00)" \
    "id:9500102,phase:2,deny,status:403,log,\
     msg:'Custom: PHP double extension in ARGS',\
     tag:'language-php',tag:'attack-php-upload'"
```

**Blocks**: `?file=shell.php.jpg`, `?name=backdoor.php.png`  
**Covers gap**: CRS 933120 checks for PHP config directive names, not filename extension patterns.

### 9500103 — Open Redirect via ARGS

```apache
SecRule ARGS "@rx (?i)^https?://[^/]" \
    "id:9500103,phase:2,chain,deny,status:403,log,\
     msg:'Custom: Open redirect - external URL in ARGS',\
     tag:'attack-protocol'"
  SecRule MATCHED_VAR_NAME "@rx (?i)(?:redirect|^url$|return|next|goto|target|dest(?:ination)?|forward)" ""
```

**Blocks**: `?redirect=https://evil.com`, `?next=http://attacker.io`, `?goto=https://phishing.site`  
**Covers gap**: CRS 921110 is HTTP Request Smuggling detection, not open redirect.

> [!warning] OAuth / SSO False Positive
> Rule 9500103 will block OAuth callbacks and SSO return URLs that pass external redirect URLs as parameters. Add a bypass for known callback paths:
> ```apache
> SecRule REQUEST_URI "@beginsWith /auth/callback" "id:9000XXX,phase:1,pass,nolog,ctl:ruleEngine=Off"
> ```

## Writing New Custom Rules

Basic structure:
```apache
SecRule TARGET "@rx PATTERN" \
    "id:UNIQUE_ID,phase:2,deny,status:403,log,msg:'Description'"
```

Key fields:
- **TARGET**: collection to inspect (`ARGS`, `ARGS_NAMES`, `REQUEST_HEADERS`, `REQUEST_URI`, etc.)
- **@rx**: regex operator (most common); alternatives: `@beginsWith`, `@endsWith`, `@contains`, `@pm` (phrase match)
- **phase**: 1 = request headers, 2 = request body (use 2 for ARGS)
- **deny,status:403**: block action; use `pass,nolog` for allow/bypass rules

## See Also

- [[crs-rule-scope]]
- [[OWASP-CRS]]
- [[ModSecurity]]
- [[bypass-presets]]
- [[waf-validation-testing]]
- [[2026-05-07-ant2-v242-v243-session]]
