import urllib.request, json, time, sys

time.sleep(5)
with urllib.request.urlopen('http://localhost:4000/api/jail/counters') as r:
    d = json.loads(r.read())

filled = [x for x in d if x.get('hosts')]
print(f'Total: {len(d)}, with domain: {len(filled)}')
for x in filled[:8]:
    print(f"  {x['ip']} cnt={x['count']} hosts={x['hosts']}")
nohosts = [x for x in d if not x.get('hosts')]
print(f'No domain: {len(nohosts)} IPs (old events beyond log retention)')
