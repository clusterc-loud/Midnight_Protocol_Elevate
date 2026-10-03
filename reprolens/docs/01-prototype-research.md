# ReproLens Prototype Research & Strategic Analysis

**Date:** 2026-10-02  
**Basis:** reference/ReproLens_Project_Document.docx + docs/00-prototype-scope-analysis.md  
**Role:** Product Researcher & Hackathon Solution Strategist  
**Goal:** Deep-dive analysis of proposed prototype scopes to inform implementation decisions

---

## Executive Summary

This document analyses the three proposed prototype scopes (A: Single-Claim, B: Multi-Claim, C: Two-Paper) against the **core innovation** of ReproLens: the **claim-to-evidence chain** from paper table cell to code mapping to sandboxed execution to numerical comparison to evidence-backed discrepancy analysis.

The critical distinction from the project document:
- **E1 (Hard Evidence):** Directly observed log lines, parsed outputs, paper text spans, file contents, hashes
- **E2 (Auto-Inferred Evidence):** Deterministically derived AST findings, config keys, version numbers, command derivation
- **E3 (LLM Interpretation):** Probabilistic extraction proposals, mapping rankings, discrepancy hypotheses

**Bottom line:** The demo's credibility hinges on **maximising E1/E2 and minimising E3 in the critical path**. Real execution + real comparison = the differentiator from a paper summarizer.


---

## 1. What Exactly Would the User Do?

### Option A (Single-Claim)
| User Action | System Response |
|-------------|-----------------|
| 1. Open pre-built report.html | Sees: paper title, repo commit, 1 claim, 1 result |
| 2. Click Re-run button (optional) | Terminal shows: docker run... live logs metric extracted |
| 3. View comparison | Paper: 0.873 Reproduced: 0.869 Verdict: near_exact |
| 4. Inspect evidence drawer | Log line #42, paper page 6 table 3, mapping confirmed by human |

**Total user interaction:** ~30 seconds passive viewing, ~2 minutes if re-running live

### Option B (Multi-Claim) Recommended
| User Action | System Response |
|-------------|-----------------|
| 1. Run python run_demo.py | Terminal: progress bar, 3 sequential Docker runs with live log tails |
| 2. Watch execution | Each run: command stdout extracted metric comparison row added |
| 3. Open report.html | Comparison table with 3 rows, different verdicts (near_exact, partial, significant) |
| 4. Click claim row evidence drawer | Paper span (E1), mapped file (E1), log line (E1), discrepancy note (E2/E3 labelled) |
| 5. Toggle Show only discrepancies | Filters to rows with partial/significant verdicts |

**Total user interaction:** ~5-8 minutes live execution + report exploration

### Option C (Two-Paper)
| User Action | System Response |
|-------------|-----------------|
| 1. Select paper from dropdown | Loads pre-computed claims + mappings for that paper |
| 2. Run experiments | 2-4 Docker runs across two different repo environments |
| 3. View combined report | Side-by-side: Paper A (reproduces well) vs Paper B (data missing/version drift) |
| 4. Drill into Paper B failure | Evidence: HTTP 404 in setup.log (E1), missing dataset (E1), insufficient evidence verdict |

**Total user interaction:** ~10-15 minutes, more complex setup

---

## 2. What Would the System Actually Demonstrate?

| Capability | Option A | Option B | Option C |
|------------|----------|----------|----------|
| Claim extraction | Pre-loaded (E3 to E1 via human verification) | Pre-loaded (E3 to E1 via human verification) | Pre-loaded x2 |
| Claim-to-code mapping | Pre-curated (E2: human-verified file+command) | Pre-curated x3 (E2) | Pre-curated x2-4 |
| Sandboxed execution | 1 real Docker run | 3 real Docker runs | 2-4 real Docker runs |
| Metric extraction | Regex/JSON parse from stdout (E1) | x3 (E1) | x2-4 (E1) |
| Numerical comparison | abs_diff, rel_dev_pct, verdict (E1) | x3 with different outcomes (E1) | x2-4 with cross-paper contrast |
| Discrepancy analysis | Limited single case | Multiple worked examples (E1/E2) | Strongest: shows failure modes |
| Evidence traceability | Basic (3-4 evidence chips) | Rich (9-12 evidence chips) | Richest (cross-paper) |
| Honest limitations | Single seed badge | Single seed + variance caveats | Full limitation disclosure |

**Key insight:** Option B hits the **sweet spot** enough experiments to show *variety of outcomes* (near_exact, partial, significant) which proves the comparison engine works, without the environmental fragility of Option C.

---

## 3. Strongest Proof This Is More Than a Paper Summarizer

The project document is explicit: The PS makes the same point explicitly (code existence checks and summaries are insufficient). The platform therefore treats execution plus comparison as the core evidence and everything else as context.

**What proves it in the demo:**

| Proof Element | How It is Demonstrated | Evidence Tier |
|---------------|----------------------|---------------|
| Real execution happened | Live Docker logs streaming in terminal; container ID, image digest, wall time recorded | E1 (resource_stat, log_line) |
| Real numbers compared | Paper value 0.873 vs reproduced 0.869 abs_diff=-0.004 computed live | E1 (arithmetic on E1 sources) |
| Verdict from math, not LLM | if abs_diff/|r| < 0.01: near_exact deterministic rule | E2 (deterministic derivation) |
| Discrepancy has evidence | hyperparameter_mismatch: paper says n_estimators=500 (E1: paper p.5), config says 100 (E1: config.yaml:12) | E1+E1 to E2 cause |
| LLM clearly labelled | Any extraction/mapping marked LLM proposed, human confirmed or Rule-based | E3 explicitly badged |

**The smoking gun for judges:** Show the **live terminal** executing docker run, capturing stdout, parsing the metric, and computing the verdict not a pre-rendered animation. The report is the *artifact*, the live run is the *proof*.

---

## 4. What Needs Real Execution (Non-Negotiable)

Per the scope analysis (section 6), these **must** run live for credibility:

| Component | Why It Must Run | Implementation |
|---|---|---|
| Docker container start | Proves sandbox isolation works | docker run --rm -v repo:/repo ... |
| Dependency install | Proves environment reproducibility | In Dockerfile (pre-build) or entrypoint script |
| Experiment code execution | The entire point runs the actual repo code | python benchmark.py --model=rf ... |
| Metric extraction from stdout | Proves we read *actual output*, not hallucinated | Regex on last line or JSON parse |
| Numerical comparison | Core evidence real arithmetic on real numbers | Python float math, deterministic |
| Report generation with real numbers | Template filled with live-captured values | Jinja2/string template to HTML |

**What CAN be precomputed (with honest labelling):**
- Paper claim values (hardcoded from PDF, labelled E1: paper page X table Y)
- Mapping decisions (human-curated, labelled E2: human-confirmed mapping)
- Docker image (pre-built, labelled with image digest sha256)
- Repository clone (pre-cloned at known commit SHA)

---

## 5. What Can Be Deterministic (No LLM Needed)

| Task | Deterministic Approach | Evidence Tier |
|---|---|---|
| Claim to metric parsing | Known table structure to hardcoded JSON | E1 (human-verified) |
| Mapping claim to command | Human writes mappings.json | E2 (human-verified file+command) |
| Command derivation | No derivation needed command is explicit in mapping | E2 |
| Metric extraction | Regex: Test accuracy: (\d.+) or JSON accuracy | E1 (log_line) |
| Comparison math | abs_diff = reproduced - reported; rel_pct = abs_diff / abs(reported) | E2 (deterministic) |
| Verdict classification | Threshold rules: <1% near_exact, <5% partial, else significant | E2 (deterministic) |
| Evidence linking | Evidence IDs assigned programmatically during run | E1/E2 |
| Report rendering | Jinja2 template with structured data | E2 |

**All of the above can be pure Python zero LLM calls.**

---

## 6. Where Should an LLM Be Used (If At All)

Given hackathon constraints, **LLM use should be minimal and explicitly optional**:

| Potential LLM Use | Verdict | Rationale |
|---|---|---|
| Paper PDF to claim extraction | **AVOID** for prototype | Brittle, non-deterministic, not the core innovation |
| Repo analysis to entry point detection | **AVOID** | Complex, language-specific; pre-curate for demo |
| Claim to code mapping proposal | **OPTIONAL** (post-demo) | Could add LLM suggested this mapping as E3 badge for contrast |
| Discrepancy hypothesis generation | **OPTIONAL** (post-demo) | LLM suggests: check random seed labelled E3, never sole basis |
| Report narrative generation | **AVOID** | Template-based is more honest; LLM narratives risk hallucination |

**If team has extra time:** Add ONE LLM feature as a future work demo e.g., Here is what an LLM *would* propose for mapping (E3), here is what we actually used (E2 human-confirmed). This *strengthens* the E1/E2/E3 distinction.

---

## 7. Where Should an LLM NOT Be Trusted

| Area | Why Not Trust | Prototype Approach |
|---|---|---|
| Numerical comparison | LLMs bad at arithmetic; non-deterministic | Pure Python math (E2) |
| Verdict assignment | Subjective; must be rule-based for auditability | Deterministic thresholds (E2) |
| Causal claims | Hallucination risk; project doc: Never claim causality | Only Potential cause supported by evidence with E1/E2 |
| Evidence tier assignment | Would create circular logic | Hardcoded by evidence kind: log_line=E1, ast_finding=E2, llm_note=E3 |
| Mapping selection | CORE-Bench/PaperBench show agents fail at this | Human-confirmed for demo (E2) |
| Missing information detection | LLM cant know what is *actually* missing vs what it missed | Explicit checklist: seed not stated (E1: paper text search) |

---

## 8. What Could Fail During a Live Demo

### High-Probability Failures (Plan For These)

| Failure Mode | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Docker image pull/build timeout | High (network) | Demo stalls | **Pre-build image, load from tar** |
| Experiment exceeds time limit | Medium (ML variance) | Run hangs | **Hard timeout (15 min), kill switch** |
| Missing dataset download | High (external URLs rot) | Setup fails | **Vendor datasets in image or local volume** |
| Metric not in stdout (format change) | Medium | Comparison fails | **Test extraction regex on actual runs beforehand** |
| Python version / dependency conflict | Medium | ImportError | **Pin exact versions in Dockerfile** |
| OOM / memory limit | Low (CPU-only, small data) | Container killed | **4GB limit, test beforehand** |

### Low-Probability / Catastrophic

| Failure Mode | Mitigation |
|---|---|
| Docker daemon not running | Pre-check in script: docker info || exit 1 |
| Port conflicts | No ports exposed pure CLI |
| Disk space full | Clean up before demo: docker system prune -f |

### **Critical: Fallback Strategy (from scope analysis section 11)**
> **If live execution fails: switch to pre-recorded run (same UI in replay mode loaded from stored run records), and say so.**

Prepare: runs/RUN-001/stdout.log, stderr.log, resource.json, outputs/metrics.json feed to report generator identically.

---

## 9. Which Workflow Can Realistically Be Made Reliable?

### Recommended: Option B Multi-Claim Sequential Pipeline

`
PRE-HACKATHON (2-4 hours, once)
1. Select Fashion-MNIST paper + benchmark repo
2. Manually extract 3 claims from Table 1 (RF, LogReg, MLP)
3. Manually map each to: python benchmark.py --model=X
4. Build Dockerfile: python:3.11-slim + scikit-learn + deps
5. Test all 3 runs locally; capture exact metrics, times
6. Save: claims.json, mappings.json, Docker image tar

HACKATHON LIVE DEMO (5-8 minutes)
1. python run_demo.py
   Loads claims.json, mappings.json
   For each claim:
      a. docker run --rm -v repo:/repo image python ...
      b. Stream stdout/stderr to terminal (live proof)
      c. Parse metric via regex
      d. Compute verdict, append to results
   Render report.html from Jinja2 template
2. Open report.html in browser
   Comparison table with 3 rows, different verdicts
   Click row evidence drawer (paper span, log line, etc.)
   Toggle Show discrepancies only
3. If ANY run fails: fallback to pre-recorded logs
`

**Why this is reliable:**
- **Sequential** no concurrency bugs
- **Pre-tested** exact same commands, image, repo commit
- **Deterministic comparison** no LLM in critical path
- **Fallback ready** pre-recorded logs produce identical report
- **Visible execution** judges see Docker running, not a mock
Part 10 testPart 10 testPart 10 test
---

## 10. Visuals
Test line

---

## 10. What Makes the Demo Visually Impressive Without Backend Complexity

### High Impact / Low Effort Visuals
Visual Element  |  Implementation  |  Why It Works
---  |  ---  |  ---
Live terminal  |  subprocess.Popen + stdout.readline() loop + print()  |  Shows real execution
Evidence drawer  |  HTML details + CSS  |  Makes traceability tangible
Verdict badges  |  span class=badge near-exact=near_exact/span  |  Instant visual summary
Dot plot  |  Simple Chart.js or matplotlib  |  Visualises deviation
Progress bar  |  tqdm or manual print  |  Shows orchestration
Image digest + commit SHA  |  sha256:abc123...  |  Proves reproducibility
Single seed badge  |  Red outline badge  |  Honest limitation disclosure

### Implementation: Single HTML File (Zero Backend)
Implementation  |  Single HTML File (Zero Backend)
---
report.html - self-contained, no server needed
style
  .evidence-chip { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
  .E1 { background: #e8f5e9; border: 1px solid #4caf50; }  /* solid green */
  .E2 { background: #fff3e0; border: 1px dashed #ff9800; }  /* outlined orange */
  .E3 { background: #fce4ec; border: 1px dotted #e91e63; }  /* dashed pink */
  .badge.near_exact { background: #c8e6c9; color: #2e7d32; }
  .badge.partial { background: #ffe0b2; color: #e65100; }
  .badge.significant { background: #ffcdd2; color: #c62828; }
  .badge.not_executable { background: #e0e0e0; color: #616161; }
  details summary { cursor: pointer; font-weight: bold; }
/style
script
  document.querySelectorAll(.evidence-toggle).forEach(btn => {
    btn.onclick = () => document.getElementById(btn.dataset.target).classList.toggle(open);
  });
/script
**No React, no Vue, no server, no build step.** Opens in browser, works offline.

---

## 11. Evidence Tier Mapping for Prototype
Evidence Kind  |  Prototype Source  |  Tier  |  Example in Demo
---  |  ---  |  ---  |  ---
paper_span  |  Hardcoded from PDF (page, table, row, col)  |  E1  |  source: page=6 table=Table1 row=RandomForest col=Accuracy
table_cell  |  Same as above  |  E1  |  Value 0.873 from paper
file_range  |  Human-curated mapping mappings.json  |  E2  |  files=benchmark.py function=run_experiment
config_key  |  Human-curated or parsed from config.yaml  |  E2  |  hyperparameters=n_estimators=100
log_line  |  Captured from docker run stdout  |  E1  |  stdout.log:42 Test accuracy 0.869
package_version  |  pip freeze in Docker image  |  E1  |  scikit-learn==1.4.2
resource_stat  |  docker stats or /proc during run  |  E1  |  wall_s=41.2 peak_mem_mb=512
llm_note  |  Not used in prototype (or explicitly added for contrast)  |  E3  |  LLM proposed mapping to train.py (not used)


**Report rule (from project doc):** A conclusion that rests only on E3 is reported as Insufficient evidence.
Prototype enforces this: any finding without E1/E2 gets Insufficient evidence verdict.

---

## 12. Recommended Scope Decision

### Choose Option B (Multi-Claim) because:
Criterion  |  Option A  |  Option B  |  Option C
---  |  ---  |  ---  |  ---
Shows verdict variety  |  No (1 row)  |  Yes (3 rows: near_exact, partial, significant)  |  Yes (but more fragile)
Proves comparison engine  |  Weak  |  Strong  |  Strong
Discrepancy analysis demo  |  Limited  |  Multiple worked examples  |  Best (but risky)
Build time  |  4-6 hrs  |  8-12 hrs  |  16-24 hrs
Live demo reliability  |  Highest  |  High (tested 3x)  |  Medium (2 repos)
Judge impression  |  Nice toy  |  Working system  |  Impressive but did it run live

### Escalation Path
- **Week before hackathon:** Build Option A first (proves pipeline works)
- **If time permits:** Extend to Option B (add 2 more claims)
- **If ahead of schedule:** Prepare Option C assets (second paper) as stretch

---

## 13. Open Questions for Team

1. **Team size & skills:** How many people? Docker experience? Python/ML background?
2. **Hackathon duration:** 24h? 48h? When is demo due?
3. **Demo slot length:** 3 min? 5 min? 10 min?
4. **Hardware:** Dedicated machine with Docker? GPU available (even if not used)?
5. **Organiser paper set:** Will they provide papers, or do we bring our own?
6. **Fashion-MNIST repo confirmed:** Does github.com/zalandoresearch/fashion-mnist have a benchmark runner? Or need fork?
7. **LLM budget:** Any API credits? Or purely local models?

---

## 14. Next Steps (Concrete)

1. **Confirm Option B** as baseline scope
2. **Verify Fashion-MNIST benchmark repo** find exact benchmark.py or equivalent, test runtime
3. **Extract 3 claims manually** from paper Table 1 to claims.json
4. **Write 3 mappings manually** to mappings.json
5. **Create Dockerfile** with pinned dependencies, test all 3 runs
6. **Build run_demo.py** orchestration script
7. **Build report.html template** with evidence drawer
8. **Full rehearsal** measure times, capture fallback logs
9. **Document limitations** in report footer

---

**End of Research** Ready for team discussion and scope lock.
