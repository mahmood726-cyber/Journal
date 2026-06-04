# PRISMA 2020 Flow & Checklist Generator

A single-file, fully-offline browser tool that generates the **PRISMA 2020
study-selection flow diagram** and the **27-item reporting checklist** for a
systematic review. It reconciles the reported study-selection counts against the
canonical PRISMA identification &rarr; screening &rarr; included identities and
surfaces any mismatch as a warning (never an error), so a partially-entered or
inconsistent flow still produces a usable diagram.

This is reporting infrastructure for the meta-analysis portfolio — the diagram
and checklist that journals require but that the portfolio previously lacked.

## What it does

- **Flow reconciliation (deterministic arithmetic).** Three PRISMA 2020
  identities are checked, each mismatch reported with *expected vs given*:
  - `recordsScreened  = recordsDb + recordsOther − duplicatesRemoved`
  - `reportsAssessed  = reportsSought − reportsNotRetrieved`
  - `studiesIncluded  = reportsAssessed − Σ(excludedReasons.n)`
- **Flow diagram** via the e156 chart-kit `renderSankey`: stages drawn left to
  right with exit ribbons peeling downward; the final stage **fans the itemised
  exclusion reasons** into side-by-side proportional sinks.
- **27-item checklist** rendered as an interactive list (section, item #, text,
  checkbox) with a **copy-as-text** export and a live completed-count.

## Provenance

| Element | Source |
|---|---|
| Flow logic & 27-item checklist | PRISMA 2020 — Page MJ et al., *BMJ* 2021;372:n71 |
| `renderSankey` visualisation | e156 chart-kit (`C:/Projects/e156/flagship/kit/chartkit.js`), copied verbatim |
| Structure / styling template | `C:/Projects/html1-effectsize` (engine/tests/index pattern) |
| LICENSE | MIT, from `C:/Projects/html1-effectsize/LICENSE` |

### Gotchas encoded

- Numeric fallbacks use `??` (nullish), **never `||`** — a real `0` count
  (e.g. `recordsOther = 0`, "databases only") must not be dropped.
- Consistency checks compare expected vs given with an integer tolerance and
  report **both** numbers, not merely that a mismatch exists.
- Warnings are **returned, never thrown** — the diagram still draws.
- Zero-count exclusion reasons are dropped from the Sankey fan (no `−0` arms).

## Layout

```
engine.js          pure logic (Node + browser), exports PrismaEngine
tests.js           Node test harness — `node tests.js`
index.html         single-file offline UI (chartkit.js + engine.js + inline UI)
chartkit.js        e156 chart-kit (copied verbatim)
README.md          this file
E156-PROTOCOL.md   E156 micro-paper protocol
LICENSE            MIT
.gitignore / .nojekyll
```

## Tests

```
$ node tests.js
29 passed, 0 failed
```

Coverage (pure arithmetic, no metafor): consistent inputs → zero warnings; each
individual identity mismatch → exactly the right warning; isolated single
mismatch → exactly one warning; `excludedReasons` sum; derived
screened/assessed/included correctness; empty / omitted other-sources handled
(`recordsOther = 0` and `null` both → treated as 0); partial flow does not throw;
`buildStages` exclusion-reason fan; zero-count reasons dropped; full 27-item
checklist; `num()`/`intEq()` edge cases.

## Reuse vs net-new

- **Reused:** the IIFE module pattern, CSS look, and test-harness style from
  `html1-effectsize`; the `renderSankey` primitive from the e156 chart-kit
  (including its multi-exit fan for itemised exclusion reasons).
- **Net-new:** the PRISMA 2020 flow reconciliation engine (three identities with
  expected-vs-given warnings), the `buildStages` adapter that maps reported
  counts onto the chart-kit Sankey contract, and the interactive 27-item
  checklist with copy-as-text export.

## Offline / GitHub Pages

No external CDN or network calls. `index.html` runs directly from the filesystem
or as a GitHub Pages root (`.nojekyll` included).
