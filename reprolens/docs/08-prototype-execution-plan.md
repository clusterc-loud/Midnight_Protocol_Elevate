# ReproLens Prototype Execution Plan

**Date:** 2026-10-02  
**Authority:** docs/03-final-prototype-scope.md (SCOPE LOCKED)  
**References:** docs/05-prototype-architecture.md, docs/06-prototype-ui-ux.md  
**Goal:** Translate approved architecture/UI into actionable coding plan for hackathon prototype

---

## 1. Project Structure

`
reprolens-prototype/
run_demo.py              # Main orchestration script (~150 lines)
claims.json              # 2 claims with E1 provenance
mappings.json            # 2 mappings: claim to command
Dockerfile               # python:3.11-slim + sklearn==1.4.2
report_template.html     # Jinja2 template with embedded CSS/JS
reprolens-demo.tar       # Pre-built Docker image (gitignore)
repo/                    # Shallow clone at pinned SHA (gitignore)
runs/                    # Fallback logs (gitignore)
    RUN-001/             # RF stdout, exit_code, wall_sec, peak_mb
    RUN-002/             # LR stdout, exit_code, wall_sec, peak_mb
report.html              # Generated output (gitignore)
`

---

## 2. Implementation Phases (Critical Path Order)

### Phase 0: Pre-Hackathon Setup (MUST complete before hackathon)
**Objective:** All manual prep work done; environment verified

| Task | Output | Verification |
|------|--------|--------------|
| 0.1 Clone repo at pinned commit | repo/ directory | cd repo && git log -1 --oneline |
| 0.2 Find benchmark command | Exact command string | python benchmark.py --model rf runs |
| 0.3 Run both experiments locally | Captured stdout | Regex extracts metric; < 3 min each |
| 0.4 Build Docker image | reprolens-demo image | docker images reprolens-demo |
| 0.5 Save image to tar | reprolens-demo.tar | docker load < reprolens-demo.tar works |
| 0.6 Capture fallback logs | runs/RUN-001/, RUN-002/ | Directory structure exists |
| 0.7 Write claims.json | 2 claims with provenance | JSON valid, matches Table 1 |
| 0.8 Write mappings.json | 2 mappings with commands | JSON valid, commands work |

**Dependencies:** None (all manual)  
**Done when:** All 8 verification checks pass

---

### Phase 1: Core Orchestration Script (run_demo.py)
**Objective:** Minimal working vertical slice - run one experiment end-to-end

**Files to create/modify:**
- run_demo.py (new)

**Functionality to implement:**
1. Load claims.json and mappings.json
2. Verify Docker daemon (docker info)
3. For ONE claim (EXP-001):
   - Run docker run with streaming stdout
   - Extract metric via regex
   - Compute comparison (abs_diff, rel_pct, verdict)
   - Build evidence objects
4. Render report.html via Jinja2
5. Fallback mechanism: on any failure, load pre-recorded logs

**Inputs:** claims.json, mappings.json, repo/, Docker image  
**Outputs:** Console logs, report.html  
**Dependencies:** Phase 0 complete  

**How to test:** python run_demo.py -> see live logs -> opens report.html  
**Done when:** Single experiment runs live, produces report with verdict

---

### Phase 2: Multi-Experiment Loop + Fallback
**Objective:** Run both experiments sequentially with full fallback

**Files to modify:**
- run_demo.py (extend loop over all claims)

**Functionality to implement:**
1. Loop over all claims in claims.json
2. Sequential execution with progress counter (EXP-001/2, EXP-002/2)
3. Fallback logic per experiment:
   - Timeout -> load fallback
   - Non-zero exit -> load fallback
   - Metric extraction failure -> load fallback
4. Track replay_mode flag
5. Aggregate results for report

**Inputs:** Phase 1 complete  
**Outputs:** Both experiments run, results aggregated  
**Dependencies:** Phase 1  

**How to test:** python run_demo.py -> both experiments run -> report has 2 rows  
**Done when:** Both experiments complete (live or fallback), report has 2 verdicts

---

### Phase 3: Evidence Model + Data Structures
**Objective:** Build evidence objects with E1/E2/E3 tagging for report

**Files to modify:**
- run_demo.py (add evidence building functions)

**Functionality to implement:**
1. EVIDENCE_TIER map (hardcoded)
2. make_evidence(kind, ref, excerpt) -> dict with id, tier, kind, ref, excerpt
3. build_evidence(claim, mapping, stdout, metric, comparison) -> list of evidence dicts
4. Per experiment: paper_span (E1), log_line (E1), mapping (E2), package_version (E1)
5. Discrepancy notes (pre-written, E2)

**Inputs:** Phase 2 complete  
**Outputs:** Evidence list passed to template  
**Dependencies:** Phase 2  

**How to test:** Verify report shows E1/E2 chips in evidence drawer  
**Done when:** Evidence drawer shows chips with correct tier styling

---

### Phase 4: Report Template (report_template.html)
**Objective:** Self-contained HTML report with evidence drawers

**Files to create:**
- report_template.html (new)

**Functionality to implement:**
1. Header: Paper title, arxiv link, repo commit, image digest, env, REPLAY MODE banner
2. Summary Cards: 5 cards (near_exact, partial, significant, not_executable, insufficient)
3. Comparison Table: Claim, Reported, Reproduced, Abs Diff, Rel%, Verdict + E1 chips
4. Evidence Drawers: <details> per row with chips + discrepancy notes
5. Limitations Footer: 4 badges + Evidence tier legend
6. Embedded CSS (E1/E2/E3 chips, verdict badges, drawers, tooltips)
7. Embedded JS (drawer toggle, ~10 lines)

**Inputs:** Phase 3 complete (data structures defined)  
**Outputs:** report.html rendered by Jinja2  
**Dependencies:** Phase 3  

**How to test:** Open report.html in browser -> verify all elements render  
**Done when:** Report renders correctly, drawers toggle, chips show correct colors

---

### Phase 5: Pre-Hackathon Verification & Rehearsal
**Objective:** Full end-to-end rehearsal; all Go/No-Go checks pass

**Tasks:**
1. Run all 7 mandatory checks from docs/03 (Go/No-Go Criteria)
2. Full live run: python run_demo.py -> verify terminal output matches spec
3. Open report.html -> verify all UI elements (table, drawers, chips, badges)
4. Test fallback: kill Docker mid-run -> verify REPLAY MODE banner appears
5. Measure total demo time (target: 4-6 min execution + 1 min report)
6. Document any issues and fixes

**Done when:** All 7 Go/No-Go checks pass + full rehearsal successful

---

