# ReproLens Prototype Competitor Analysis

**Date:** 2026-10-02  
**Context:** Hackathon prototype (Option B: Multi-Claim, Fashion-MNIST paper)  
**Reference:** references/ReproLens_Project_Document.docx Section 7 (Existing Solutions) + Section 8 (Research Gap)  
**Goal:** Answer What can our prototype demonstrate that makes ReproLens distinct from simply tracking an ML experiment?

---

## The Core Question

Experiment tracking tools (MLflow, DVC, W&B) answer: What did I run, with what parameters, and what were the metrics?  
They assume the author is the user, running their own code in their own environment.

ReproLens answers: Given this paper claimed result and this repository, does the code actually produce that number and if not, why?  
The user is a third party (reviewer, reader, researcher) assessing someone else work.

The prototype must demonstrate this distinction concretely.

---

## 1. Overlapping Functionality

What the prototype shares with existing tools (and what judges might mistake it for):

| Capability | MLflow / DVC / W&B | Docker / repo2docker | ReproLens Prototype |
|------------|-------------------|---------------------|---------------------|
| Environment capture | MLflow Projects, DVC pipelines | Docker images, repo2docker builds | Pre-built Docker image (same) |
| Parameter/metric logging | Automatic via API / mlflow.log_metric | Manual / via ReproZip trace | Regex extraction from stdout (manual) |
| Run history / comparison UI | MLflow UI, W&B dashboard, DVC metrics diff | N/A | Single HTML report with comparison table |
| Code versioning | Git commit via MLflow/DVC | Image digest + repo commit SHA | Image digest + repo commit SHA (pinned) |
| Re-execution | mlflow run, dvc repro | docker run | docker run (same command) |

What this means for the demo:  
If the prototype only shows we ran code in Docker and logged metrics, judges will correctly categorise it as another experiment tracker. The differentiation must be visible in the workflow, not the infrastructure.

---

## 2. Genuinely Differentiating Workflow

The prototype demonstrates a seven-step chain that no single existing tool covers end-to-end:

| Step | What Existing Tools Do | What ReproLens Prototype Does | Why It is Different |
|------|------------------------|------------------------------|-------------------|
| 1. Paper + Repo as input | Not applicable (tools start from code) | Pre-loaded paper PDF + repo at known commit | Starts from claim, not code |
| 2. Claim extraction | Not applicable | Pre-extracted claims from Table 1 (RF: 0.873, LogReg: 0.851, MLP: 0.862) with page/table/row provenance | Claims have paper provenance (E1), not just parameter logs |
| 3. Claim to code mapping | User manually chooses run | Human-curated mappings.json: claim to python benchmark.py --model=rf | Mapping is explicit and auditable (E2), not implicit in logging code |
| 4. Controlled execution | Author environment (MLflow) or dvc repro | Fresh Docker container per run, network disabled, CPU/memory limits | Sandbox is independent of author environment |
| 5. Reported vs reproduced comparison | Compare your runs against each other | Compare paper value (0.873) vs reproduced value (0.869) to abs_diff=-0.004, rel_dev_pct=-0.46% | Comparison is paper to execution, not run to run |
| 6. Discrepancy analysis with evidence | Not applicable | Hyperparameter mismatch: paper says n_estimators=500 (E1: p.5), config says 100 (E1: config.yaml:12) | Finds specific, evidence-backed causes, not just metrics differ |
| 7. Evidence-backed assessment | Dashboard with metrics | Report with verdict (near_exact/partial/significant) + evidence chips (E1/E2/E3) per finding | Every conclusion traces to source |

The prototype proves this by showing:
- Paper claim values hardcoded but labelled with page/table/cell (E1)
- Mapping explicit in mappings.json (E2: human-confirmed file+command)
- Live Docker execution streaming stdout (E1: log_line)
- Regex extraction from actual stdout (E1: log_line)
- Deterministic comparison math (E2: abs_diff/rel_dev_pct)
- Verdict from thresholds, not LLM (E2: <1% to near_exact)
- Discrepancy note citing paper span + config file (E1+E1 to E2 cause)

---

## 3. Features Unnecessary for Demonstrating Differentiation

These exist in the full project design but add no differentiation value for the prototype. Including them wastes time and risks looking like feature parity with tracking tools.

| Feature | Why It is Unnecessary for Prototype | What to Do Instead |
|---------|-----------------------------------|---------------------|
| Arbitrary paper upload + PDF parsing | MLflow does not parse PDFs either; not the differentiator | Pre-extract 3 claims manually to claims.json |
| Arbitrary repo URL + auto-clone | Tracking tools assume you have the repo; ReproLens differentiates at claim mapping, not clone | Pre-clone at known commit SHA |
| LLM-assisted extraction/mapping | CORE-Bench/PaperBench show agents fail at this; adds non-determinism | Human-curate mappings; optionally show LLM would propose X (E3) as contrast |
| Multi-seed variance (3+ seeds) | Tracking tools support multiple runs; variance estimation is nice, not differentiating | 1 seed + explicit Single seed variance not estimated badge |
| Full UI (8 screens, stepper, evidence drawer) | MLflow/W&B have polished UIs; competing on UI loses | Single HTML report judges read reports, not click through steppers |
| Database (15 tables), REST API, auth, multi-user | Tracking tools have these; not the innovation | JSON files + CLI script (run_demo.py) |
| Follow-up ablation experiments | Conceptually valuable but time-consuming | Manual what if notes in report (e.g., Rerun with paper n_estimators=500) |
| Tolerance policy configuration UI | Thresholds are demo parameters, not product features | Hardcode thresholds (1%/5%) in run_demo.py |
| GPU support, multi-language, stronger sandboxing | Out of scope for CPU-only hackathon | Explicitly document as future work |

---

## 4. Features That MUST Be Visible in the Demo

These are the minimum visible differentiators that make judges understand: This is not experiment tracking.

### 4.1 Live Execution (Not Simulated)
- What judges see: Terminal running docker run --rm -v repo:/repo image python benchmark.py --model=rf
- What judges hear: This is the actual repository code executing in a fresh sandbox right now
- Why it matters: Tracking tools show past runs; this shows live reproduction attempt

### 4.2 Paper Claim Values with Provenance
- What judges see: Report header: Paper: Fashion-MNIST Benchmark, Table 1, Row: RandomForest, Col: Accuracy to 0.873
- Why it matters: Tracking tools have no concept of paper claim; this grounds the comparison

### 4.3 Explicit Claim-to-Command Mapping
- What judges see: mappings.json displayed or referenced: claim: RF 0.873, command: python benchmark.py --model=rf, files: [benchmark.py]
- Why it matters: Tracking tools link metrics to your logging calls; this links paper cell to their code

### 4.4 Real Numerical Comparison (Paper to Execution)
- What judges see: Table row: Reported: 0.873 | Reproduced: 0.869 | Abs Diff: -0.004 | Rel %: -0.46% | Verdict: near_exact
- Why it matters: Tracking tools compare your runs; this compares paper vs reality

### 4.5 Deterministic Verdict (Not LLM)
- What judges see: Code snippet or explanation: if rel_dev_pct < 1.0: verdict = near_exact
- Why it matters: Tracking tools do not assign reproducibility verdicts; this shows explainable rules

### 4.6 Evidence-Drawer with Tier Badges
- What judges see: Click a row side panel shows:
  - E1 Paper span: Table 1, Row RandomForest, Col Accuracy
  - E1 Log line: stdout.log:42 Test accuracy: 0.869
  - E2 Mapping: mappings.json to benchmark.py --model=rf
  - E3 (if shown): LLM proposed alternative mapping (not used)
- Why it matters: Tracking tools show metrics; this shows evidence hierarchy

### 4.7 Honest Limitation Disclosure
- What judges see: Badges on every row: Single seed variance not estimated, Mapping human-confirmed, Docker image: sha256:abc123
- Why it matters: Tracking tools hide environment drift; this surfaces it

---

## 5. Competitor-by-Competitor: What the Prototype Shows That They Do Not

| Competitor | What They Do | What Prototype Shows That They Do Not |
|------------|--------------|--------------------------------------|
| MLflow | Tracks your runs, parameters, metrics; mlflow run for packaging | Paper claim as ground truth MLflow has no paper input; claim-to-code mapping MLflow links metrics to your log calls, not to a paper table cell |
| DVC | Versions data/pipelines; dvc repro re-runs your pipeline | Third-party assessment DVC assumes you own the pipeline; ReproLens tests their repo against their paper |
| W&B | Hosted tracking, sweeps, reports of your runs | Paper to execution comparison W&B compares your runs; ReproLens compares paper numbers to actual execution |
| Docker / repo2docker / ReproZip | Environment capture; docker run executes code | Claim-level linkage Docker runs a command; ReproLens maps a paper claim to the right command and compares the number |
| Code Ocean | Compute capsules (code+data+env) for reproducible runs | Discrepancy analysis with evidence Code Ocean runs capsules; ReproLens explains why paper and execution differ |
| Checklists / Artifact Evaluation | Human self-declaration (checklists) or human review (artifacts) | Automated evidence-backed assessment Checklists are self-reported; artifact eval is manual; ReproLens runs code and links evidence programmatically |
| CORE-Bench / PaperBench | Benchmarks for agents to reproduce papers | Deployable assessment platform Benchmarks evaluate agents; ReproLens is a tool a human uses to assess a paper-repo pair |

---

## 6. Demo Script: Making the Differentiation Explicit

30-second verbal framing for judges:

MLflow, DVC, W&B track your experiments. ReproLens assesses someone else paper against their repository.

Here is the chain: Paper Table 1 claims RandomForest = 0.873 accuracy. We map that to benchmark.py --model=rf. We run it in a fresh Docker sandbox. We extract 0.869 from stdout. We compute -0.46% deviation. Verdict: near_exact.

Every number in this report traces to evidence: the paper cell (E1), the log line (E1), the mapping (E2). No LLM judged the numbers deterministic rules did.

If there is a discrepancy, we show why with evidence: paper says n_estimators=500, config says 100. That is not a guess that is a file diff.

---

## 7. Summary: Prototype Differentiation Checklist

Before demo, verify each item is visibly demonstrated:

| Must Be Visible | How to Verify in Demo |
|----------------|----------------------|
| Paper claim values with page/table provenance | Report shows Table 1, Row RF, Col Accuracy to 0.873 |
| Explicit claim to command mapping | mappings.json or verbal: This claim maps to this command |
| Live Docker execution (not playback) | Terminal shows docker run + streaming stdout |
| Metric extracted from actual stdout | Regex shown or verbal: We parse Test accuracy: 0.869 from line 42 |
| Paper vs execution comparison math | Table shows reported / reproduced / abs_diff / rel% / verdict |
| Deterministic verdict (threshold-based) | Code or verbal: <1% = near_exact, <5% = partial |
| Evidence drawer with E1/E2/E3 badges | Click row chips labelled E1/E2/E3 with sources |
| Discrepancy note with cited evidence | Hyperparameter mismatch: paper p.5 (E1) vs config.yaml:12 (E1) |
| Honest limitations badged | Single seed, Human-curated mapping, Image sha256:... |

---

## 8. What NOT to Say

| Avoid Saying | Why |
|--------------|-----|
| We are like MLflow but for papers | MLflow does not do paper to code mapping or paper to execution comparison |
| We automate reproducibility | Prototype has human-curated mappings; full automation is future work |
| Our LLM extracts claims and maps code | Prototype uses zero LLMs in critical path (by design) |
| We replace artifact evaluation | Artifact evaluation is human review; we are automated evidence gathering |

---

## 9. Conclusion

The prototype entire differentiation rests on demonstrating one complete instance of:

Paper claim (with provenance) to Explicit code mapping to Sandboxed execution to Real metric extraction to Deterministic paper to execution comparison to Evidence-linked discrepancy analysis to Honest verdict

Everything else (UI, database, API, LLM, multi-seed, arbitrary upload) is noise for the hackathon. If the seven-step chain is visibly working with evidence at each step, the concept is proven distinct from experiment tracking.

---

End of Analysis Ready for prototype build.
