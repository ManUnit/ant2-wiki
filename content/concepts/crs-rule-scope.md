---
title: "CRS Rule Scope — What Each Rule Actually Checks"
type: concept
tags: [crs, modsecurity, rule-scope, testing, false-negative, 933110, 933120, 921110]
sources: [2026-05-07-ant2-v242-v243-session]
created: 2026-05-07
updated: 2026-05-07
---

# CRS Rule Scope — What Each Rule Actually Checks

A frequent source of false confidence in WAF testing: assuming a test payload triggers a specific CRS rule when the rule's *targets* (the collections ModSecurity inspects) do not include the payload location.

## The Three Misunderstood Rules

### Rule 933110 — PHP Script File Upload

**Claimed by**: tests sending `?file=shell.php` as a GET parameter  
**Actual target**: `FILES:filename`, `REQUEST_HEADERS:X-Filename`, `X_Filename`, `X.Filename`, `X-File-Name`

Rule 933110 is designed to catch PHP filenames arriving via **multipart file upload** (`enctype="multipart/form-data"`) or explicit filename headers. A GET query string parameter `?file=shell.php` is in the `ARGS` collection, which this rule never inspects at any paranoia level.

**Implication**: An app that receives PHP filenames in URL params is not covered by CRS 933110. Requires a custom rule.

### Rule 933120 — PHP Config Injection

**Claimed by**: tests sending `?file=shell.php.jpg` (double extension)  
**Actual target**: `ARGS` — but inspected for **PHP configuration directive names** (`allow_url_fopen`, `open_basedir`, `safe_mode`, `disable_functions`, etc.)

Rule 933120 catches attempts to inject PHP ini directives into application parameters (e.g. `?config=allow_url_fopen=1`). A filename like `shell.php.jpg` contains no directive names, so this rule never fires.

Double-extension bypass is a separate attack class requiring a custom rule.

### Rule 921110 — HTTP Request Smuggling

**Claimed by**: tests sending `?redirect=https://evil.com` (open redirect)  
**Actual target**: `ARGS`, `REQUEST_BODY` — inspected for **embedded HTTP method patterns** like `GET /path HTTP/1.0` or `POST / HTTP/1.1`

Rule 921110 detects HTTP Request Smuggling — where an attacker embeds a second HTTP request inside the body of the first. Open redirect (a user-supplied URL that the server follows) is an application-level vulnerability, not a protocol-level attack. CRS has no default open-redirect rules because they cannot be distinguished from legitimate URL parameters without application context.

## Rule Target Collections Reference

| Collection | Contains |
|-----------|----------|
| `ARGS` | All GET + POST parameters (key=value) |
| `ARGS_NAMES` | Parameter names only |
| `FILES` | Multipart upload filename metadata |
| `REQUEST_HEADERS` | All HTTP request headers |
| `REQUEST_BODY` | Raw request body (non-multipart) |
| `REQUEST_URI` | Full URI including query string |
| `REQUEST_FILENAME` | Path component only |
| `MATCHED_VAR` | Value of the last matched variable |
| `MATCHED_VAR_NAME` | Name of the last matched variable |

## Custom Rules for Uncovered Attack Patterns

When CRS doesn't cover a pattern in the target collection you need, add a custom rule in `modsecurity-engine.conf` (global) or the per-host custom section:

```apache
# PHP extension in GET/POST ARGS (covers 933110 gap)
SecRule ARGS "@rx \.ph(?:p[0-9]?|tml|ar)(\s*$|%00)" \
    "id:9500101,phase:2,deny,status:403,log,msg:'Custom: PHP file extension in ARGS'"

# PHP double extension in ARGS (covers 933120 gap)
SecRule ARGS "@rx \.ph(?:p[0-9]?|tml|ar)\.[a-z]{2,4}($|%00)" \
    "id:9500102,phase:2,deny,status:403,log,msg:'Custom: PHP double extension in ARGS'"

# Open redirect in redirect/url/return params (covers 921110 gap)
SecRule ARGS "@rx (?i)^https?://[^/]" \
    "id:9500103,phase:2,chain,deny,status:403,log,msg:'Custom: Open redirect in ARGS'"
  SecRule MATCHED_VAR_NAME "@rx (?i)(?:redirect|^url$|return|next|goto|target|dest(?:ination)?|forward)" ""
```

> [!warning] False Positive Risk
> Rule 9500103 (open redirect) will block any application that legitimately accepts external URLs in `redirect=` style parameters — for example, OAuth callback parameters. Add a bypass rule for known safe paths.

## How to Verify Rule Targets

Check the actual rule in the CRS source:
```
/opt/owasp-crs/rules/REQUEST-933-APPLICATION-ATTACK-PHP.conf
/opt/owasp-crs/rules/REQUEST-921-PROTOCOL-ATTACK.conf
```

Look at the first argument after `SecRule` — that is the collection(s) the rule inspects. If your payload is not in that collection, the rule cannot fire regardless of paranoia level.

## See Also

- [[custom-waf-rules]]
- [[waf-validation-testing]]
- [[OWASP-CRS]]
- [[paranoia-levels]]
- [[2026-05-07-ant2-v242-v243-session]]
