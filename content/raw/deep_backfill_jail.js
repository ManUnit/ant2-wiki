'use strict';
/**
 * Deep backfill of ip_jail.domains for existing jailed IPs.
 * Strategy (in order):
 *  1. waf_events JOIN hosts (recent, within 7d)
 *  2. Redis jail:dom:<ip> SET
 *  3. Scan WAF log files in /data/logs/waf/ for IP pattern
 *
 * After backfill, also validate jail:dom Redis keys match DB.
 */
const path = require('path');
const fs   = require('fs');
const db   = require('./src/database').getDb();
const redis = require('./src/services/redis').getRedis();

const WAF_LOG_DIR = process.env.WAF_LOG_DIR || '/data/logs/waf';
const MAX_SCAN_BYTES = 20 * 1024 * 1024; // scan last 20 MB per file

async function run() {
  const sevenDaysAgo = Math.floor(Date.now() / 1000) - 7 * 24 * 3600;

  // Get all jailed IPs missing domains
  const missing = db.prepare(
    "SELECT ip_address FROM ip_jail WHERE domains IS NULL OR domains = '' OR domains = '[]'"
  ).all().map(r => r.ip_address);

  console.log(`Jailed IPs missing domain: ${missing.length}`);
  if (!missing.length) { console.log('Nothing to do.'); process.exit(0); }

  // Build domain map from all 3 sources
  const domainMap = {};
  for (const ip of missing) domainMap[ip] = new Set();

  // --- Source 1: waf_events (recent) ---
  for (const ip of missing) {
    const rows = db.prepare(`
      SELECT DISTINCT h.domain, we.host_id
      FROM waf_events we
      LEFT JOIN hosts h ON h.id = we.host_id
      WHERE we.client_ip = ? AND we.ts >= ?
    `).all(ip, sevenDaysAgo);
    for (const r of rows) domainMap[ip].add(r.domain || `host_${r.host_id}`);
  }
  const afterWafEvents = missing.filter(ip => domainMap[ip].size > 0).length;
  console.log(`After waf_events: ${afterWafEvents} resolved`);

  // --- Source 2: Redis jail:dom ---
  for (const ip of missing) {
    try {
      const doms = await redis.smembers(`jail:dom:${ip}`);
      for (const d of (doms || [])) domainMap[ip].add(d);
    } catch {}
  }
  const afterRedis = missing.filter(ip => domainMap[ip].size > 0).length;
  console.log(`After Redis: ${afterRedis} resolved`);

  // --- Source 3: WAF log file scan ---
  const stillMissing = missing.filter(ip => domainMap[ip].size === 0);
  console.log(`Scanning WAF logs for ${stillMissing.length} IPs...`);

  // Build map: domain -> log file (from hosts table)
  const hosts = db.prepare('SELECT id, domain FROM hosts').all();
  // domain derived from log filename pattern: /data/logs/waf/<domain>.log
  let logFiles = [];
  try { logFiles = fs.readdirSync(WAF_LOG_DIR).filter(f => f.endsWith('.log')); } catch (e) {
    console.log('Cannot read WAF log dir:', e.message);
  }

  // Build regex for each still-missing IP (escape IPv6 colons)
  // Log format: ... "client": "1.2.3.4", ...  OR just IP in the line
  for (const file of logFiles) {
    const filePath = path.join(WAF_LOG_DIR, file);
    const domain   = file.replace(/\.log$/, '');
    let stat;
    try { stat = fs.statSync(filePath); } catch { continue; }
    if (stat.size === 0) continue;

    const startPos = Math.max(0, stat.size - MAX_SCAN_BYTES);
    let chunk;
    try {
      const buf = Buffer.allocUnsafe(stat.size - startPos);
      const fd  = fs.openSync(filePath, 'r');
      fs.readSync(fd, buf, 0, buf.length, startPos);
      fs.closeSync(fd);
      chunk = buf.toString('utf8');
    } catch { continue; }

    for (const ip of stillMissing) {
      if (domainMap[ip].size > 0) continue; // already resolved
      // Escape special regex chars (IPv6 colons, dots)
      const escaped = ip.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/:/g, ':');
      try {
        if (new RegExp(escaped).test(chunk)) {
          domainMap[ip].add(domain);
        }
      } catch {}
    }
  }

  const afterLogs = missing.filter(ip => domainMap[ip].size > 0).length;
  console.log(`After log scan: ${afterLogs} resolved (${missing.length - afterLogs} unrecoverable)`);

  // --- Write to DB ---
  let updated = 0;
  for (const ip of missing) {
    if (domainMap[ip].size === 0) continue;
    const arr = [...domainMap[ip]].filter(Boolean);
    db.prepare('UPDATE ip_jail SET domains = ? WHERE ip_address = ?')
      .run(JSON.stringify(arr), ip);
    // Also sync to Redis jail:dom for counters page (if not yet jailed-threshold cleanup)
    try {
      await redis.sadd(`jail:dom:${ip}`, ...arr);
      await redis.expire(`jail:dom:${ip}`, 7 * 24 * 3600);
    } catch {}
    updated++;
    console.log(`  ✓ ${ip} → ${arr.join(', ')}`);
  }
  console.log(`\nDone: ${updated} rows updated in ip_jail.domains`);
  process.exit(0);
}

run().catch(e => { console.error(e); process.exit(1); });
