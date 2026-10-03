# ReproLens Prototype - UI/UX Design

**Date:** 2026-10-02  
**Scope:** docs/03-final-prototype-scope.md (Option B Reduced: 2 claims, Fashion-MNIST)  
**Reference:** Original project document Section 20 (UI/UX) + Prototype Architecture (docs/05-prototype-architecture.md)  
**Design Philosophy:** Functional, not decorative. Show provenance everywhere. Show uncertainty explicitly. Never hide interpretation. Single HTML report + terminal = entire UI.

---

## The Story the UI Must Tell

Paper > Claims > Code > Execution > Results > Discrepancy > Evidence

Each transition must be visibly traceable in the UI:

| Story Step | Where Visible | Evidence Tier |
|------------|---------------|---------------|
| Paper > Claims | Report header + claim rows | E1 (paper span) |
| Claims > Code | Evidence drawer (mapping chip) | E2 (human-confirmed mapping) |
| Code > Execution | Terminal (live docker logs) | E1 (stdout log lines) |
| Execution > Results | Comparison table + extracted metric | E1 (extracted value) |
| Results > Discrepancy | Comparison table (verdict) + drawer notes | E2 (threshold rule) |
| Discrepancy > Evidence | Evidence drawer (chips with refs) | E1/E2/E3 badges |

---

## Screens Required for Prototype

Only **two screens** exist in the prototype:

| Screen | When | Purpose |
|--------|------|---------|
| **Terminal (Live)** | During python run_demo.py | Show live execution, prove real work happens |
| **Report.html (Browser)** | After execution completes | Present results, evidence, verdicts, limitations |

**No other screens:** No landing page, no upload screens, no steppers, no dashboards, no settings. The prototype scope explicitly excludes all of these.


---

## Screen 1: Terminal (Live Execution)

### Purpose
Prove that **real code execution happens in a sandbox**. This is the #1 differentiator from experiment trackers and paper summarizers. Judges must see: Docker starts, code runs, logs stream, metrics extracted.

### Components

| Component | Specification |
|-----------|---------------|
| **Header banner** | [ReproLens] Loading claims.json... 2 claims<br>[ReproLens] Docker image: sha256:abc123... (pre-built)<br>[ReproLens] Repo commit: a1b2c3d (pinned) |
| **Per-experiment section** | === EXP-001: RandomForest ===<br>Command: python benchmark.py --model rf |
| **Docker log stream** | [docker] Starting container...<br>[docker] Loading Fashion-MNIST data...<br>[docker] Training RandomForest (n_estimators=100)...<br>[docker] Test accuracy: 0.869<br>[docker] Container exited (0), wall: 112s, peak_mem: 384MB |
| **Metric extraction** | Extracted: 0.869 (highlighted) |
| **Comparison result** | Reported: 0.873 | abs_diff: -0.004 | rel: -0.46% |
| **Verdict** | Verdict: near_exact (green text) |
| **Progress indicator** | Simple counter: EXP-001/2, EXP-002/2 |

### Displayed Data

| Data | Source | Visual Treatment |
|------|--------|------------------|
| Docker image digest | Pre-built image | Monospace, truncated sha256:abc123... |
| Repo commit SHA | Pinned commit | Monospace a1b2c3d |
| Command executed | mappings.json | Monospace, bold |
| Streaming stdout | Docker container | Live, line-by-line, prefixed [docker] |
| Extracted metric | Regex on stdout | Bold, green, large |
| Comparison math | Computed live | Monospace, aligned columns |
| Verdict | Threshold rule | Colored badge: green/yellow/red |

### User Actions

| Action | Trigger | Feedback |
|--------|---------|----------|
| Start demo | python run_demo.py | Terminal clears, header prints immediately |
| Watch | Passive | Logs stream in real time |
| Interrupt | Ctrl+C | Clean exit, partial report generated if possible |

### Loading States

| State | Visual |
|-------|--------|
| Docker starting | [docker] Starting container... (immediate) |
| Experiment running | Streaming logs (variable duration 2-3 min) |
| Extracting metric | Extracted: 0.869 (instant after container exits) |
| Rendering report | [ReproLens] Rendering report.html... (instant) |

### Error States

| Error | Terminal Display | Fallback |
|-------|------------------|----------|
| Docker daemon down | [ERROR] Docker daemon not running. Run docker info to verify. | Exit 1 |
| Image pull fails | [WARN] Image load failed. Using pre-recorded fallback. | Load runs/RUN-XXX/ |
| Container timeout (15 min) | [WARN] Experiment timed out after 900s. Falling back. | Load fallback |
| Container OOM | [WARN] Container killed (OOM). Falling back. | Load fallback |
| Metric extraction fails | [WARN] Could not extract metric. Falling back. | Load fallback |
| Non-zero exit code | [WARN] Container exited with code X. Falling back. | Load fallback |

### Demo Interaction

Presenter: Watch - this is the actual repository code running in a fresh Docker sandbox.
[docker logs stream for ~2 minutes]
Presenter: There is the accuracy: 0.869. The paper claimed 0.873. That is -0.46% deviation.
[Verdict appears: near_exact in green]
Presenter: The verdict comes from deterministic math: abs_diff / reported < 1%. No LLM involved.


---

## Screen 2: Report.html (Static Browser Page)

### Purpose
Present the **complete reproducibility assessment** with full evidence traceability. This is the deliverable judges will read and scrutinize.

### Layout Structure

HEADER: ReproLens Assessment: Fashion-MNIST Benchmark
        Paper: arXiv:1708.07747 | Repo: a1b2c3d | Image: sha256:abc...
        Env: Python 3.11, sklearn 1.4.2 | CPU-only | 4GB RAM
        [REPLAY MODE banner - only if fallback used]

COMPARISON TABLE
Claim | Reported | Reproduced | Abs Diff | Rel% | Verdict
RF    | 0.873    | 0.869      | -0.004   | -0.46% | near_exact
LogReg| 0.851    | 0.848      | -0.003   | -0.35% | near_exact

Summary: near_exact: 2 | partial: 0 | significant: 0

EVIDENCE DRAWERS (click row to expand)
RF:  E1: Paper Table 1  E1: stdout.log:42  E2: map
     Discrepancy: Paper n_estimators=100 matches repo default...
LogReg: E1: Paper Table 1  E1: stdout.log:38  E2: map
     Discrepancy: Paper max_iter not stated; repo default=100 used...

LIMITATIONS BADGES
Single seed - variance not estimated  Human-curated mapping
CPU-only execution  sklearn version not in paper


### Components

#### 1. Header Bar
| Element | Specification |
|---------|---------------|
| Title | ReproLens Assessment: Fashion-MNIST Benchmark |
| Paper | arXiv:1708.07747 (link to arXiv) |
| Repository | Commit a1b2c3d (link to GitHub) |
| Docker Image | sha256:abc123... (truncated, tooltip = full digest) |
| Environment | Python 3.11, scikit-learn 1.4.2 | CPU-only | 4GB RAM | 15-min timeout |
| REPLAY MODE | Red banner at top if fallback used |

#### 2. Comparison Table
| Column | Specification |
|--------|---------------|
| Claim | Model name (RF / LogReg) with experiment ID badge (EXP-001) |
| Reported | Paper value (0.873) with E1 chip on hover |
| Reproduced | Extracted value (0.869) with E1 chip on hover |
| Abs Diff | reproduced - reported (4 decimal places, negative = red) |
| Rel% | (abs_diff / |reported|) * 100 (2 decimal places, % sign) |
| Verdict | Color badge with tooltip showing threshold rule |

#### 3. Verdict Badges (Color-Coded)
| Verdict | Color | Tooltip |
|---------|-------|---------|
| near_exact | Green | rel_dev < 1% |
| partial | Yellow | 1% <= rel_dev < 5% |
| significant | Red | rel_dev >= 5% |
| not_executable | Gray | Container failed |
| insufficient | White dashed border | Only E3 evidence |

#### 4. Evidence Drawer (Per-Row Expandable)
| Trigger | Click anywhere on table row (or chevron) |
|---------|------------------------------------------|
| Animation | Smooth slide-down (CSS max-height transition) |
| Content | Horizontal chips + discrepancy notes |

**Evidence Chips (Horizontal Row):**
E1: Paper Table 1, Row RF, Col Accuracy
E1: stdout.log:42 Test accuracy: 0.869
E2: mappings.json:EXP-001 > python benchmark.py --model rf
E2: benchmark.py defaults: n_estimators=100
E3: LLM proposed: train.py (not used) [OPTIONAL]

**Chip Styling (E1/E2/E3):**
| Tier | Background | Border | Label |
|------|------------|--------|-------|
| E1 (Hard) | #e8f5e9 (light green) | 1px solid #4caf50 (solid green) | E1 |
| E2 (Inferred) | #fff3e0 (light orange) | 1px dashed #ff9800 (dashed orange) | E2 |
| E3 (Interpreted) | #fce4ec (light pink) | 1px dotted #e91e63 (dotted pink) | E3 |

**Discrepancy Notes (below chips):**
Potential cause (E2): Paper n_estimators=100 matches repo default.
Single seed - variance not estimated.

#### 5. Summary Cards (Above Table)
| Card | Value | Color |
|------|-------|-------|
| near_exact | 2 | Green |
| partial | 0 | Yellow |
| significant | 0 | Red |
| not_executable | 0 | Gray |
| insufficient | 0 | White |

#### 6. Limitation Badges (Footer)
| Badge | Text | Color |
|-------|------|-------|
| | Single seed - variance not estimated | Yellow outline |
| | Human-curated mapping | Yellow outline |
| | CPU-only execution | Yellow outline |
| | sklearn version not stated in paper | Yellow outline |

### Displayed Data

| Data Element | Source | Evidence Tier |
|--------------|--------|---------------|
| Paper claim values (0.873, 0.851) | claims.json | E1 |
| Claim provenance (Table 1, Row RF) | claims.json | E1 |
| Reproduced metrics (0.869, 0.848) | Live stdout / fallback | E1 |
| Extracted log lines | Docker stdout | E1 |
| Comparison math (abs_diff, rel%) | Computed live | E2 |
| Verdict thresholds | Hardcoded | E2 |
| Mapping command | mappings.json | E2 |
| Mapping files | mappings.json | E2 |
| Docker image digest | Pre-built | E1 |
| Repo commit SHA | Pinned | E1 |
| Package versions | pip freeze in image | E1 |
| Discrepancy notes | Pre-written | E2 |
| Limitation badges | Hardcoded | E2 |

### User Actions

| Action | Trigger | Feedback |
|--------|---------|----------|
| Open report | open report.html (or double-click) | Browser opens instantly |
| Click row | Click tr or chevron | Drawer slides down smoothly |
| Close drawer | Click row again or x | Drawer slides up |
| Hover evidence chip | Mouseover | Tooltip with full ref text |
| Hover verdict badge | Mouseover | Tooltip: rel_dev < 1% rule |
| Scroll | Mouse/trackpad | Standard browser scroll |

### Loading States

| State | Visual |
|-------|--------|
| Initial load | Instant (static HTML, no JS fetch) |
| Drawer expand | 200ms CSS transition (max-height) |
| Tooltip show | 150ms delay, fade-in |

### Error States

| Error | Display |
|-------|---------|
| Template render failed | Minimal static HTML with raw JSON data in pre |
| Missing evidence | Chip shows E? with ? tooltip |
| Missing fallback logs | Row shows not_executable verdict, drawer shows error |

### Demo Interaction

Presenter opens report.html in browser (fullscreen)
Presenter: Here is the full assessment. Two experiments, both near_exact.
[Clicks RF row > drawer expands]
Presenter: Click any row for full evidence. Green E1 = directly observed. Orange E2 = inferred.
[Hovers over E1 chip]
Presenter: Paper Table 1, Row RandomForest, Col Accuracy. That is hard evidence from the PDF.
[Hovers over E2 chip]
Presenter: Mapping is human-confirmed. Orange = inferred from our mappings.json.
[Points to verdict badge]
Presenter: Green badge = near_exact. Hover shows the rule: rel_dev < 1%. No LLM judgment.
[Points to limitation badges]
Presenter: Honest limitations: single seed, human mapping, CPU-only. We do not hide these.


---

## Evidence Tier Visual Language (Critical)

The E1/E2/E3 distinction is **central to the prototype's credibility**. Every piece of evidence must visibly communicate its tier.

### Chip Design Specification

E1: Paper Table 1, Row RF, Col Accuracy        [E1 chip]
  Background: #e8f5e9    Border: 1px solid #4caf50 (SOLID)
  Label: E1 in #2e7d32

E2: mappings.json > python benchmark.py --model rf  [E2 chip]
  Background: #fff3e0    Border: 1px dashed #ff9800 (DASHED)
  Label: E2 in #e65100

E3: LLM proposed train.py (not used)              [E3 chip]
  Background: #fce4ec    Border: 1px dotted #e91e63 (DOTTED)
  Label: E3 in #c62828

### Tier Legend (Always Visible in Report Footer)

Evidence Tiers:  E1 = Directly observed (log line, paper span, hash)
                 E2 = Deterministically inferred (mapping, config, version)
                 E3 = LLM interpretation (not used in critical path)
Rule: Conclusions resting only on E3 > Insufficient evidence

---

## Color Palette (Accessible)

| Role | Hex | Usage |
|------|-----|-------|
| E1 bg | #e8f5e9 | Evidence chips, near_exact badge |
| E1 border/text | #2e7d32 / #4caf50 | Solid green |
| E2 bg | #fff3e0 | Evidence chips, partial badge |
| E2 border/text | #e65100 / #ff9800 | Dashed orange |
| E3 bg | #fce4ec | Evidence chips, insufficient badge |
| E3 border/text | #c62828 / #e91e63 | Dotted pink |
| near_exact | #c8e6c9 / #2e7d32 | Green badge |
| partial | #ffe0b2 / #e65100 | Yellow badge |
| significant | #ffcdd2 / #c62828 | Red badge |
| not_executable | #e0e0e0 / #616161 | Gray badge |
| limitation | #fff3e0 / #e65100 | Yellow outline badge |
| replay mode | #ffcdd2 / #c62828 | Red banner |
| text primary | #212121 | Body text |
| text muted | #757575 | Secondary text |
| background | #ffffff | Page background |
| table header | #f5f5f5 | Table headers |
| row hover | #fafafa | Table row hover |

**Accessibility:** All color combinations meet WCAG AA contrast (4.5:1). Text labels accompany all color coding (no color-only information).

---

## Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Page title | System UI / -apple-system / sans-serif | 1.5rem | 600 |
| Section headers | System UI | 1.1rem | 600 |
| Table headers | System UI | 0.875rem | 600 |
| Table cells | System UI | 0.875rem | 400 |
| Evidence chips | System UI | 0.75rem | 500 |
| Verdict badges | System UI | 0.75rem | 600 |
| Limitation badges | System UI | 0.7rem | 500 |
| Discrepancy notes | System UI | 0.8rem | 400 |
| Monospace (code, hashes) | ui-monospace, SFMono-Regular, monospace | 0.8rem | 400 |

---

## Spacing & Layout

| Element | Spacing |
|---------|---------|
| Page padding | 24px |
| Section gap | 24px |
| Table cell padding | 12px 16px |
| Evidence chip gap | 8px |
| Chip internal padding | 4px 8px |
| Drawer transition | max-height 0.2s ease-out |
| Tooltip delay | 150ms show / 50ms hide |

---

## Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| Desktop (>=1024px) | Full table, horizontal chip rows, side-by-side summary cards |
| Tablet (768-1023px) | Table scrolls horizontally, chips wrap, summary cards stack |
| Mobile (<768px) | Not required for hackathon (desktop-first per original spec) |


---

## Technical Implementation (Jinja2 Template)

### Template Structure (report_template.html)

The template is a single self-contained HTML file with embedded CSS and JavaScript. No external dependencies.

Key template sections:

1. **Header** - Paper title, arxiv link, repo commit, image digest, environment, REPLAY MODE banner
2. **Summary Cards** - Counts for each verdict category
3. **Comparison Table** - Claim, Reported, Reproduced, Abs Diff, Rel%, Verdict with evidence chips
4. **Evidence Drawers** - Clickable rows expanding to show evidence chips + discrepancy notes
5. **Limitations Footer** - Limitation badges + Evidence tier legend

The template uses Jinja2 syntax for:
- Variable interpolation: {{ variable }}
- Conditionals: {% if replay_mode %}...{% endif %}
- Loops: {% for r in results %}...{% endfor %}
- Filters: {{ value|floatformat(2) }}

All CSS and JavaScript are embedded inline - no external files needed.

### Key Data Structures Passed to Template

`python
{
    'paper_title': 'Fashion-MNIST Benchmark',
    'paper_arxiv': 'arXiv:1708.07747',
    'repo_commit': 'a1b2c3d',
    'image_digest': 'sha256:abc123...',
    'python_version': '3.11',
    'sklearn_version': '1.4.2',
    'replay_mode': False,
    'summary': {'near_exact': 2, 'partial': 0, 'significant': 0, 'not_executable': 0, 'insufficient': 0},
    'results': [
        {
            'claim_id': 'EXP-001',
            'model': 'RandomForest',
            'reported': 0.873,
            'reproduced': 0.869,
            'comparison': {'abs_diff': -0.004, 'rel_pct': -0.46, 'verdict': 'near_exact'},
            'provenance': {'table': 'Table 1', 'row': 'RandomForest', 'col': 'Accuracy'},
            'log_line': 'stdout.log:42',
            'metric_text': 'Test accuracy: 0.869',
            'mapping': {'command': 'python benchmark.py --model rf', 'files': ['benchmark.py']},
            'config_note': 'benchmark.py defaults: n_estimators=100',
            'discrepancy_note': 'Paper n_estimators=100 matches repo default. Single seed - variance not estimated.',
            'llm_note': None
        },
        # ... second experiment
    ],
    'limitations': [
        'Single seed - variance not estimated',
        'Human-curated mapping',
        'CPU-only execution',
        'sklearn version not stated in paper'
    ]
}
`

The template renders this data into the complete report.html file.


---

## Demo Flow Summary

| Time | Action | Screen | Presenter Says |
|------|--------|--------|----------------|
| 0:00 | python run_demo.py | Terminal | We run one command. Two claims, two Docker runs. |
| 0:10 | Header prints | Terminal | Pre-built image, pinned repo commit. No network during execution. |
| 0:30 | RF logs stream | Terminal | Real sklearn training on Fashion-MNIST. CPU only. |
| 2:30 | RF verdict | Terminal | Extracted 0.869 vs paper 0.873. -0.46%. Near exact. |
| 3:00 | LR logs stream | Terminal | Second experiment. LogisticRegression. |
| 5:00 | LR verdict | Terminal | 0.848 vs 0.851. Also near_exact. |
| 5:30 | Report renders | Terminal | Generating HTML report... |
| 5:45 | Open report.html | Browser | Full assessment with evidence traceability. |
| 6:00 | Click RF row | Browser | Full evidence chain: paper > mapping > log > verdict. |
| 6:30 | Hover chips | Browser | E1 = observed. E2 = inferred. E3 = LLM (not used). |
| 7:00 | Point to badges | Browser | Honest limitations. No hidden assumptions. |

---

## What Is Explicitly NOT in the UI

| Excluded UI | Reason |
|-------------|--------|
| Landing page | Not in prototype scope |
| Project creation / upload | Pre-extracted claims only |
| PDF viewer with highlights | No PDF parsing |
| Repository mapping UI (split view) | Human-curated mappings.json |
| Run queue table | Sequential CLI output |
| Multi-screen stepper | Single report is deliverable |
| Tolerance slider | Hardcoded thresholds |
| Follow-up run button | Pre-recorded only |
| Export buttons (PDF/JSON) | HTML is the deliverable |
| Auth / user management | Not in scope |
| Settings / preferences | Not in scope |

---

## Implementation Checklist

| Task | File | Effort |
|------|------|--------|
| Embed CSS in template | report_template.html | 30 min |
| Embed JS (drawer toggle) | report_template.html | 10 min |
| Jinja2 template structure | report_template.html | 45 min |
| Evidence chip CSS (E1/E2/E3) | report_template.html | 20 min |
| Verdict badge CSS | report_template.html | 15 min |
| Drawer toggle JS | report_template.html | 10 min |
| Tooltip CSS | report_template.html | 15 min |
| Render call in run_demo.py | run_demo.py | 15 min |
| Evidence data structure | run_demo.py | 30 min |
| **Total** | | **~3 hours** |

---

## Demo Day Checklist

- report_template.html renders without errors
- Evidence drawers toggle smoothly
- E1/E2/E3 chips show correct colors/borders
- Verdict badges show correct colors
- Tooltips appear on hover
- REPLAY MODE banner appears when fallback used
- Limitation badges visible in footer
- Tier legend visible in footer
- Table scrolls horizontally on narrow screens
- Page prints cleanly (for handouts)
- Works in Chrome/Firefox/Safari (test on demo machine)

---

**UI/UX Status:** COMPLETE - Ready for implementation alongside run_demo.py.
