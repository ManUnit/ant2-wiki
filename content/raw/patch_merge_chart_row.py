with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

# ── 1. Widen the grid from 3-col to 5-col ────────────────────────────────────
old_grid = 'className="grid grid-cols-1 xl:grid-cols-3 gap-4">'
new_grid = 'className="grid grid-cols-1 xl:grid-cols-5 gap-4">'
assert old_grid in src, 'MISS: grid-cols-3'
src = src.replace(old_grid, new_grid, 1)

# ── 2. Ant2 Connections stays at col-span-2, height 140 → already 140 OK ─────
# (no change needed, xl:col-span-2 already on that div)

# ── 3. Close the grid BEFORE Per-host section was previously after Ant2 div
#       Now we need to inject Traffic Trend chart inside the grid first,
#       then close the grid div.
#
#  Target: the closing </div> of the grid (which comes right after Ant2 block).
#  We find the unique string just after the Ant2 Connections closing tag.

OLD_GRID_CLOSE = """        </div>
      </div>

      {/* \u2500\u2500 Nginx stub_status cards"""

NEW_GRID_CLOSE = """        </div>

        {/* Traffic Trend chart \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */}
        <div className="card p-4 xl:col-span-2">
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 mb-2">
            Traffic Trend <span className="text-slate-300 ml-1 font-normal normal-case tracking-normal">\xb7 last 3 min</span>
          </p>
          {history.length < 2
            ? <div className="h-[130px] flex items-center justify-center text-slate-400 text-sm">
                {connected ? 'Waiting for traffic data\u2026' : 'Disconnected'}
              </div>
            : <ResponsiveContainer width="100%" height={130}>
                <AreaChart data={history} margin={{ top: 4, right: 4, bottom: 0, left: -24 }}>
                  <defs>
                    <linearGradient id="gRq" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#10b981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gE4" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gE5" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="t" tick={{ fontSize: 9 }} stroke="#cbd5e1" interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 9 }} stroke="#cbd5e1" />
                  <Tooltip contentStyle={LIGHT_TT} />
                  <Legend iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                  <Area type="monotone" dataKey="req" stroke="#10b981" fill="url(#gRq)" strokeWidth={2}
                        name="Requests" dot={false} isAnimationActive={false} />
                  <Area type="monotone" dataKey="e4"  stroke="#f59e0b" fill="url(#gE4)" strokeWidth={1.5}
                        name="4xx" dot={false} isAnimationActive={false} />
                  <Area type="monotone" dataKey="e5"  stroke="#ef4444" fill="url(#gE5)" strokeWidth={1.5}
                        name="5xx" dot={false} isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
          }
        </div>
      </div>

      {/* \u2500\u2500 Nginx stub_status cards"""

assert OLD_GRID_CLOSE in src, 'MISS: grid close'
src = src.replace(OLD_GRID_CLOSE, NEW_GRID_CLOSE, 1)

# ── 4. Remove the standalone Traffic Trend section ───────────────────────────
OLD_TRAFFIC = """
      {/* \u2500\u2500 Traffic trend chart \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */}
      <div className="card p-4">
        <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 mb-3">
          Traffic Trend <span className="text-slate-300 ml-1 font-normal normal-case tracking-normal">\xb7 last 3 min</span>
        </p>
        {history.length < 2
          ? <div className="h-[160px] flex items-center justify-center text-slate-400 text-sm">
              {connected ? 'Waiting for traffic data\u2026' : 'Disconnected'}
            </div>
          : <ResponsiveContainer width="100%" height={160}>
              <AreaChart data={history} margin={{ top: 4, right: 4, bottom: 0, left: -24 }}>
                <defs>
                  <linearGradient id="gRq" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gE4" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gE5" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="t" tick={{ fontSize: 9 }} stroke="#cbd5e1" interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 9 }} stroke="#cbd5e1" />
                <Tooltip contentStyle={LIGHT_TT} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                <Area type="monotone" dataKey="req" stroke="#10b981" fill="url(#gRq)" strokeWidth={2}
                      name="Requests" dot={false} isAnimationActive={false} />
                <Area type="monotone" dataKey="e4"  stroke="#f59e0b" fill="url(#gE4)" strokeWidth={1.5}
                      name="4xx" dot={false} isAnimationActive={false} />
                <Area type="monotone" dataKey="e5"  stroke="#ef4444" fill="url(#gE5)" strokeWidth={1.5}
                      name="5xx" dot={false} isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
        }
      </div>

"""

assert OLD_TRAFFIC in src, f'MISS: standalone traffic section'
src = src.replace(OLD_TRAFFIC, '\n', 1)

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('OK: Traffic Trend merged into 5-col grid row with System Health + Ant2 Connections')
