'use strict';
const db = require('./src/database').getDb();
const total = db.prepare('SELECT COUNT(*) as c FROM ip_jail').get().c;
const withDom = db.prepare("SELECT COUNT(*) as c FROM ip_jail WHERE domains IS NOT NULL AND domains != '[]' AND domains != ''").get().c;
console.log(`total_jailed:${total} with_domain:${withDom} pct:${(withDom/total*100).toFixed(0)}%`);
console.log(`no_domain:${total - withDom} (events older than all log retention)`);
const s = db.prepare("SELECT ip_address, domains FROM ip_jail ORDER BY jailed_at DESC LIMIT 8").all();
s.forEach(r => console.log('  ' + r.ip_address + ' ' + r.domains));
