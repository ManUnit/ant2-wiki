with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

# ── Add redis to the destructured state from latest ──────────────────
old_ng = "  const ng    = latest?.nginx   || {}"
new_ng = "  const ng    = latest?.nginx   || {}\n  const rd    = latest?.redis   || {}"
if "const rd    = latest" not in src:
    src = src.replace(old_ng, new_ng)

# ── Redis panel JSX to insert before per-host detail panel ───────────
redis_panel = r"""
      {/* ── Redis cache panel ────────────────────────────────────────── */}
      <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 p-4 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-rose-400" />
            Redis Cache
            <span className="text-slate-600 font-normal normal-case tracking-normal">· ioredis 7-alpine</span>
          </p>
          {rd.connected === true  && <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-900/60 text-emerald-400 border border-emerald-700">CONNECTED</span>}
          {rd.connected === false && <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-rose-900/60 text-rose-400 border border-rose-700">OFFLINE</span>}
          {rd.connected == null   && <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-700/60 text-slate-400 border border-slate-600">—</span>}
        </div>

        {rd.connected === false ? (
          <div className="h-20 flex items-center justify-center text-slate-500 text-sm">Redis offline or unreachable</div>
        ) : (
          <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">

            {/* Memory gauge */}
            <div className="flex flex-col items-center">
              <Gauge
                pct={rd.usedMemoryPct ?? 0}
                color={rd.usedMemoryPct >= 85 ? '#ef4444' : rd.usedMemoryPct >= 60 ? '#f59e0b' : '#10b981'}
                value={rd.usedMemoryPct != null ? `${rd.usedMemoryPct}%` : '—'}
                label="Mem Used"
              />
              <p className="text-center text-[11px] text-slate-500 mt-1">
                {rd.usedMemoryHuman || '—'} / {rd.maxMemoryBytes ? `${Math.round(rd.maxMemoryBytes / 1048576)}MB` : '—'}
              </p>
            </div>

            {/* Hit rate gauge */}
            <div className="flex flex-col items-center">
              <Gauge
                pct={rd.hitRate ?? 0}
                color={rd.hitRate == null ? '#475569' : rd.hitRate >= 80 ? '#10b981' : rd.hitRate >= 50 ? '#f59e0b' : '#ef4444'}
                value={rd.hitRate != null ? `${rd.hitRate}%` : '—'}
                label="Hit Rate"
              />
              <p className="text-center text-[11px] text-slate-500 mt-1">
                {rd.hits ?? 0} hits · {rd.misses ?? 0} miss
              </p>
            </div>

            {/* Keys + Ops stats */}
            <div className="flex flex-col justify-center gap-3 col-span-2 xl:col-span-2">
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
                  <p className="text-[9px] uppercase tracking-widest text-slate-500 font-bold mb-0.5">Keys</p>
                  <p className="text-xl font-bold text-white tabular-nums">{rd.keys ?? '—'}</p>
                  <p className="text-[10px] text-slate-500">{rd.expires ?? 0} with TTL</p>
                </div>
                <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
                  <p className="text-[9px] uppercase tracking-widest text-slate-500 font-bold mb-0.5">Ops/sec</p>
                  <p className="text-xl font-bold text-white tabular-nums">{rd.opsPerSec ?? '—'}</p>
                  <p className="text-[10px] text-slate-500">{rd.connectedClients ?? 0} clients</p>
                </div>
                <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
                  <p className="text-[9px] uppercase tracking-widest text-slate-500 font-bold mb-0.5">Version</p>
                  <p className="text-sm font-bold text-cyan-400 tabular-nums">{rd.version ? `v${rd.version}` : '—'}</p>
                  <p className="text-[10px] text-slate-500">LRU · 128 MB cap</p>
                </div>
                <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
                  <p className="text-[9px] uppercase tracking-widest text-slate-500 font-bold mb-0.5">Uptime</p>
                  <p className="text-sm font-bold text-slate-200 tabular-nums">{rd.uptimeSec != null ? fmtUptime(rd.uptimeSec) : '—'}</p>
                  <p className="text-[10px] text-slate-500">allkeys-lru policy</p>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>

"""

# Insert before per-host detail panel
marker = "      {/* ── Per-host detail panel"
if "Redis cache panel" not in src:
    src = src.replace(marker, redis_panel + marker)

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('DONE — redis panel:', src.count('Redis cache panel'), 'rd.connected:', src.count('rd.connected'))
