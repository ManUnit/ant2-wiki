---
title: "Custom Dropdown Portal Pattern"
type: concept
tags: [react, tailwind, ui-component, dropdown, portal, css, position-fixed]
sources: [custom-selectbox-portal-dropdown]
created: 2026-05-10
updated: 2026-05-10
---

# Custom Dropdown Portal Pattern

A React + Tailwind pattern for building a custom `<select>` replacement that renders its dropdown list outside the DOM hierarchy using `createPortal`, avoiding all z-index, overflow, and browser-native rendering issues.

---

## When to Use

Replace native `<select>` when you need any of:
- Animated open/close arrow indicator (ChevronDown ↔ ChevronUp)
- Consistent rendering across Windows/macOS/Chrome/Firefox
- Dropdown that layers above cards with `overflow: hidden`, modals, or elements with stacking contexts
- Custom item styling (highlighted selected item, icons, grouping)

---

## Component: SelectBox

### Required Imports

```jsx
import React, { useEffect, useState, useRef } from 'react'
import { createPortal } from 'react-dom'
import { ChevronDown } from 'lucide-react'
```

### Full Implementation

```jsx
function SelectBox({ value, onChange, options, small = false }) {
  const [open, setOpen]       = useState(false)
  const [dropPos, setDropPos] = useState(null)
  const btnRef  = useRef(null)
  const dropRef = useRef(null)

  const handleToggle = () => {
    if (!open && btnRef.current) {
      const r = btnRef.current.getBoundingClientRect()
      setDropPos({ top: r.bottom + 4, left: r.left })
    }
    setOpen(v => !v)
  }

  useEffect(() => {
    if (!open) return
    const close = (e) => {
      if (btnRef.current?.contains(e.target))  return
      if (dropRef.current?.contains(e.target)) return
      setOpen(false)
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])

  const selected = options.find(o => o.value === value)

  return (
    <div className="inline-block">
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
        <span className={`pl-3 pr-2 text-slate-700 text-left whitespace-nowrap
                          ${small ? 'py-0.5' : 'py-2'}`}>
          {selected?.label ?? '—'}
        </span>
        <span className={`flex items-center justify-center bg-slate-100
                          border-l border-slate-300 shrink-0 rounded-r-lg
                          ${small ? 'w-6 py-0.5' : 'w-8 py-2'}`}>
          <ChevronDown className={`text-slate-500 transition-transform duration-200
                                   ${open ? 'rotate-180' : ''}
                                   ${small ? 'w-3 h-3' : 'w-4 h-4'}`} />
        </span>
      </button>

      {open && dropPos && createPortal(
        <div
          ref={dropRef}
          style={{ position: 'fixed', top: dropPos.top, left: dropPos.left, zIndex: 9999 }}
          className="bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden"
        >
          {options.map(o => (
            <button
              key={o.value}
              type="button"
              onClick={() => { onChange(o.value); setOpen(false) }}
              className={`block text-left px-4 py-2 whitespace-nowrap transition-colors
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

### Options Format

```js
const OPTIONS = [
  { label: '1 hour',    value: 1   },
  { label: 'Permanent', value: 0   },
]
// value can be any type — number, string, etc.
// For number arrays: [20,50,100].map(n => ({ label: String(n), value: n }))
```

---

## CSS Pitfalls

### 1. `w-full` inside `position: fixed` → Viewport Width

The containing block for percentage widths inside a `position: fixed` element is the **viewport**, not the nearest parent. `width: 100%` resolves to `~100vw`.

```
Fixed container (shrink-to-fit)
  └─ w-full button → width: 100% of viewport = 1440px
     → container expands to 1440px
```

**Fix:** Use `block` (no `w-full`) + `whitespace-nowrap` on option buttons. A `position: fixed` container with no explicit width + block children with `width: auto` shrinks to the widest text content.

### 2. `w-max` does not help with `w-full` children

`width: max-content` on the container still yields viewport-width because `w-full` children's max-content also resolves to viewport width. Remove both `w-max` and `w-full`.

### 3. `z-index: 9999` is not enough without a portal

Parent elements that create stacking contexts (via `transform`, `opacity < 1`, `overflow: hidden`, `will-change`, `isolation: isolate`) can cap the effective z-index of descendants. `createPortal` into `document.body` exits all such contexts.

### 4. `click` event causes immediate re-open

Using `document.addEventListener('click', close)` fires after the trigger button's own `onClick` fires. Sequence: `document click` fires → `setOpen(false)` → button `onClick` fires → `setOpen(true)`. Net result: stays open.

**Fix:** Use `mousedown`. It fires before `click`. Guard: if `btnRef.current.contains(e.target)`, return early — let `handleToggle` manage the toggle.

### 5. Missing `type="button"` submits form

Every `<button>` inside `<form>` defaults to `type="submit"`. Option buttons without `type="button"` will submit the form on click.

---

## Visual Design

Windows combo-box style: text area + separated arrow box.

```
┌─────────────────┬───┐
│  Permanent      │ ▼ │   closed
└─────────────────┴───┘
         └── border-l separates text from arrow

┌─────────────────┬───┐
│  Permanent      │ ▲ │   open (ChevronDown rotated 180°)
└─────────────────┴───┘
  ┌───────────────┐
  │ 1 hour        │   portal: position:fixed, z:9999
  │ 2 hours       │   block buttons, whitespace-nowrap
  │ ▓▓▓▓▓▓▓▓▓▓▓▓ │   selected = bg-indigo-600 text-white
  │ Permanent     │
  └───────────────┘
```

---

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | any | required | Currently selected value |
| `onChange` | `(val) => void` | required | Called with the new value on selection |
| `options` | `{ label: string, value: any }[]` | required | Option list |
| `small` | boolean | `false` | Compact variant for dense UI (pagination controls, etc.) |

---

## Limitations

- No keyboard navigation (arrow keys, Enter, Escape)
- Position not recalculated on window resize while open
- No upward-opening fallback when near viewport bottom

---

## See Also

- [[2026-05-10-custom-selectbox-portal-dropdown]] — source document with full debug trace
- [[wysiwyg-iframe-editor]] — related "escape native browser element" pattern
- [[Ant2-Proxy-Security-Manager]] — project context
