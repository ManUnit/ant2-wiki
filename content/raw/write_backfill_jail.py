"""Backfill ip_jail.domains for existing rows from waf_events + Redis"""
import subprocess, json

script = r"""
'use strict';
const db = require('./src/database').getDb();
const redis = require('./src/services/redis').getRedis();

async function run() {
  // Ensure column exists (migration may not have run yet in this process)
  try { db.exec('ALTER TABLE ip_jail ADD COLUMN domains TEXT NOT NULL DEFAULT "[]"'); } catch {}

  const rows = db.prepare('SELECT ip_address, domains FROM ip_jail').all();
  const sevenDaysAgo = Math.floor(Date.now() / 1000) - 7 * 24 * 3600;
  let updated = 0;

  for (const row of rows) {
    // Skip if already has domains
    try { if (JSON.parse(row.domains || '[]').length > 0) continue; } catch {}

    const domSet = new Set();

    // Try waf_events
    const attacked = db.prepare(`
      SELECT DISTINCT h.domain, we.host_id
      FROM waf_events we
      LEFT JOIN hosts h ON h.id = we.host_id
      WHERE we.client_ip = ? AND we.ts >= ?
    `).all(row.ip_address, sevenDaysAgo);
    for (const r of attacked) domSet.add(r.domain || `host_${r.host_id}`);

    // Try Redis jail:dom
    try {
      const doms = await redis.smembers(`jail:dom:${row.ip_address}`);
      for (const d of (doms || [])) domSet.add(d);
    } catch {}

    if (domSet.size > 0) {
      db.prepare('UPDATE ip_jail SET domains = ? WHERE ip_address = ?')
        .run(JSON.stringify([...domSet]), row.ip_address);
      updated++;
      console.log(`  backfilled ${row.ip_address}: ${[...domSet].join(', ')}`);
    }
  }
  console.log(`Backfill done: ${updated}/${rows.length} rows updated`);
  process.exit(0);
}
run().catch(e => { console.error(e); process.exit(1); });
"""
with open('/tmp/backfill_jail_domains.js', 'w') as f:
    f.write(script)
print('Written /tmp/backfill_jail_domains.js')
