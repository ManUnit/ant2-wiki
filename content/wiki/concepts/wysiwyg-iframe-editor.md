---
title: "WYSIWYG Editor: iframe designMode Pattern"
type: concept
tags: [wysiwyg, iframe, designMode, react, frontend, contenteditable]
sources: [2026-05-06-ant2-v2361-release-notes]
created: 2026-05-06
updated: 2026-05-06
---

# WYSIWYG Editor: iframe designMode Pattern

A key frontend architecture decision in [[Ant2-Proxy-Security-Manager]]'s error page editor. Documents why `contentEditable` fails for full-page HTML editing and how an iframe-based approach solves it.

## The Problem with contentEditable

When building a WYSIWYG editor for full HTML pages (with `<!DOCTYPE html>`, `<head>`, `<style>`, `<body>`), a `contentEditable` div cannot render:

- `<body>` background gradients/images (the div inherits the host app's CSS)
- CSS defined in `<style>` blocks within the edited document
- Page-level layout (flexbox on `<body>`, `min-height:100vh`, etc.)

Result: the editor shows white regardless of the error page's dark-gradient design — **what you see is not what users see**.

## The Solution: iframe with designMode

```js
const initIframe = (html) => {
  const doc = iframe.contentDocument
  doc.open()
  doc.write(html)          // full <!DOCTYPE html>...<html>... page
  doc.close()
  doc.designMode = 'on'    // makes entire document editable
}
```

The iframe renders the **complete HTML page** including its own CSS. `designMode = 'on'` enables editing of all text content within the iframe's browsing context.

## Key Implementation Details

### Toolbar execCommand

All toolbar commands must target the **iframe's document**, not the parent:

```js
const exec = (cmd, val = null) => {
  iframe.contentWindow.focus()  // restore focus to iframe
  iframe.contentDocument.execCommand(cmd, false, val)
}
```

### Selection Preservation

Clicking a toolbar button shifts focus from iframe to button. Save the iframe's selection on `selectionchange`, restore it before `execCommand`:

```js
doc.addEventListener('selectionchange', () => {
  const sel = doc.getSelection()
  if (sel?.rangeCount) savedRange = sel.getRangeAt(0).cloneRange()
})

// Before exec:
iframe.contentWindow.focus()
const sel = doc.getSelection()
sel.removeAllRanges()
sel.addRange(savedRange)
```

### Serialization

`doc.documentElement.outerHTML` does not include `<!DOCTYPE html>`. Prepend it manually:

```js
const serialize = () => '<!DOCTYPE html>\n' + doc.documentElement.outerHTML
```

### overflow:hidden Override

Error pages commonly use `body { overflow: hidden }` to prevent scrollbars. In a fixed-height editor iframe this clips content and hides the page background. Inject an override and strip it on save:

```js
// After doc.designMode = 'on':
const override = doc.createElement('style')
override.id = '__ant2_editor_override'
override.textContent = 'html,body{overflow:auto!important;}'
doc.head.appendChild(override)

// On serialize:
doc.getElementById('__ant2_editor_override')?.remove()
const html = '<!DOCTYPE html>\n' + doc.documentElement.outerHTML
// Re-add for continued editing
```

### React Key for Clean Remounts

When the user switches between different error pages, the `HtmlEditor` component must remount to reset iframe state:

```jsx
<HtmlEditor key={editing} value={html} onChange={setHtml} />
```

## Sandbox Requirement

The iframe requires `sandbox="allow-same-origin"` to allow accessing `contentDocument` and setting `designMode`:

```jsx
<iframe sandbox="allow-same-origin" ref={iframeRef} />
```

Without `allow-same-origin`, `iframe.contentDocument` throws a security error.

## See Also

- [[Ant2-Proxy-Security-Manager]]
- [[2026-05-06-ant2-v2361-release-notes]]
