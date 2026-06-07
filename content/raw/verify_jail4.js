'use strict';
const db = require('./src/database').getDb();
const u = db.prepare('SELECT username, role FROM users WHERE username = ?').get('admin');
console.log('admin_db_user:', JSON.stringify(u));
// Test direct token sign
const jwt = require('jsonwebtoken');
const secret = process.env.JWT_SECRET;
const token = jwt.sign({ id: 1, username: 'admin', role: 'admin' }, secret, { expiresIn: '1h' });
console.log('test_token:', token.slice(0, 40) + '...');

// Use it
const http = require('http');
const req = http.request({
  hostname: 'localhost', port: 4000, path: '/api/jail/counters', method: 'GET',
  headers: { Authorization: 'Bearer ' + token }
}, (res) => {
  let b = '';
  res.on('data', c => { b += c; });
  res.on('end', () => {
    const d = JSON.parse(b);
    if (!Array.isArray(d)) { console.log('not array:', b.slice(0, 200)); return; }
    const f = d.filter(x => x.hosts && x.hosts.length > 0);
    console.log('Total:' + d.length + ' with_domain:' + f.length + ' no_domain:' + (d.length - f.length));
    f.slice(0, 8).forEach(x => console.log('  ' + x.ip + ' cnt=' + x.count + ' ' + JSON.stringify(x.hosts)));
  });
});
req.on('error', e => console.error(e));
req.end();
