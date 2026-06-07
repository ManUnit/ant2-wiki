import json

for path in ['/opt/ant2-proxy/api/package.json']:
    with open(path) as f:
        p = json.load(f)
    p['version'] = '2.4.20'
    with open(path, 'w') as f:
        json.dump(p, f, indent=2)
        f.write('\n')
    print(f'{path}: {p["version"]}')
