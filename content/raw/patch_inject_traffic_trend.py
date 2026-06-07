with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

# ── 1. Change grid to 5 cols ─────────────────────────────────────────────────
OLD_GRID = 'className="grid grid-cols-1 xl:grid-cols-3 gap-4">'
NEW_GRID = 'className="grid grid-cols-1 xl:grid-cols-5 gap-4">'
assert OLD_GRID in src, 'MISS: grid-cols-3'
src = src.replace(OLD_GRID, NEW_GRID, 1)

# ── 2. Inject Traffic Trend before grid closing tag ──────────────────────────
# The grid closing sequence (unique - ends before Nginx stub_status)
OLD_CLOSE = "        </div>\n      </div>\n\n      {/* \u2500\u2500 Nginx stub_status cards"
NEW_CLOSE = """        </div>

        {/* Traffic Trend inside the 5-col grid */}
        <div className="card p-4 xl:col-span-2">
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 mb-2">
            Traffic Trend <span className="text-slate-300 ml-1 font-normal normal-case tracking-normal">\u00b7 last 3 min</span>
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

if OLD_CLOSE in src:
    src = src.replace(OLD_CLOSE, NEW_CLOSE, 1)
    print('OK: injected Traffic Trend into 5-col grid')
else:
    # fallback: try with different box-drawing chars (utf-8 decoded)
    print('MISS close — dumping context:')
    idx = src.find('Nginx stub_status cards')
    print(repr(src[idx-120:idx+50]))
    exit(1)

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('Done. Grid: System Health (1) | Ant2 Connections (2) | Traffic Trend (2)')
