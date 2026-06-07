with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    src = f.read()

OLD = '''        {/* Traffic Trend inside the 5-col grid */}
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
        </div>'''

NEW = '''        {/* Traffic Trend inside the 5-col grid */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 p-4 shadow-lg xl:col-span-2">
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 mb-2">
            Traffic Trend <span className="text-slate-600 ml-1 font-normal normal-case tracking-normal">\u00b7 last 3 min</span>
          </p>
          {history.length < 2
            ? <div className="h-[130px] flex items-center justify-center text-slate-600 text-sm">
                {connected ? 'Waiting for traffic data\u2026' : 'Disconnected'}
              </div>
            : <ResponsiveContainer width="100%" height={130}>
                <AreaChart data={history} margin={{ top: 4, right: 4, bottom: 0, left: -24 }}>
                  <defs>
                    <linearGradient id="gRq" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#10b981" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                    </linearGradient>
                    <linearGradient id="gE4" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.05} />
                    </linearGradient>
                    <linearGradient id="gE5" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
                  <XAxis dataKey="t" tick={{ fontSize: 9, fill: '#475569' }} stroke="#1e293b" interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 9, fill: '#475569' }} stroke="#1e293b" />
                  <Tooltip contentStyle={DARK_TT} />
                  <Legend iconSize={8} wrapperStyle={{ fontSize: 10, color: '#94a3b8' }} />
                  <Area type="monotone" dataKey="req" stroke="#10b981" fill="url(#gRq)" strokeWidth={2}
                        name="Requests" dot={false} isAnimationActive={false} />
                  <Area type="monotone" dataKey="e4"  stroke="#f59e0b" fill="url(#gE4)" strokeWidth={1.5}
                        name="4xx" dot={false} isAnimationActive={false} />
                  <Area type="monotone" dataKey="e5"  stroke="#ef4444" fill="url(#gE5)" strokeWidth={1.5}
                        name="5xx" dot={false} isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
          }
        </div>'''

assert OLD in src, 'MISS'
src = src.replace(OLD, NEW, 1)

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.write(src)

print('OK: Traffic Trend panel is now dark')
