# Compact Row Table Theme — React + Tailwind

วันที่ทำ: 2026-05-13  
Project: Ant2 Proxy Security Manager v2.4.21  
หน้าที่แก้: WAF Settings (`web/src/pages/WAF.jsx`)  
อ้างอิง: GeoIP.jsx (IP Jail page) เป็น reference pattern

---

## ปัญหาเดิม (ก่อนแก้)

หน้า WAF Settings ใช้ `.card` class ต่อ row ทำให้:
- แต่ละ row มี shadow, rounded-2xl, margin ของตัวเอง
- spacing ระหว่าง row ใหญ่มาก ดูเป็น card stack
- ไม่เหมาะกับ 20+ domain (ต้อง scroll เยอะ)

---

## Container Pattern (Outer Wrapper)

```jsx
{/* sticky toolbar: search + column header */}
<div className="sticky top-0 z-20 bg-white border border-slate-200 rounded-t-xl shadow-sm">
  {/* Search row */}
  <div className="flex items-center gap-3 px-4 py-2 border-b border-slate-100">
    <input className="input pl-9 pr-8 text-sm py-1.5" />
    <span className="text-xs text-slate-400">20 / 20 hosts</span>
  </div>

  {/* Column header row */}
  <div className="flex items-center gap-3 px-4 py-1.5 bg-slate-50">
    <div className="w-4 shrink-0" />  {/* icon spacer */}
    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider w-56 shrink-0">Domain</span>
    <span className="flex-1 text-xs font-semibold text-slate-500 uppercase tracking-wider">Upstream</span>
    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider shrink-0 pr-5">WAF Status</span>
  </div>
</div>

{/* List body — connects directly below sticky header */}
<div className="border-x border-b border-slate-200 rounded-b-xl divide-y divide-slate-100 overflow-hidden bg-white">
  {pageHosts.map(h => <WAFHostRow key={h.id} host={h} />)}
</div>
```

### สาเหตุที่ใช้ `rounded-t-xl` + `rounded-b-xl` แยก

sticky header ต้องแยก element ออกจาก list body ถ้าใช้ container เดียวแล้วมี sticky child
มันจะ overflow:hidden ไม่ให้ sticky ทำงาน จึงแบ่ง:
- header: `rounded-t-xl` + `border border-slate-200 shadow-sm`
- body: `border-x border-b border-slate-200 rounded-b-xl`

---

## Row Pattern (Compact ~40px height)

```jsx
<div
  onClick={handleToggle}
  className={`flex items-center gap-3 px-4 py-2 cursor-pointer select-none transition-colors
    ${open ? 'bg-indigo-50/50' : 'hover:bg-slate-50'}`}
>
  {/* Icon: 16px fixed */}
  <Icon className="w-4 h-4 shrink-0 text-emerald-500" />

  {/* Domain: fixed width, truncate */}
  <span className="font-semibold text-slate-800 text-sm w-56 truncate shrink-0">
    {host.domain}
  </span>

  {/* Upstream: fills remaining space */}
  <span className="flex-1 text-xs text-slate-400 font-mono truncate">
    {host.upstream}
  </span>

  {/* Badge + chevron: right-aligned, no shrink */}
  <div className="flex items-center gap-2 shrink-0">
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
      <ShieldCheck className="w-3 h-3" />
      WAF Block P1
    </span>
    <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
  </div>
</div>
```

### Row spacing breakdown

| Property | Value | หมายเหตุ |
|----------|-------|---------|
| `py-2` | 8px top + bottom | ได้ ~40px row height |
| `px-4` | 16px left + right | ชิดพอดีกับ column header |
| `gap-3` | 12px | ระยะห่างระหว่าง columns |
| divider | `divide-y divide-slate-100` | บน container ไม่ใช่บน row |
| hover | `hover:bg-slate-50` | เฉพาะตอน closed |
| active | `bg-indigo-50/50` | ตอน expanded |

---

## Separator Pattern

ใช้ `divide-y divide-slate-100` บน container แทนการใส่ `border-b` ต่อ row
เพราะ:
- ไม่มี double border (row แรกไม่มีเส้นบน)
- ลด boilerplate
- `divide-slate-100` อ่อนกว่า `divide-slate-200` เหมาะกับ dense list

```jsx
{/* ✓ ถูก */}
<div className="divide-y divide-slate-100">
  {rows.map(r => <Row key={r.id} />)}
</div>

{/* ✗ ผิด — double border + ต้อง manage ต่อ row */}
<div>
  {rows.map(r => <div className="border-b border-slate-100"><Row /></div>)}
</div>
```

---

## Accordion Expand Pattern

```jsx
{/* CSS height animation — ไม่ใช้ {condition && <panel/>} เพราะ unmount ทุกครั้ง */}
<div style={{
  maxHeight: open ? '3200px' : '0',
  overflow: 'hidden',
  transition: 'max-height 220ms ease-in-out'
}}>
  {everOpen && <ExpandedPanel />}  {/* render ครั้งเดียว ไม่ unmount */}
</div>
```

### ทำไมใช้ `max-height` แทน `height`

CSS transition บน `height: auto` ไม่ทำงาน ต้องใช้ `max-height` แทน
ตั้ง max-height สูงพอ (3200px) แล้ว transition ลงมา 0 เมื่อปิด

### `everOpen` lazy render pattern

```jsx
const [open,     setOpen]     = useState(false)
const [everOpen, setEverOpen] = useState(false)

const handleToggle = useCallback(() => {
  setOpen(o => {
    if (!o && !everOpen) setEverOpen(true)  // set ครั้งแรกที่เปิด
    return !o
  })
}, [everOpen])

// expanded content: render เฉพาะหลัง open ครั้งแรก
{everOpen && <ExpandedPanel />}
```

ประโยชน์: panel ไม่ถูก mount/unmount ทุกครั้ง — state ของ form ยังคงอยู่เมื่อปิดแล้วเปิดใหม่

---

## Badge Pattern

```jsx
{/* Badge sizes */}
{/* Compact (row): px-2 py-0.5 rounded-full text-xs */}
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
  <ShieldCheck className="w-3 h-3" />
  WAF Block P1
</span>

{/* Standard (card): px-2.5 py-0.5 rounded-full text-xs */}
<span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ...">
```

---

## Data Loading Pattern (Badge vs Heavy Data)

badge ต้องโหลดทันทีตอน mount, IP rules โหลด lazy ตอน expand

```jsx
// ✓ เสมอโหลด config (badge ต้องการ)
useEffect(() => {
  api.get(`/waf/${host.id}`).then(r => { setWaf(r.data); setForm(r.data) })
}, [host.id])

// ✓ lazy โหลด ip-rules เฉพาะตอน expand ครั้งแรก
useEffect(() => {
  if (!everOpen) return
  api.get(`/waf/${host.id}/ip-rules`).then(r => setIpRules(r.data || []))
}, [host.id, everOpen])
```

ถ้าทำผิด (gate config ด้วย everOpen ด้วย) badge จะแสดง `—` จนกว่าจะ click

---

## Pagination Pattern

```jsx
const PAGE_SIZE = 25

const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
const pageHosts  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

// Reset page เมื่อ search เปลี่ยน
useEffect(() => { setPage(1) }, [search])
```

---

## Performance Optimizations

```jsx
// 1. memo — ป้องกัน re-render เมื่อ parent update
const WAFHostRow = memo(function WAFHostRow({ host }) { ... })

// 2. useCallback — stable reference สำหรับ event handlers
const save = useCallback(async () => { ... }, [host.id, form, toast])
const handleToggle = useCallback(() => { ... }, [everOpen])

// 3. useMemo — filter เฉพาะตอน hosts/search เปลี่ยน
const filtered = useMemo(() =>
  hosts.filter(h => !search || h.domain.toLowerCase().includes(search.toLowerCase())),
  [hosts, search]
)
```

---

## Tailwind Class Reference สำหรับ Dense Table

| ใช้ทำ | Class |
|------|-------|
| Row hover | `hover:bg-slate-50` |
| Row active (expanded) | `bg-indigo-50/50` |
| Row padding | `px-4 py-2` |
| Divider | `divide-y divide-slate-100` |
| Container border | `border border-slate-200` |
| Container shape | `rounded-xl overflow-hidden` |
| Header background | `bg-slate-50` |
| Header text | `text-xs font-semibold text-slate-500 uppercase tracking-wider` |
| Icon size (row) | `w-4 h-4` |
| Badge icon | `w-3 h-3` |
| Chevron | `w-3.5 h-3.5 transition-transform duration-200` + `rotate-180` when open |
| Domain fixed col | `w-56 truncate shrink-0` |
| Upstream flex col | `flex-1 truncate` |
| Sticky header | `sticky top-0 z-20` |

---

## Lesson: Docker Image vs Volume Mount

**ปัญหาที่เจอ**: แก้ source + build Vite แล้ว restart container แต่หน้าไม่เปลี่ยน

**สาเหตุ**: `web/Dockerfile` ใช้ `COPY dist /usr/share/nginx/html` → dist ถูก bake เข้า image  
restart/up container เดิมจะยังใช้ image เก่า

**Correct deploy workflow**:
```bash
# 1. Build Vite dist
sudo docker run --rm -v /opt/ant2-proxy/web:/app -w /app node:20-alpine sh -c 'npm run build'

# 2. Rebuild Docker image (bakes new dist)
sudo docker compose build web

# 3. Recreate container
sudo docker compose up -d web
```
