# Retail Business Intelligence Platform
## SRS Clarification Addendum v1.3

**Relationship to prior documents:** extends v1.2 → v1.1 → `SRS.md` v1.0. Changes Power BI from the v1.0 footnote status ("optional export path... not built in v1") to real, in-scope work. Updated authority order:

1. This document (v1.3)
2. SRS Clarification Addendum v1.2
3. SRS Clarification Addendum v1.1
4. Base SRS v1.0
5. No undocumented assumptions

---

### 21. Power BI Integration — now in scope

**What changes:** `SRS.md` §7.3 listed Power BI as an optional, undeveloped export path. It is now a real deliverable: the `marts` schema must be safely connectable from Power BI Desktop, with documentation and DAX measures consistent with the web dashboard's numbers.

**What does not change:** the custom web dashboard (Next.js, Phase 7) remains the primary product. Power BI is an additional consumer of the same `marts` data, not a replacement for any planned page.

### 21.1 Access & credential boundary (binding)

This is the part that needed explicit resolution rather than a blanket grant:

| Access Codex has | Access Codex does **not** have |
|---|---|
| Ability to create a new, dedicated PostgreSQL role (`powerbi_reader`) via migration, scoped **read-only to the `marts` schema only** | Any Microsoft account, Power BI Service workspace, Azure AD app registration, or OAuth credential |
| Ability to add `POWERBI_READER_PASSWORD` to `backend/.env.example` and ask the human to set it in their own `.env` — same pattern already used for `JWT_SECRET`, `ADMIN_PASSWORD`, etc. | Any instruction to prompt the user for a personal Microsoft/Power BI login, or to attempt Power BI Service publishing/authentication on the user's behalf |
| Ability to write connection documentation and a DAX measure library | Ability to install or drive Power BI Desktop itself — it is a licensed, Windows-only GUI application; Codex's environment cannot operate it, and should say so rather than attempt to fake an artifact it can't actually produce |

**Rule:** if Codex hits a point where it believes it needs a real third-party login to proceed (Microsoft account, Power BI Service, anything outside this repo's own infrastructure), it must **stop and ask the human directly**, the same as any other unspecified decision — it does not proceed on the assumption that "access to everything" was intended to cover external accounts. Internal, project-owned secrets (the new DB role's password) follow the existing `.env` pattern and do not require this pause.

### 21.2 What gets built

1. **Database layer** — `powerbi_reader` role, least privilege:
```sql
CREATE ROLE powerbi_reader LOGIN PASSWORD :'powerbi_reader_password'; -- from env, never hardcoded
GRANT CONNECT ON DATABASE retail_bi TO powerbi_reader;
GRANT USAGE ON SCHEMA marts TO powerbi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO powerbi_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO powerbi_reader;
-- No grants on raw, curated, or ml — those carry internal/PII-adjacent
-- fields (zip/city-level location, model artifacts) with no reason to be
-- exposed to a BI client.
```
2. **Documentation deliverable** — `docs/powerbi-integration.md`, containing: the Postgres connection parameters (server/database/port, using the `powerbi_reader` role — password supplied by the human, never committed); an Import-vs-DirectQuery recommendation (Import is the default recommendation given the dataset's size and the fact that marts already refresh nightly per SRS §8.3 — DirectQuery only if a stakeholder specifically needs live/on-demand refresh); the recommended table relationships between the `marts` tables (to be written **once the mart-grain question in this phase's report is resolved**, so the documented model matches what was actually built, not what §8.3 assumed); and a full DAX measure library that reimplements the Addendum §7 business-metrics dictionary exactly (Revenue, AOV, Customer Count, MoM/YoY growth, CLV) — this is the part that matters most: if Power BI computes "Revenue" with different logic than the web dashboard's `/dashboard/summary` endpoint, the two tools will disagree, which is precisely the KPI-inconsistency risk Addendum §7 was written to prevent. The DAX must be a direct translation of the same rule, not a reinterpretation.
3. **`.pbit` template — best effort, not guaranteed.** If Codex's environment has a reliable way to produce a valid Power BI template file, it may attempt one, pre-wired with the relationships and DAX measures above. If it does not, it should say so plainly in its report rather than produce something that looks like a `.pbit` but isn't valid — the documentation in item 2 is the guaranteed deliverable either way, and is sufficient for a human to build the report themselves in Power BI Desktop in under the time it would take to debug a broken template.

### 21.3 Phase placement (no renumbering)

- **Phase 5 (API Layer)** gains one task: create the `powerbi_reader` role/grants migration and the `POWERBI_READER_PASSWORD` env var — natural to do alongside the rest of that phase's access-control work (JWT, auth tables).
- **Phase 9 (Deployment & Documentation)** gains the finalized `docs/powerbi-integration.md` and a corresponding line in the README's **Features** section (SRS §20, item 9) — not "Future Scope" (item 12), since this is now real, built functionality, not an aspiration.

---

*This addendum does not authorize any phase to begin early. Phase 5's Power BI task is scoped now so it isn't forgotten; it is still built during Phase 5, not before.*
