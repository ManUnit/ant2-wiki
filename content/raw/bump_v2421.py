import subprocess

TODAY = '2026-05-13T00:00:00Z'
NEW_VER = '2.4.21'

files = [
    '/opt/ant2-proxy/VERSION',
    '/opt/ant2-proxy/api/VERSION',
]
for f in files:
    with open(f) as fh:
        src = fh.read()
    src = src.replace('version=2.4.20', f'version={NEW_VER}')
    src = src.replace('built=2026-05-12T00:00:00Z', f'built={TODAY}')
    with open(f, 'w') as fh:
        fh.write(src)
    print(f'Updated {f}')

# api/package.json
import json
with open('/opt/ant2-proxy/api/package.json') as f:
    pkg = json.load(f)
pkg['version'] = NEW_VER
with open('/opt/ant2-proxy/api/package.json', 'w') as f:
    json.dump(pkg, f, indent=2)
    f.write('\n')
print('Updated package.json')
print(f'Version is now {NEW_VER}')
