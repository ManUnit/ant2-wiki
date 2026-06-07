import React, { useState, useEffect, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import { ChevronDown, Trash2, PlusCircle, RefreshCw, BarChart2, X, ShieldCheck } from 'lucide-react'
import api from '../api/client'

function flag(code) {
  if (!code || code.length !== 2) return ''
  const [a, b] = code.toUpperCase().split('')
  return String.fromCodePoint(0x1F1E6 + a.charCodeAt(0) - 65) +
         String.fromCodePoint(0x1F1E6 + b.charCodeAt(0) - 65)
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('th-TH', { dateStyle: 'short', timeStyle: 'short' })
}
function fmtRemaining(secs) {
  if (secs == null) return 'Permanent'
  if (secs <= 0)    return 'Expired'
  const d = Math.floor(secs / 86400)
  const h = Math.floor((secs % 86400) / 3600)
  const m = Math.floor((secs % 3600) / 60)
  if (d > 0) return `${d}d ${h}h ${m}m`
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

const DURATION_OPTIONS = [
  { label: '1 hour',    value: 1    },
  { label: '6 hours',   value: 6    },
  { label: '12 hours',  value: 12   },
  { label: '1 day',     value: 24   },
  { label: '3 days',    value: 72   },
  { label: '7 days',    value: 168  },
  { label: '14 days',   value: 336  },
  { label: '30 days',   value: 720  },
  { label: '60 days',   value: 1440 },
  { label: '90 days',   value: 2160 },
  { label: 'Permanent', value: 0    },
]

const PAGE_SIZE_OPTIONS = [
  { label: '20',  value: 20  },
  { label: '50',  value: 50  },
  { label: '100', value: 100 },
]

function SelectBox({ value, onChange, options, small = false }) {
  const [open, setOpen]       = useState(false)
  const [dropPos, setDropPos] = useState(null)
  const btnRef  = useRef(null)
  const dropRef = useRef(null)

  const handleToggle = () => {
    if (!open && btnRef.current) {
      const r = btnRef.current.getBoundingClientRect()
      setDropPos({ top: r.bottom + 4, left: r.left })
    }
    setOpen(v => !v)
  }

  useEffect(() => {
    if (!open) return
    const close = (e) => {
      if (btnRef.current?.contains(e.target))  return
      if (dropRef.current?.contains(e.target)) return
      setOpen(false)
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])

  const selected = options.find(o => o.value === value)

  return (
    <div className="inline-block">
      <button ref={btnRef} type="button" onClick={handleToggle}
        className={`flex items-center border rounded-lg bg-white focus:outline-none
                    focus:ring-2 focus:ring-indigo-500 hover:border-indigo-400 transition-colors
                    ${open ? 'border-indigo-500' : 'border-slate-300'}
                    ${small ? 'text-xs' : 'text-sm'}`}>
        <span className={`pl-3 pr-2 text-slate-700 whitespace-nowrap ${small ? 'py-0.5' : 'py-2'}`}>
          {selected?.label ?? '—'}
        </span>
        <span className={`flex items-center justify-center bg-slate-100 border-l border-slate-300
                          shrink-0 rounded-r-lg ${small ? 'w-6 py-0.5' : 'w-8 py-2'}`}>
          <ChevronDown className={`text-slate-500 transition-transform duration-200
                                   ${open ? 'rotate-180' : ''} ${small ? 'w-3 h-3' : 'w-4 h-4'}`} />
        </span>
      </button>
      {open && dropPos && createPortal(
        <div ref={dropRef}
          style={{ position: 'fixed', top: dropPos.top, left: dropPos.left, zIndex: 9999 }}
          className="bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden w-max">
          {options.map(o => (
            <button key={o.value} type="button"
              onClick={() => { onChange(o.value); setOpen(false) }}
              className={`w-full text-left px-3 py-2 transition-colors hover:bg-indigo-50 hover:text-indigo-700
                          ${small ? 'text-xs' : 'text-sm'}
                          ${o.value === value ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-700'}`}>
              {o.label}
            </button>
          ))}
        </div>,
        document.body
      )}
    </div>
  )
}

function PaginationBar({ total, page, pageSize, onPage, onPageSize }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1
  const to   = Math.min(page * pageSize, total)
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1)
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-t border-slate-100 text-sm text-slate-500">
      <span>
        Showing <strong className="text-slate-700">{from}–{to}</strong> of{' '}
        <strong className="text-slate-700">{total}</strong> entries
        &nbsp;·&nbsp; Per page:&nbsp;
        <SelectBox small value={pageSize} onChange={v => { onPageSize(v); onPage(1) }} options={PAGE_SIZE_OPTIONS} />
      </span>
      <div className="flex items-center gap-1">
        <button onClick={() => onPage(1)} disabled={page === 1}
          className="px-2 py-1 rounded text-xs hover:bg-slate-100 disabled:opacity-40">{'< First'}</button>
        {pages.map(p => (
          <button key={p} onClick={() => onPage(p)}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors
              ${p === page ? 'bg-indigo-600 text-white' : 'hover:bg-slate-100 text-slate-600'}`}>
            {p}{p === totalPages ? ':End' : ''}
          </button>
        ))}
        <button onClick={() => onPage(totalPages)} disabled={page === totalPages}
          className="px-2 py-1 rounded text-xs hover:bg-slate-100 disabled:opacity-40">{'End >'}</button>
      </div>
    </div>
  )
}

function ManualJailModal({ settings, onClose, onDone }) {
  const [ip,     setIp]     = useState('')
  const [reason, setReason] = useState('')
  const [dur,    setDur]    = useState(settings.duration_hours ?? 168)
  const [busy,   setBusy]   = useState(false)
  const [err,    setErr]    = useState('')

  async function submit(e) {
    e.preventDefault()
    if (!ip.trim()) return
    setBusy(true); setErr('')
    try {
      await api.post('/jail', { ip_address: ip.trim(), reason: reason || 'Manual jail', duration_hours: dur })
      onDone()
    } catch (ex) {
      setErr(ex.response?.data?.error || ex.message)
      setBusy(false)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="font-bold text-slate-800">Manual Jail</h2>
          <button type="button" onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg">
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>
        <form onSubmit={submit} className="px-6 py-5 space-y-4">
          {err && <p className="text-xs text-rose-600 bg-rose-50 rounded-lg px-3 py-2">{err}</p>}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">IP Address *</label>
            <input value={ip} onChange={e => setIp(e.target.value)} placeholder="1.2.3.4"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Reason</label>
            <input value={reason} onChange={e => setReason(e.target.value)} placeholder="Manual jail"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Duration</label><br/>
            <SelectBox value={dur} onChange={setDur} options={DURATION_OPTIONS} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
            <button type="submit" disabled={busy || !ip.trim()}
              className="flex items-center gap-1.5 px-5 py-2 bg-rose-600 text-white rounded-lg text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
              <PlusCircle className="w-4 h-4" />
              {busy ? 'Jailing…' : 'Jail IP'}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  )
}

function AddWhitelistModal({ onClose, onDone }) {
  const [ip,   setIp]   = useState('')
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [err,  setErr]  = useState('')

  async function submit(e) {
    e.preventDefault()
    if (!ip.trim()) return
    setBusy(true); setErr('')
    try {
      await api.post('/jail/whitelist', { ip_address: ip.trim(), note: note || 'Whitelisted' })
      onDone()
    } catch (ex) {
      setErr(ex.response?.data?.error || ex.message)
      setBusy(false)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="font-bold text-slate-800">Add to Whitelist</h2>
          <button type="button" onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg">
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>
        <form onSubmit={submit} className="px-6 py-5 space-y-4">
          {err && <p className="text-xs text-rose-600 bg-rose-50 rounded-lg px-3 py-2">{err}</p>}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">IP Address *</label>
            <input value={ip} onChange={e => setIp(e.target.value)} placeholder="1.2.3.4"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Note / Reason</label>
            <input value={note} onChange={e => setNote(e.target.value)} placeholder="e.g. Office IP, trusted scanner…"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
            <button type="submit" disabled={busy || !ip.trim()}
              className="flex items-center gap-1.5 px-5 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50">
              <ShieldCheck className="w-4 h-4" />
              {busy ? 'Adding…' : 'Add to Whitelist'}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  )
}

export default function IpJail() {
  const [jailed,   setJailed]   = useState([])
  const [counters, setCounters] = useState([])
  const [settings, setSettings] = useState({ enabled: true, threshold: 8, duration_hours: 168 })
  const [loading,  setLoading]  = useState(true)
  const [showModal, setShowModal] = useState(false)

  const [enabled,   setEnabled]   = useState(true)
  const [threshold, setThreshold] = useState(8)
  const [durHours,  setDurHours]  = useState(168)
  const [saving,    setSaving]    = useState(false)

  const [jailPage,     setJailPage]     = useState(1)
  const [jailPageSize, setJailPageSize] = useState(20)

  const [activeTab,   setActiveTab]   = useState('jailed')
  const [whitelist,   setWhitelist]   = useState([])
  const [showWlModal, setShowWlModal] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [j, c, s, w] = await Promise.all([
        api.get('/jail'),
        api.get('/jail/counters'),
        api.get('/jail/settings'),
        api.get('/jail/whitelist'),
      ])
      setJailed(j.data)
      setCounters(c.data)
      setSettings(s.data)
      setEnabled(s.data.enabled)
      setThreshold(s.data.threshold)
      setDurHours(s.data.duration_hours)
      setWhitelist(Array.isArray(w.data) ? w.data : [])
    } catch (e) { console.error(e) }
    finally     { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  async function saveSettings(e) {
    e.preventDefault()
    setSaving(true)
    try {
      const res = await api.put('/jail/settings', {
        enabled, threshold: Number(threshold), duration_hours: Number(durHours)
      })
      setSettings(res.data)
      if (res.data.newly_jailed?.length) await load()
    } catch (ex) { alert(ex.response?.data?.error || ex.message) }
    finally      { setSaving(false) }
  }

  async function releaseOne(id) {
    if (!confirm('Release this IP from jail?')) return
    try {
      await api.delete(`/jail/${id}`)
      setJailed(prev => prev.filter(r => r.id !== id))
    } catch (ex) { alert(ex.response?.data?.error || ex.message) }
  }

  async function releaseAll() {
    if (!confirm(`Release all ${jailed.length} jailed IPs?`)) return
    try {
      await api.delete('/jail/all')
      setJailed([])
    } catch (ex) { alert(ex.response?.data?.error || ex.message) }
  }

  async function jailCounter(ip) {
    try {
      await api.post('/jail', { ip_address: ip, reason: 'Threshold exceeded', duration_hours: settings.duration_hours })
      await load()
    } catch (ex) { alert(ex.response?.data?.error || ex.message) }
  }

  async function removeWhitelist(id) {
    if (!confirm('Remove this IP from the whitelist?')) return
    try {
      await api.delete(`/jail/whitelist/${id}`)
      setWhitelist(prev => prev.filter(r => r.id !== id))
    } catch (ex) { alert(ex.response?.data?.error || ex.message) }
  }

  const jailTotal = jailed.length
  const jailSlice = jailed.slice((jailPage - 1) * jailPageSize, jailPage * jailPageSize)

  return (
    <div className="space-y-5 animate-fade-in">

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-rose-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-rose-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <path d="M12 8v4m0 4h.01" strokeLinecap="round"/>
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800">IP Jail</h1>
            <p className="text-sm text-slate-500">
              Auto-block IPs after repeated WAF attacks
              {jailTotal > 0 && <> · currently <strong className="text-rose-600">{jailTotal}</strong> jailed</>}
            </p>
          </div>
        </div>
        <button onClick={load}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="flex gap-1 border-b border-slate-200">
        <button type="button" onClick={() => setActiveTab('jailed')}
          className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors ${activeTab === 'jailed' ? 'border-rose-500 text-rose-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Jailed IPs
          {jailTotal > 0 && <span className="px-1.5 py-0.5 bg-rose-100 text-rose-600 text-xs font-bold rounded-full">{jailTotal}</span>}
        </button>
        <button type="button" onClick={() => setActiveTab('whitelist')}
          className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors ${activeTab === 'whitelist' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
          <ShieldCheck className="w-4 h-4" />
          Whitelist
          {whitelist.length > 0 && <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full">{whitelist.length}</span>}
        </button>
      </div>

      {activeTab === 'jailed' && <>
      <div className="card p-5">
        <p className="text-xs font-semibold text-indigo-600 flex items-center gap-1.5 mb-4">
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          Jail Settings
        </p>
        <form onSubmit={saveSettings} className="flex flex-wrap items-end gap-6">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-slate-500">Auto-Jail</span>
            <button type="button" onClick={() => setEnabled(v => !v)}
              className={`relative inline-flex items-center w-12 h-6 rounded-full transition-colors
                ${enabled ? 'bg-indigo-500' : 'bg-slate-300'}`}>
              <span className={`absolute w-5 h-5 bg-white rounded-full shadow transition-transform
                ${enabled ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
            <span className={`text-xs font-medium ${enabled ? 'text-indigo-600' : 'text-slate-400'}`}>
              {enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-slate-500">Attack threshold</span>
            <div className="flex items-center gap-2">
              <input type="number" min="1" value={threshold} onChange={e => setThreshold(e.target.value)}
                className="w-20 border border-slate-200 rounded-lg px-3 py-2 text-sm text-center
                           focus:outline-none focus:ring-2 focus:ring-indigo-300" />
              <span className="text-sm text-slate-400">attacks before jail</span>
            </div>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-slate-500">Jail duration</span>
            <SelectBox value={durHours} onChange={setDurHours} options={DURATION_OPTIONS} />
          </div>
          <button type="submit" disabled={saving}
            className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold
                       hover:bg-indigo-700 disabled:opacity-50 transition-colors">
            {saving ? 'Saving…' : 'Save'}
          </button>
        </form>
      </div>

      <div className="card overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
          <p className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <BarChart2 className="w-4 h-4 text-orange-400" />
            Attack Counters
            <span className="text-xs font-normal text-slate-400 ml-1">— IPs accumulating attacks (not yet jailed)</span>
          </p>
          {counters.length > 0 && (
            <span className="px-2 py-0.5 bg-orange-500 text-white text-xs font-bold rounded-full">
              {counters.length}
            </span>
          )}
        </div>
        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Loading…</div>
        ) : counters.length === 0 ? (
          <div className="p-10 text-center text-slate-400 text-sm">No active attack counters</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">IP Address</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Country</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Domain</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Progress</th>
                <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-400 uppercase tracking-wide">Count</th>
                <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-400 uppercase tracking-wide">%</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {counters.map(row => {
                const pct      = Math.min(100, Math.round((row.count / row.threshold) * 100))
                const barColor = pct >= 100 ? 'bg-red-500' : pct >= 75 ? 'bg-orange-400' : 'bg-yellow-400'
                const pctColor = pct >= 75 ? 'text-orange-500 font-bold' : 'text-yellow-600 font-bold'
                return (
                  <tr key={row.ip} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-2.5 font-mono text-xs font-medium text-slate-800">{row.ip}</td>
                    <td className="px-4 py-2.5 text-xs text-slate-600 whitespace-nowrap">
                      {row.country_code
                        ? <>{flag(row.country_code)} <span className="font-semibold">{row.country_code}</span> {row.country_name}</>
                        : '—'}
                    </td>
                    <td className="px-4 py-2.5 text-xs max-w-[180px]">
                      {row.hosts?.length
                        ? <span title={row.hosts.join(', ')}
                            className="inline-block px-2 py-0.5 bg-slate-100 text-slate-600 rounded
                                       border border-slate-200 truncate max-w-[160px] font-mono text-[11px]">
                            {row.hosts[0]}{row.hosts.length > 1 ? ` +${row.hosts.length - 1}` : ''}
                          </span>
                        : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-4 py-2.5 min-w-[200px]">
                      <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs text-slate-600 whitespace-nowrap">
                      {row.count}/{row.threshold}
                    </td>
                    <td className={`px-4 py-2.5 text-right font-mono text-xs ${pctColor}`}>{pct}%</td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => jailCounter(row.ip)}
                        className="px-2.5 py-1 text-xs font-semibold bg-rose-100 text-rose-700
                                   rounded-lg hover:bg-rose-200 transition-colors whitespace-nowrap">
                        Jail Now
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="card overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
          <p className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <svg className="w-4 h-4 text-rose-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            Jailed IPs
            {jailTotal > 0 && (
              <span className="px-2 py-0.5 bg-rose-100 text-rose-600 text-xs font-bold rounded-full">
                {jailTotal}
              </span>
            )}
          </p>
          <div className="flex items-center gap-2">
            {jailTotal > 0 && (
              <button onClick={releaseAll}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600
                           border border-rose-200 hover:bg-rose-50 rounded-lg transition-colors">
                <Trash2 className="w-3.5 h-3.5" /> Release All
              </button>
            )}
            <button onClick={() => setShowModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white
                         bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors">
              <PlusCircle className="w-3.5 h-3.5" /> Manual Jail
            </button>
          </div>
        </div>

        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Loading…</div>
        ) : jailTotal === 0 ? (
          <div className="p-10 text-center text-slate-400 text-sm">No IPs currently jailed</div>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">IP Address</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Country</th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-400 uppercase tracking-wide">Attacks</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Domains</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Reason</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Type</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Jailed At</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide whitespace-nowrap">Time Remaining</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {jailSlice.map(row => (
                  <tr key={row.id} className={`hover:bg-slate-50 transition-colors ${row.is_expired ? 'opacity-50' : ''}`}>
                    <td className="px-4 py-2.5 font-mono text-xs font-semibold text-rose-600">{row.ip_address}</td>
                    <td className="px-4 py-2.5 text-xs text-slate-600 whitespace-nowrap">
                      {row.country_code
                        ? <>{flag(row.country_code)} <span className="font-semibold">{row.country_code}</span> {row.country_name}</>
                        : '—'}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs font-bold text-orange-500">
                      {(row.attack_count ?? 0).toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5 text-xs max-w-[220px]">
                      {row.domains?.length
                        ? <span title={row.domains.join(', ')}
                            className="inline-block px-2 py-0.5 bg-slate-100 text-slate-600 rounded
                                       border border-slate-200 truncate max-w-[200px] font-mono text-[11px]">
                            {row.domains[0]}{row.domains.length > 1 ? ` +${row.domains.length - 1}` : ''}
                          </span>
                        : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-slate-500 max-w-[160px] truncate">{row.reason || '—'}</td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold
                        ${row.auto_jailed ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-100 text-indigo-700'}`}>
                        {row.auto_jailed ? 'Auto' : 'Manual'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-xs text-slate-500 whitespace-nowrap">{fmtDate(row.jailed_at)}</td>
                    <td className="px-4 py-2.5 text-xs font-semibold whitespace-nowrap">
                      {row.is_expired
                        ? <span className="text-slate-400">Expired</span>
                        : <span className={row.expires_in != null && row.expires_in < 3600 ? 'text-rose-500' : 'text-emerald-600'}>
                            {fmtRemaining(row.expires_in)}
                          </span>
                      }
                    </td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => releaseOne(row.id)}
                        className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-emerald-700
                                   border border-emerald-300 rounded-lg hover:bg-emerald-50 transition-colors">
                        ✓ Release
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <PaginationBar
              total={jailTotal}
              page={jailPage}
              pageSize={jailPageSize}
              onPage={setJailPage}
              onPageSize={setJailPageSize}
            />
          </>
        )}
      </div>
      </>}

      {activeTab === 'whitelist' && <>
      <div className="card overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
          <p className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            Whitelisted IPs
            <span className="text-xs font-normal text-slate-400 ml-1">— bypass jail · never blocked</span>
            {whitelist.length > 0 && (
              <span className="px-2 py-0.5 bg-emerald-500 text-white text-xs font-bold rounded-full">
                {whitelist.length}
              </span>
            )}
          </p>
          <button onClick={() => setShowWlModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors">
            <PlusCircle className="w-3.5 h-3.5" /> Add IP
          </button>
        </div>
        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Loading…</div>
        ) : whitelist.length === 0 ? (
          <div className="p-10 text-center text-slate-400 text-sm">No IPs whitelisted · add an IP above to bypass the jail</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">IP Address</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Note</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">Added At</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {whitelist.map(row => (
                <tr key={row.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2.5 font-mono text-xs font-semibold text-emerald-700">{row.ip_address}</td>
                  <td className="px-4 py-2.5 text-xs text-slate-500">{row.note || '—'}</td>
                  <td className="px-4 py-2.5 text-xs text-slate-500 whitespace-nowrap">{fmtDate(row.created_at)}</td>
                  <td className="px-4 py-2.5">
                    <button onClick={() => removeWhitelist(row.id)}
                      className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-rose-600 border border-rose-200 rounded-lg hover:bg-rose-50 transition-colors">
                      <Trash2 className="w-3.5 h-3.5" /> Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      </>}

      {showModal && (
        <ManualJailModal
          settings={settings}
          onClose={() => setShowModal(false)}
          onDone={async () => { setShowModal(false); await load() }}
        />
      )}
      {showWlModal && (
        <AddWhitelistModal
          onClose={() => setShowWlModal(false)}
          onDone={async () => { setShowWlModal(false); await load() }}
        />
      )}
    </div>
  )
}
