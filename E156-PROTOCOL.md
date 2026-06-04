# E156 Protocol — PRISMA 2020 Flow & Checklist Generator

- **Project:** PRISMA 2020 Flow & Checklist Generator
- **Repo (docs):** Journal
- **Primary chart-kit function:** `renderSankey`
- **Built:** 2026-06-04

## CURRENT BODY

Systematic reviews must report study selection as a PRISMA 2020 flow diagram and document the 27-item checklist, yet the portfolio lacked offline reporting infrastructure to produce either reliably. We take the reviewer's own study-selection counts — records identified via databases and other sources, duplicates removed, records screened and excluded, reports sought, not retrieved, and assessed, itemised exclusion reasons, and studies and reports included — as the dataset. The engine derives the canonical identification-to-screening-to-included flow by deterministic arithmetic and reconciles it against three PRISMA identities, returning a warning (never an error) for each mismatch with the expected and given counts side by side. Across the worked example the tool reproduces the flow exactly, reports zero warnings when the counts are internally consistent, and isolates a single inconsistent count to exactly one identity warning, while the Sankey fan renders the itemised exclusion reasons as proportional sinks. Robustness rests on nullish-coalescing fallbacks that preserve a genuine zero count, an integer tolerance on every comparison, and dropping zero-count reasons from the fan so no spurious arm appears. The contribution is auditable reporting infrastructure: every number in the diagram is the reviewer's own, traceable, and checked rather than re-estimated. The boundary is deliberate — the tool reconciles and visualises reported counts and does not screen records, deduplicate, or infer missing values.

SUBMITTED: [ ]
