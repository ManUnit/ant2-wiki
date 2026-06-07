with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

# Use unique text within each comment (avoid box-drawing chars)
TRAFFIC_MARKER = 'Traffic trend chart'
REDIS_MARKER   = 'Redis cache panel'
DETAIL_MARKER  = 'Per-host detail panel'

# Find start of each section (the whole comment line)
def find_section_start(text, keyword):
    idx = text.index(keyword)
    # Walk back to start of line
    start = text.rfind('\n', 0, idx)
    return start + 1  # skip the \n

i_traffic = find_section_start(src, TRAFFIC_MARKER)
i_redis   = find_section_start(src, REDIS_MARKER)
i_detail  = find_section_start(src, DETAIL_MARKER)

if not (i_traffic < i_redis < i_detail):
    print(f'ORDER UNEXPECTED: traffic={i_traffic} redis={i_redis} detail={i_detail}')
    exit(1)

before        = src[:i_traffic]
traffic_block = src[i_traffic:i_redis]
redis_block   = src[i_redis:i_detail]
after         = src[i_detail:]

# Swap: Redis first, then Traffic Trend
src = before + redis_block + traffic_block + after

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('OK: Redis panel now above Traffic Trend panel')
