with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

old = """      {/* ── Redis cache panel ────────────────────────────────────────── */}
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
      </div>"""

new = """      {/* ── Redis cache panel ────────────────────────────────────────── */}
      <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 p-4 shadow-lg">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-rose-400" />
            Redis Cache
            <span className="text-slate-600 font-normal normal-case tracking-normal text-xs">· ioredis 7-alpine</span>
          </p>
          {rd.connected === true  && <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-emerald-900/60 text-emerald-400 border border-emerald-700">CONNECTED</span>}
          {rd.connected === false && <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-rose-900/60 text-rose-400 border border-rose-700">OFFLINE</span>}
          {rd.connected == null   && <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-700/60 text-slate-400 border border-slate-600">—</span>}
        </div>

        {rd.connected === false ? (
          <div className="h-16 flex items-center justify-center text-slate-500 text-sm">Redis offline or unreachable</div>
        ) : (
          <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">

            {/* Memory */}
            <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
              <p className="text-xs font-semibold text-slate-400 mb-1">Mem Used</p>
              <p className={`text-2xl font-bold tabular-nums ${(rd.usedMemoryPct ?? 0) >= 85 ? 'text-rose-400' : (rd.usedMemoryPct ?? 0) >= 60 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {rd.usedMemoryPct != null ? `${rd.usedMemoryPct}%` : '—'}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">{rd.usedMemoryHuman || '—'} / {rd.maxMemoryBytes ? `${Math.round(rd.maxMemoryBytes/1048576)}MB` : '128MB'}</p>
              {/* thin bar */}
              <div className="mt-1.5 h-1 rounded-full bg-slate-600 overflow-hidden">
                <div className={`h-full rounded-full ${(rd.usedMemoryPct ?? 0) >= 85 ? 'bg-rose-500' : (rd.usedMemoryPct ?? 0) >= 60 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                  style={{ width: `${Math.min(rd.usedMemoryPct ?? 0, 100)}%` }} />
              </div>
            </div>

            {/* Hit Rate */}
            <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
              <p className="text-xs font-semibold text-slate-400 mb-1">Hit Rate</p>
              <p className={`text-2xl font-bold tabular-nums ${rd.hitRate == null ? 'text-slate-500' : rd.hitRate >= 80 ? 'text-emerald-400' : rd.hitRate >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                {rd.hitRate != null ? `${rd.hitRate}%` : '—'}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">{(rd.hits ?? 0).toLocaleString()} hits · {(rd.misses ?? 0).toLocaleString()} miss</p>
              <div className="mt-1.5 h-1 rounded-full bg-slate-600 overflow-hidden">
                <div className={`h-full rounded-full ${rd.hitRate == null ? 'bg-slate-500' : rd.hitRate >= 80 ? 'bg-emerald-500' : rd.hitRate >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                  style={{ width: `${Math.min(rd.hitRate ?? 0, 100)}%` }} />
              </div>
            </div>

            {/* Keys + Ops */}
            <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
              <p className="text-xs font-semibold text-slate-400 mb-1">Keys</p>
              <p className="text-2xl font-bold text-white tabular-nums">{(rd.keys ?? '—').toLocaleString?.() ?? rd.keys ?? '—'}</p>
              <p className="text-xs text-slate-500 mt-0.5">{rd.expires ?? 0} with TTL</p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-slate-500">Ops/sec</span>
                <span className="text-sm font-bold text-white tabular-nums">{rd.opsPerSec ?? '—'}</span>
                <span className="text-xs text-slate-600">· {rd.connectedClients ?? 0} clients</span>
              </div>
            </div>

            {/* Version + Uptime */}
            <div className="rounded-xl bg-slate-700/50 px-3 py-2.5">
              <p className="text-xs font-semibold text-slate-400 mb-1">Uptime</p>
              <p className="text-2xl font-bold text-slate-200 tabular-nums">{rd.uptimeSec != null ? fmtUptime(rd.uptimeSec) : '—'}</p>
              <p className="text-xs text-slate-500 mt-0.5">allkeys-lru policy</p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-slate-500">Version</span>
                <span className="text-sm font-bold text-cyan-400">{rd.version ? `v${rd.version}` : '—'}</span>
                <span className="text-xs text-slate-600">· 128 MB cap</span>
              </div>
            </div>

          </div>
        )}
      </div>"""

if old in src:
    src = src.replace(old, new, 1)
    print('+ Redis panel redesigned: compact cards + bigger fonts + progress bars')
else:
    print('MISS')

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)
print('Done.')
