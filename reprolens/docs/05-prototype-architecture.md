# ReproLens Prototype - Technical Architecture

**Date:** 2026-10-02  
**Scope:** docs/03-final-prototype-scope.md (Option B Reduced: 2 claims, Fashion-MNIST)  
**Architecture Style:** Modular Monolith (single Python process, no services)  
**Goal:** Working end-to-end demo with minimal complexity, maximum reliability

---

## High-Level Architecture

`
+---------------------------------------------------------------------------------+
|                         REPROLENS PROTOTYPE (CLI)                               |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  +-------------+    +-------------+    +-------------+    +-------------+      |
|  | claims.json |    | mappings.json|    | Docker Image|    | repo/ (src) |      |
|  |  (E1/E2)    |    |   (E2)      |    |  (pre-built)|    |  (pinned)   |      |
|  +------+------+    +------+------+    +------+------+    +-----+-------+      |
|         |                  |                  |                  |            |
|         v                  v                  v                  v            |
|  +-----------------------------------------------------------------------+   |
|  |                    run_demo.py (orchestrator)                         |   |
|  |  1. Load claims & mappings                                            |   |
|  |  2. For each claim:                                                   |   |
|  |     a. docker run (stream logs)                                       |   |
|  |     b. Extract metric via regex                                       |   |
|  |     c. Compare: abs_diff, rel_pct, verdict                           |   |
|  |     d. Build evidence objects                                         |   |
|  |  3. Render report.html via Jinja2                                     |   |
|  +-----------------------------------------------------------------------+   |
|                               |                                            |
|                               v                                            |
|  +-----------------------------------------------------------------------+   |
|  |                     report.html (static, self-contained)              |   |
|  |  - Comparison table (reported vs reproduced)                          |   |
|  |  - Evidence drawer (E1/E2/E3 chips per row)                           |   |
|  |  - Limitation badges                                                  |   |
|  |  - REPLAY MODE banner (if fallback)                                   |   |
|  +-----------------------------------------------------------------------+   |
|                                                                                 |
+---------------------------------------------------------------------------------+


---

## Component Specifications

### 1. Frontend - Report.html (Static HTML)

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Display comparison results, evidence traceability, limitation disclosures |
| **Input** | Rendered HTML from Jinja2 template (claims, results, evidence, metadata) |
| **Output** | Interactive HTML page opened in browser |
| **Technology** | Pure HTML/CSS/JS (no framework, no build step, no server) |
| **Deterministic?** | YES - template rendering is pure function |
| **Real/Precomputed** | REAL rendering with live values; structure is pre-defined |
| **Failure Fallback** | If template fails - write minimal static HTML with raw data |

**Key UI Elements:**
- **Comparison Table:** Claim | Reported | Reproduced | Abs Diff | Rel% | Verdict badge
- **Evidence Drawer:** <details> per row - shows E1/E2/E3 chips with refs
- **Verdict Badges:** Color-coded (green/yellow/red) with threshold rule tooltip
- **Limitation Badges:** Single seed, Human-curated mapping, CPU-only, Image sha256:...
- **REPLAY MODE Banner:** Red banner if fallback used
- **Environment Header:** Paper title, repo commit, image digest, Python/sklearn versions

**CSS Classes (embedded):**
`css
.evidence-chip { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
.E1 { background: #e8f5e9; border: 1px solid #4caf50; }   /* solid green = observed */
.E2 { background: #fff3e0; border: 1px dashed #ff9800; }   /* outlined orange = inferred */
.E3 { background: #fce4ec; border: 1px dotted #e91e63; }   /* dashed pink = interpreted */
.badge.near_exact { background: #c8e6c9; color: #2e7d32; }
.badge.partial { background: #ffe0b2; color: #e65100; }
.badge.significant { background: #ffcdd2; color: #c62828; }
details summary { cursor: pointer; font-weight: bold; }
`

**JS (embedded, ~10 lines):**
`js
document.querySelectorAll(.evidence-toggle).forEach(btn => {
  btn.onclick = () => document.getElementById(btn.dataset.target).classList.toggle(open);
});
`

---

### 2. Backend - run_demo.py (Orchestrator)

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | End-to-end orchestration: load inputs - execute experiments - compare - render report |
| **Input** | claims.json, mappings.json, Docker image digest, repo path |
| **Output** | report.html (and console logs) |
| **Technology** | Python 3.11+, stdlib + jinja2, docker CLI via subprocess |
| **Deterministic?** | YES - no LLM, no randomness, pure functions |
| **Real/Precomputed** | REAL execution (Docker runs); claims/mappings precomputed |
| **Failure Fallback** | If any experiment fails - load runs/RUN-XXX/ pre-recorded logs, generate identical report with REPLAY MODE banner |

**Architecture (single file, ~150 lines):**
`python
# run_demo.py
import json, re, subprocess, time, sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# CONFIG
CLAIMS_FILE = claims.json
MAPPINGS_FILE = mappings.json
REPO_PATH = Path(repo).resolve()
IMAGE_NAME = reprolens-demo
TIMEOUT = 900  # 15 min
REGEX_PATTERNS = {
    EXP-001: rTest accuracy:\s+([\d.]+),
    EXP-002: rTest accuracy:\s+([\d.]+),
}
VERDICT_THRESHOLDS = {near_exact: 1.0, partial: 5.0}  # %

# EVIDENCE TIER MAP
EVIDENCE_TIER = {
    paper_span: E1, table_cell: E1, log_line: E1,
    package_version: E1, resource_stat: E1,
    file_range: E2, config_key: E2, mapping: E2,
    llm_note: E3,
}

def load_json(path): return json.loads(Path(path).read_text())

def run_docker(command: str) -> tuple[str, int, float, int]:
    cmd = [
        docker, run, --rm,
        -v, f{REPO_PATH}:/repo,
        -w, /repo,
        --cpus=2, --memory=4g, --memory-swap=4g,
        --network=none, --pids-limit=256,
        IMAGE_NAME, bash, -c, command
    ]
    start = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    stdout_lines = []
    for line in proc.stdout:
        print(f[docker] {line.rstrip()})  # LIVE streaming
        stdout_lines.append(line)
    
    proc.wait(timeout=TIMEOUT)
    wall = time.time() - start
    peak_mb = 0  # placeholder
    return .join(stdout_lines), proc.returncode, wall, peak_mb

def extract_metric(exp_id: str, stdout: str) -> float | None:
    pattern = REGEX_PATTERNS[exp_id]
    matches = re.findall(pattern, stdout)
    return float(matches[-1]) if matches else None

def compare(reported: float, reproduced: float) -> dict:
    abs_diff = reproduced - reported
    if abs(reported) < 1e-10:
        rel_pct = None
    else:
        rel_pct = (abs_diff / abs(reported)) * 100
    
    if rel_pct is not None and abs(rel_pct) < VERDICT_THRESHOLDS[near_exact]:
        verdict = near_exact
    elif rel_pct is not None and abs(rel_pct) < VERDICT_THRESHOLDS[partial]:
        verdict = partial
    else:
        verdict = significant
    return {abs_diff: abs_diff, rel_pct: rel_pct, verdict: verdict}

def make_evidence(kind: str, ref: str, excerpt: str = ) -> dict:
    return {id: fEV-{kind}-{hash(ref) % 10000}, tier: EVIDENCE_TIER[kind], kind: kind, ref: ref, excerpt: excerpt}

def build_evidence(claim: dict, mapping: dict, stdout: str, metric: float, comparison: dict) -> list:
    ev = []
    ev.append(make_evidence(paper_span, fTable 1, Row {claim[model]}, Col Accuracy, str(claim[reported_value])))
    ev.append(make_evidence(log_line, fstdout.log:last, fTest accuracy: {metric}))
    ev.append(make_evidence(mapping, fmappings.json:{claim[id]}, mapping[command]))
    ev.append(make_evidence(package_version, pip freeze, scikit-learn==1.4.2))
    return ev

def render_report(claims: list, results: list, all_evidence: list, replay_mode: bool = False) -> str:
    env = Environment(loader=FileSystemLoader(.))
    template = env.get_template(report_template.html)
    return template.render(
        paper_title=Fashion-MNIST Benchmark,
        paper_arxiv=arXiv:1708.07747,
        repo_commit=a1b2c3d,
        image_digest=sha256:abc123...,
        python_version=3.11,
        sklearn_version=1.4.2,
        claims=claims,
        results=results,
        evidence=all_evidence,
        replay_mode=replay_mode,
        limitations=[Single seed - variance not estimated, Human-curated mapping, CPU-only execution, sklearn version not stated in paper]
    )

def load_fallback(exp_id: str) -> tuple[str, int, float, int]:
    run_dir = Path(fruns/{exp_id})
    stdout = (run_dir / stdout.log).read_text()
    rc = int((run_dir / exit_code.txt).read_text().strip())
    wall = float((run_dir / wall_sec.txt).read_text().strip())
    peak_mb = int((run_dir / peak_mb.txt).read_text().strip())
    return stdout, rc, wall, peak_mb

def main():
    claims = load_json(CLAIMS_FILE)
    mappings = {m[claim_id]: m for m in load_json(MAPPINGS_FILE)}
    
    subprocess.run([docker, info], check=True, capture_output=True)
    
    results = []
    all_evidence = []
    replay_mode = False
    
    for claim in claims:
        mapping = mappings[claim[id]]
        exp_id = claim[id]
        
        print(f
=== {exp_id}: {claim[model]} ===)
        print(fCommand: {mapping[command]})
        
        try:
            stdout, rc, wall, peak_mb = run_docker(mapping[command])
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f[WARN] Live run failed: {e}. Falling back to pre-recorded.)
            stdout, rc, wall, peak_mb = load_fallback(exp_id)
            replay_mode = True
        
        if rc != 0:
            print(f[WARN] Container exited with code {rc}. Falling back.)
            stdout, rc, wall, peak_mb = load_fallback(exp_id)
            replay_mode = True
        
        metric = extract_metric(exp_id, stdout)
        if metric is None:
            print(f[WARN] Metric extraction failed. Falling back.)
            stdout, rc, wall, peak_mb = load_fallback(exp_id)
            metric = extract_metric(exp_id, stdout)
            replay_mode = True
        
        comparison = compare(claim[reported_value], metric)
        evidence = build_evidence(claim, mapping, stdout, metric, comparison)
        
        results.append({
            claim_id: exp_id,
            model: claim[model],
            reported: claim[reported_value],
            reproduced: metric,
            comparison: comparison,
        })
        all_evidence.extend(evidence)
        
        print(fExtracted: {metric})
        print(fReported: {claim[reported_value]} | abs_diff: {comparison[abs_diff]:.4f} | rel: {comparison[rel_pct]:.2f}%)
        print(fVerdict: {comparison[verdict]})
    
    html = render_report(claims, results, all_evidence, replay_mode)
    Path(report.html).write_text(html)
    print(
[ReproLens] Report generated: report.html)
    if replay_mode:
        print([WARN] REPLAY MODE - used pre-recorded runs)

if __name__ == __main__:
    main()
`

---

### 3. Database / Storage - JSON Files (No Database)

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Persist claims, mappings, fallback run logs; no migrations, no ORM |
| **Input** | Human-authored claims.json, mappings.json; captured run logs |
| **Output** | Read by run_demo.py; fallback logs written during rehearsal |
| **Technology** | Plain JSON files on disk |
| **Deterministic?** | YES |
| **Real/Precomputed** | PRECOMPUTED (claims, mappings); REAL (fallback logs captured during rehearsal) |
| **Failure Fallback** | If file missing/corrupt - exit with clear error message |

**File Structures:**

claims.json:
`json
[
  {
    id: EXP-001,
    model: RandomForest,
    reported_value: 0.873,
    provenance: { paper: arXiv:1708.07747, page: 4, table: Table 1, row: RandomForest, col: Accuracy }
  },
  {
    id: EXP-002,
    model: LogisticRegression,
    reported_value: 0.851,
    provenance: { paper: arXiv:1708.07747, page: 4, table: Table 1, row: LogisticRegression, col: Accuracy }
  }
]
`

mappings.json:
`json
[
  { claim_id: EXP-001, command: python benchmark.py --model rf, files: [benchmark.py] },
  { claim_id: EXP-002, command: python benchmark.py --model logreg, files: [benchmark.py] }
]
`

Fallback run structure (runs/RUN-001/):
`
stdout.log          # captured stdout
stderr.log          # captured stderr (usually empty)
exit_code.txt       # 0
wall_sec.txt        # 112.3
peak_mb.txt         # 384
`

---


### 4. Paper Processing - Pre-extracted Claims (No Processing)

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Provide experimental claims with paper provenance (page, table, row, col) |
| **Input** | Paper PDF (manually read by human) |
| **Output** | claims.json (hardcoded, human-verified) |
| **Technology** | None (manual) |
| **Deterministic?** | YES - human-verified, no code involved |
| **Real/Precomputed** | PRECOMPUTED (before hackathon) |
| **Failure Fallback** | If claims missing - demo cannot run; verify at T-7 days |

**Provenance Fields (E1):**
- paper: arXiv ID or title
- page: page number
- table: table identifier (e.g., Table 1)
- row: row label (e.g., RandomForest)
- col: column label (e.g., Accuracy)

**Note:** No PDF parsing code exists in prototype. Claims are manually extracted during rehearsal and hardcoded into claims.json. This is explicitly honest - labelled E1 in report.


### 5. Repository Processing - Pre-cloned at Pinned Commit (No Processing)

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Provide repository source code at known-good commit |
| **Input** | GitHub URL (manually cloned before hackathon) |
| **Output** | repo/ directory (shallow clone at pinned SHA) |
| **Technology** | git clone --depth=1 --branch <sha> <url> repo/ (run once pre-hackathon) |
| **Deterministic?** | YES - pinned commit SHA |
| **Real/Precomputed** | PRECOMPUTED (before hackathon) |
| **Failure Fallback** | If repo missing - demo cannot run; verify at T-7 days |

**Pre-hackathon Verification:**
git clone --depth=1 --branch a1b2c3d https://github.com/zalandoresearch/fashion-mnist repo/
cd repo && python benchmark.py --model rf  # verify < 3 min

**Note:** No repo analysis code exists (no AST, no config scanning, no entry-point detection). The benchmark command is human-identified and hardcoded in mappings.json.

---

### 6. Experiment Execution - Docker Sandbox (Real Execution)

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Run repository code in isolated, resource-limited container; stream logs |
| **Input** | Command from mappings.json, Docker image, repo path |
| **Output** | stdout/stderr (streamed), exit code, wall time, peak memory |
| **Technology** | Docker Engine via subprocess.Popen; --network=none, CPU/memory limits |
| **Deterministic?** | YES - same image, same command, same repo commit |
| **Real/Precomputed** | REAL (live during demo); fallback uses pre-recorded logs |
| **Failure Fallback** | On timeout/OOM/error - load runs/RUN-XXX/ logs, set REPLAY MODE |

**Docker Run Command:**
docker run --rm -v /abs/path/to/repo:/repo -w /repo --cpus=2 --memory=4g --memory-swap=4g --network=none --pids-limit=256 reprolens-demo bash -c python benchmark.py --model rf

**Pre-built Image (eliminates network risk):**
docker build -t reprolens-demo .
docker save reprolens-demo > reprolens-demo.tar
docker load < reprolens-demo.tar

**Dockerfile:**
FROM python:3.11-slim
WORKDIR /repo
RUN pip install --no-cache-dir scikit-learn==1.4.2 numpy==1.24.3

**Resource Limits:** 2 vCPU, 4GB RAM, 15-min timeout, no network, 256 pids


### 7. Comparison Engine - Deterministic Math

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Compute absolute difference, relative deviation %, assign verdict |
| **Input** | reported_value (from claims.json), reproduced_value (from stdout) |
| **Output** | {abs_diff, rel_pct, verdict} |
| **Technology** | Pure Python arithmetic (IEEE 754 float) |
| **Deterministic?** | YES - no randomness, no LLM |
| **Real/Precomputed** | REAL (computed live on captured values) |
| **Failure Fallback** | If reported ~ 0 - rel_pct = None, verdict based on abs_diff |

**Logic:**
abs_diff = reproduced - reported
rel_pct = (abs_diff / abs(reported)) * 100  # None if reported ~ 0

if rel_pct is not None and abs(rel_pct) < 1.0:    verdict = near_exact
elif rel_pct is not None and abs(rel_pct) < 5.0:  verdict = partial
else:                                              verdict = significant

**Thresholds hardcoded:** near_exact < 1%, partial < 5%, else significant

---

### 8. Discrepancy Engine - Manual Notes Only

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Provide discrepancy analysis notes with evidence citations |
| **Input** | Comparison result, claim provenance, repo config (human-known) |
| **Output** | Static text notes in report (evidence drawer) |
| **Technology** | Hardcoded strings in Python / template |
| **Deterministic?** | YES - pre-written, not computed |
| **Real/Precomputed** | PRECOMPUTED (manual analysis during rehearsal) |
| **Failure Fallback** | If no discrepancy - No significant discrepancy detected |

**Implementation:**
DISCREPANCY_NOTES = {
    EXP-001: Paper n_estimators=100 matches repo default. Single seed - variance not estimated.,
    EXP-002: Paper max_iter not stated; repo default=100 used. Single seed - variance not estimated.,
}
# Optional perturbation (pre-recorded only):
# What if: --n-estimators 10 -> 0.823 (significant deviation). Evidence: config mismatch.

**Note:** No automated cause analysis engine. Notes are human-written during rehearsal, citing E1/E2 evidence explicitly.

---

### 9. Evidence Model - Explicit E1/E2/E3 Tagging

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Attach evidence tier to every claim, mapping, metric, finding |
| **Input** | Evidence kind (paper_span, log_line, mapping, etc.) |
| **Output** | Evidence objects with id, tier, kind, ref, excerpt |
| **Technology** | Python dicts; hardcoded tier map |
| **Deterministic?** | YES - tier assigned by kind, not content |
| **Real/Precomputed** | REAL (created during live run) + PRECOMPUTED (paper claims) |
| **Failure Fallback** | If evidence creation fails - minimal evidence with tier |

**Tier Definitions (from project doc):**
- **E1 (Hard Evidence):** Directly observed - log lines, stdout, paper text spans, file contents, hashes, resource stats
- **E2 (Auto-Inferred):** Deterministically derived - AST findings, config keys, version numbers, command from mapping
- **E3 (LLM Interpretation):** Probabilistic - extraction proposals, mapping rankings, discrepancy hypotheses

**Hardcoded Tier Map:**
EVIDENCE_TIER = {
    paper_span: E1, table_cell: E1, log_line: E1,
    package_version: E1, resource_stat: E1,
    file_range: E2, config_key: E2, mapping: E2,
    llm_note: E3,
}

**Report Rule:** A conclusion that rests only on E3 is reported as Insufficient evidence.


### 10. LLM Integration - None in Critical Path

| Aspect | Specification |
|--------|---------------|
| **Responsibility** | Zero LLM calls in critical path |
| **Input** | N/A |
| **Output** | N/A |
| **Technology** | N/A |
| **Deterministic?** | N/A |
| **Real/Precomputed** | N/A |
| **Failure Fallback** | N/A |

**Explicitly Excluded:**
- LLM for claim extraction - pre-extracted manually
- LLM for mapping suggestion - human-curated mappings.json
- LLM for discrepancy analysis - manual notes
- LLM for report narrative - Jinja2 template

**Optional Contrast (if time permits):**
Displayed in evidence drawer as E3 badge: LLM proposed alternative (not used) - this is a contrast demo, not part of workflow.

---

## Data Flow Summary

claims.json (E1)     mappings.json (E2)     repo/ (pinned)     Docker image (E1)
      |                    |                      |                   |
      +-------------------+----------------------+-------------------+
                           v
                  +-----------------+
                  |  run_demo.py    |
                  |  (orchestrator) |
                  +--------+--------+
                           |
          +----------------+----------------+
          v              v              v
   Docker run      Regex extract   Compare (E2)
   (stdout, E1)    (metric, E1)    (verdict, E2)
          |             |             |
          +-------------+-------------+
                          v
                  Build Evidence (E1/E2)
                          |
                          v
                  Jinja2 Template
                          |
                          v
                      report.html

---

## File Structure

reprolens-prototype/
run_demo.py              # Orchestrator (~150 lines)
claims.json              # 2 claims with E1 provenance
mappings.json            # 2 mappings: claim to command (E2)
Dockerfile               # python:3.11-slim + sklearn==1.4.2
report_template.html     # Jinja2 template with embedded CSS/JS
reprolens-demo.tar       # Pre-built Docker image (gitignore)
repo/                    # Shallow clone at pinned SHA (gitignore)
runs/                    # Fallback logs (gitignore)
    RUN-001/             # RF stdout, exit_code, wall_sec, peak_mb
    RUN-002/             # LR stdout, exit_code, wall_sec, peak_mb
report.html              # Generated output (gitignore)


---

## Reliability Guarantees

| Risk | Mitigation |
|------|------------|
| Docker daemon down | docker info check at start; exit with clear message |
| Image pull fails | Pre-built image saved as .tar; load via docker load |
| Network during demo | --network=none; image pre-loaded |
| Experiment timeout | 15-min hard timeout; fallback to pre-recorded |
| Metric extraction fails | Fallback to pre-recorded stdout |
| Container OOM | 4GB limit; pre-tested |
| Repo unavailable | Pre-cloned at pinned SHA in repo/ |
| Report template error | Minimal static HTML fallback |

---

## Demo Checklist (Pre-Hackathon)

| Check | Pass Criteria |
|-------|---------------|
| docker info | Returns version |
| docker build -t reprolens-demo . | Success, < 2GB |
| docker save > reprolens-demo.tar | File ~1-2GB |
| docker load < reprolens-demo.tar | Loads < 30s |
| docker run ... --model rf | Exit 0, Test accuracy: 0.XXX, < 180s |
| docker run ... --model logreg | Exit 0, Test accuracy: 0.XXX, < 180s |
| Regex on captured stdout | Returns [0.XXX] |
| mkdir runs/RUN-001 RUN-002 + copy logs | Dir structure exists |
| python run_demo.py (fallback) | Generates report.html |
| Open report.html click row | Drawer toggles, shows E1/E2 chips |

**If ANY fails - Option A fallback (RandomForest only)**

---

## Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Disk | 10 GB free | 20 GB free |
| CPU | 2 cores | 4+ cores |
| Docker | Desktop 4.x+ | Latest |
| Python | 3.11+ | 3.11+ |
| Network | Pre-hackathon only | None during demo |

---

## What This Architecture Explicitly Does NOT Include

| Component | Reason |
|-----------|--------|
| Database (SQLite/Postgres) | JSON files sufficient for single-run demo |
| REST API / async / SSE | CLI script sufficient |
| Multi-screen UI / stepper | Single HTML report is the deliverable |
| LLM in critical path | Breaks determinism; API risk |
| PDF parsing / table extraction | Pre-extracted manually |
| Repo auto-clone / AST analysis | Pre-cloned; mapping human-curated |
| Multi-seed / variance | 3x runtime; single seed with badge |
| Automated discrepancy engine | Manual notes with evidence sufficient |
| Parallel execution / queue | Sequential is simpler and reliable |
| Advanced sandboxing (gVisor) | Docker defaults sufficient for demo |

---

**Architecture Status:** COMPLETE - Ready for implementation.
