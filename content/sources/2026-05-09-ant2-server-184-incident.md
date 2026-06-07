---
title: "Server 184 Incident — Disk Full, Docker Network, NPM Password Reset"
type: source
tags: [server-184, nginx-proxy-manager, docker, disk-full, bcrypt, incident-response]
created: 2026-05-09
updated: 2026-05-09
---

# Server 184 Incident — Disk Full, Docker Network, NPM Password Reset

Incident response on 172.20.20.184 (SSH port 9229): disk 100% full caused by unbounded NPM log files, Docker network misconfiguration caused "Bad Gateway" after container restart, and NPM admin password reset via direct MySQL/bcrypt.

## Abstract

The root cause of all three problems was a single disk-full condition caused by NPM proxy logs growing to 13 GB. After clearing logs, MariaDB restarted successfully but NPM still showed "Bad Gateway" — a Docker network isolation issue where the two containers (nginx-proxy and docker_db_1) were on different compose networks and could not reach each other. Fixed by joining nginx-proxy to the docker_default network. The password reset revealed a critical bash `$` variable expansion trap: bcrypt hashes contain `$2b$13$...` which bash silently corrupts when passed via double-quoted `-e "..."` shell arguments.

## Key Takeaways

- **NPM log rotation is not enabled by default** — proxy logs grow unbounded. Add `logrotate` or periodic `truncate -s 0` to cron.
- **Docker network isolation after compose restart** — containers from different compose projects land on different networks. Hard-coded IPs (like `172.28.0.2`) only work if the target container is on a reachable network. `docker network connect` is the runtime fix; docker-compose `networks:` section is the permanent fix.
- **Bash `$` expansion silently corrupts bcrypt hashes** — `$2b$13$` inside double-quoted shell string becomes `b$` after bash expands `$2`, `$b`, `$13` as empty variables. Always pipe SQL containing bcrypt hashes via stdin (`exec_command + stdin.write()`), never via `-e "..."`.
- **Always verify DB writes with SELECT before reporting success** — bcrypt hash corruption is invisible from MySQL "Query OK" output. Read back and run `checkpw()`.
- **MariaDB in jc21/mariadb-aria image has no bash** — `docker exec container bash -c '...'` fails. Use `docker exec -i container mysql < file` or pipe via stdin.

## Notable Details

> "Stored: b3$.PQAYEwClDLE/... — the `$2b$13$` prefix missing, hash is invalid salt." — observed during failed password reset attempt, this source

> "docker exec -i docker_db_1 mysql ... + stdin.write(sql) — bypasses bash entirely, hash stored intact as $2b$13$..." — working fix, this source

## Gaps / Questions

- Permanent Docker network fix not yet applied (need to update `/opt/docker/nginx-proxy/docker-compose.yml` with explicit `networks:` section).
- NPM log rotation configuration not yet set up — disk will fill again.
- Old Docker images `jc21/nginx-proxy-manager:v1.1` (1.6 GB) and `tbp1` (1.38 GB) still present — `docker rmi` can be run now that disk has space.

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[request-flow-layers]]
