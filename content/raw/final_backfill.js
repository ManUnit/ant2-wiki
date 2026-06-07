'use strict';
// Backfill ip_jail.domains from waf_ip_summary for remaining IPs
const db = require('./src/database').getDb();

const missing = db.prepare(
  "SELECT ip_address FROM ip_jail WHERE domains IS NULL OR domains='[]' OR domains=''"
).all().map(r => r.ip_address);

console.log('Still missing domain:', missing.length);

let updated = 0;
for (const ip of missing) {
  const rows = db.prepare(`
    SELECT DISTINCT h.domain
    FROM waf_ip_summary s
    LEFT JOIN hosts h ON h.id = s.host_id
    WHERE s.client_ip = ? AND h.domain IS NOT NULL
  `).all(ip);
  if (rows.length) {
    const doms = rows.map(r => r.domain);
    db.prepare('UPDATE ip_jail SET domains=? WHERE ip_address=?')
      .run(JSON.stringify(doms), ip);
    console.log(`  ${ip} → ${doms.join(', ')}`);
    updated++;
  }
}

const total = db.prepare('SELECT COUNT(*) as c FROM ip_jail').get().c;
const withDom = db.prepare("SELECT COUNT(*) as c FROM ip_jail WHERE domains IS NOT NULL AND domains!='[]' AND domains!=''").get().c;
console.log(`\nBackfill: ${updated} updated`);
console.log(`Final: ${withDom}/${total} jailed IPs have domain (${(withDom/total*100).toFixed(0)}%)`);
