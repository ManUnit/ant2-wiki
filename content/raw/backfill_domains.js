'use strict';
// Backfill jail:dom:<ip> for all existing jail:cnt:* keys from current waf_events
const { getRedis } = require('./src/services/redis');
const { getDb }    = require('./src/database');

async function main() {
  const redis = getRedis();
  await new Promise(res => setTimeout(res, 800));

  const db   = getDb();
  const keys = await redis.keys('jail:cnt:*');
  if (!keys.length) { console.log('No jail:cnt keys found'); redis.disconnect(); return; }

  const ips          = keys.map(k => k.replace('jail:cnt:', ''));
  const placeholders = ips.map(() => '?').join(',');

  const rows = db.prepare(`
    SELECT DISTINCT we.client_ip, h.domain, we.host_id
    FROM   waf_events we
    LEFT JOIN hosts h ON h.id = we.host_id
    WHERE  we.client_ip IN (${placeholders})
  `).all(...ips);

  const ipDomains = {};
  for (const r of rows) {
    if (!ipDomains[r.client_ip]) ipDomains[r.client_ip] = new Set();
    if (r.domain) ipDomains[r.client_ip].add(r.domain);
    else if (r.host_id) ipDomains[r.client_ip].add(`host_${r.host_id}`);
  }

  let filled = 0;
  for (const ip of ips) {
    const doms = ipDomains[ip];
    if (!doms || doms.size === 0) continue;
    const domKey = `jail:dom:${ip}`;
    await redis.sadd(domKey, ...[...doms]);
    await redis.expire(domKey, 7 * 24 * 3600);
    filled++;
  }

  console.log(`Backfilled jail:dom for ${filled}/${ips.length} IPs from waf_events`);

  // Show a few results
  const sample = ips.slice(0, 5);
  for (const ip of sample) {
    const doms = await redis.smembers(`jail:dom:${ip}`);
    console.log(`  ${ip} → [${doms.join(', ') || '(none)'}]`);
  }

  redis.disconnect();
  process.exit(0);
}
main().catch(e => { console.error(e); process.exit(1); });
