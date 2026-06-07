import re

with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'r') as f:
    src = f.read()

# 1. Reduce header row padding: py-4 → py-2.5, px-5 → px-4
old_header = 'className="flex items-center justify-between px-5 py-4 cursor-pointer select-none"'
new_header = 'className="flex items-center justify-between px-4 py-2.5 cursor-pointer select-none"'
if old_header in src:
    src = src.replace(old_header, new_header, 1)
    print('  + header padding reduced to py-2.5')
else:
    print('  MISS: header padding')

# 2. Add hover:bg-slate-50 to row wrapper (when closed)
old_wrapper = 'className={`transition-all ${open ? \'bg-indigo-50/30\' : \'\'}`}'
new_wrapper = 'className={`transition-all ${open ? \'bg-indigo-50/30\' : \'hover:bg-slate-50\'}`}'
if old_wrapper in src:
    src = src.replace(old_wrapper, new_wrapper, 1)
    print('  + hover:bg-slate-50 added to row wrapper')
else:
    print('  MISS: row wrapper')

# 3. Reduce expanded content padding: px-5 py-5 → px-4 py-4
old_content = 'className="border-t border-slate-100 px-5 py-5 space-y-5 animate-fade-in"'
new_content = 'className="border-t border-slate-100 px-4 py-4 space-y-4 animate-fade-in"'
if old_content in src:
    src = src.replace(old_content, new_content, 1)
    print('  + expanded content padding reduced')
else:
    print('  MISS: expanded content padding')

# 4. Fix outer container: add mb-3 between info banner/search and the list
# Currently: animate-fade-in flex flex-col gap-0 → keep gap-0 but items need spacing
# Add space-y-3 back to outer wrapper (gap between banner, search, list is fine)
old_outer = '<div className="animate-fade-in flex flex-col gap-0">'
new_outer = '<div className="animate-fade-in space-y-3">'
if old_outer in src:
    src = src.replace(old_outer, new_outer, 1)
    print('  + outer container spacing fixed (space-y-3)')
else:
    print('  MISS: outer container')

with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'w') as f:
    f.write(src)

print('Done.')
