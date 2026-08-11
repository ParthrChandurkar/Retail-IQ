# NLP Feasibility Gate

- **Generated at:** `2026-08-11T17:49:42.585120Z`
- **Dataset row counts used:** unique review IDs=98410; non-null comments=40641
- **Code/commit reference:** `23f76a939e5e2e603a17370762a4a09e0c2e05a1`
- **Decision:** **NO-GO**

## Required evidence

| Measure | Result |
|---|---:|
| Null comment rate | 58.7024% |
| Non-null comment rate | 41.2976% |
| Average token length, non-null comments | 11.6802 |
| Median token length, non-null comments | 9.0000 |
| Language sample successfully classified | 200 comments |
| Dominant language | `pt` |
| Dominant-language share | 95.50% |

The language sample is deterministic (`RANDOM_SEED=42`) and uses non-empty comments with at least three whitespace-delimited tokens. `pt` denotes Portuguese.

## Decision rationale

Most reviews have no comment text, and the available text is predominantly Portuguese. A defensible sentiment/topic module therefore requires a separately validated Portuguese NLP pipeline; generic English tooling would create misleading business signals. Score distribution and trend remain the governed fallback.

No sentiment analysis, keyword extraction, word cloud, or topic-modeling code is built in Phase 6. `GET /reviews/nlp-summary` exposes the governed score-distribution and trend fallback with this no-go status.
