# ReproLens Final Prototype Scope

**Decision Date:** 2026-10-02  
**Role:** Hackathon Technical Lead  
**Status:** SCOPE LOCKED -- This is the implementation boundary

---

## Selected Scope: Option B (Reduced) -- Two-Claim Verification

**Paper:** Fashion-MNIST Benchmark (Xiao et al., 2017)  
**Repository:** github.com/zalandoresearch/fashion-mnist (or benchmark fork) at pinned commit  
**Claims:** 2 experiments from Table 1 -- RandomForest and Logistic Regression accuracy  
**Demo Time:** 4-6 minutes live execution + report  
**Build Target:** 6-8 hours (single developer) / 4-6 hours (pair)

### Why Not Option A?
Fails to demonstrate **discrepancy analysis** and **verdict variety** -- two explicit PS deliverables. A single near-exact result looks like a toy.

### Why Not Option C?
Two repositories = double environment fragility. 16-24 hours build time is unrealistic for hackathon. High probability of live failure.

### Why Option B Reduced (2 claims, not 3)?
- MLP on Fashion-MNIST (70k samples) on CPU: likely 5-10+ minutes. Unacceptable risk.
- RandomForest + Logistic Regression: ~2-3 minutes each on CPU. Verifiable beforehand.
- Two claims = verdict variety possible (near_exact + near_exact, or near_exact + partial if we perturb one)
- Third claim adds 3+ minutes execution time + 30% more failure surface for marginal demo gain.

---

## 1. EXACTLY What the Prototype WILL Do

| # | Capability | Implementation |
|---|------------|----------------|
| 1 | **Load pre-extracted claims** | Read claims.json with 2 claims: RF (0.873), LogReg (0.851) -- each with paper page/table/row provenance |
| 2 | **Load pre-curated mappings** | Read mappings.json: claim to python benchmark.py --model=rf|logreg |
| 3 | **Execute in Docker sandbox** | docker run --rm -v repo:/repo -w /repo <image> python benchmark.py --model=X -- network disabled, 4GB RAM, 15-min timeout |
| 4 | **Stream live logs** | Print stdout/stderr line-by-line to terminal during execution |
| 5 | **Extract metric from stdout** | Regex: Test accuracy:\s+([\d.]+) on last relevant line |
| 6 | **Compute comparison** | abs_diff = reproduced - reported, rel_pct = abs_diff / abs(reported) * 100 |
| 7 | **Assign deterministic verdict** | < 1% to near_exact, < 5% to partial, else to significant |
| 8 | **Generate HTML report** | Jinja2 template to report.html with comparison table, evidence drawer, limitation badges |
| 9 | **Show evidence traceability** | Click row to drawer with E1 (paper span, log line), E2 (mapping, config) chips |
| 10 | **Fallback to pre-recorded** | If any run fails: load runs/RUN-XXX/ logs, generate identical report, display REPLAY MODE banner |

---

## 2. EXACTLY What the Prototype Will NOT Do

| Category | Excluded Items |
|----------|----------------|
| **Paper processing** | PDF upload, text extraction, table parsing, OCR, arXiv fetch |
| **Repo analysis** | Auto-clone, AST parsing, config scanning, entry-point detection, language detection |
| **Mapping** | LLM-assisted mapping, embedding search, candidate ranking, confidence scoring |
| **Multi-seed** | Multiple seeds, variance estimation, statistical tests |
| **Follow-up experiments** | Ablation runs, hyperparameter sweeps, automatic cause investigation |
| **UI** | Multi-screen stepper, project dashboard, settings, auth, user management |
| **Persistence** | Database, multi-project, session storage, API, REST endpoints |
| **Advanced discrepancy** | Automated cause ranking, settling checks, causal language |
| **Scalability** | Parallel execution, queue management, resource scheduling |
| **Security hardening** | gVisor, rootless Docker, network policies, capability dropping (beyond basic) |
| **LLM in critical path** | Zero LLM calls during extraction, mapping, comparison, verdict, report generation |

---

## 3. Single Primary Demo Scenario

**Title:** Reproducing Fashion-MNIST Benchmark Claims

**Narrative (30 seconds):**
We took the Fashion-MNIST paper (Table 1) and their repository. The paper claims RandomForest = 87.3% and Logistic Regression = 85.1% accuracy. We mapped each claim to the repo benchmark runner, executed both in fresh Docker sandboxes, and compared the actual outputs to the paper. Here is the live run...

**Flow:**
1. python run_demo.py -- terminal shows progress bar
2. Run 1: RandomForest -- live logs stream to metric extracted to verdict displayed
3. Run 2: LogisticRegression -- live logs stream to metric extracted to verdict displayed
4. report.html opens in browser -- comparison table with 2 rows
5. Click row to evidence drawer opens (paper span, log line, mapping)
6. Presenter notes: Numbers come from execution. Mapping human-confirmed. Single seed -- variance not estimated.

**Total live time:** ~4 minutes execution + ~1 minute report walkthrough

---

## 4. Paper / Repository for Demo

| Item | Specification |
|------|---------------|
| **Paper** | Fashion-MNIST: a Novel Image Dataset for Benchmarking Machine Learning Algorithms (Xiao, Rasul, Vollgraf, 2017) -- arXiv:1708.07747 |
| **Table** | Table 1: Classification accuracies on Fashion-MNIST test set |
| **Claims** | Row RandomForest to 0.873; Row LogisticRegression to 0.851 |
| **Repository** | https://github.com/zalandoresearch/fashion-mnist (official) -- must verify it has benchmark.py or equivalent runner |
| **Commit** | Pinned to specific SHA (e.g., a1b2c3d) -- tested beforehand |
| **Fallback** | If official repo lacks runner: use https://github.com/fashion-mnist/benchmark fork |

**Pre-hackathon verification (MANDATORY):**
- Clone repo at pinned commit
- Find exact benchmark command (e.g., python benchmark.py --model rf)
- Run both experiments locally on CPU -- confirm < 3 min each
- Capture exact stdout format for regex
- Build Docker image -- confirm it runs
- Save runs/ logs as fallback

---

## 5. Exact Experiments Executed

| Experiment | Claim | Command | Expected Runtime | Expected Verdict |
|------------|-------|---------|------------------|------------------|
| EXP-001 | RandomForest accuracy = 0.873 | python benchmark.py --model rf | 2-3 min | near_exact (or partial if env differs) |
| EXP-002 | LogisticRegression accuracy = 0.851 | python benchmark.py --model logreg | 2-3 min | near_exact (or partial if env differs) |

**If MLP is verified < 3 min:** Add as EXP-003 (bonus, not required).

**Perturbation for discrepancy demo (optional, pre-recorded):**
- Run EXP-001 with --n-estimators 10 (vs paper 100) to expect significant deviation
- Include in report as what if note with evidence -- NOT executed live

---

## 6. Which Steps Are REAL (Live Execution)

| Step | Real? | Evidence |
|------|-------|----------|
| Docker container start | YES | docker run visible in terminal |
| Dependency availability | YES | Pre-built image; pip freeze in image |
| Experiment code execution | YES | Actual repo benchmark.py runs |
| Stdout/stderr capture | YES | Streamed live to terminal |
| Metric extraction | YES | Regex on actual stdout |
| Numerical comparison | YES | Python arithmetic on captured values |
| Verdict assignment | YES | Deterministic threshold check |
| Report rendering | YES | Jinja2 template with live values |

---

## 7. Which Steps Are DETERMINISTIC (No Randomness)

| Step | Deterministic? | Notes |
|------|----------------|-------|
| Claim loading | YES | JSON parse |
| Mapping loading | YES | JSON parse |
| Command construction | YES | String from mappings.json |
| Docker run invocation | YES | Same command every time |
| Metric regex extraction | YES | Same pattern, same stdout |
| abs_diff / rel_pct math | YES | IEEE 754 float |
| Verdict thresholds | YES | Hardcoded constants (1%, 5%) |
| Evidence ID assignment | YES | Sequential integers |
| HTML template rendering | YES | Jinja2 with dict input |

---

## 8. Which Steps Use an LLM

**NONE.** Zero LLM calls in the critical path.

**Optional (post-demo only, if time permits):**
- LLM Mapping Proposal badge in evidence drawer showing what an LLM *would* have suggested (E3) -- static, pre-computed, clearly labelled
- This is a **contrast demonstration**, not part of the workflow

---

## 9. Which Steps Are Precomputed (With Honest Labelling)

| Step | Precomputed? | Label in Report |
|------|--------------|-----------------|
| Paper claim values (0.873, 0.851) | YES | E1: Paper Table 1, Row X, Col Accuracy |
| Claim provenance (page, table, row) | YES | E1: Paper p.4, Table 1 |
| Claim-to-command mapping | YES | E2: Human-confirmed mapping |
| Repository commit SHA | YES | E1: Repo commit a1b2c3d |
| Docker image digest | YES | E1: Image sha256:abc123... |
| Fallback run logs | YES | REPLAY MODE: Pre-recorded run (banner) |

**Honesty rule:** Every precomputed value displays its evidence tier badge (E1/E2). No simulated step is unlabelled.

---

## 10. What Evidence Is Shown to the User

### In Terminal (Live)
- docker run command
- Streaming stdout/stderr
- Extracted metric: Extracted accuracy: 0.869
- Verdict: Verdict: near_exact (rel_dev: -0.46%)

### In Report (HTML)
| Element | Evidence Shown | Tier |
|---------|----------------|------|
| Paper claim value | 0.873 + Table 1, Row RandomForest, Col Accuracy | E1 |
| Reproduced value | 0.869 + stdout.log line 42 | E1 |
| Comparison math | abs_diff: -0.004, rel_dev_pct: -0.46% | E2 |
| Verdict | near_exact + threshold rule | E2 |
| Mapping | benchmark.py --model rf + mappings.json | E2 |
| Environment | Image digest, commit SHA, sklearn version | E1 |
| Limitations | Single seed, Human-curated mapping, CPU-only | Badges |

### Evidence Drawer (Click Row)
- E1 Paper span: Table 1 to RandomForest to Accuracy to 0.873
- E1 Log line: stdout.log:42 Test accuracy: 0.869
- E2 Mapping: mappings.json to python benchmark.py --model rf
- E2 Config: benchmark.py defaults: n_estimators=100
- E3 (optional) LLM proposed: train.py (not used)

---

## 11. Final Demo Appearance

### Terminal (Live)
python run_demo.py
[ReproLens] Loading claims.json... 2 claims
[ReproLens] Loading mappings.json... 2 mappings
[ReproLens] Docker image: sha256:abc123... (pre-built)
[ReproLens] Repo commit: a1b2c3d (pinned)

EXP-001: RandomForest
Command: python benchmark.py --model rf
[docker] Starting container...
[docker] Loading Fashion-MNIST data...
[docker] Training RandomForest (n_estimators=100)...
[docker] Test accuracy: 0.869
[docker] Container exited (0), wall: 112s, peak_mem: 384MB
Extracted: 0.869
Reported: 0.873 | abs_diff: -0.004 | rel: -0.46%
Verdict: near_exact

EXP-002: LogisticRegression
Command: python benchmark.py --model logreg
[docker] Starting container...
[docker] Training LogisticRegression (max_iter=100)...
[docker] Test accuracy: 0.848
[docker] Container exited (0), wall: 87s, peak_mem: 256MB
Extracted: 0.848
Reported: 0.851 | abs_diff: -0.003 | rel: -0.35%
Verdict: near_exact

[ReproLens] Rendering report.html...
[ReproLens] Done. Open report.html in browser.

### Report.html (Browser)
ReproLens Assessment: Fashion-MNIST Benchmark
Paper: arXiv:1708.07747 | Repo: a1b2c3d | Image: sha256:abc...
Env: Python 3.11, sklearn 1.4.2 | CPU-only | 4GB RAM

Comparison Table
Claim | Reported | Reproduced | Abs Diff | Rel% | Verdict
RF | 0.873 | 0.869 | -0.004 | -0.46% | near_exact
LogReg | 0.851 | 0.848 | -0.003 | -0.35% | near_exact

Evidence (click row to expand)
RF: E1: Paper Table 1 E1: stdout.log:42 E2: map
LR: E1: Paper Table 1 E1: stdout.log:38 E2: map

Limitations: Single seed, Human-curated mapping, CPU-only, sklearn version not in paper

### Fallback Mode (If Live Fails)
- Identical report.html
- Top banner: REPLAY MODE -- Live execution failed; showing pre-recorded run from 2026-10-01
- All evidence, verdicts, numbers identical

---

## Scope Boundary Enforcement

**If anyone proposes adding:** to **Reject with reference to this document**

| Proposal | Response |
|----------|----------|
| Add PDF upload | Not in scope -- pre-extracted claims only |
| Add LLM for mapping | Not in scope -- human-curated only |
| Add 3rd experiment (MLP) | Only if verified < 3 min CPU beforehand |
| Add multi-seed | Not in scope -- single seed with badge |
| Add database/API | Not in scope -- JSON + CLI only |
| Add web UI with steppers | Not in scope -- single HTML report only |
| Auto-detect benchmark command | Not in scope -- explicit in mappings.json |
| Auto-discrepancy analysis | Not in scope -- manual what if notes only |

---

## Go/No-Go Criteria (Pre-Hackathon)

| Check | Required? | Owner | Deadline |
|-------|-----------|-------|----------|
| Repo has working benchmark.py --model rf|logreg | YES | Team | T-7 days |
| Both experiments < 3 min on CPU | YES | Team | T-5 days |
| Docker image builds and runs | YES | Team | T-3 days |
| Regex extracts metric from stdout | YES | Team | T-3 days |
| Fallback logs captured | YES | Team | T-1 day |
| Report.html renders with evidence drawer | YES | Team | T-1 day |
| Full rehearsal (live + fallback) | YES | Team | T-0 (day of) |

**If ANY check fails to Fall back to Option A (Single-Claim: RandomForest only)**

---

## Appendix: File Structure (Prototype)

reprolens-prototype/
run_demo.py              # Main orchestration script (~150 lines)
claims.json              # 2 claims with provenance
mappings.json            # 2 mappings: claim to command
Dockerfile               # python:3.11-slim + sklearn + deps
report_template.html     # Jinja2 template with CSS/JS
repo/                    # Shallow clone at pinned commit (gitignore)
runs/                    # Fallback logs (gitignore)
    RUN-001/             # RF stdout, stderr, resource.json
    RUN-002/             # LR stdout, stderr, resource.json
report.html              # Generated output (gitignore)

---

**SCOPE LOCKED.** Implementation begins from this boundary.
