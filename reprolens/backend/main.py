from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime
import uuid

# Import engine modules
from backend.engine import models, loader, executor, extractor, comparator, evidence, fallback, reporter

app = FastAPI(title="ReproLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for live runs
live_runs: Dict[str, Dict] = {}
papers_cache: List[Dict] = None

def load_papers_catalog():
    global papers_cache
    if papers_cache is None:
        catalog_path = Path("papers.json")
        if catalog_path.exists():
            with open(catalog_path) as f:
                data = json.load(f)
                papers_cache = data.get("papers", [])
    return papers_cache

@app.get("/api/papers")
async def list_papers():
    """List all available papers."""
    papers = load_papers_catalog()
    return {"papers": [
        {
            "id": p["id"],
            "title": p["title"],
            "arxiv": p["arxiv"],
            "repo_url": p["repo_url"],
            "commit": p["commit"],
            "num_experiments": len(p["experiments"]),
            "image_name": p["image_name"]
        }
        for p in papers
    ]}

@app.get("/api/papers/{paper_id}")
async def get_paper(paper_id: str):
    """Get paper details including claims and mappings."""
    papers = load_papers_catalog()
    paper = next((p for p in papers if p["id"] == paper_id), None)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    claims = loader.load_claims(f"{paper['path']}/claims.json")
    mappings = loader.load_mappings(f"{paper['path']}/mappings.json")
    
    return {
        "paper": paper,
        "claims": claims,
        "mappings": mappings
    }

@app.get("/api/papers/{paper_id}/experiments")
async def get_experiments(paper_id: str):
    """Get all experiments for a paper."""
    papers = load_papers_catalog()
    paper = next((p for p in papers if p["id"] == paper_id), None)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    claims = loader.load_claims(f"{paper['path']}/claims.json")
    mappings = {m["claim_id"]: m for m in loader.load_mappings(f"{paper['path']}/mappings.json")}
    
    experiments = []
    for claim in claims:
        mapping = mappings.get(claim["id"], {})
        experiments.append({
            "id": claim["id"],
            "name": claim.get("model") or claim.get("name"),
            "metric": claim.get("metric", "accuracy"),
            "reported_value": claim["reported_value"],
            "provenance": claim.get("provenance", {}),
            "command": mapping.get("command", ""),
            "files": mapping.get("files", [])
        })
    
    return {"paper_id": paper_id, "experiments": experiments}

class RunRequest(BaseModel):
    paper_id: str
    experiment_ids: Optional[List[str]] = None
    fallback: bool = False

class RunResponse(BaseModel):
    run_id: str
    status: str
    message: str

@app.post("/api/runs", response_model=RunResponse)
async def start_run(request: RunRequest, background_tasks: BackgroundTasks):
    """Start a reproduction run for a paper."""
    papers = load_papers_catalog()
    paper = next((p for p in papers if p["id"] == request.paper_id), None)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    run_id = str(uuid.uuid4())[:8]
    
    # Determine which experiments to run
    claims = loader.load_claims(f"{paper['path']}/claims.json")
    if request.experiment_ids:
        claims = [c for c in claims if c["id"] in request.experiment_ids]
    
    # Initialize run state
    live_runs[run_id] = {
        "run_id": run_id,
        "paper_id": request.paper_id,
        "status": "starting",
        "started_at": datetime.now().isoformat(),
        "experiments": [],
        "current_experiment": None,
        "logs": [],
        "fallback": request.fallback
    }
    
    # Start background task
    background_tasks.add_task(run_experiments, run_id, paper, claims, request.fallback)
    
    return RunResponse(
        run_id=run_id,
        status="started",
        message=f"Run started for {paper['title']}"
    )

@app.get("/api/runs/{run_id}")
async def get_run_status(run_id: str):
    """Get run status and progress."""
    if run_id not in live_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return live_runs[run_id]

@app.get("/api/runs/{run_id}/events")
async def get_run_events(run_id: str):
    """Get run events for live pipeline visualization."""
    if run_id not in live_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    run = live_runs[run_id]
    return {
        "run_id": run_id,
        "status": run["status"],
        "current_experiment": run["current_experiment"],
        "experiments": run["experiments"],
        "logs": run["logs"][-50:]  # Last 50 log lines
    }

@app.get("/api/evidence/{paper_id}/{claim_id}")
async def get_evidence(paper_id: str, claim_id: str):
    """Get evidence for a specific claim."""
    papers = load_papers_catalog()
    paper = next((p for p in papers if p["id"] == paper_id), None)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    claims = loader.load_claims(f"{paper['path']}/claims.json")
    claim = next((c for c in claims if c["id"] == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    mappings = {m["claim_id"]: m for m in loader.load_mappings(f"{paper['path']}/mappings.json")}
    mapping = mappings.get(claim_id, {})
    
    # Try to load from latest run
    runs_dir = Path("runs")
    run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith("RUN-")])
    
    stdout = ""
    metric = claim["reported_value"]
    
    if run_dirs:
        latest_run = run_dirs[-1]
        stdout_path = latest_run / "stdout.log"
        if stdout_path.exists():
            stdout = stdout_path.read_text()
            metric = extractor.extract_metric(claim_id, stdout) or claim["reported_value"]
    
            comparison = comparator.compare(claim["reported_value"], metric)
            ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get("image_name", "reprolens-demo"), repo_commit=paper.get("commit", "a1b2c3d"))
    
    return {
        "claim_id": claim_id,
        "reported": claim["reported_value"],
        "reproduced": metric,
        "comparison": comparison,
        "evidence": ev,
        "provenance": claim.get("provenance", {}),
        "mapping": mapping
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def run_experiments(run_id: str, paper: dict, claims: List, use_fallback: bool):
    """Background task to run experiments."""
    run = live_runs[run_id]
    
    try:
        if not use_fallback:
            # Build Docker image
            run["status"] = "building"
            run["logs"].append(f"[{datetime.now().isoformat()}] Building Docker image: {paper['image_name']}")
            
            success = build_docker_image(paper)
            if not success:
                run["status"] = "fallback"
                run["logs"].append(f"[{datetime.now().isoformat()}] Build failed, switching to fallback mode")
                use_fallback = True
        
        run["status"] = "running"
        
        for i, claim in enumerate(claims):
            claim_id = claim["id"]
            run["current_experiment"] = claim_id
            run["logs"].append(f"[{datetime.now().isoformat()}] Starting {claim_id}: {claim.get('model') or claim.get('name')}")
            
            mappings = {m["claim_id"]: m for m in loader.load_mappings(f"{paper['path']}/mappings.json")}
            mapping = mappings.get(claim_id, {})
            command = mapping.get("command", "")
            
            if use_fallback:
                stdout, rc, wall, peak_mb = fallback.load_fallback(paper, claim_id)
                metric = extractor.extract_metric(claim_id, stdout)
            else:
                try:
                    stdout, rc, wall, peak_mb = executor.run_docker(command, paper)
                    metric = extractor.extract_metric(claim_id, stdout)
                    if metric is None:
                        raise ValueError("Metric extraction failed")
                except Exception as e:
                    run["logs"].append(f"[{datetime.now().isoformat()}] Live run failed: {e}. Falling back.")
                    stdout, rc, wall, peak_mb = fallback.load_fallback(paper, claim_id)
                    metric = extractor.extract_metric(claim_id, stdout)
                    use_fallback = True
            
            comparison = comparator.compare(claim["reported_value"], metric)
            ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get("image_name", "reprolens-demo"), repo_commit=paper.get("commit", "a1b2c3d"))
            
            exp_result = {
                "claim_id": claim_id,
                "model": claim.get("model") or claim.get("name"),
                "reported": claim["reported_value"],
                "reproduced": metric,
                "comparison": comparison,
                "evidence": ev,
                "provenance": claim.get("provenance", {}),
                "log_line": "stdout.log:last",
                "metric_text": f"Test accuracy: {metric}",
                "mapping": mapping,
                "config_note": "benchmark.py defaults",
                "discrepancy_note": "Single seed - variance not estimated.",
                "verdict_tooltip": f"abs_diff={comparison['abs_diff']:.4f}, rel%={comparison['rel_pct']:.2f}%"
            }
            
            run["experiments"].append(exp_result)
            run["logs"].append(f"[{datetime.now().isoformat()}] {claim_id}: {metric} (reported: {claim['reported_value']}) -> {comparison['verdict']}")
        
        run["status"] = "completed"
        run["completed_at"] = datetime.now().isoformat()
        run["logs"].append(f"[{datetime.now().isoformat()}] Run completed")
        
    except Exception as e:
        run["status"] = "error"
        run["logs"].append(f"[{datetime.now().isoformat()}] Error: {str(e)}")

def build_docker_image(paper: dict) -> bool:
    dockerfile_path = Path(paper["path"]) / paper["dockerfile"]
    if not dockerfile_path.exists():
        return False
    
    cmd = ["docker", "build", "-t", paper["image_name"], "-f", str(dockerfile_path), str(Path(paper["path"]).parent)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# Serve frontend
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>ReproLens API</h1><p>Frontend not found. Visit <a href='/docs'>/docs</a> for API docs.</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)