with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'r') as f:
    lines = f.readlines()

# Find the standalone Traffic trend section to delete
# Start: line containing "Traffic trend chart" comment (not inside the new grid)
# End: the closing </div> followed by blank line before Per-host detail

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'Traffic trend chart' in line and start_idx is None:
        # The one inside the grid has indentation of 8 spaces (inside grid div)
        # The standalone one has 6 spaces indentation
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent == 6:  # standalone (outer level)
            start_idx = i
        # If indent is 8, it's inside the grid — skip

# Find the end: next </div> at 6-space indent after start, then blank line
if start_idx is not None:
    for i in range(start_idx + 1, len(lines)):
        stripped = lines[i].lstrip()
        indent = len(lines[i]) - len(stripped)
        if stripped.startswith('</div>') and indent == 6:
            # Check next line is blank
            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                end_idx = i + 2  # include the blank line after
                break

print(f'start_idx={start_idx}  end_idx={end_idx}')
if start_idx is None or end_idx is None:
    print('MISS — could not locate standalone traffic section')
    exit(1)

print('Removing lines:')
for l in lines[start_idx:end_idx]:
    print(repr(l[:80]))

# Remove lines start_idx..end_idx-1
new_lines = lines[:start_idx] + lines[end_idx:]

with open('/opt/ant2-proxy/web/src/pages/Monitor.jsx', 'w') as f:
    f.writelines(new_lines)

print('OK: standalone Traffic Trend section removed')
