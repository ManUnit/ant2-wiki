'use strict';
const http = require('http');

function req(opts, body) {
  return new Promise((resolve, reject) => {
    const r = http.request(opts, res => {
      let b = '';
      res.on('data', c => { b += c; });
      res.on('end', () => resolve({ s: res.statusCode, b }));
    });
    r.on('error', reject);
    if (body) r.write(body);
    r.end();
  });
}

async function main() {
  const l = await req(
    { hostname: 'localhost', port: 4000, path: '/api/auth/login', method: 'POST', headers: { 'Content-Type': 'application/json' } },
    JSON.stringify({ username: 'admin', password: 'Admin@12345' })
  );
  const tok = JSON.parse(l.b).token;
  if (!tok) { console.log('login fail', l.b.slice(0, 200)); return; }

  const c = await req(
    { hostname: 'localhost', port: 4000, path: '/api/jail/counters', method: 'GET', headers: { Authorization: 'Bearer ' + tok } }
  );
  const d = JSON.parse(c.b);
  if (!Array.isArray(d)) { console.log('not array:', c.b.slice(0, 200)); return; }

  const f = d.filter(x => x.hosts && x.hosts.length > 0);
  console.log('Total:' + d.length + ' with_domain:' + f.length + ' no_domain:' + (d.length - f.length));
  f.slice(0, 8).forEach(x => console.log('  ' + x.ip + ' cnt=' + x.count + ' ' + JSON.stringify(x.hosts)));
}
main().catch(e => console.error(e));
