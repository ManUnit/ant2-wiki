'use strict';
const { getRedis } = require('./src/services/redis');
const { getDb } = require('./src/database');

async function main() {
  const r = getRedis();
  await new Promise(res => setTimeout(res, 1000));

  // Check jail:cnt keys
  const cntKeys = await r.keys('jail:cnt:*');
  console.log('=== jail:cnt keys:', cntKeys.length);
  if (cntKeys.length > 0) {
    const vals = await r.mget(...cntKeys.slice(0, 5));
    cntKeys.slice(0, 5).forEach((k, i) => console.log('  ', k, '=', vals[i]));
  }

  // Check waf_events table - does it have host_id / domain
  const db = getDb();
  try {
    const cols = db.prepare("PRAGMA table_info(waf_events)").all();
    console.log('\n=== waf_events columns:');
    cols.forEach(c => console.log('  ', c.name, c.type));

    const sample = db.prepare('SELECT * FROM waf_events ORDER BY id DESC LIMIT 3').all();
    console.log('\n=== sample waf_events:');
    sample.forEach(row => console.log(JSON.stringify(row)));
  } catch(e) { console.error('waf_events error:', e.message); }

  r.disconnect();
  process.exit(0);
}
main().catch(e => { console.error(e); process.exit(1); });
