import re

with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'r') as f:
    src = f.read()

# 1. WAFHostCard return: change `card transition-all` wrapper to borderless item
# The card class adds: rounded-2xl shadow-sm border border-slate-200 overflow-hidden
# We remove card and let the parent container handle border/rounded/shadow
old_card = '    <div className={`card transition-all ${open ? \'ring-2 ring-indigo-300\' : \'\'}`}>'
new_card = '    <div className={`transition-all ${open ? \'bg-indigo-50/30\' : \'\'}`}>'

if old_card in src:
    src = src.replace(old_card, new_card, 1)
    print('  + WAFHostCard wrapper updated')
else:
    print('  MISS: WAFHostCard wrapper - trying alternate')
    # Try without leading spaces
    alt_old = 'className={`card transition-all ${open ? \'ring-2 ring-indigo-300\' : \'\'}`}'
    alt_new = 'className={`transition-all ${open ? \'bg-indigo-50/30\' : \'\'}`}'
    if alt_old in src:
        src = src.replace(alt_old, alt_new, 1)
        print('  + WAFHostCard wrapper updated (alt)')
    else:
        print('  FAIL: could not find WAFHostCard wrapper')

# 2. List container: change `space-y-4 animate-fade-in` to accordion-style card
old_container = '<div className="space-y-4 animate-fade-in">'
new_container = '<div className="animate-fade-in flex flex-col gap-0">'

if old_container in src:
    src = src.replace(old_container, new_container, 1)
    print('  + list container space-y-4 removed')
else:
    print('  MISS: list container')

# 3. Wrap the .map() result in a card container with divide-y
# Before: .map(h => <WAFHostCard key={h.id} host={h} />)
# After: wrap in <div className="card overflow-hidden divide-y divide-slate-200">
old_map = '          .map(h => <WAFHostCard key={h.id} host={h} />)'
new_map = '''          .reduce((acc, h, i, arr) => {
            if (i === 0) acc.push(<div key="waf-list" className="card overflow-hidden divide-y divide-slate-200">)
            acc.push(<WAFHostCard key={h.id} host={h} />)
            if (i === arr.length - 1) acc.push(</div>)
            return acc
          }, [])'''

# Actually simpler approach: just wrap the whole expression
old_map2 = '''        hosts
          .filter(h => {
            if (!search) return true
            return h.domain.toLowerCase().includes(search.toLowerCase())
          })
          .map(h => <WAFHostCard key={h.id} host={h} />)'''

new_map2 = '''        <div className="card overflow-hidden divide-y divide-slate-200">
          {hosts
            .filter(h => {
              if (!search) return true
              return h.domain.toLowerCase().includes(search.toLowerCase())
            })
            .map(h => <WAFHostCard key={h.id} host={h} />)
          }
        </div>'''

if old_map2 in src:
    src = src.replace(old_map2, new_map2, 1)
    print('  + map wrapped in card container')
else:
    print('  MISS: map wrapper - check indentation')
    # Try with different whitespace
    import re as _re
    found = _re.search(r'hosts\s*\n\s*\.filter', src)
    if found:
        print('  Found hosts.filter at position:', found.start())
        print('  Context:', repr(src[found.start()-10:found.start()+100]))

with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'w') as f:
    f.write(src)

print('Done.')
