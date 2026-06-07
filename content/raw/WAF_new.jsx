import React, { useEffect, useState, useCallback, useMemo, memo } from 'react'
import {
  ShieldCheck, ShieldOff, ShieldAlert, Save, ChevronDown, ChevronLeft, ChevronRight,
  Info, Zap, Layers, Plus, Trash2, Ban, KeyRound, Search, X,
} from 'lucide-react'
import { useToast } from '../components/Toast'
import api from '../api/client'

// ── Constants ─────────────────────────────────────────────────────
const PAGE_SIZE = 25

const PARANOIA_DESC = {
  1: 'Default — low false positive rate, catches common attacks',
  2: 'Balanced — more rules active, slightly higher false positives',
  3: 'Strict — thorough detection, may need exclusions for complex apps',
  4: 'Paranoid — maximum detection, expect many false positives',
}

const BYPASS_PRESETS_UI = [
  { key: 'google_oauth',    label: 'Google OAuth / Google Login',             desc: 'Covers sign-in/callback routes; fixes scope/state/code false positives' },
  { key: 'nextauth',        label: 'NextAuth.js / Auth.js (all providers)',    desc: 'Covers /api/auth/* — Google, GitHub, Facebook, Microsoft in one rule' },
  { key: 'facebook_oauth',  label: 'Facebook OAuth',                          desc: 'Fixes: long state/code params resemble SQLi patterns' },
  { key: 'github_oauth',    label: 'GitHub OAuth',                            desc: 'Fixes: auth code values trigger rule 932150 (RCE detection)' },
  { key: 'microsoft_oauth', label: 'Microsoft / Azure AD / OIDC',             desc: 'Fixes: JWT id_token in POST body triggers 941100/942100/920230' },
  { key: 'saml_sso',        label: 'SAML SSO (Assertion POST)',               desc: 'Fixes: large base64 SAMLResponse triggers 920230/941100/942100' },
  { key: 'line_oauth',      label: 'LINE Login OAuth',                        desc: 'LINE OAuth2 callback — common in Thai/Asian web apps' },
  { key: 'stripe_webhook',  label: 'Stripe Webhook',                          desc: 'Fixes: payment fields trigger SQLi/XSS rules' },
  { key: 'github_webhook',  label: 'GitHub Webhook',                          desc: 'Fixes: code diff content in payload triggers injection rules' },
  { key: 'paypal_webhook',  label: 'PayPal IPN / Webhook',                    desc: 'Fixes: payment notification payloads trigger injection rules' },
]

const PLATFORM_PRESETS_UI = [
  { key: '',             label: '— None —',                    category: '',            desc: '' },
  { key: 'wordpress',   label: 'WordPress',                   category: 'CMS',         desc: 'Gutenberg editor, shortcodes, WooCommerce, wp-admin false positives' },
  { key: 'laravel',     label: 'Laravel (PHP)',                category: 'Framework',   desc: 'CSRF _token pollution, Eloquent ORM params, signed URL encoding' },
  { key: 'php',         label: 'PHP (generic)',                category: 'Language',    desc: 'PHP injection false positives from form data' },
  { key: 'php_fpm',     label: 'PHP-FPM (FastCGI)',            category: 'Language',    desc: 'PHP generic + SCRIPT_FILENAME / PATH_INFO fcgi conflicts' },
  { key: 'nodejs',      label: 'Node.js (Express/Fastify)',    category: 'Language',    desc: 'JSON Content-Type, PATCH/PUT/DELETE method rules' },
  { key: 'python',      label: 'Python (Django/Flask/FastAPI)',category: 'Language',    desc: 'Django CSRF token pollution, DRF application/json' },
  { key: 'nextjs',      label: 'Next.js (Vercel)',             category: 'Framework',   desc: 'API route JSON, server actions, _next params, NextAuth routes' },
  { key: 'spring_boot', label: 'Java Spring Boot (REST)',      category: 'Framework',   desc: 'JSON Content-Type, REST methods, Spring Security CSRF' },
  { key: 'dotnet',      label: '.NET / ASP.NET Core',          category: 'Framework',   desc: 'ViewState encoding, .NET serialization, CSRF token' },
  { key: 'asp_classic', label: 'ASP Classic (VBScript)',       category: 'Framework',   desc: 'VBScript syntax triggers Perl detection rules' },
  { key: 'java',        label: 'Java (J2EE / Jakarta EE)',     category: 'Language',    desc: 'Java serialization/deserialization detection rules' },
  { key: 'tomcat',      label: 'Apache Tomcat',                category: 'App Server',  desc: 'Java rules + JSP EL expression ${...} in responses' },
  { key: 'sap',         label: 'SAP (NetWeaver/HANA/Fiori)',   category: 'Enterprise',  desc: 'SAP-specific URLs, Java serialization, OData requests' },
  { key: 'perl',        label: 'Perl (CGI/Dancer2/Mojo)',      category: 'Language',    desc: 'Perl syntax detection misfires on form data' },
  { key: 'apache',      label: 'Apache HTTP Server',           category: 'Web Server',  desc: 'mod_rewrite request-line artifacts' },
  { key: 'nginx_app',   label: 'Ant2 (as upstream)',           category: 'Web Server',  desc: 'Minimal exclusions — CRS is optimized for Ant2' },
  { key: 'iis',         label: 'IIS (Windows)',                category: 'Web Server',  desc: 'Windows paths, .asp/.aspx extension, IIS headers' },
]

const MODES = [
  { key: 'off',    label: 'Off',    desc: 'WAF disabled — all traffic passes through',                                              icon: ShieldOff,   btn: 'bg-slate-100 text-slate-600 hover:bg-slate-200', active: 'bg-slate-600 text-white shadow',   badge: 'bg-slate-100 text-slate-600', badgeLabel: 'WAF Off' },
  { key: 'detect', label: 'Detect', desc: 'Detection only — logs threats but does NOT block (SecRuleEngine DetectionOnly)',         icon: ShieldAlert, btn: 'bg-amber-50 text-amber-700 hover:bg-amber-100', active: 'bg-amber-500 text-white shadow',   badge: 'bg-amber-100 text-amber-700', badgeLabel: 'WAF Detect' },
  { key: 'block',  label: 'Block',  desc: 'Active blocking — detects and blocks matching requests (SecRuleEngine On)',              icon: ShieldCheck, btn: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100', active: 'bg-emerald-600 text-white shadow', badge: 'bg-emerald-100 text-emerald-700', badgeLabel: 'WAF Block' },
]

// ── Expanded settings panel ───────────────────────────────────────
function WAFExpandedPanel({ host, form, setForm, waf, saving, save, ipRules, setIpRules, newIp, setNewIp }) {
  const toast = useToast()
  const curMode  = form.mode || (form.enabled ? 'block' : 'off')
  const modeMeta = MODES.find(m => m.key === curMode) || MODES[0]

  return (
    <div className="bg-slate-50/60 border-t border-slate-100 px-4 py-4 space-y-5">

      {/* Mode selector */}
      <div>
        <label className="label mb-2">WAF Mode</label>
        <div className="grid grid-cols-3 gap-2">
          {MODES.map(m => {
            const Icon = m.icon
            const isActive = curMode === m.key
            return (
              <button key={m.key} type="button"
                onClick={() => setForm(f => ({ ...f, mode: m.key, enabled: m.key !== 'off' }))}
                className={`flex flex-col items-center gap-1.5 rounded-xl border-2 py-3 px-2 font-semibold text-sm transition-all
                  ${isActive ? m.active + ' border-transparent' : m.btn + ' border-slate-200'}`}>
                <Icon className="w-5 h-5" />
                {m.label}
              </button>
            )
          })}
        </div>
        <p className={`mt-2 text-xs px-1 ${curMode === 'detect' ? 'text-amber-600' : curMode === 'block' ? 'text-emerald-700' : 'text-slate-400'}`}>
          {modeMeta.desc}
        </p>
      </div>

      {curMode !== 'off' && (
        <>
          {/* Platform */}
          <div>
            <label className="label flex items-center gap-1.5 mb-2">
              <Layers className="w-3.5 h-3.5 text-indigo-500" />
              Platform / Framework Compatibility
            </label>
            <select className="input text-sm" value={form.platform_preset || ''}
              onChange={e => setForm(f => ({ ...f, platform_preset: e.target.value }))}>
              {PLATFORM_PRESETS_UI.map(p => (
                <option key={p.key} value={p.key}>
                  {p.category ? `[${p.category}]  ${p.label}` : p.label}
                </option>
              ))}
            </select>
            {form.platform_preset && (() => {
              const p = PLATFORM_PRESETS_UI.find(x => x.key === form.platform_preset)
              return p?.desc ? (
                <div className="mt-2 p-2.5 bg-indigo-50 rounded-lg flex gap-2">
                  <Info className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-indigo-700">{p.desc}</p>
                </div>
              ) : null
            })()}
          </div>

          {/* Bypass presets */}
          <div>
            <label className="label flex items-center gap-1.5 mb-2">
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              Bypass Rules — Skip WAF for specific URLs
            </label>
            <div className="rounded-xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
              {BYPASS_PRESETS_UI.map(p => {
                const checked = Array.isArray(form.bypass_presets) && form.bypass_presets.includes(p.key)
                return (
                  <label key={p.key} className={`flex items-start gap-3 px-3 py-2.5 cursor-pointer select-none transition-colors ${checked ? 'bg-amber-50' : 'bg-white hover:bg-slate-50'}`}>
                    <input type="checkbox" className="mt-0.5 accent-amber-500" checked={checked}
                      onChange={e => setForm(f => {
                        const cur = Array.isArray(f.bypass_presets) ? f.bypass_presets : []
                        return { ...f, bypass_presets: e.target.checked ? [...cur, p.key] : cur.filter(k => k !== p.key) }
                      })} />
                    <div>
                      <span className={`text-sm font-semibold ${checked ? 'text-amber-700' : 'text-slate-700'}`}>{p.label}</span>
                      <p className="text-xs text-slate-400 mt-0.5">{p.desc}</p>
                    </div>
                  </label>
                )
              })}
            </div>
            <div className="mt-2">
              <label className="label text-xs">Custom Bypass Paths (one per line)</label>
              <textarea rows={3} className="input font-mono text-xs resize-y mt-1"
                placeholder={'/api/auth/callback/myapp\n/webhooks/custom\n/legacy/login'}
                value={form.bypass_custom || ''}
                onChange={e => setForm(f => ({ ...f, bypass_custom: e.target.value }))} />
              <p className="text-xs text-slate-400 mt-1">Enter URI prefixes — WAF will be disabled for requests matching these paths</p>
            </div>
          </div>

          {/* Paranoia */}
          <div>
            <label className="label mb-2">
              Paranoia Level:&nbsp;<span className="text-indigo-600 font-bold">{form.paranoia_level}</span>
              &nbsp;<span className="text-xs text-slate-400 font-normal">— {PARANOIA_DESC[form.paranoia_level]}</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[1,2,3,4].map(lvl => (
                <button key={lvl} type="button"
                  onClick={() => setForm(f => ({ ...f, paranoia_level: lvl }))}
                  className={`rounded-lg border-2 py-2 text-sm font-bold transition-all
                    ${form.paranoia_level === lvl
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow'
                      : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300 hover:text-indigo-600'}`}>
                  {lvl}
                </button>
              ))}
            </div>
            <div className="flex justify-between text-xs text-slate-400 mt-1 px-0.5">
              <span>Permissive</span><span /><span /><span>Paranoid</span>
            </div>
          </div>

          {/* Thresholds */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Inbound Threshold</label>
              <input type="number" min={1} max={100} className="input" value={form.inbound_threshold}
                onChange={e => setForm(f => ({ ...f, inbound_threshold: +e.target.value }))} />
              <p className="text-xs text-slate-400 mt-1">Block if score ≥ this (default: 5)</p>
            </div>
            <div>
              <label className="label">Outbound Threshold</label>
              <input type="number" min={1} max={100} className="input" value={form.outbound_threshold}
                onChange={e => setForm(f => ({ ...f, outbound_threshold: +e.target.value }))} />
              <p className="text-xs text-slate-400 mt-1">Block outbound if score ≥ this (default: 4)</p>
            </div>
          </div>

          {/* Excluded rules */}
          <div>
            <label className="label">Excluded Rule IDs (comma-separated)</label>
            <input className="input font-mono text-xs" placeholder="941100, 942100, 932150"
              value={form.excluded_rules}
              onChange={e => setForm(f => ({ ...f, excluded_rules: e.target.value }))} />
            <p className="text-xs text-slate-400 mt-1">Rule IDs to disable — use to reduce false positives</p>
          </div>

          {/* Custom rules */}
          <div>
            <label className="label">Custom ModSecurity Rules</label>
            <textarea rows={6} className="input font-mono text-xs resize-y"
              placeholder={'# Add custom SecRule directives here\n# Example:\n# SecRule REQUEST_URI "@contains /admin" "id:1000001,phase:1,deny,status:403"'}
              value={form.custom_rules}
              onChange={e => setForm(f => ({ ...f, custom_rules: e.target.value }))} />
          </div>

          {/* IP Access Rules */}
          <div>
            <label className="label flex items-center gap-1.5 mb-2">
              <KeyRound className="w-3.5 h-3.5 text-cyan-500" />
              IP Access Control — Bypass / Deny WAF by Source IP
            </label>
            {ipRules.length > 0 && (
              <div className="rounded-xl border border-slate-200 divide-y divide-slate-100 overflow-hidden mb-3">
                {ipRules.map(r => (
                  <div key={r.id} className={`flex items-center justify-between px-3 py-2 text-sm
                    ${r.action === 'deny' ? 'bg-rose-50' : 'bg-cyan-50'}`}>
                    <div className="flex items-center gap-2">
                      {r.action === 'deny'
                        ? <Ban className="w-3.5 h-3.5 text-rose-500" />
                        : <KeyRound className="w-3.5 h-3.5 text-cyan-500" />}
                      <span className="font-mono text-xs">{r.ip_address}</span>
                      <span className={`px-1.5 py-0.5 rounded text-xs font-medium
                        ${r.action === 'deny' ? 'bg-rose-100 text-rose-700' : 'bg-cyan-100 text-cyan-700'}`}>
                        {r.action === 'deny' ? 'DENY (403)' : 'BYPASS WAF'}
                      </span>
                      {r.note && <span className="text-xs text-slate-400">{r.note}</span>}
                    </div>
                    <button onClick={async () => {
                      await api.delete(`/waf/${host.id}/ip-rules/${r.id}`)
                      setIpRules(prev => prev.filter(x => x.id !== r.id))
                      toast('IP rule removed', 'success')
                    }} className="p-1 text-slate-400 hover:text-rose-500">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <input value={newIp.ip_address} onChange={e => setNewIp(p => ({ ...p, ip_address: e.target.value }))}
                  placeholder="IP or CIDR (e.g. 10.0.0.0/8)" className="input text-xs py-1.5" />
              </div>
              <select value={newIp.action} onChange={e => setNewIp(p => ({ ...p, action: e.target.value }))}
                className="input text-xs py-1.5 w-36">
                <option value="bypass">Bypass WAF</option>
                <option value="deny">Hard Deny (403)</option>
              </select>
              <input value={newIp.note} onChange={e => setNewIp(p => ({ ...p, note: e.target.value }))}
                placeholder="Note (optional)" className="input text-xs py-1.5 w-40" />
              <button onClick={async () => {
                if (!newIp.ip_address) return
                try {
                  const { data } = await api.post(`/waf/${host.id}/ip-rules`, newIp)
                  setIpRules(prev => [data, ...prev])
                  setNewIp({ ip_address: '', action: 'bypass', note: '' })
                  toast('IP rule added', 'success')
                } catch (err) { toast(err.response?.data?.error || 'Failed', 'error') }
              }} className="btn-primary text-xs py-1.5 px-3 shrink-0">
                <Plus className="w-3.5 h-3.5" /> Add
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-1.5">
              <strong>Bypass</strong>: trusted IPs skip WAF entirely.
              <strong className="ml-2">Deny</strong>: banned IPs get 403 immediately (before WAF).
            </p>
          </div>
        </>
      )}

      <div className="flex justify-end pt-2 border-t border-slate-100">
        <button onClick={save} disabled={saving} className="btn-primary">
          <Save className="w-4 h-4" />
          {saving ? 'Saving…' : 'Save WAF Settings'}
        </button>
      </div>
    </div>
  )
}

// ── Compact memoized row ──────────────────────────────────────────
const WAFHostRow = memo(function WAFHostRow({ host }) {
  const toast    = useToast()
  const [waf,      setWaf]      = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [open,     setOpen]     = useState(false)
  const [everOpen, setEverOpen] = useState(false)
  const [form,     setForm]     = useState(null)
  const [ipRules,  setIpRules]  = useState([])
  const [newIp,    setNewIp]    = useState({ ip_address: '', action: 'bypass', note: '' })

  // Lazy-load WAF config on first open
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
  }, [host.id, everOpen])

  const handleToggle = useCallback(() => {
    setOpen(o => {
      if (!o && !everOpen) setEverOpen(true)
      return !o
    })
  }, [everOpen])

  const save = useCallback(async () => {
    setSaving(true)
    try {
      const { data } = await api.put(`/waf/${host.id}`, form)
      if (!Array.isArray(data.bypass_presets)) {
        try { data.bypass_presets = JSON.parse(data.bypass_presets || '[]') } catch { data.bypass_presets = [] }
      }
      setWaf(data); setForm(data)
      toast(`WAF saved for ${host.domain}`, 'success')
    } catch (err) {
      toast(err.response?.data?.error || 'Save failed', 'error')
    } finally { setSaving(false) }
  }, [host.id, host.domain, form, toast])

  const savedMode  = waf ? (waf.mode || (waf.enabled ? 'block' : 'off')) : null
  const badgeMeta  = savedMode ? (MODES.find(m => m.key === savedMode) || MODES[0]) : null
  const curMode    = form ? (form.mode || (form.enabled ? 'block' : 'off')) : 'off'
  const RowIcon    = MODES.find(m => m.key === curMode)?.icon || ShieldOff
  const iconColor  = curMode === 'block' ? 'text-emerald-500' : curMode === 'detect' ? 'text-amber-500' : 'text-slate-300'

  return (
    <div>
      {/* ── Compact row: ~40px height ── */}
      <div
        onClick={handleToggle}
        className={`flex items-center gap-3 px-4 py-2 cursor-pointer select-none transition-colors
          ${open ? 'bg-indigo-50/50' : 'hover:bg-slate-50'}`}
      >
        {/* Shield icon */}
        <RowIcon className={`w-4 h-4 shrink-0 ${iconColor}`} />

        {/* Domain */}
        <span className="font-semibold text-slate-800 text-sm w-56 truncate shrink-0">{host.domain}</span>

        {/* Upstream */}
        <span className="flex-1 text-xs text-slate-400 font-mono truncate">{host.upstream}</span>

        {/* Badge + chevron */}
        <div className="flex items-center gap-2 shrink-0">
          {badgeMeta
            ? (
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${badgeMeta.badge}`}>
                {badgeMeta.key === 'block'  && <ShieldCheck className="w-3 h-3" />}
                {badgeMeta.key === 'detect' && <ShieldAlert  className="w-3 h-3" />}
                {badgeMeta.key === 'off'    && <ShieldOff    className="w-3 h-3" />}
                {badgeMeta.badgeLabel}{badgeMeta.key !== 'off' ? ` P${waf.paranoia_level}` : ''}
              </span>
            )
            : <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-400">—</span>
          }
          <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
        </div>
      </div>

      {/* ── Expanded panel with smooth height animation ── */}
      <div style={{ maxHeight: open ? '3200px' : '0', overflow: 'hidden', transition: 'max-height 220ms ease-in-out' }}>
        {everOpen && form && (
          <WAFExpandedPanel
            host={host} form={form} setForm={setForm}
            waf={waf} saving={saving} save={save}
            ipRules={ipRules} setIpRules={setIpRules}
            newIp={newIp} setNewIp={setNewIp}
          />
        )}
        {everOpen && !form && (
          <div className="px-4 py-6 text-center text-slate-400 text-sm border-t border-slate-100 bg-slate-50/60 animate-pulse">
            Loading WAF settings…
          </div>
        )}
      </div>
    </div>
  )
})

// ── Main WAF page ─────────────────────────────────────────────────
export default function WAF() {
  const [hosts,   setHosts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [search,  setSearch]  = useState('')
  const [page,    setPage]    = useState(1)

  useEffect(() => {
    api.get('/hosts').then(r => setHosts(r.data)).finally(() => setLoading(false))
  }, [])

  useEffect(() => { setPage(1) }, [search])

  const filtered   = useMemo(() =>
    hosts.filter(h => !search || h.domain.toLowerCase().includes(search.toLowerCase())),
    [hosts, search]
  )
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const pageHosts  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div className="animate-fade-in">

      {/* ── Sticky toolbar: search + column header ── */}
      <div className="sticky top-0 z-20 bg-white border border-slate-200 rounded-t-xl shadow-sm">
        {/* Search row */}
        <div className="flex items-center gap-3 px-4 py-2 border-b border-slate-100">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400 pointer-events-none" />
            {search && (
              <button onClick={() => setSearch('')}
                className="absolute right-2.5 top-2 p-0.5 text-slate-400 hover:text-slate-600 transition-colors">
                <X className="w-3.5 h-3.5" />
              </button>
            )}
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search domains…"
              className="input pl-9 pr-8 text-sm py-1.5"
            />
          </div>
          <span className="text-xs text-slate-400 shrink-0 tabular-nums whitespace-nowrap">
            {filtered.length} / {hosts.length} hosts
          </span>
        </div>

        {/* Column header row */}
        <div className="flex items-center gap-3 px-4 py-1.5 bg-slate-50">
          <div className="w-4 shrink-0" />
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider w-56 shrink-0">Domain</span>
          <span className="flex-1 text-xs font-semibold text-slate-500 uppercase tracking-wider">Upstream</span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider shrink-0 pr-5">WAF Status</span>
        </div>
      </div>

      {/* ── List ── */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 text-sm animate-pulse border-x border-b border-slate-200 rounded-b-xl">
          Loading hosts…
        </div>
      ) : hosts.length === 0 ? (
        <div className="py-16 text-center border-x border-b border-slate-200 rounded-b-xl">
          <ShieldOff className="w-12 h-12 text-slate-200 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Add proxy hosts first to configure WAF settings</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-12 text-center text-slate-400 text-sm border-x border-b border-slate-200 rounded-b-xl">
          No domains match "{search}"
        </div>
      ) : (
        <div className="border-x border-b border-slate-200 rounded-b-xl divide-y divide-slate-100 overflow-hidden bg-white">
          {pageHosts.map(h => <WAFHostRow key={h.id} host={h} />)}
        </div>
      )}

      {/* ── Pagination ── */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-2 mt-2 bg-white border border-slate-200 rounded-xl">
          <span className="text-xs text-slate-400 tabular-nums">
            Page {page} of {totalPages} · {filtered.length} hosts
          </span>
          <div className="flex items-center gap-1">
            <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
              className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
              <ChevronLeft className="w-4 h-4" />
            </button>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
              const p = totalPages <= 7 ? i + 1
                : page <= 4 ? i + 1
                : page >= totalPages - 3 ? totalPages - 6 + i
                : page - 3 + i
              return (
                <button key={p} onClick={() => setPage(p)}
                  className={`w-7 h-7 rounded-lg text-xs font-medium transition-colors
                    ${p === page ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`}>
                  {p}
                </button>
              )
            })}
            <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}
              className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
