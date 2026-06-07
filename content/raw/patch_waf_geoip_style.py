with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'r') as f:
    src = f.read()

changes = []

# 1. Header row: px-4 py-2.5 → px-3 py-2 (match GeoIP jail row density)
old1 = 'className="flex items-center justify-between px-4 py-2.5 cursor-pointer select-none"'
new1 = 'className="flex items-center justify-between px-3 py-2 cursor-pointer select-none"'
if old1 in src:
    src = src.replace(old1, new1, 1)
    changes.append('+ header: px-4 py-2.5 → px-3 py-2')

# 2. List container: card (rounded-2xl shadow-sm) → rounded-xl no shadow (match GeoIP)
old2 = 'className="card overflow-hidden divide-y divide-slate-200"'
new2 = 'className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100 overflow-hidden"'
if old2 in src:
    src = src.replace(old2, new2, 1)
    changes.append('+ container: card → rounded-xl no shadow, divider slate-100')

# 3. Expanded content: px-4 py-4 → px-3 py-3 (consistent)
old3 = 'className="border-t border-slate-100 px-4 py-4 space-y-4 animate-fade-in"'
new3 = 'className="border-t border-slate-100 px-3 py-3 space-y-4 animate-fade-in"'
if old3 in src:
    src = src.replace(old3, new3, 1)
    changes.append('+ expanded panel: px-4 py-4 → px-3 py-3')

if changes:
    with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'w') as f:
        f.write(src)
    for c in changes:
        print(c)
    print('Done.')
else:
    print('No matches found - verify strings.')
