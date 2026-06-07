# Custom SelectBox — Portal Dropdown Pattern (React + Tailwind)

**Context:** Built for Ant2 Proxy Security Manager v2.4.17  
**Date:** 2026-05-10  
**File:** `web/src/pages/IpJail.jsx`  
**Stack:** React 18, Tailwind CSS v3, Lucide React icons

---

## Problem: Why Native `<select>` Fails

Native HTML `<select>` has several unresolvable issues in polished UIs:

1. **Garbage character rendering** — On Windows with certain system fonts, the browser renders a blinking text cursor `|` inside the selected option text when the element is focused. "Permanent" appears as "Permanent|" — looks like a garbage character.

2. **No open-state tracking** — There is no reliable cross-browser CSS selector or JS event to detect whether the native dropdown is open. You cannot flip a ChevronDown ↔ ChevronUp arrow based on state.

3. **`appearance-none` is not enough** — Removing native chrome via `appearance-none` suppresses the default arrow but does NOT fix the text cursor artifact.

4. **z-index / overflow clipping** — A native `<select>` dropdown may still be clipped by parent containers with `overflow: hidden`, but the bigger problem for custom-styled elements is that the absolutely-positioned dropdown popup gets buried under sibling elements.

5. **Inconsistent styling across browsers/OS** — Native select styling is deeply OS-specific. Windows, macOS, Chrome, Firefox all render differently.

**Bottom line:** For any UI that needs (a) a custom arrow that animates open/close, (b) consistent rendering across OSes, and (c) reliable z-index layering — replace native `<select>` with a fully custom component.

---

## Solution: SelectBox Component with Portal

### Core Design Principles

1. **Use `createPortal` to escape DOM hierarchy** — Render the dropdown list directly into `document.body`. This means no parent `overflow: hidden`, `z-index` stacking context, or card boundary can ever clip the list.

2. **Use `position: fixed` with `getBoundingClientRect()`** — Calculate the trigger button's viewport-relative position at click time, then place the dropdown there. Fixed positioning means the position is stable regardless of scroll.

3. **Track open state in React** — `const [open, setOpen] = useState(false)`. This allows ChevronDown to animate (`rotate-180`) when open.

4. **Outside-click to close** — `document.addEventListener('mousedown', handler)` captures clicks outside both the button and the dropdown. Use refs to both elements to check containment.

5. **Windows combo-box visual** — Split button into two parts: text area (left) + arrow box (right, separated by `border-l`). The arrow never overlaps text.

---

## Full Implementation

### Dependencies

```jsx
import React, { useEffect, useState, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import { ChevronDown } from 'lucide-react'
```

### Component

```jsx
function SelectBox({ value, onChange, options, small = false }) {
  const [open, setOpen]       = useState(false)
  const [dropPos, setDropPos] = useState(null)
  const btnRef  = useRef(null)
  const dropRef = useRef(null)

  // Calculate button position at click time, then toggle open
  const handleToggle = () => {
    if (!open && btnRef.current) {
      const r = btnRef.current.getBoundingClientRect()
      setDropPos({
        top:   r.bottom + 4,   // 4px gap below button
        left:  r.left,
        width: r.width,        // for reference (not always used for popup width)
      })
    }
    setOpen(v => !v)
  }

  // Close on outside click — checks BOTH button and dropdown refs
  useEffect(() => {
    if (!open) return
    const close = (e) => {
      if (btnRef.current?.contains(e.target))  return   // click on trigger = let handleToggle handle
      if (dropRef.current?.contains(e.target)) return   // click inside list = selection in progress
      setOpen(false)
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])

  const selected = options.find(o => o.value === value)

  return (
    <div className="inline-block">
      {/* Trigger button — Windows combo-box style */}
      <button
        ref={btnRef}
        type="button"
        onClick={handleToggle}
        className={`flex items-center border rounded-lg bg-white
                    focus:outline-none focus:ring-2 focus:ring-indigo-500
                    hover:border-indigo-400 transition-colors
                    ${open ? 'border-indigo-500' : 'border-slate-300'}
                    ${small ? 'text-xs' : 'text-sm'}`}
      >
        {/* Text area */}
        <span className={`pl-3 pr-2 text-slate-700 text-left whitespace-nowrap
                          ${small ? 'py-0.5' : 'py-2'}`}>
          {selected?.label ?? '—'}
        </span>

        {/* Arrow box — separated by border-left */}
        <span className={`flex items-center justify-center bg-slate-100
                          border-l border-slate-300 shrink-0 rounded-r-lg
                          ${small ? 'w-6 py-0.5' : 'w-8 py-2'}`}>
          <ChevronDown className={`text-slate-500 transition-transform duration-200
                                   ${open ? 'rotate-180' : ''}
                                   ${small ? 'w-3 h-3' : 'w-4 h-4'}`} />
        </span>
      </button>

      {/* Dropdown list — rendered into document.body via portal */}
      {open && dropPos && createPortal(
        <div
          ref={dropRef}
          style={{
            position: 'fixed',
            top:      dropPos.top,
            left:     dropPos.left,
            zIndex:   9999,
          }}
          className="bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden w-max"
        >
          {options.map(o => (
            <button
              key={o.value}
              type="button"
              onClick={() => { onChange(o.value); setOpen(false) }}
              className={`w-full text-left px-3 py-2 transition-colors
                          hover:bg-indigo-50 hover:text-indigo-700
                          ${small ? 'text-xs' : 'text-sm'}
                          ${o.value === value
                            ? 'bg-indigo-600 text-white font-semibold'
                            : 'text-slate-700'}`}
            >
              {o.label}
            </button>
          ))}
        </div>,
        document.body
      )}
    </div>
  )
}
```

### Usage

```jsx
// Options format — value can be any type (number, string)
const DURATION_OPTIONS = [
  { label: '1 hour',    value: 1   },
  { label: '2 hours',   value: 2   },
  { label: '12 hours',  value: 12  },
  { label: '1 day',     value: 24  },
  { label: 'Permanent', value: 0   },
]

// Normal size
<SelectBox
  value={selectedHours}
  onChange={(val) => setSelectedHours(val)}
  options={DURATION_OPTIONS}
/>

// Small variant (for dense UI, e.g. pagination per-page selector)
<SelectBox
  small
  value={pageSize}
  onChange={(val) => setPageSize(val)}
  options={[20, 50, 100, 200, 500].map(s => ({ label: String(s), value: s }))}
/>
```

---

## Key Technical Details

### Why `position: fixed` over `position: absolute`

`absolute` positioning is relative to the nearest positioned ancestor. In a complex component tree (cards, flex containers, modals), the ancestor chain is unpredictable. `fixed` positioning is always relative to the **viewport** — 100% predictable, no ancestor can interfere.

Downside: the position doesn't scroll with the page. Fix: recalculate `getBoundingClientRect()` on every open click. Since the user must click the button to open the dropdown, and clicking changes focus (potentially scrolling), recalculating at open time is sufficient.

### Why `createPortal(content, document.body)`

Portals render React children into a **different DOM node** while keeping them in the React tree. By appending to `document.body`, the dropdown is:
- Visually on top of everything (no z-index context interference)
- Not clipped by any parent `overflow: hidden`
- Still connected to React's event system (state, hooks work normally)

Without portal: even `z-index: 9999` fails if a parent creates a new stacking context (e.g., via `transform`, `filter`, `will-change`, `isolation: isolate`, or `opacity < 1`).

### Why `w-max` on the dropdown container

`w-max` (CSS: `width: max-content`) makes the dropdown as wide as its widest option text. This is almost always the right behavior — the list should not be artificially stretched to match the trigger button's width, especially when the trigger button adapts its size to the currently selected value (e.g., "1 hour" is shorter than "Permanent").

### ChevronDown Animation

```jsx
className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
```

Tailwind's `rotate-180` applies `transform: rotate(180deg)`. Combined with `transition-transform duration-200`, the arrow smoothly flips when `open` changes. A ChevronDown rotated 180° becomes a ChevronUp — no separate icon import needed.

### `type="button"` on All Internal Buttons

Critical when SelectBox is used inside a `<form>`. Without `type="button"`, clicking an option button submits the form. Every button inside SelectBox must have `type="button"` explicitly.

### Outside-Click Handler Pattern

```jsx
useEffect(() => {
  if (!open) return                          // no-op when closed — save event listener
  const close = (e) => {
    if (btnRef.current?.contains(e.target))  return   // let handleToggle decide
    if (dropRef.current?.contains(e.target)) return   // selection in progress
    setOpen(false)
  }
  document.addEventListener('mousedown', close)
  return () => document.removeEventListener('mousedown', close)  // cleanup on close or unmount
}, [open])
```

Key: `mousedown` fires before `click`. If you use `click`, the button's own click handler fires first and re-opens after `setOpen(false)`. Using `mousedown` on document and NOT calling `setOpen(false)` when the target is inside `btnRef` lets `handleToggle` handle the toggle correctly.

### Small Variant

The `small` prop switches:
- Text size: `text-sm` → `text-xs`
- Padding: `py-2` → `py-0.5`  
- Arrow box width: `w-8` → `w-6`
- Icon size: `w-4 h-4` → `w-3 h-3`

Useful for compact UI elements like pagination controls, table row selectors, inline filter chips.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| No `createPortal` | Dropdown hidden behind other cards | Always use portal into `document.body` |
| `position: absolute` in portal | Dropdown position wrong when page is scrolled | Use `position: fixed` |
| `click` event for outside close | Click on trigger re-opens after closing | Use `mousedown` instead of `click` |
| Missing `type="button"` | Selecting an option submits the parent form | Add `type="button"` to ALL buttons inside |
| `minWidth: triggerWidth` on popup | Dropdown too wide when trigger shows short value | Use `w-max` — size to content, not to trigger |
| Not cleaning up event listener | Memory leak / stale handler accumulates | Always return cleanup in useEffect |
| Calculating position once in state init | Position wrong if component re-renders before open | Recalculate in `handleToggle` each time |

---

## Visual Anatomy

```
┌─────────────────────┬───┐
│  Permanent          │ ▼ │   ← trigger button (closed)
└─────────────────────┴───┘
         border-left ──^

┌─────────────────────┬───┐
│  Permanent          │ ▲ │   ← trigger button (open, arrow rotated)
└─────────────────────┴───┘
  ┌──────────────┐
  │ 1 hour       │   ← dropdown portal (position:fixed, z:9999)
  │ 2 hours      │
  │ 4 hours      │
  │ ▓▓▓▓▓▓▓▓▓▓▓ │   ← selected option (bg-indigo-600 text-white)
  │ Permanent    │
  └──────────────┘
```

---

## Dependencies Summary

| Dep | Purpose |
|-----|---------|
| `react` | `useState`, `useEffect`, `useRef` |
| `react-dom` | `createPortal` |
| `lucide-react` | `ChevronDown` SVG icon |
| `tailwindcss` | All styling |

No additional libraries needed. Total component code: ~60 lines.
