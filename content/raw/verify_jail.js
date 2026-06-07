'use strict';
const http = require('http');
setTimeout(() => {
  http.get('http://localhost:4000/api/jail/counters', (r) => {
    let b = '';
    r.on('data', c => { b += c; });
    r.on('end', () => {
      const d = JSON.parse(b);
      const f = d.filter(x => x.hosts && x.hosts.length > 0);
      console.log('Total:', d.length, 'with_domain:', f.length);
      f.slice(0, 8).forEach(x => console.log(' ', x.ip, 'cnt=' + x.count, 'hosts=' + JSON.stringify(x.hosts)));
      const none = d.filter(x => !x.hosts || x.hosts.length === 0);
      console.log('No domain (old/purged events):', none.length);
    });
  }).on('error', e => console.error(e));
}, 3000);
