# Retail IQ — Dataset Migration Addendum v2.1

**Relationship to prior documents:** extends `SRS-Migration-Addendum-v2.0.md`, which extends the v1.x clarification addenda and `SRS.md`. Resolves one data-integrity finding discovered empirically during Migration Phase M1. Updated authority order:

1. **This document (v2.1)**
2. SRS-Migration-Addendum-v2.0.md
3. SRS-Clarifications-Addendum-v1.4.md through v1.1
4. SRS.md v1.0
5. No undocumented assumptions

---

### Finding (confirmed by Codex during M1)

Each of the dataset's 10 distinct `State` values appears under all four `Region` values (North/South/East/West) in the raw data. **`State → Region` is not a valid functional dependency.** This is inconsistent with real-world Indian geography — a state cannot genuinely belong to all four zones — and indicates `Region`, as given, was very likely assigned independently of `State` during the dataset's synthetic generation, not derived from real geography.

This has two implications, not one:

1. **(Narrow, structural)** `state_geocode` cannot store one region per state, as Migration Addendum v2.0 §3 originally specified — `region` cannot be a column on a table keyed by `state` alone.
2. **(Broader, analytical)** `Region`, as given, is not a trustworthy geographic grouping for *any* analysis that assumes it reflects real regional structure. This affects `revenue_by_region`, the regional ANOVA test (§7), and the entire premise of the Regional Dashboard's region-level views (§9) — not just the one table Codex flagged.

### Resolution (binding — supersedes the `state_geocode` DDL in Migration Addendum v2.0 §3)

**a. `state_geocode` loses `region` entirely** — it becomes purely a coordinate lookup:

```sql
CREATE TABLE curated.state_geocode (
    state       VARCHAR PRIMARY KEY,
    latitude       DOUBLE PRECISION NOT NULL,
    longitude         DOUBLE PRECISION NOT NULL
);
```

**b. The raw dataset's own `Region` field is preserved, not deleted** — carried through as `region_as_reported` (on `curated.customers`, per v2.0 §3's existing placement). Kept for transparency and auditability, but documented explicitly in the post-clean data quality report as **not geographically reliable**, and never presented as if it were real geography.

**c. A new, separate static reference table provides the actually-correct mapping:**

```sql
CREATE TABLE curated.state_region_reference (
    state       VARCHAR PRIMARY KEY REFERENCES curated.state_geocode(state),
    region         VARCHAR NOT NULL   -- 'North' | 'South' | 'East' | 'West'
);
```

Populate from a standard, citable source (e.g. India's zonal council classification or an equivalent widely-used reference) — cite the source in the M1 completion report, the same discipline already required for `state_geocode`'s coordinates.

**d. Every consumer of "region" as a geographic grouping uses the `state_region_reference`-derived value, not `region_as_reported`.** This includes: the `revenue_by_region` mart, the regional ANOVA in Migration Addendum v2.0 §7, and every Regional Dashboard view in §9. `region_as_reported` may still be exposed as an independent filterable attribute if it's ever useful on its own terms, but it must never be labeled or implied as real geography anywhere in the UI or a report.

**e. This finding must be stated plainly in `analytics/reports/data_quality_report_post_clean.md`** as a genuine data-quality anomaly discovered during migration — not silently patched around. State the exact number of states/regions involved and the finding, the same way the original project documented the `review_id` duplicate-grain finding rather than quietly fixing it off the record.

---

*M1 may now be finalized and completed under this corrected design.*
