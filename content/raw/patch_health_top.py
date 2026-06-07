with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

def find_section_start(text, keyword):
    idx = text.index(keyword)
    start = text.rfind('\n', 0, idx)
    return start + 1

i_nginx   = find_section_start(src, 'Nginx stub_status cards')
i_redis   = find_section_start(src, 'Redis cache panel')
i_traffic = find_section_start(src, 'Traffic trend chart')
i_health  = find_section_start(src, 'System + Connection chart')
i_detail  = find_section_start(src, 'Per-host detail panel')

if not (i_nginx < i_redis < i_traffic < i_health < i_detail):
    print(f'ORDER UNEXPECTED: nginx={i_nginx} redis={i_redis} traffic={i_traffic} health={i_health} detail={i_detail}')
    exit(1)

before         = src[:i_nginx]
nginx_block    = src[i_nginx:i_redis]
redis_block    = src[i_redis:i_traffic]
traffic_block  = src[i_traffic:i_health]
health_block   = src[i_health:i_detail]
after          = src[i_detail:]

# New order: Health → Nginx → Redis → Traffic → Per-host
src = before + health_block + nginx_block + redis_block + traffic_block + after

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('OK: System Health moved to TOP')
