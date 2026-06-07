with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

def find_section_start(text, keyword):
    idx = text.index(keyword)
    start = text.rfind('\n', 0, idx)
    return start + 1

i_health  = find_section_start(src, 'System + Connection chart')
i_redis   = find_section_start(src, 'Redis cache panel')
i_traffic = find_section_start(src, 'Traffic trend chart')
i_detail  = find_section_start(src, 'Per-host detail panel')

if not (i_health < i_redis < i_traffic < i_detail):
    print(f'ORDER UNEXPECTED: health={i_health} redis={i_redis} traffic={i_traffic} detail={i_detail}')
    exit(1)

before         = src[:i_health]
health_block   = src[i_health:i_redis]
redis_block    = src[i_redis:i_traffic]
traffic_block  = src[i_traffic:i_detail]
after          = src[i_detail:]

# New order: Redis → Traffic → Health → Per-host
src = before + redis_block + traffic_block + health_block + after

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('OK: System Health moved to bottom (after Traffic Trend)')
