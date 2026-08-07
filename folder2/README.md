# Retail IQ — Power BI progress dashboard pack

This separate faculty-demo folder presents the real work completed through Phase 3. It does not modify the governed frontend or claim that later phases are complete.

## View immediately

Open `preview/index.html` in a browser. It works without Docker, a database, or a Microsoft account.

## Build in Power BI Desktop

1. Run `python scripts/generate_progress_data.py` from this folder whenever the analytics reports change.
2. Open Power BI Desktop and choose **Get data → Text/CSV**. Import every CSV in `data/`.
3. Apply `powerbi/RetailIQ-Progress-Theme.json` from **View → Themes → Browse for themes**.
4. Add the measures from `powerbi/progress-measures.dax` and construct the four pages in `dashboard-spec.md`.
5. Save the local report as `RetailIQ-Progress-Dashboard.pbix` in this folder. PBIX is intentionally ignored because it is a generated binary; the reproducible sources remain version controlled.

`powerbi/PowerQuery.pq` supplies a parameterized import pattern if folder-based refresh is preferred. No Microsoft, Azure, or Power BI Service credentials are required.

## Evidence contract

- Dataset numbers are parsed from `analytics/reports/`, not fabricated.
- Delivered revenue and AOV use the project metric contract: delivered orders only, item price plus freight, purchase timestamp as the date axis.
- Cleaning and preprocessing are visible: layer row counts, reconciliation, duplicate handling, and retained outlier flags.
- The preview reports Phases 1–3 complete and Phase 4 onward pending because no checked-in target-selection report currently exists.

Power BI Desktop is not installed on this machine, so a genuine `.pbix` binary cannot be produced or visually verified here. The browser preview and reproducible Power BI assets provide the dashboard now without pretending that a renamed or fabricated file is a valid PBIX.
