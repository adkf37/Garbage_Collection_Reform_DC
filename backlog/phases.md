# Project Phases

## Phase 1: Planner (COMPLETE)
**Outcome**: `backlog/plan.md` and initial task files created.
**Artifacts**: `backlog/plan.md`, `backlog/tasks/01-06`

## Phase 2: Squad Init (COMPLETE)
**Outcome**: Squad CLI initialized; team assembled with 6 agents.
**Artifacts**: `.squad/team.md`, `.squad/routing.md`, `.squad/decisions.md`,
`.squad/agents/*/charter.md`

## Phase 3: Squad Review (COMPLETE)
**Outcome**: All task files fully detailed, sprint plan created, ready for coding.
**Artifacts**: `backlog/tasks/` (detailed), `backlog/README.md`,
`backlog/data_sources.md`, `backlog/phases.md`, `.squad/sprint.md`

## Phase 4: Coder (CURRENT)
**Objective**: Implement all six backlog tasks in dependency order.

### Execution Order
```
Task 01 (research)  ─────────────────────────────→ [independent]
Task 02 (spatial)   ──→ Task 03 (placement) ──→ Task 04 (capacity)
                                             ──→ Task 05 (cost)
                    Tasks 03+04+05 ───────────→ Task 06 (app+report)
```

### Coder Phase Completion Criteria
- [ ] `research/barcelona_shared_waste.md` exists with all required sections
- [ ] `data/raw/dc_addresses.parquet` and `dc_blocks.parquet` exist
- [ ] `data/processed/container_locations.parquet` exists
- [ ] `data/processed/capacity_analysis.json` exists
- [ ] `data/processed/cost_analysis.json` exists
- [ ] `streamlit run app/app.py` runs without errors
- [ ] `quarto render report/ironcurb.qmd` renders without errors

## Phase 5: Tester
**Objective**: Validate all outputs against acceptance criteria in task files.

### Tester Phase Completion Criteria
- [ ] All acceptance criteria in all 6 task files verified
- [ ] Edge cases documented (missing data, API failures, etc.)
- [ ] Performance benchmarks validated (<60s for placement, <1s for app lookup)

## Phase 6: Reviewer
**Objective**: Final review, fact-checking, polish.

### Reviewer Phase Completion Criteria
- [ ] All assumption values cross-checked against sources
- [ ] Report reviewed for accuracy and clarity
- [ ] No broken references or missing figures in report
- [ ] README.md and AGENTS.md updated if needed
