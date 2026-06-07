# Ant2 Server 184 — Incident Response: Disk Full + NPM Recovery

Date: 2026-05-09  
Host: 172.20.20.184  
SSH port: 9229  
User: anan  
Service: NGINX Proxy Manager v2.10.3 (jc21/nginx-proxy-manager:latest)

---

## Incident: Disk 100% Full

### Symptom
- MariaDB (`docker_db_1`) restarting in loop: `ERROR: Can't start server: can't create PID file: No space left on device`
- NPM container (`nginx-proxy`) could not execute any `docker exec` commands: `OCI runtime exec failed: no space left on device`
- NPM login page returned "Bad Gateway" (backend never started)

### Root Cause
`/opt/docker/nginx-proxy/data/logs/` had grown to **13 GB** of nginx proxy access/error logs with no rotation configured.

Notable files: `proxy_host-14.log` (886 MB), `proxy_host-15.log` (529 MB), `fallback_error.log` (565 MB)

### Fix
Truncated all `.log` files in-place (safe for running containers — no need to stop):
```bash
find /opt/docker/nginx-proxy/data/logs -type f -name '*.log' -exec truncate -s 0 {} \;
find /opt/docker/nginx-proxy/data/logs -type f \( -name '*.gz' -o -name '*.log.*' \) -delete
```
Result: 29G → 16G used (12 GB freed, 59% utilization).

Also cleaned journal logs (freed ~772 MB from `/var/log/journal`, but these were mostly already freed from `/run` tmpfs — not on main disk).

Also found: two old unused NPM Docker images (`jc21/nginx-proxy-manager:v1.1` 1.6 GB, `jc21/nginx-proxy-manager:tbp1` 1.38 GB) — `docker rmi` failed because no space to write temp metadata. These can be removed after freeing space first.

---

## Incident: Docker Network Mismatch — "Bad Gateway"

### Symptom
After restarting containers, NPM logs showed continuous:  
`connect ETIMEDOUT` attempting to reach `DB_MYSQL_HOST: 172.28.0.2`

### Root Cause
`nginx-proxy` and `docker_db_1` are managed by **two separate docker-compose projects**:
- `nginx-proxy` → `nginx-proxy_default` network (172.30.0.2)
- `docker_db_1` → `docker_default` network (172.28.0.2)

The NPM docker-compose.yml hard-codes `DB_MYSQL_HOST: "172.28.0.2"` which is the DB's IP on `docker_default`. But `nginx-proxy` has no route to that network.

After a restart, the two containers came up on their separate networks and could not reach each other.

### Fix (temporary — survives until next restart)
```bash
docker network connect docker_default nginx-proxy
```
After this, `nginx-proxy` has IPs on both networks (172.28.0.3 on docker_default, 172.30.0.2 on nginx-proxy_default) and can reach the DB at 172.28.0.2.

### Fix (permanent — not yet applied)
Update `/opt/docker/nginx-proxy/docker-compose.yml` to explicitly join `docker_default` network, or use a container name/service alias instead of a hard-coded IP.

---

## NPM Password Reset Procedure

### DB credentials
- User: `npm` / Password: `npm`
- Connect: `docker exec -i docker_db_1 mysql -u root -pnpm -h 127.0.0.1 npm`
- Note: must use `-h 127.0.0.1` (TCP), not default socket — NPM user is only granted for TCP connections

### Schema
```
user table:  id, email, name, nickname, roles
auth table:  id, user_id, type ('password'), secret (bcrypt hash), is_deleted
```
auth.user_id is a FK to user.id. No `identity` column (common mistake from older NPM docs).

### Users
| user_id | email | notes |
|---------|-------|-------|
| 1 | admin@thailandpages.com | main admin |
| 2 | hs1gab@gmail.com | Anan (had no auth row — needed INSERT) |
| 3 | superuser@thailandpages.com | |
| 4 | fiw@tbpcloud.com | |
| 5 | sciantman@gmail.com | |

### Critical: Bash `$` expansion bug
bcrypt hashes start with `$2b$13$...`. When embedded in a MySQL `-e "UPDATE auth SET secret='$2b$13$...'"` command, bash inside double quotes expands `$2` (positional param) and `$b`, `$13` (variables) to empty strings. The stored hash becomes `b$...` — invalid.

**Fix: pipe SQL via stdin, never use `-e "..."` for values containing `$`:**
```python
stdin, stdout, stderr = ssh.exec_command('docker exec -i docker_db_1 mysql -u root -pnpm -h 127.0.0.1 npm')
stdin.write(f"UPDATE auth SET secret='{hash}'...\n")
stdin.channel.shutdown_write()
```

### Hash generation
Generate bcrypt hash locally with Python (cost 13, `$2b$` format — compatible with NPM's Node.js `bcrypt` module):
```python
import bcrypt
new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(13)).decode('utf-8')
```
Always verify with `bcrypt.checkpw()` before updating DB.

### Verify after update
Always SELECT back the stored hash and confirm it starts with `$2b$13$` — partial expansion produces `b$` prefix which is an invalid salt.
