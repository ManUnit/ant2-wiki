---
title: "Ant2 Docker Deploy Pattern"
type: concept
tags: [docker, deployment, ant2, dockerfile, nginx]
sources: [2026-05-13-compact-row-table-theme]
created: 2026-05-13
updated: 2026-05-13
---

# Ant2 Docker Deploy Pattern

Pattern การ deploy web frontend ของ [[Ant2-Proxy-Security-Manager]] ที่ต้องระวัง เพราะ web container ใช้ Docker image build (bake) แทน volume mount ([[2026-05-13-compact-row-table-theme]])

## Dockerfile ของ web container

```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html   # dist ถูก bake เข้า image ตอน build
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

เนื่องจาก `COPY dist` อยู่ใน Dockerfile การแก้ไข source แล้ว build Vite บน host
**ไม่มีผล** ต่อ container ที่รันอยู่ — ต้อง rebuild Docker image ด้วย

## Correct Workflow

```bash
# 1. Build Vite dist บน host (สร้าง /opt/ant2-proxy/web/dist/)
sudo docker run --rm \
  -v /opt/ant2-proxy/web:/app \
  -w /app \
  node:20-alpine \
  sh -c 'npm install --silent 2>/dev/null; npm run build'

# 2. Rebuild Docker image (bakes dist ใหม่เข้า image)
cd /opt/ant2-proxy && sudo docker compose build web

# 3. Recreate container ด้วย image ใหม่
sudo docker compose up -d web
```

## Anti-pattern (ใช้ไม่ได้)

```bash
# ✗ restart ใช้ image เดิม — dist ข้างในยังเก่า
sudo docker compose restart web

# ✗ up -d โดยไม่ build — ถ้า image เดิมยังอยู่ จะใช้ image เดิม
sudo docker compose up -d web
```

## Contrast: API container

API container mount source เป็น volume ดังนั้นแค่ restart พอ:

```bash
sudo docker compose restart api
```

## One-liner Deploy

```bash
cd /opt/ant2-proxy && \
  sudo docker run --rm -v $(pwd)/web:/app -w /app node:20-alpine \
    sh -c 'npm install --silent 2>/dev/null; npm run build 2>&1 | tail -3' && \
  sudo docker compose build web 2>&1 | tail -3 && \
  sudo docker compose up -d web 2>&1 | tail -2
```

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[compact-row-table-theme]]
- [[inotify-write-order-pattern]]
