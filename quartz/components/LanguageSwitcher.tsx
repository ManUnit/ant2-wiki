import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

const LanguageSwitcher: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
  const slug = fileData.slug ?? "index"
  const isThPage = slug.startsWith("th/")

  const getEnPath = (s: string) => (s === "index" ? "/" : `/${s}`)
  const getThPath = (s: string) => (s === "index" ? "/th/" : `/th/${s}`)

  let enHref: string
  let thHref: string

  if (isThPage) {
    const enSlug = slug.replace(/^th\//, "")
    enHref = getEnPath(enSlug)
    thHref = getThPath(enSlug)
  } else {
    enHref = getEnPath(slug)
    thHref = getThPath(slug)
  }

  return (
    <div class="lang-switcher">
      <a href={enHref} class={`lang-btn${!isThPage ? " active" : ""}`}>
        EN
      </a>
      <a href={thHref} class={`lang-btn${isThPage ? " active" : ""}`}>
        TH
      </a>
    </div>
  )
}

LanguageSwitcher.css = `
.lang-switcher {
  display: flex;
  gap: 0.3rem;
  margin: 0.25rem 0 0.75rem 0;
}
.lang-btn {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 4px;
  text-decoration: none;
  color: var(--darkgray);
  border: 1px solid var(--lightgray);
  letter-spacing: 0.04em;
  transition: background 0.12s, color 0.12s;
}
.lang-btn:hover {
  background: var(--lightgray);
  text-decoration: none;
}
.lang-btn.active {
  background: var(--secondary);
  color: #fff;
  border-color: var(--secondary);
}
`

export default (() => LanguageSwitcher) satisfies QuartzComponentConstructor
