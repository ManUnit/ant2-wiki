with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'r') as f:
    src = f.read()

# Split the lazy useEffect into:
# 1. Always-on effect for waf config (badge needs this)
# 2. Lazy effect for ip-rules only (heavy, only needed when expanded)

old = """  // Lazy-load WAF config on first open
  useEffect(() => {
    if (!everOpen) return
    api.get(`/waf/${host.id}`).then(r => {
      const d = r.data
      if (!Array.isArray(d.bypass_presets)) {
        try { d.bypass_presets = JSON.parse(d.bypass_presets || '[]') } catch { d.bypass_presets = [] }
      }
      setWaf(d); setForm(d)
    }).catch(() => {
      const defaults = { mode: 'block', enabled: true, paranoia_level: 1, inbound_threshold: 5, outbound_threshold: 4, custom_rules: '', excluded_rules: '', bypass_presets: [], bypass_custom: '', platform_preset: '' }
      setWaf(defaults); setForm(defaults)
    })
    api.get(`/waf/${host.id}/ip-rules`).then(r => setIpRules(r.data || [])).catch(() => {})
  }, [host.id, everOpen])"""

new = """  // Always load WAF config on mount (badge needs it immediately)
  useEffect(() => {
    api.get(`/waf/${host.id}`).then(r => {
      const d = r.data
      if (!Array.isArray(d.bypass_presets)) {
        try { d.bypass_presets = JSON.parse(d.bypass_presets || '[]') } catch { d.bypass_presets = [] }
      }
      setWaf(d); setForm(d)
    }).catch(() => {
      const defaults = { mode: 'block', enabled: true, paranoia_level: 1, inbound_threshold: 5, outbound_threshold: 4, custom_rules: '', excluded_rules: '', bypass_presets: [], bypass_custom: '', platform_preset: '' }
      setWaf(defaults); setForm(defaults)
    })
  }, [host.id])

  // Lazy-load ip-rules only on first open (heavier, not needed for badge)
  useEffect(() => {
    if (!everOpen) return
    api.get(`/waf/${host.id}/ip-rules`).then(r => setIpRules(r.data || [])).catch(() => {})
  }, [host.id, everOpen])"""

if old in src:
    src = src.replace(old, new, 1)
    print('+ split useEffect: waf always-on, ip-rules lazy')
else:
    print('MISS - string not found')

with open('/opt/ant2-proxy/web/src/pages/WAF.jsx', 'w') as f:
    f.write(src)
print('Done.')
