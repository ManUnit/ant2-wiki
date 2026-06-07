import shutil, re

# Copy IpJail.jsx into pages
shutil.copy('/tmp/IpJail.jsx', '/opt/ant2-proxy/web/src/pages/IpJail.jsx')
print('+ Copied IpJail.jsx')

# ── Patch App.jsx ─────────────────────────────────────────────────────────────
with open('/opt/ant2-proxy/web/src/App.jsx') as f:
    app = f.read()

# Add import after GeoIP import
app = app.replace(
    "import GeoIP       from './pages/GeoIP'",
    "import GeoIP       from './pages/GeoIP'\nimport IpJail      from './pages/IpJail'"
)

# Add route after geoip route
app = app.replace(
    "                    <Route path=\"geoip\"        element={<GeoIP />} />",
    "                    <Route path=\"geoip\"        element={<GeoIP />} />\n                    <Route path=\"ip-jail\"      element={<IpJail />} />"
)

with open('/opt/ant2-proxy/web/src/App.jsx', 'w') as f:
    f.write(app)
print('+ Patched App.jsx (import + route)')

# ── Patch Sidebar.jsx ─────────────────────────────────────────────────────────
with open('/opt/ant2-proxy/web/src/components/Sidebar.jsx') as f:
    sb = f.read()

# Add ShieldAlert to imports
sb = sb.replace(
    'ShieldCheck, Lock,',
    'ShieldCheck, Lock, ShieldAlert,'
)

# Add sidebar link after geoip
sb = sb.replace(
    "  { to: '/geoip',        icon: MapPin,          label: 'Country Block' },",
    "  { to: '/geoip',        icon: MapPin,          label: 'Country Block' },\n  { to: '/ip-jail',      icon: ShieldAlert,     label: 'IP Jail' },"
)

with open('/opt/ant2-proxy/web/src/components/Sidebar.jsx', 'w') as f:
    f.write(sb)
print('+ Patched Sidebar.jsx (icon import + link)')

# Verify
import subprocess
r = subprocess.run(['grep', '-n', 'IpJail\|ip-jail\|ShieldAlert',
    '/opt/ant2-proxy/web/src/App.jsx',
    '/opt/ant2-proxy/web/src/components/Sidebar.jsx'], capture_output=True, text=True)
print(r.stdout)
