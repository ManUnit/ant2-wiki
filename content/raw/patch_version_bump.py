import json, re

# API
with open('/opt/ant2-proxy/api/package.json') as f: d = json.load(f)
d['version'] = '2.4.22'
with open('/opt/ant2-proxy/api/package.json', 'w') as f: json.dump(d, f, indent=2)

# Web
with open('/opt/ant2-proxy/web/package.json') as f: d = json.load(f)
d['version'] = '2.3.7'
with open('/opt/ant2-proxy/web/package.json', 'w') as f: json.dump(d, f, indent=2)

# VERSION file
t = open('/opt/ant2-proxy/VERSION').read()
t = re.sub(r'version=.*', 'version=2.4.22', t)
t = re.sub(r'built=.*', 'built=2026-05-13T00:00:00Z', t)
open('/opt/ant2-proxy/VERSION', 'w').write(t)

print('OK: api=2.4.22  web=2.3.7')
print(open('/opt/ant2-proxy/VERSION').read())
