---
title: "Compact Row Table Theme"
type: concept
tags: [react, tailwind, ui-pattern, dense-list, accordion, performance]
sources: [2026-05-13-compact-row-table-theme]
created: 2026-05-13
updated: 2026-05-13
---

# Compact Row Table Theme

Pattern สำหรับสร้าง dense management list ใน React + Tailwind CSS เป้าหมาย row height ~40px รองรับ operation-heavy use case (100–1000+ items) โดยมี sticky header, accordion expand, lazy load, และ pagination ([[2026-05-13-compact-row-table-theme]])

## Container Structure

```jsx
{/* sticky header — แยกจาก body เพราะ overflow:hidden blocks sticky */}
<div className="sticky top-0 z-20 bg-white border border-slate-200 rounded-t-xl shadow-sm">
  <div className="flex items-center gap-3 px-4 py-2 border-b border-slate-100">
    {/* search + count */}
  </div>
  <div className="flex items-center gap-3 px-4 py-1.5 bg-slate-50">
    {/* column headers */}
  </div>
</div>

{/* body — rounded-b-xl ต่อจาก header */}
<div className="border-x border-b border-slate-200 rounded-b-xl divide-y divide-slate-100 overflow-hidden bg-white">
  {rows}
</div>
```

**Key**: sticky header และ list body เป็น sibling elements — ถ้าเป็น parent/child กัน `overflow:hidden` บน parent จะทำให้ `sticky` ทำงานไม่ได้

## Row Layout

```
[icon w-4] [domain w-56 truncate shrink-0] [upstream flex-1 truncate] [badge shrink-0] [chevron w-3.5]
     px-4 ←————————————————————————————————————————————————————————————————————————→ py-2
```

```jsx
<div className={`flex items-center gap-3 px-4 py-2 cursor-pointer select-none transition-colors
  ${open ? 'bg-indigo-50/50' : 'hover:bg-slate-50'}`}>
  <Icon className="w-4 h-4 shrink-0" />
  <span className="font-semibold text-slate-800 text-sm w-56 truncate shrink-0">{domain}</span>
  <span className="flex-1 text-xs text-slate-400 font-mono truncate">{upstream}</span>
  <div className="flex items-center gap-2 shrink-0">
    <Badge />
    <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
  </div>
</div>
```

## Divider Pattern

```jsx
{/* ✓ ถูก: divide-y บน container */}
<div className="divide-y divide-slate-100">
  {rows}
</div>

{/* ✗ ผิด: border-b ต่อ row — double border + boilerplate */}
{rows.map(r => <div className="border-b border-slate-100">...</div>)}
```

`divide-slate-100` (อ่อนกว่า 200) เหมาะกับ dense list ที่ต้องการ separator บาง

## Accordion Expand

### max-height CSS transition

```jsx
<div style={{
  maxHeight: open ? '3200px' : '0',
  overflow: 'hidden',
  transition: 'max-height 220ms ease-in-out'
}}>
  {everOpen && <Panel />}
</div>
```

`height: auto` ไม่รองรับ CSS transition — ใช้ `max-height` แทน ตั้งค่าสูงพอ (>= panel height จริง)

### everOpen lazy render

```jsx
const [open, setOpen]         = useState(false)
const [everOpen, setEverOpen] = useState(false)

const toggle = useCallback(() => {
  setOpen(o => {
    if (!o && !everOpen) setEverOpen(true)
    return !o
  })
}, [everOpen])

{everOpen && <Panel />}  // mount ครั้งแรกที่เปิด, ไม่ unmount เมื่อปิด
```

ประโยชน์: form state คงอยู่เมื่อ collapse, ไม่ re-fetch ทุก toggle

## Data Loading: Eager vs Lazy

```jsx
// Eager — badge ต้องการตอน mount
useEffect(() => {
  api.get(`/resource/${id}`).then(r => setBadgeData(r.data))
}, [id])

// Lazy — heavy data โหลดเฉพาะตอน expand ครั้งแรก
useEffect(() => {
  if (!everOpen) return
  api.get(`/resource/${id}/details`).then(r => setDetails(r.data))
}, [id, everOpen])
```

**Anti-pattern**: gate config ด้วย `everOpen` เช่นกัน → badge แสดง `—` จนกว่าจะ click

## Performance

```jsx
// Memoized row component
const Row = memo(function Row({ item }) { ... })

// Stable callbacks
const save = useCallback(async () => { ... }, [deps])

// Memoized filter
const filtered = useMemo(() =>
  items.filter(i => !search || i.name.includes(search)),
  [items, search]
)

// Pagination
const PAGE_SIZE = 25
const page = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)
useEffect(() => setCurrentPage(1), [search])  // reset on search
```

## Badge Sizes

```jsx
{/* Compact row badge */}
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
  <Icon className="w-3 h-3" /> Label
</span>

{/* Standard card badge */}
<span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ...">
```

## Tailwind Quick Reference

| Element | Classes |
|---------|---------|
| Row hover/active | `hover:bg-slate-50` / `bg-indigo-50/50` |
| Row padding | `px-4 py-2` |
| Divider | `divide-y divide-slate-100` |
| Container | `border border-slate-200 rounded-xl overflow-hidden` |
| Column header | `text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-50` |
| Icon (row) | `w-4 h-4 shrink-0` |
| Chevron | `w-3.5 h-3.5 transition-transform duration-200` + `rotate-180` |
| Fixed col | `w-56 truncate shrink-0` |
| Flex col | `flex-1 truncate` |
| Sticky header | `sticky top-0 z-20` |

## See Also

- [[2026-05-13-compact-row-table-theme]]
- [[custom-dropdown-portal-pattern]]
- [[ant2-docker-deploy-pattern]]
- [[Ant2-Proxy-Security-Manager]]
