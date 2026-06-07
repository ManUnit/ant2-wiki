---
title: "Bypass Presets"
type: concept
tags: [crs, bypass, oauth, webhooks, ant2, false-positives]
sources: [2026-05-05-ant2-progress]
created: 2026-05-05
updated: 2026-05-05
---

# Bypass Presets

Bypass presets disable WAF rule evaluation entirely for specific URI paths using `ctl:ruleEngine=Off`. They are used for paths where legitimate traffic structurally resembles attacks and rule exclusions alone are insufficient.

## How They Differ from Platform Presets

| | [[platform-presets]] | Bypass Presets |
|--|---------------------|----------------|
| Mechanism | `SecRuleRemoveById` — disables specific rules globally | `ctl:ruleEngine=Off` — disables all WAF for a URI path |
| Scope | Per-rule, site-wide | Per-path, all rules |
| Use case | Framework FPs that fire on normal traffic | OAuth callbacks, webhook deliveries |
| Risk | Low — specific rules only | Higher — no WAF coverage for that path |

## All 10 Presets

| Key | Use Case | Why WAF fires |
|-----|---------|---------------|
| `google_oauth` | Google Login / OAuth2 callback | `scope=googleapis.com` in URL looks like injection |
| `nextauth` | NextAuth.js / Auth.js (`/api/auth/*`) | Covers all NextAuth providers |
| `facebook_oauth` | Facebook OAuth2 callback | Long `state`/`code` params resemble SQLi |
| `github_oauth` | GitHub OAuth2 callback | Auth code values trigger rule 932150 (RCE) |
| `microsoft_oauth` | Microsoft / Azure AD / OIDC | JWT `id_token` in POST triggers 941100/942100/920230 |
| `saml_sso` | SAML SSO Assertion POST | base64 `SAMLResponse` triggers 920230/941100 |
| `line_oauth` | LINE Login OAuth | Common in Thai/Asian web apps |
| `stripe_webhook` | Stripe Webhook delivery | Payment fields trigger SQLi/XSS rules |
| `github_webhook` | GitHub Webhook delivery | Code diff in payload triggers injection rules |
| `paypal_webhook` | PayPal IPN / REST Webhook | Payment notifications trigger injection rules |

## LINE OAuth Note

`line_oauth` is specifically listed for Thai/Asian web apps — relevant for any Thai-market application behind [[Ant2-Proxy-Security-Manager]].

## Custom Bypass Paths

In addition to presets, Ant2 provides a free-text textarea for custom bypass paths (one URI prefix per line). Each generates a `SecRule REQUEST_URI ... ctl:ruleEngine=Off` before CRS rules.

## Code Location

Defined in `api/src/wafPresets.js`. Applied by `nginxConfig.js` in [[Ant2-Proxy-Security-Manager]].

## See Also

- [[platform-presets]]
- [[false-positive-false-negative-tradeoff]]
- [[OWASP-CRS]]
- [[Ant2-Proxy-Security-Manager]]
