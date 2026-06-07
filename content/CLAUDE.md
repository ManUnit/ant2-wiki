# Second Brain Wiki — Schema & Rules

This file is the authoritative schema for this wiki. Read it at the start of every session. Every interaction must follow these rules.

---

## Domain

**Topic:** NGINX + OWASP CRS WAF — architecture, configuration, tuning, attack patterns, deployment, and security operations.

This is an evolving second brain. The domain will expand as sources are added.

---

## Directory Layout

```
/                         ← vault root (Obsidian opens here)
├── CLAUDE.md             ← this schema (authoritative)
├── index.md              ← wiki page catalog (LLM-maintained)
├── log.md                ← append-only ingest/query/lint log
├── raw/                  ← immutable source documents (never modify)
│   ├── assets/           ← locally downloaded images and attachments
│   └── *.md / *.pdf / *  ← clipped articles, papers, notes, data
└── wiki/                 ← all LLM-generated pages (LLM owns this)
    ├── sources/          ← one summary page per raw source
    ├── entities/         ← people, organizations, tools, products
    ├── concepts/         ← technical and conceptual topics
    └── analyses/         ← comparisons, syntheses, query outputs
```

**Rules:**
- `raw/` is read-only. Never edit or delete source files.
- `wiki/` is fully owned by the LLM. Create, update, and cross-reference freely.
- `CLAUDE.md`, `index.md`, and `log.md` live at the vault root.

---

## Page Format

Every wiki page must have YAML frontmatter:

```yaml
---
title: "Page Title"
type: source | entity | concept | analysis
tags: [tag1, tag2]
sources: [source-slug-1, source-slug-2]   # omit if none
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Body conventions:**
- Use `[[WikiLink]]` for all internal cross-references (Obsidian wikilink syntax).
- Cite sources inline as `([[source-slug]])` after claims that derive from a specific source.
- Use `## Section` headers; avoid going deeper than `###`.
- End every page with a `## See Also` section listing related wiki pages.
- Keep pages focused. If a section grows to >300 words, consider splitting it out.

**Naming:**
- Source pages: `wiki/sources/YYYY-MM-DD-slug.md` (slug = 3–5 word kebab-case title)
- Entity pages: `wiki/entities/Entity-Name.md` (Title Case)
- Concept pages: `wiki/concepts/concept-name.md` (kebab-case)
- Analysis pages: `wiki/analyses/YYYY-MM-DD-analysis-title.md`

---

## Operations

### INGEST — adding a new source

When the user says "ingest [source]" or drops a file in `raw/`:

1. **Read** the source fully. If it contains images, read the text first, then view key images.
2. **Discuss** with the user: confirm the 3–5 most important takeaways before writing anything.
3. **Write** a source summary page at `wiki/sources/YYYY-MM-DD-slug.md`. Must include:
   - Frontmatter (type: source)
   - One-paragraph abstract
   - Key takeaways as a bullet list
   - Notable quotes (verbatim, with context)
   - Gaps / unanswered questions
   - See Also links
4. **Update** existing wiki pages touched by this source:
   - Entity pages: add new facts, update existing ones, note contradictions
   - Concept pages: integrate new information, flag if the source challenges prior understanding
   - If a relevant page doesn't exist yet, create it
5. **Update** `index.md`: add the new source page; add any new entity/concept pages.
6. **Append** to `log.md` with the entry format below.

Typical ingest touches 5–15 wiki pages. Don't skip the cross-referencing step.

### QUERY — answering questions

When the user asks a question:

1. Read `index.md` to identify relevant pages.
2. Read those pages. Read additional linked pages if needed.
3. Synthesize an answer with citations (`([[page-name]])`).
4. **Ask the user** if the answer should be filed back into the wiki as a new analysis page. If yes, write it to `wiki/analyses/`.
5. Append a `query` entry to `log.md`.

### LINT — health check

When the user says "lint the wiki" or periodically on request:

1. Scan all wiki pages and report:
   - Contradictions between pages
   - Claims superseded by newer sources
   - Orphan pages (no inbound wikilinks)
   - Concepts mentioned but lacking their own page
   - Missing cross-references
   - Data gaps that could be filled by a web search
2. Propose new questions to investigate and new sources to seek.
3. Optionally fix issues in-place if the user approves.
4. Append a `lint` entry to `log.md`.

---

## log.md Entry Format

Each entry must start with this header pattern (for grep-ability):

```
## [YYYY-MM-DD] TYPE | Title
```

TYPE is one of: `ingest`, `query`, `lint`, `update`, `note`

Example:
```markdown
## [2026-05-05] ingest | OWASP CRS v4 Release Notes
- Source file: raw/owasp-crs-v4-release-notes.md
- Summary page: wiki/sources/2026-05-05-owasp-crs-v4-release-notes.md
- Pages updated: [[OWASP-CRS]], [[ModSecurity]], [[WAF-Rule-Tuning]]
- Pages created: [[CRS-v4-Migration]]
- Key insight: paranoia level system redesigned for v4
```

---

## index.md Structure

The index has three sections:

```markdown
## Sources
| Page | Summary | Date |
| ...  | ...     | ...  |

## Entities
| Page | Type | Summary |
| ...  | ...  | ...     |

## Concepts
| Page | Summary | Key Sources |
| ...  | ...     | ...         |

## Analyses
| Page | Question | Date |
| ...  | ...      | ...  |
```

Update the relevant table(s) after every ingest or query that produces a new page.

---

## Cross-Reference Rules

- When writing or updating any page, scan the index for related pages and add `[[WikiLink]]`s.
- Every entity and concept page must link to its source pages.
- Source pages must link to every entity and concept they introduce or update.
- The index must link to every page. No page should be unreachable from the index.

---

## Behavioral Rules

1. **Never modify raw/.** Read only.
2. **Always update index.md and log.md** after any ingest or page-creating query.
3. **Discuss before writing** during ingest — confirm takeaways with the user first.
4. **File valuable answers** — always ask if a good query answer should become an analysis page.
5. **Prefer updating existing pages** over creating new ones unless the topic clearly warrants its own page.
6. **One source at a time** by default. Don't batch-ingest without explicit user instruction.
7. **Cite everything.** No claims on wiki pages without a source link.
8. **Flag contradictions explicitly.** If a new source contradicts an existing page, add a `> [!warning] Contradiction` callout and leave both views until the user resolves it.
9. **Keep pages navigable.** Every page must have at least two outbound wikilinks.
10. **Read this file at session start.** If asked "what schema are we using?", quote the relevant section.
