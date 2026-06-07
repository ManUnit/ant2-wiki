---
title: "inotify Write Order Pattern"
type: concept
tags: [nginx, inotify, race-condition, architecture, ant2, bug-pattern]
sources: [2026-05-05-ant2-progress, 2026-05-05-ant2-changelog]
created: 2026-05-05
updated: 2026-05-05
---

# inotify Write Order Pattern

A critical architectural rule for any system that uses `inotifywait` to auto-reload NGINX when config files change. Discovered and fixed in [[Ant2-Proxy-Security-Manager]] v2.2.

## The Bug

When the API writes nginx host config (`host_N.conf`) before the WAF config (`host_N_modsec.conf`), the inotify watcher triggers `nginx -t && nginx -s reload` on the first write. At that moment, `host_N.conf` references a WAF config file that doesn't exist yet — nginx test fails and the reload is skipped.

```
Timeline (broken):
  1. writeFileSync(host_1.conf)        ← nginx conf written
  2. inotify triggers nginx -t         ← fires immediately
  3. nginx -t FAILS                    ← modsec conf not yet written
  4. writeFileSync(modsec_host_1.conf) ← too late
```

## The Fix

Always write WAF/ModSecurity config **before** nginx config.

```
Timeline (correct):
  1. writeFileSync(modsec_host_1.conf) ← WAF conf written first
  2. writeFileSync(host_1.conf)        ← nginx conf triggers inotify
  3. inotify triggers nginx -t         ← both files exist
  4. nginx -t PASSES → nginx -s reload ← success
```

## Code Location

`api/src/services/nginxConfig.js` in [[Ant2-Proxy-Security-Manager]]:

```js
// CORRECT order:
if (waf && wafMode !== 'off') {
  fs.writeFileSync(wafConfPath(host.id), wafConf);   // WAF first
}
fs.writeFileSync(hostConfPath(host.id), nginxConf);  // nginx after
```

## Generalization

This pattern applies to **any dual-file config system** where:
- File A references File B
- A file-watcher triggers validation/reload on any write
- Both files are written by the same process

Rule: always write the dependency (File B) before the dependent (File A).

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[docker-compose-architecture]]
