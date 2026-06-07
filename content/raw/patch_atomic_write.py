import os
import re

# ── Patch nginxConfig.js ──────────────────────────────────────────
with open('/opt/ant2-proxy/api/src/services/nginxConfig.js', 'r') as f:
    src = f.read()

atomic_helper = '''
/**
 * Atomic write: write to a .tmp file then fs.rename() so NGINX never reads
 * a partially-written config (avoids pread() truncation errors on reload).
 * inotify watcher uses -e moved_to which fires on rename — reload still works.
 */
function atomicWrite(filePath, content, encoding) {
  if (!encoding) encoding = 'utf8';
  var tmp = filePath + '.tmp';
  try {
    fs.writeFileSync(tmp, content, encoding);
    fs.renameSync(tmp, filePath);
  } catch (err) {
    try { fs.unlinkSync(tmp); } catch (_e) {}
    throw err;
  }
}

'''

insert_after = '// no-op: inotify watcher in entrypoint.sh handles reload\n}'
if 'function atomicWrite' not in src:
    src = src.replace(insert_after, insert_after + '\n' + atomic_helper, 1)
    print('  + atomicWrite helper added')
else:
    print('  atomicWrite helper already present')

# Replace nginx .conf writeFileSync calls with atomicWrite
replacements = [
    ("fs.writeFileSync(wafConfPath(host.id), wafConf, 'utf8');",
     "atomicWrite(wafConfPath(host.id), wafConf);"),
    ("fs.writeFileSync(hostConfPath(host.id), nginxConf, 'utf8');",
     "atomicWrite(hostConfPath(host.id), nginxConf);"),
    ("fs.writeFileSync(redirectConfPath(redirect.id), conf, 'utf8');",
     "atomicWrite(redirectConfPath(redirect.id), conf);"),
    ("fs.writeFileSync(streamConfPath(stream.id), conf, 'utf8');",
     "atomicWrite(streamConfPath(stream.id), conf);"),
]

count = 0
for old, new in replacements:
    if old in src:
        src = src.replace(old, new)
        print('  + replaced: ' + new)
        count += 1
    else:
        print('  MISS: ' + old[:70])

# default site conf writes (2 occurrences)
old_conf = "fs.writeFileSync(confPath, conf, 'utf8');"
new_conf = "atomicWrite(confPath, conf);"
occurrences = src.count(old_conf)
if occurrences > 0:
    src = src.replace(old_conf, new_conf)
    print('  + replaced ' + str(occurrences) + 'x: atomicWrite(confPath, conf)')
    count += occurrences

with open('/opt/ant2-proxy/api/src/services/nginxConfig.js', 'w') as f:
    f.write(src)

print('nginxConfig.js: ' + str(count) + ' writes patched to atomic')

# ── Patch settings.js (nginx-ant2-custom.conf write) ─────────────
for settings_path in [
    '/opt/ant2-proxy/api/src/services/settings.js',
    '/opt/ant2-proxy/api/src/routes/settings.js',
]:
    if not os.path.exists(settings_path):
        continue
    with open(settings_path, 'r') as f:
        s = f.read()

    old_s = "fs.writeFileSync(p, content, 'utf8');"
    if old_s in s:
        idx = s.index(old_s)
        context = s[max(0, idx - 300):idx + len(old_s) + 100]
        if 'nginx-ant2-custom' in context or 'custom' in context.lower():
            # Add atomicWrite helper near top of file if not present
            if 'function atomicWrite' not in s:
                insert = (
                    "\nfunction atomicWrite(filePath, content, encoding) {\n"
                    "  if (!encoding) encoding = 'utf8';\n"
                    "  var tmp = filePath + '.tmp';\n"
                    "  try { fs.writeFileSync(tmp, content, encoding); fs.renameSync(tmp, filePath); }\n"
                    "  catch (err) { try { fs.unlinkSync(tmp); } catch (_e) {} throw err; }\n"
                    "}\n"
                )
                s = s.replace("'use strict';", "'use strict';" + insert, 1)
            s = s.replace(old_s, "atomicWrite(p, content);", 1)
            with open(settings_path, 'w') as f:
                f.write(s)
            print(os.path.basename(settings_path) + ': custom.conf write patched to atomic')
        else:
            print(os.path.basename(settings_path) + ': writeFileSync(p) context unclear - skip')

print('Done.')
