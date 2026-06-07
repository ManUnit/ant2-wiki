---
title: "Server Header Disclosure"
type: concept
tags: [nginx, security-headers, information-disclosure, headers-more, server-tokens]
sources: [2026-05-06-ant2-v2361-release-notes]
created: 2026-05-06
updated: 2026-05-06
---

# Server Header Disclosure

The HTTP `Server` response header reveals the web server software and version (e.g., `Server: nginx/1.28.2`). This is an information disclosure risk — attackers can target known CVEs for that exact version.

## Two-Level Suppression in NGINX

NGINX offers two settings for hiding server identity:

| Directive | Effect |
|-----------|--------|
| `server_tokens off` | Removes version from `Server` header → `Server: nginx` |
| `more_clear_headers 'Server'` | Removes the header entirely — no `Server:` in response |

`server_tokens off` alone is insufficient — it still reveals the software name. `more_clear_headers` (from `ngx_http_headers_more_filter_module`) removes the header entirely.

## ngx_http_headers_more_filter_module

This dynamic module is not included in the standard NGINX package. It must be compiled from source against the exact NGINX version.

### Build in Dockerfile

```dockerfile
RUN NGINX_VERSION=$(nginx -v 2>&1 | grep -oP 'nginx/\K[0-9.]+') && \
    cd /tmp && \
    wget -q http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar -xzf nginx-${NGINX_VERSION}.tar.gz && \
    git clone --depth 1 https://github.com/openresty/headers-more-nginx-module.git && \
    cd nginx-${NGINX_VERSION} && \
    ./configure --with-compat \
        --add-dynamic-module=../headers-more-nginx-module && \
    make modules && \
    cp objs/ngx_http_headers_more_filter_module.so /etc/nginx/modules/
```

Can be combined with other dynamic modules (e.g., `ngx_http_geoip2_module`) in a single `./configure` pass using multiple `--add-dynamic-module=` flags.

### nginx.conf

```nginx
load_module modules/ngx_http_headers_more_filter_module.so;

http {
    server_tokens   off;
    more_clear_headers 'Server';
    ...
}
```

## Implementation in Ant2 (v2.3.6)

- Module built in `nginx-waf/Dockerfile` alongside geoip2.
- `more_clear_headers 'Server'` placed in the `http {}` block of `nginx.conf`, after `server_tokens off`.
- Verified: `curl -sI http://localhost:80` returns no `Server:` header.
- The `more_clear_headers` directive applies globally to all virtual hosts.

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[rate-limiting-nginx]]
- [[2026-05-06-ant2-v2361-release-notes]]
