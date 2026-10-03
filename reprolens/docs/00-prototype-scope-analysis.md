# ReproLens Prototype Scope Analysis

**Date:** 2026-10-02
**Source Document:** `references/ReproLens_Project_Document.docx` (full project specification)
**Purpose:** Identify what to build for a realistic, working hackathon prototype that demonstrates the core innovation without over-engineering.

---

## 1. OFFICIAL REQUIREMENT (from Problem Statement EL-01)

The official problem statement requires **exactly** this chain:

| Step | Requirement |
|------|-------------|
| 1 | **Paper + repository** as input |
| 2 | **Experimental claim** extraction from paper |
| 3 | **Relevant implementation** identification in repository |
| 4 | **Experiment execution** in controlled environment |
| 5 | **Reported vs reproduced result** comparison |
| 6 | **Discrepancy analysis** with evidence |
| 7 | **Evidence-backed assessment** report |

**Explicit constraints from PS:**
- CPU-only resources (hackathon papers curated for this)
- Papers and repositories are lightweight and curated by organisers
- System must NOT reduce to "does code exist?" or "paper summary"
- Working prototype/UI demonstrating the reproducibility workflow
- Demonstration of experiment execution, result comparison, discrepancy analysis
- Sample reproducibility assessment/report with supporting evidence

**Evaluation criteria (inferred from deliverables):**
- Soundness of architecture
- Working end-to-end demo
- Real experiment execution with real result comparison
- Quality of discrepancy analysis and evidence
- Usable, honest report
- Respect for CPU-only constraint

---

## 2. EXISTING FULL-PROJECT DESIGN (from reference document)

The reference document proposes a **comprehensive production system** with:

### 2.1 Core Modules (12+)
1. Paper Parsing & Claim Extraction
2. Repository Indexing & Inventory
3. Experiment Mapping (claim to code)
4. Execution Command Derivation
5. Docker-based Execution Environment
6. Result Comparison Engine
7. Discrepancy Analysis Engine
8. Evidence Model (E1/E2/E3 tiers)
9. Reproducibility Scoring (Readiness + Execution + Verdict)
10. Report Generation (JSON/HTML/PDF)
11. Database (15 tables)
12. REST API (10+ endpoints)
13. Full UI (8 screens with stepper navigation)
13. Security Hardening

### 2.2 Infrastructure
- PostgreSQL/SQLite database
- Docker containers per run (setup + run phases)
- Worker process with Docker socket access
- SSE/polling for async operations
- File storage for logs, artifacts, reports

### 2.3 Advanced Features
- Multi-seed variance estimation (3+ seeds)
- Follow-up ablation experiments
- Human checkpoints at extraction and mapping
- Tolerance policy configuration
- Evidence traceability on every conclusion
- LLM-assisted extraction with span verification
- Confidence scoring for mappings

### 2.4 Non-Goals (Explicit)
- Autonomous reimplementation from scratch
- GPU/large-scale reproduction
- Scientific validity judgement
- Multi-tenant production security

---

## 3. PROTOTYPE REQUIREMENT (What We Actually Need)

For a **convincing hackathon demo** by a small student team (3-5 people, ~48 hours), the prototype must:

### Must Demonstrate (Core Innovation)
- End-to-end chain from paper claim to code to execution to comparison to report
- Real execution in a sandbox (Docker) not simulated
- Real comparison of actual numbers (paper vs reproduced)
- Evidence-backed discrepancy analysis at least one worked example
- Paper parsing to pre-extracted claims for demo paper(s)
- Repository analysis to pre-identified entry points for demo repo(s)
- Database to JSON files or SQLite (no migrations, no ORM)
- API to CLI script or minimal local server (no auth, no rate limiting)
- UI to Single-page HTML report or simple Streamlit/Gradio app
- Multi-experiment to 1-2 key experiments from 1 paper
- Multi-seed to 1 seed (explicitly note variance limitation)
- LLM components to rule-based extraction or manual curation for demo

### Must NOT Do
- Multi-user, multi-project, persistence across sessions
- Arbitrary paper/repo upload (use pre-vetted demo pair only)
- Complex mapping algorithms (manual or simple heuristic is fine)
- Full security hardening (run on isolated machine, pre-vetted code only)
- PDF parsing, table extraction, OCR
- Embedding-based similarity, LLM re-ranking

---

## 3. PROTOTYPE REQUIREMENT (What We Actually Need)

For a **convincing hackathon demo** by a small student team (3-5 people, ~48 hours), the prototype must:

### Must Demonstrate (Core Innovation)
- End-to-end chain from paper claim to code to execution to comparison to report
- Real execution in a sandbox (Docker) not simulated
- Real comparison of actual numbers (paper vs reproduced)
- Evidence-backed discrepancy analysis at least one worked example
- Honest reporting shows what worked, what didn
'
t, and why
- Human-in-the-loop at critical decisions (claim review, mapping confirmation)

### Can Be Simplified / Hardcoded / Precomputed
- Paper parsing to pre-extracted claims for demo paper(s)
- Repository analysis to pre-identified entry points for demo repo(s)
- Database to JSON files or SQLite (no migrations, no ORM)
- API to CLI script or minimal local server (no auth, no rate limiting)
- UI to Single-page HTML report or simple Streamlit/Gradio app
- Multi-experiment to 1-2 key experiments from 1 paper
- Multi-seed to 1 seed (explicitly note variance limitation)
- LLM components to rule-based extraction or manual curation for demo

### Must NOT Do
- Multi-user, multi-project, persistence across sessions
- Arbitrary paper/repo upload (use pre-vetted demo pair only)
- Complex mapping algorithms (manual or simple heuristic is fine)
- Full security hardening (run on isolated machine, pre-vetted code only)
- PDF parsing, table extraction, OCR
- Embedding-based similarity, LLM re-ranking

---

## 4. SIMPLIFICATION DECISIONS

| Full Project Feature | Prototype Approach | Rationale |
|---------------------|-------------------|-----------|
| Paper PDF parsing | Pre-extracted claim JSON | PDF parsing is brittle; not the core innovation |
| Repo indexing (AST, config scan) | Pre-identified entry points + simple file glob | Mapping is hard; demo with known-good mapping |
| Database (15 tables) | In-memory dicts to JSON export | Zero setup; sufficient for single-run demo |
| REST API (10 endpoints) | Single CLI command run_demo.py | No network complexity; easier to debug |
| 8-screen UI | 1 HTML report + optional simple web view | Report IS the demo output; judges read reports |
| Multi-experiment orchestration | Sequential loop over 1-2 hardcoded experiments | Demonstrates the chain; parallelism not needed |
| 3-seed variance | 1 seed + explicit single run badge | Honest about limitation; saves 3x runtime |
| LLM extraction | Rule-based (table to claim) + manual review | Avoids API costs, latency, non-determinism |
| LLM mapping | Manual mapping file (claim to command) | Mapping is the hardest part; human-curated for demo |
| Docker per-run | Single pre-built image + docker run | Pre-build saves demo time; reproducible env |
| Evidence tiers (E1/E2/E3) | Simplified: source: paper code log inference | Keeps traceability without complexity |
| Scoring (readiness + execution) | Simple verdict: near_exact / partial / significant / not_executable / insufficient | Verdict is what judges see; scores are secondary |
| Follow-up ablation runs | Manual what if notes in report | Can demonstrate concept without extra execution |

---

## 5. DEFERRED / FUTURE FEATURES

These are **explicitly out of scope** for the prototype:

| Feature | Defer To |
|---------|----------|
| Arbitrary paper upload + parsing | Full product |
| Arbitrary repo URL + auto-clone | Full product |
| Multi-user, auth, project persistence | Full product |
| Embedding-based code search | Full product |
| LLM-assisted extraction/mapping | Full product |
| Multi-seed variance estimation | Full product |
| Automated follow-up ablation experiments | Full product |
| Tolerance policy configuration UI | Full product |
| Stronger sandboxing (gVisor, Kata, Firecracker) | Future scope |
| GPU support | Future scope |
| Multi-language (non-Python) repos | Future scope |
| Benchmark evaluation (CORE-Bench, PaperBench) | Future scope |
| CI/CD, deployment, monitoring | Future scope |

---

## 6. WHAT GENUINELY NEEDS TO EXECUTE (Credibility Check)

For the demo to be **credible and not dishonest**, these MUST actually run:

| Component | Must Execute? | How |
|-----------|---------------|-----|
| Docker container start | Yes | docker run --rm ... |
| Dependency install (setup phase) | Yes | In Dockerfile or entrypoint |
| Experiment code execution | Yes | Actual python train.py ... |
| Metric extraction from stdout/logs | Yes | Parse actual output |
| Numerical comparison (paper vs actual) | Yes | Real arithmetic |
| Report generation with real numbers | Yes | Template filled with actual values |

**What can be precomputed/faked WITHOUT dishonesty:**
- Paper claim values (they are from the PDF just hardcode them)
- Mapping decision (human-curated transparent about it)
- Repository clone (pre-cloned at known commit)
- Docker image (pre-built saves time, same result)
- Analysis progress UI (can be a simple progress bar)

**Honesty requirement:** Every simulated step must be **visibly labelled** in the report (e.g., Mapping confirmed by human, Single seed variance not estimated).

---

## 7. RISKY / TIME-CONSUMING PARTS TO AVOID

| Risk | Why Avoid | Alternative |
|------|-----------|-------------|
| PDF table extraction | Unreliable, many edge cases | Use demo paper with known tables; pre-extract |
| Repo analysis (AST, configs) | Complex, language-specific | Pre-analyse demo repo; hardcode entry points |
| LLM API integration | Cost, latency, non-determinism, prompt tuning | Rule-based + human for demo |
| Multi-experiment scheduler | State machine complexity | Sequential for-loop |
| SSE/async API | Debugging difficulty | Synchronous CLI |
| Database migrations | Schema evolution pain | JSON files |
| Docker socket security | Root-equivalent risk | Run on dedicated VM; pre-vetted repos only |
| OCR for scanned PDFs | Entire separate problem | Organisers provide text-based PDFs |

---

## 8. SMALLEST END-TO-END WORKFLOW (Minimum Viable Demo)

```
INPUT (prepared):
  paper.pdf (Fashion-MNIST benchmark paper)
  repo/ (shallow clone at known commit)
  claims.json (pre-extracted: 2-3 key table rows)
  mappings.json (human-curated: claim to run command)

EXECUTE (live, ~5-10 min):
  1. Build/load Docker image (pre-built preferred)
  2. For each claim:
     a. Run container: docker run --rm -v repo:/repo -w /repo image python benchmark.py --model=rf --dataset=fashion-mnist
     b. Capture stdout, stderr, exit code, wall time, peak memory
     c. Parse metric from output (regex on last line or JSON output)
  3. Compare: compute abs_diff, rel_dev_pct, verdict
  4. Generate report.html with:
     - Paper info, repo commit, environment
     - Per-claim: reported value, reproduced value, diff, verdict
     - Evidence links (log line numbers, paper page/table)
     - Discrepancy notes (if any)
     - Honest limitations section

OUTPUT:
  report.html (open in browser for judges)
```

**Total live execution time:** ~5-10 minutes (2-3 experiments x 2-3 min each)  
**Prep time (before hackathon):** ~2-4 hours (extract claims, curate mappings, build Docker image, test runs)

---

## 9. PROPOSED PROTOTYPE SCOPES (2-3 Options)

### Option A: Single-Claim Deep Dive (Minimal Risk)
- **1 paper, 1 claim, 1 experiment**
- Pre-extracted claim, pre-curated mapping
- Single Docker run, single comparison
- Generates one clean report
- **Time to build:** ~4-6 hours
- **Demo time:** ~2 minutes
- **Risk:** Very low
- **Impressiveness:** Shows chain works but limited scope

### Option B: Multi-Claim Comparison (Recommended Balance)
- **1 paper (Fashion-MNIST), 2-3 claims (e.g., RF, Logistic Regression, MLP)**
- Pre-extracted claims, pre-curated mappings
- Sequential Docker runs (or parallel if time)
- Comparison table with multiple rows
- Demonstrates: some near-exact, some partial, maybe one failure
- **Time to build:** ~8-12 hours
- **Demo time:** ~5-8 minutes
- **Risk:** Low-medium (multiple runs = more failure points)
- **Impressiveness:** Shows breadth; verdict variety makes report interesting

### Option C: Two-Paper Contrast (Maximum Demo Impact)
- **2 papers (e.g., Fashion-MNIST + fastText or Tabular revisited)**
- 1-2 claims each
- Shows generalisation across domains (vision + NLP/tabular)
- One paper reproduces well; one has discrepancies (missing data, version diff)
- **Time to build:** ~16-24 hours
- **Demo time:** ~10-15 minutes
- **Risk:** Medium-high (two repos = double env issues)
- **Impressiveness:** Highest shows platform concept, not just one-off

---

## 10. DECISION FRAMEWORK

Choose based on **team capacity** and **hackathon constraints**:

| Factor | Choose A | Choose B | Choose C |
|--------|----------|----------|----------|
| Team size | 2-3 | 3-4 | 4-5 |
| Python/ML experience | Low | Medium | High |
| Docker experience | Low | Medium | High |
| Time before hackathon | <1 day | 1-2 days | 2+ days |
| Demo slot length | 3 min | 5-8 min | 10+ min |
| Want to show discrepancy analysis | No | Yes | Yes |
| Want to show cross-domain | No | No | Yes |

**Recommendation:** Start with **Option B** as baseline. If team finishes early, extend to Option C. If running behind, fall back to Option A.

---

## 11. NEXT STEPS

1. **Team selects prototype scope** (A, B, or C)
2. **Identify exact demo paper(s) and repo(s)** confirm they run on CPU in <5 min each
3. **Pre-extract claims** and **curate mappings** (manual work, done before hackathon)
4. **Build Docker base image** with all dependencies (test it runs)
5. **Implement minimal orchestration script** (run_demo.py)
6. **Build report template** (HTML with evidence links)
7. **Rehearse full run** measure actual times, fix failures
8. **Prepare fallback** (pre-recorded run logs + report)

---

## Appendix: Demo Paper Candidates (from reference doc)

| Candidate | Paper | Repo | Claim Type | Est. CPU Time | Status |
|-----------|-------|------|------------|---------------|--------|
| **1 (Primary)** | Fashion-MNIST benchmark | github.com/zalandoresearch/fashion-mnist (or benchmark fork) | Table of sklearn classifier accuracies | 2-5 min/classifier | Verified |
| 2 | fastText text classification | github.com/facebookresearch/fastText | Classification accuracy on AG News | ~3 min | To verify |
| 3 | Revisiting Deep Learning for Tabular Data | github.com/... | Tabular benchmarks (MLP vs RF vs XGBoost) | 5-10 min | To verify |
| 4 | UMAP | github.com/lmcinnes/umap | Embedding quality metrics | ~5 min | To verify |

**Selection guidance:** Use Candidate 1 for main demo (confirmed working). Use Candidate 3 or 4 only to show honest partial/insufficient outcomes if time permits.

---

**End of Analysis** Ready for team review and scope selection.
