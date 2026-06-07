'use strict';
// Backfill jail:dom:<ip> by scanning access logs (last 512KB per host file)
const { getRedis } = require('./src/services/redis');
const { getDb }    = require('./src/database');
const fs   = require('fs');
const path = require('path');

const LOG_DIR   = process.env.NGINX_LOG_DIR || '/data/logs';
const TAIL_BYTES = 4 * 1024 * 1024; // 4 MB per log

async function main() {
  const redis = getRedis();
  await new Promise(res => setTimeout(res, 800));

  const db   = getDb();
  const keys = await redis.keys('jail:cnt:*');
  if (!keys.length) { console.log('No jail:cnt keys'); redis.disconnect(); return; }

  const targetIps = new Set(keys.map(k => k.replace('jail:cnt:', '')));
  const ipDomains = {};  // ip → Set<domain>

  // Load host id→domain map
  const hosts = db.prepare('SELECT id, domain FROM hosts').all();
  const hostMap = {};
  for (const h of hosts) hostMap[h.id] = h.domain;

  // Scan each host_N_access.log
  const logFiles = fs.readdirSync(LOG_DIR).filter(f => f.match(/^host_\d+_access\.log$/));
  console.log(`Scanning ${logFiles.length} access log files...`);

  for (const file of logFiles) {
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
        const entry = JSON.parse(line);
        const ip    = entry.client_ip || entry.remote_addr;
        if (!ip || !targetIps.has(ip)) continue;
        const status = parseInt(entry.status || '0', 10);
        if (status !== 403) continue; // only count actual WAF blocks
        if (!ipDomains[ip]) ipDomains[ip] = new Set();
        if (domain) ipDomains[ip].add(domain);
        else if (hostIdStr) ipDomains[ip].add(`host_${hostIdStr}`);
      } catch { /* skip malformed */ }
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

  console.log(`Backfilled jail:dom for ${filled}/${targetIps.size} IPs from access logs`);

  // Sample
  const sample = [...targetIps].slice(0, 8);
  for (const ip of sample) {
    const doms = await redis.smembers(`jail:dom:${ip}`);
    const cnt  = await redis.get(`jail:cnt:${ip}`);
    console.log(`  ${ip} (${cnt}) → [${doms.join(', ') || '(none)'}]`);
  }

  redis.disconnect();
  process.exit(0);
}
main().catch(e => { console.error(e); process.exit(1); });
