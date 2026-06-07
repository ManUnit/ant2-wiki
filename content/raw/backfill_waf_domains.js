'use strict';
// Backfill jail:dom:<ip> by scanning WAF logs (ModSecurity transaction JSON)
// WAF log files are named by domain: /data/logs/waf/<domain>.log
const { getRedis } = require('./src/services/redis');
const { getDb }    = require('./src/database');
const fs   = require('fs');
const path = require('path');

const LOG_DIR    = process.env.NGINX_LOG_DIR || '/data/logs';
const WAF_DIR    = path.join(LOG_DIR, 'waf');
const TAIL_BYTES = 8 * 1024 * 1024; // 8 MB per WAF log

async function main() {
  const redis = getRedis();
  await new Promise(res => setTimeout(res, 800));

  const keys = await redis.keys('jail:cnt:*');
  if (!keys.length) { console.log('No jail:cnt keys'); redis.disconnect(); return; }

  const targetIps = new Set(keys.map(k => k.replace('jail:cnt:', '')));
  const ipDomains = {};

  // Scan WAF log files (named by domain)
  let wafFiles = [];
  try { wafFiles = fs.readdirSync(WAF_DIR).filter(f => f.endsWith('.log') && f !== 'modsec-debug.log'); } catch {}
  console.log(`Scanning ${wafFiles.length} WAF log files in ${WAF_DIR}...`);

  for (const file of wafFiles) {
    const domain   = file.replace(/\.log$/, '');
    const filePath = path.join(WAF_DIR, file);

    let lines = [];
    try {
      const stat  = fs.statSync(filePath);
      const start = Math.max(0, stat.size - TAIL_BYTES);
      const len   = stat.size - start;
      if (len <= 0) continue;
      const buf = Buffer.alloc(len);
      const fd  = fs.openSync(filePath, 'r');
      fs.readSync(fd, buf, 0, len, start);
      fs.closeSync(fd);
      lines = buf.toString('utf8').split('\n').filter(Boolean);
    } catch { continue; }

    let matched = 0;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        const ip    = entry?.transaction?.client_ip;
        if (!ip || !targetIps.has(ip)) continue;
        if (!ipDomains[ip]) ipDomains[ip] = new Set();
        ipDomains[ip].add(domain);
        matched++;
      } catch { /* skip */ }
    }
    if (matched > 0) console.log(`  ${domain}: matched ${matched} events`);
  }

  // Also scan access logs as secondary source (status=403)
  const db       = getDb();
  const hosts    = db.prepare('SELECT id, domain FROM hosts').all();
  const hostMap  = {};
  for (const h of hosts) hostMap[h.id] = h.domain;

  const accessFiles = fs.readdirSync(LOG_DIR).filter(f => f.match(/^host_\d+_access\.log$/));
  for (const file of accessFiles) {
    const hostIdStr = file.match(/host_(\d+)_access/)?.[1];
    const domain    = hostIdStr ? hostMap[parseInt(hostIdStr)] : null;
    const filePath  = path.join(LOG_DIR, file);
    let lines = [];
    try {
      const stat  = fs.statSync(filePath);
      const start = Math.max(0, stat.size - TAIL_BYTES);
      const len   = stat.size - start;
      if (len <= 0) continue;
      const buf = Buffer.alloc(len);
      const fd  = fs.openSync(filePath, 'r');
      fs.readSync(fd, buf, 0, len, start);
      fs.closeSync(fd);
      lines = buf.toString('utf8').split('\n').filter(Boolean);
    } catch { continue; }

    for (const line of lines) {
      try {
        const e  = JSON.parse(line);
        const ip = e.client_ip || e.remote_addr;
        if (!ip || !targetIps.has(ip)) continue;
        const status = parseInt(e.status || '0', 10);
        if (status !== 403) continue;
        if (!ipDomains[ip]) ipDomains[ip] = new Set();
        if (domain) ipDomains[ip].add(domain);
        else if (hostIdStr) ipDomains[ip].add(`host_${hostIdStr}`);
      } catch {}
    }
  }

  // Write to Redis
  let filled = 0;
  for (const [ip, doms] of Object.entries(ipDomains)) {
    if (!doms.size) continue;
    const domKey = `jail:dom:${ip}`;
    await redis.sadd(domKey, ...[...doms]);
    await redis.expire(domKey, 7 * 24 * 3600);
    filled++;
  }

  console.log(`\nBackfilled jail:dom for ${filled}/${targetIps.size} IPs`);

  // Show sample including some with domains
  const withDomains = Object.entries(ipDomains).filter(([,d]) => d.size > 0).slice(0, 5);
  for (const [ip, doms] of withDomains) {
    const cnt = await redis.get(`jail:cnt:${ip}`);
    console.log(`  ${ip} (cnt=${cnt}) → [${[...doms].join(', ')}]`);
  }
  const noDomains = keys.map(k => k.replace('jail:cnt:', '')).filter(ip => !ipDomains[ip]).slice(0, 3);
  for (const ip of noDomains) {
    const cnt = await redis.get(`jail:cnt:${ip}`);
    console.log(`  ${ip} (cnt=${cnt}) → (no domain found in logs)`);
  }

  redis.disconnect();
  process.exit(0);
}
main().catch(e => { console.error(e); process.exit(1); });
