'use strict';
const db = require('./src/database').getDb();
const r = db.prepare('SELECT COUNT(*) as c FROM waf_ip_summary').get();
console.log('waf_ip_summary rows:', r.c);
const sample = db.prepare('SELECT s.client_ip, h.domain FROM waf_ip_summary s LEFT JOIN hosts h ON h.id = s.host_id LIMIT 5').all();
console.log('sample:', JSON.stringify(sample));
