# Work Routing

How to decide who handles what for Project IRONCURB.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|---------|
| Architecture & technical decisions | Lead | CRS selection, algorithm design, pipeline structure |
| Data fetching & pipeline scripts | Data Engineer | `src/fetch_dc_data.py`, parquet generation, API integration |
| Geospatial analysis & container placement | Geo Developer | `analysis/container_placement.py`, distance thresholds, k-means clustering |
| Capacity & cost modeling | Data Engineer | `analysis/capacity_model.py`, `analysis/cost_model.py` |
| Interactive map & Streamlit app | Geo Developer | `app/app.py`, folium maps, address lookup |
| Research & written summaries | Scribe | `research/barcelona_shared_waste.md`, `report/ironcurb.qmd` |
| Code review | Lead | Review PRs, check quality, suggest improvements |
| Testing & validation | Tester | Write tests, verify outputs, check acceptance criteria |
| Scope & priorities | Lead | What to build next, trade-offs, decisions |
| Session logging | Scribe | Automatic — never needs routing |
| Memory & cross-session context | Ralph | Store facts, surface prior decisions |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Lead |
| `squad:data-engineer` | Data pipeline, fetch scripts, modeling | Data Engineer |
| `squad:geo-developer` | Spatial analysis, container placement, app | Geo Developer |
| `squad:tester` | Testing, validation, acceptance criteria | Tester |
| `squad:scribe` | Documentation, report writing, history | Scribe |
| `squad:ralph` | Memory consolidation, context sync | Ralph |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, the **Lead** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

## Task-to-Agent Mapping (Backlog)

| Backlog Task | Primary Agent | Supporting Agent |
|-------------|--------------|-----------------|
| 01 — Barcelona Research | Scribe | Lead |
| 02 — DC Spatial Baseline | Data Engineer | Geo Developer |
| 03 — Container Placement | Geo Developer | Data Engineer |
| 04 — Capacity Model | Data Engineer | Lead |
| 05 — Cost & Parking Model | Data Engineer | Lead |
| 06 — App & Report | Geo Developer | Scribe |

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. The Lead handles all `squad` (base label) triage.
8. **CRS is always EPSG:2248** — all spatial work must use NAD83 / Maryland State Plane (US feet). Route any CRS inconsistency to Geo Developer immediately.
