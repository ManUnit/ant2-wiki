---
title: "Custom SelectBox — Portal Dropdown Pattern"
type: source
tags: [react, tailwind, ui-component, dropdown, portal, css]
sources: [custom-selectbox-portal-dropdown]
created: 2026-05-10
updated: 2026-05-10
---

# Custom SelectBox — Portal Dropdown Pattern

**Raw file:** `raw/custom-selectbox-portal-dropdown.md`  
**Built for:** [[Ant2-Proxy-Security-Manager]] v2.4.17 — `IpJail.jsx`

---

## Abstract

Documents the design, implementation, and debugging of a fully custom React dropdown component (`SelectBox`) built as a replacement for native HTML `<select>`. The component uses `createPortal` + `position: fixed` to escape DOM stacking contexts, `getBoundingClientRect()` for viewport-relative positioning, and ChevronDown rotation for open/close animation. Iterated through three rendering bugs before reaching the final working form.

---

## Key Takeaways

- **Native `<select>` has three unresolvable problems on Windows:** blinking text cursor artifact (`|` appears next to selected text), no open/close state accessible in JS/CSS, and inconsistent OS-level rendering. `appearance-none` alone is not sufficient.

- **`createPortal(content, document.body)` is the only reliable z-index fix.** Even `z-index: 9999` fails when a parent element creates a new stacking context via `transform`, `opacity < 1`, `overflow: hidden`, `will-change`, or `isolation: isolate`. Portaling into `document.body` escapes all ancestry entirely.

- **`position: fixed` + `getBoundingClientRect()` recalculated on every open.** Fixed positioning is viewport-relative and immune to ancestor transforms or scroll offsets. Recalculate at click time (not in state init) to handle scroll-before-open.

- **`mousedown` not `click` for outside-close handler.** `mousedown` fires before `click`. Using `click` on document causes the trigger button's own click handler to re-open the dropdown immediately after closing it. Skip closing when target is inside `btnRef` or `dropRef`.

- **`w-full` (`width: 100%`) inside `position: fixed` resolves to viewport width.** The containing block for percentage widths in fixed elements is the viewport, not the nearest parent. A `w-full` block child inside a fixed container becomes ~100vw wide. Fix: use `block` (no `w-full`) + `whitespace-nowrap` on option buttons — the fixed container then shrinks to fit the widest text naturally.

- **`w-max` alone does not fix width.** `width: max-content` on a fixed container with `w-full` children does not shrink to text content — it still expands to viewport width because `w-full` children's max-content resolves to viewport width.

- **`type="button"` required on all internal buttons.** Without it, clicking an option inside a `<form>` submits the form before the `onChange` handler fires.

---

## Notable Quotes / Findings

> "The dropdown list is too wide" — user after `w-max` fix still showed full-viewport-width dropdown.

Root cause trace:
1. First attempt: overlapping ChevronDown icon with `absolute right-X` — overlaps text
2. Second attempt: `appearance-none` + `pointer-events-none` overlay — native cursor artifact persisted
3. Third attempt: custom SelectBox with `absolute` dropdown — hidden behind sibling card (stacking context)
4. Fourth attempt: `createPortal` + `w-max` — dropdown appeared on top but viewport-wide
5. **Final fix:** `createPortal` + `block whitespace-nowrap` buttons (no `w-full`) — shrink-to-fit correctly

---

## Gaps / Open Questions

- Keyboard navigation (arrow keys, Enter, Escape) not implemented — functional but not accessible.
- Dropdown position does not recalculate on window resize while open.
- No upward-opening fallback when the dropdown would overflow the bottom of the viewport.

---

## See Also

- [[custom-dropdown-portal-pattern]] — full implementation reference and CSS pitfall catalog
- [[wysiwyg-iframe-editor]] — another "replace native browser element with custom React" pattern
- [[Ant2-Proxy-Security-Manager]] — project where this was built
