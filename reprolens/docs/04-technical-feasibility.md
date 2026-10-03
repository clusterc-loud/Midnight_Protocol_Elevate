# ReproLens Prototype Technical Feasibility Analysis

**Date:** 2026-10-02  
**Scope:** docs/03-final-prototype-scope.md (Option B Reduced: 2 claims, Fashion-MNIST)  
**Environment:** Student laptop (Windows/macOS/Linux), Docker Desktop, Python 3.11+, 8-16GB RAM  
**Goal:** Identify what will actually work reliably during a hackathon demo

---

## Executive Summary

The prototype scope is highly feasible because it deliberately excludes all hard problems (PDF parsing, repo analysis, LLM mapping, multi-seed, database, UI framework). The critical path is ~150 lines of Python + Docker + Jinja2 template. Primary risks are external (Docker daemon, repo availability, network) not algorithmic.

**Verdict:** A single developer can build this in 4-6 hours if pre-verification is done. Pair can do it in 2-3 hours.

---

## Component-by-Component Feasibility

### 1. PDF Extraction
**Scope status:** EXPLICITLY EXCLUDED (docs/03 section 2)

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Yes (pdfplumber, PyMuPDF, pymupdf) |
| Should we? | NO -- Not in scope. Pre-extract claims manually. |
| Complexity if attempted | Medium-High (table detection is brittle, merged cells, no standard format) |
| Dependencies | pdfplumber, PyMuPDF, pandas |
| CPU requirements | Low |
| External API | None |
| Failure modes | Scanned PDFs, multi-column tables, rotated pages, encoding issues |
| Demo risk | HIGH -- would consume 50%+ of hackathon time for unreliable results |
| Simplification | Pre-extract 2 claims manually to claims.json (15 min work) |

**Decision:** DO NOT BUILD. Hardcode claims.

---

### 2. Experimental Claim Extraction
**Scope status:** EXPLICITLY EXCLUDED (automated extraction)

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Yes (LLM + prompt engineering, or rule-based table parsing) |
| Should we? | NO -- Not in scope. Claims are pre-extracted. |
| Complexity if attempted | High (requires PDF parsing first, then cell-to-claim mapping) |
| Dependencies | LLM API (OpenAI/Anthropic) or local LLM (Ollama) |
| CPU requirements | Low (but GPU needed for local LLM) |
| External API | YES -- LLM API key required, rate limits, cost |
| Failure modes | Hallucinated claims, missed claims, wrong provenance, non-deterministic |
| Demo risk | CRITICAL -- non-deterministic output breaks demo reproducibility |
| Simplification | Pre-extract manually to claims.json with explicit provenance |

**Decision:** DO NOT BUILD. Manual curation is the only reliable approach for hackathon.

---

### 3. Repository Cloning / Indexing
**Scope status:** EXPLICITLY EXCLUDED (auto-clone, AST, config scanning)

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Yes (gitpython, GitHub API, tree-sitter for AST) |
| Should we? | NO -- Not in scope. Repo pre-cloned at pinned commit. |
| Complexity if attempted | Medium (auth, private repos, large repos, submodules, LFS) |
| Dependencies | gitpython, GitHub CLI/token, tree-sitter, language parsers |
| CPU requirements | Low-Medium (AST parsing) |
| External API | GitHub API (rate limits, auth) |
| Failure modes | Private repo, network timeout, huge repo (>1GB), missing credentials |
| Demo risk | HIGH -- network-dependent, unrepeatable |
| Simplification | git clone --depth=1 <url> --branch <sha> repo/ beforehand |

**Decision:** DO NOT BUILD. Pre-clone at known commit SHA.

---

### 4. Claim-to-Code Mapping
**Scope status:** EXPLICITLY EXCLUDED (automated mapping, LLM, embeddings)

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Theoretically yes (embeddings + AST + config parsing) |
| Should we? | NO -- CORE-Bench/PaperBench show SOTA agents fail at this |
| Complexity if attempted | VERY HIGH (semantic code search, config tracing, CLI arg analysis) |
| Dependencies | Embedding model, vector DB, tree-sitter, LLM for re-ranking |
| CPU requirements | Medium-High (embeddings) |
| External API | LLM API for re-ranking |
| Failure modes | Wrong file, wrong function, missed hyperparameters, false confidence |
| Demo risk | CRITICAL -- mapping errors cascade to wrong execution |
| Simplification | Human writes mappings.json: claim_id: EXP-001, command: python benchmark.py --model rf, files: [benchmark.py] |

**Decision:** DO NOT BUILD. Human-curated mapping only. This is the honest approach -- the prototype demonstrates the workflow, not the automation.

---

### 5. Experiment Command Generation
**Scope status:** SIMPLIFIED -- explicit in mappings.json

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Yes -- trivial string interpolation |
| Should we? | YES -- but keep it trivial |
| Complexity | TRIVIAL (string from JSON) |
| Dependencies | None |
| CPU requirements | None |
| External API | None |
| Failure modes | Command not found, wrong working dir, missing args |
| Demo risk | LOW -- test beforehand |
| Simplification | Command is literal string in mappings.json. No generation logic needed. |

**Implementation:**
command = mapping[command]  # python benchmark.py --model rf
# No parsing, no arg injection, no derivation

**Decision:** BUILD -- 3 lines of code. Command comes from JSON.
Part 2 content placeholder
---

### 6. Docker Execution
**Scope status:** CORE -- real execution in sandbox

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | YES -- standard docker run via subprocess |
| Should we? | YES -- this IS the differentiator |
| Complexity | LOW-MEDIUM (subprocess, timeout, resource limits, log streaming) |
| Dependencies | Docker Desktop / Engine, Python subprocess, docker Python SDK optional |
| CPU requirements | 2 vCPU, 4GB RAM per container (host needs 8GB+) |
| External API | None (local Docker daemon) |
| Failure modes | Daemon not running, image pull timeout, OOM, timeout, network blocked, permission denied |
| Demo risk | MEDIUM -- external dependency (Docker daemon) |
| Simplification | Pre-build image (docker save > image.tar), load from tar (docker load < image.tar) -- eliminates pull/network risk |

**Critical Implementation Details:**
def run_experiment(command, image, repo_path, timeout=900):
    cmd = [
        docker, run, --rm,
        -v, repo_path:/repo,
        -w, /repo,
        --cpus=2, --memory=4g, --memory-swap=4g,
        --network=none,  # No network during execution
        --pids-limit=256,
        image,
        bash, -c, command
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Stream logs live
    for line in proc.stdout:
        print([docker] + line.rstrip())
        yield line
    
    proc.wait(timeout=timeout)
    return proc.returncode

**Pre-build Checklist:**
- Dockerfile with pinned base (python:3.11-slim) and exact pip install scikit-learn==1.4.2
- docker build -t reprolens-demo .
- docker save reprolens-demo > reprolens-demo.tar
- Test docker load < reprolens-demo.tar + run both experiments
- Verify image digest: docker images --digests reprolens-demo

**Decision:** BUILD -- Core differentiator. Pre-build image eliminates network risk.

---

### 7. Metric Extraction
**Scope status:** CORE -- regex on stdout

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | YES -- trivial regex |
| Should we? | YES |
| Complexity | TRIVIAL |
| Dependencies | Python re module |
| CPU requirements | None |
| External API | None |
| Failure modes | Output format changes, multiple numbers, no match, locale issues |
| Demo risk | LOW -- test regex on actual captured stdout beforehand |
| Simplification | Single regex pattern per experiment, validated beforehand |

**Implementation:**
PATTERNS = {
    EXP-001: rTest accuracy:\s+([\d.]+),  # RandomForest
    EXP-002: rTest accuracy:\s+([\d.]+),  # LogisticRegression
}

def extract_metric(experiment_id, stdout):
    pattern = PATTERNS[experiment_id]
    matches = re.findall(pattern, stdout)
    if not matches:
        return None
    return float(matches[-1])  # Last occurrence

**Pre-verification:** Run experiments locally to capture stdout to verify regex matches exactly one value to save pattern.

**Decision:** BUILD -- 10 lines of code. Pre-validated regex.

---

### 8. Reported-vs-Reproduced Comparison
**Scope status:** CORE -- deterministic math

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | YES -- basic arithmetic |
| Should we? | YES |
| Complexity | TRIVIAL |
| Dependencies | None |
| CPU requirements | None |
| External API | None |
| Failure modes | Division by zero (reported=0), float precision |
| Demo risk | NONE |
| Simplification | Hardcode thresholds (1%, 5%) |

**Implementation:**
def compare(reported, reproduced):
    abs_diff = reproduced - reported
    if abs(reported) < 1e-10:
        rel_pct = None
    else:
        rel_pct = (abs_diff / abs(reported)) * 100
    
    if rel_pct is not None and abs(rel_pct) < 1.0:
        verdict = near_exact
    elif rel_pct is not None and abs(rel_pct) < 5.0:
        verdict = partial
    else:
        verdict = significant
    
    return {abs_diff: abs_diff, rel_pct: rel_pct, verdict: verdict}

**Decision:** BUILD -- 15 lines. Zero risk.

---

### 9. Discrepancy Detection
**Scope status:** SIMPLIFIED -- manual what if notes only

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Automated: MEDIUM-HARD (requires cause analysis engine) |
| Should we? | NO -- Not in scope for prototype |
| Complexity if automated | HIGH (hyperparameter diff, version diff, data diff, seed diff, env diff) |
| Dependencies | Config parsers, package version comparison, git diff |
| External API | None |
| Failure modes | False positives, missed causes, unactionable suggestions |
| Demo risk | HIGH if automated -- could show wrong cause |
| Simplification | Pre-compute ONE discrepancy note for demo: Paper says n_estimators=100, config uses default=100 (match) or perturb one run in fallback |

**Decision:** DO NOT BUILD automated engine. 

**What to show instead:**
- In report: Static Discrepancy Analysis section with manual notes
- Example: No significant discrepancy detected. Paper n_estimators=100 matches repo default. Single seed -- variance not estimated.
- Optional pre-recorded: Run with --n-estimators 10 to show significant deviation as what if (pre-recorded, not live)

---

### 10. Evidence Generation
**Scope status:** CORE -- explicit E1/E2/E3 tagging

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | YES -- explicit evidence objects |
| Should we? | YES -- this IS the differentiator |
| Complexity | LOW (structured data, not inference) |
| Dependencies | None |
| CPU requirements | None |
| External API | None |
| Failure modes | Missing evidence links, tier mislabeling |
| Demo risk | LOW -- deterministic assignment |
| Simplification | Hardcode evidence tier per source type |

**Evidence Model (simplified):**
EVIDENCE_TIER = {
    paper_span: E1,
    table_cell: E1, 
    log_line: E1,
    package_version: E1,
    resource_stat: E1,
    file_range: E2,
    config_key: E2,
    mapping: E2,
    llm_note: E3,
}

def make_evidence(kind, ref, excerpt=None):
    return {
        id: EV- + str(next_evidence_id()),
        tier: EVIDENCE_TIER[kind],
        kind: kind,
        ref: ref,
        excerpt: excerpt
    }

**Usage in report:**
- Paper claim to make_evidence(paper_span, Table 1, Row RF, Col Accuracy)
- Reproduced metric to make_evidence(log_line, stdout.log:42, Test accuracy: 0.869)
- Mapping to make_evidence(mapping, mappings.json:EXP-001)

**Decision:** BUILD -- ~20 lines. Makes traceability visible.

---

### 11. Frontend (Report.html)
**Scope status:** SIMPLIFIED -- single static HTML with JS toggle

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | YES -- Jinja2 + embedded CSS/JS |
| Should we? | YES |
| Complexity | LOW |
| Dependencies | Jinja2, (optional) Chart.js via CDN for dot plot |
| CPU requirements | None (browser renders) |
| External API | None (embed Chart.js locally or use inline SVG) |
| Failure modes | Browser JS disabled, CSS conflicts, template errors |
| Demo risk | LOW -- static HTML works offline |
| Simplification | No framework. Pure HTML/CSS/JS in one file. |

**Implementation:**
- report_template.html -- Jinja2 template with {{ claims }}, {{ results }}, {{ evidence }}
- Embedded <style> -- verdict badges, evidence chips (E1/E2/E3 colors), evidence drawer (<details>)
- Embedded <script> -- 10 lines for drawer toggle
- Render: jinja2.Environment().from_string(template).render(data) to report.html

**Decision:** BUILD -- ~80 lines template + 20 lines Python. Zero runtime dependencies.

---

### 12. Backend
**Scope status:** SIMPLIFIED -- single CLI script (run_demo.py)

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | YES -- sequential script |
| Should we? | YES |
| Complexity | LOW |
| Dependencies | docker (CLI via subprocess), jinja2, re, json, subprocess, time, pathlib |
| CPU requirements | Minimal (orchestration only) |
| External API | None |
| Failure modes | Docker CLI not in PATH, permission errors, subprocess timeout |
| Demo risk | LOW -- test beforehand |
| Simplification | No server, no async, no queue, no database. Just main() function. |

**Architecture:**
def main():
    claims = load_json(claims.json)
    mappings = load_json(mappings.json)
    image = load_image_digest()
    
    results = []
    for claim in claims:
        mapping = mappings[claim[id]]
        stdout, stderr, rc, wall, mem = run_docker(mapping[command], image)
        metric = extract_metric(claim[id], stdout)
        comparison = compare(claim[reported_value], metric)
        results.append({...})
    
    evidence = build_evidence(claims, mappings, results)
    render_report(claims, results, evidence)

**Decision:** BUILD -- Single file, no framework.

---

### 13. LLM Integration
**Scope status:** EXPLICITLY EXCLUDED from critical path

| Aspect | Assessment |
|--------|------------|
| Can it be implemented? | Yes (OpenAI/Anthropic API, or local Ollama) |
| Should we? | NO -- Zero LLM calls in critical path |
| Complexity if added | MEDIUM (API key, prompts, retries, parsing, cost) |
| Dependencies | openai or anthropic SDK, or ollama |
| CPU requirements | Low (but GPU for local) |
| External API | YES -- API key, rate limits, latency, cost |
| Failure modes | Rate limit, timeout, hallucination, non-deterministic output, API key missing |
| Demo risk | CRITICAL -- breaks reproducibility of demo itself |
| Simplification | Pre-compute ONE LLM output for contrast badge (static JSON) |

**What NOT to do:**
- LLM for claim extraction
- LLM for mapping suggestion  
- LLM for discrepancy analysis
- LLM for report narrative

**Optional contrast demo (if time):**
llm_contrast.json (pre-computed, static)
{
  EXP-001: {
    proposed_mapping: train.py::main(),
    confidence: 0.72,
    note: LLM proposed train.py but human confirmed benchmark.py
  }
}
Display in evidence drawer as E3 badge: LLM proposed alternative (not used)

**Decision:** DO NOT BUILD in critical path. Optional static contrast only.

---

## Summary: Implementation Priority

| Priority | Component | Effort | Risk | Build? |
|----------|-----------|--------|------|--------|
| 1 | Docker execution + log streaming | 2-3 hrs | MEDIUM | YES |
| 2 | Metric extraction (regex) | 30 min | LOW | YES |
| 3 | Comparison math + verdict | 30 min | NONE | YES |
| 4 | Evidence model + linking | 1 hr | LOW | YES |
| 5 | HTML report (Jinja2 + CSS/JS) | 1-2 hrs | LOW | YES |
| 6 | Main orchestration script | 1 hr | LOW | YES |
| 7 | Pre-built Docker image | 1-2 hrs | MEDIUM | YES (pre-hackathon) |
| 8 | Fallback logs capture | 30 min | LOW | YES |
| - | PDF extraction | 8+ hrs | HIGH | NO |
| - | Claim extraction (auto) | 8+ hrs | CRITICAL | NO |
| - | Repo cloning/indexing | 4+ hrs | HIGH | NO |
| - | Auto mapping | 16+ hrs | CRITICAL | NO |
| - | Multi-seed variance | 4+ hrs | MEDIUM | NO |
| - | Automated discrepancy | 8+ hrs | HIGH | NO |
| - | LLM integration | 4+ hrs | CRITICAL | NO |
| - | Database/API/UI | 16+ hrs | MEDIUM | NO |

**Total build time (core only):** ~6-8 hours single / ~4-6 hours pair  
**Total excluded time:** ~68+ hours

---

## DO NOT BUILD LIST

| # | Feature | Reason |
|---|---------|--------|
| 1 | PDF upload / parsing / table extraction | Excluded from scope; brittle; not differentiator |
| 2 | Automated claim extraction from PDF | Requires #1; non-deterministic; LLM-dependent |
| 3 | GitHub repo auto-clone / auth | Network-dependent; not in scope |
| 4 | Repository AST parsing / config scanning | Complex; not in scope |
| 5 | Automated claim-to-code mapping (embeddings/LLM) | SOTA fails at this; human-curated only |
| 6 | LLM-assisted mapping re-ranking | Non-deterministic; API-dependent |
| 7 | Multi-seed execution / variance estimation | 3x runtime; not required for demo |
| 8 | Automated discrepancy cause analysis | Complex engine; manual notes sufficient |
| 9 | Follow-up ablation experiments | Time-consuming; pre-recorded only |
| 10 | Database (SQLite/PostgreSQL) | Overhead; JSON sufficient |
| 11 | REST API / async endpoints | Overhead; CLI sufficient |
| 12 | Multi-screen UI (stepper, dashboard, settings) | Overhead; single HTML report sufficient |
| 13 | Auth / multi-user / sessions | Not in scope |
| 14 | LLM in critical path (extraction, mapping, comparison, verdict, report) | Breaks determinism; API risk |
| 15 | Parallel execution / queue / scheduler | Not needed; sequential is fine |
| 16 | gVisor / rootless / advanced sandboxing | Docker defaults sufficient for demo |
| 17 | Tolerance policy configuration UI | Hardcode thresholds |
| 18 | Chart.js from CDN | Embed locally or use inline SVG (offline) |
| 19 | Any smart automation not explicitly in section 1 of scope doc | Scope boundary |

---

## Pre-Hackathon Verification Checklist (MANDATORY)

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| Docker daemon | docker info | Returns version info |
| Image build | docker build -t reprolens-demo . | Success, < 2GB |
| Image save | docker save reprolens-demo > image.tar | File exists, ~1-2GB |
| Image load | docker load < image.tar | Loads in < 30s |
| RF run | docker run --rm -v repo:/repo -w /repo reprolens-demo python benchmark.py --model rf | Exits 0, stdout contains Test accuracy: 0.XXX, < 180s |
| LR run | docker run --rm -v repo:/repo -w /repo reprolens-demo python benchmark.py --model logreg | Exits 0, stdout contains Test accuracy: 0.XXX, < 180s |
| Regex match | python -c import re; print(re.findall(rTest accuracy:\s+([\d.]+), open(stdout_rf.txt).read())) | Returns [0.XXX] |
| Fallback capture | mkdir -p runs/RUN-001 runs/RUN-002 + copy logs | Dir structure exists |
| Report render | python run_demo.py (with fallback mode) | Generates report.html, opens in browser |
| Evidence drawer | Open report.html to click row | Drawer toggles, shows E1/E2 chips |

**If ANY check fails to Option A fallback (RandomForest only)**

---

## Resource Requirements (Laptop)

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Disk | 10 GB free | 20 GB free |
| CPU | 2 cores | 4+ cores |
| Docker | Desktop 4.x+ | Latest |
| Python | 3.11+ | 3.11+ |
| Network | For git clone + docker pull (pre-hackathon only) | None during demo |

---

## Conclusion

**The prototype is technically feasible.** Every component in scope is:
- Implementable in < 2 hours each
- Deterministic (no LLM, no randomness)
- Testable beforehand
- Runnable offline during demo (with pre-built image)

**The only real risks are external:**
1. Docker daemon not running -- check docker info at demo start
2. Repo unavailable -- pre-cloned at pinned commit
3. Network during demo -- --network=none + pre-loaded image

**Build the 7 core components. Ignore the 19 DO NOT BUILD items.**
