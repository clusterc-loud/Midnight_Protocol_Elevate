"""Fallback mechanism for ReproLens."""
from pathlib import Path
from typing import Tuple


# Map experiment IDs to run directories per paper
FALLBACK_RUN_MAP = {
    "fashion-mnist": {
        "EXP-001": "RUN-001",
        "EXP-002": "RUN-002",
    },
    "sklearn-benchmarks": {
        "EXP-001": "RUN-003",
        "EXP-002": "RUN-004",
        "EXP-003": "RUN-005",
        "EXP-004": "RUN-006",
    }
}


def load_fallback(paper: dict, exp_id: str) -> Tuple[str, int, float, int]:
    """
    Load pre-recorded fallback run data for a paper.
    Returns: (stdout, return_code, wall_time, peak_memory_mb)
    """
    paper_id = paper.get("id", "fashion-mnist")
    run_dir_map = FALLBACK_RUN_MAP.get(paper_id, {})
    run_dir_name = run_dir_map.get(exp_id)
    
    if not run_dir_name:
        raise FileNotFoundError(f"No fallback run mapping for {paper_id}:{exp_id}")
    
    run_dir = Path(f"runs/{run_dir_name}")
    
    if not run_dir.exists():
        raise FileNotFoundError(f"Fallback run directory not found: {run_dir}")
    
    stdout = (run_dir / "stdout.log").read_text(encoding="utf-8")
    rc = int((run_dir / "exit_code.txt").read_text().strip())
    wall = float((run_dir / "wall_sec.txt").read_text().strip())
    peak_mb = int((run_dir / "peak_mb.txt").read_text().strip()) if (run_dir / "peak_mb.txt").exists() else 0
    
    return stdout, rc, wall, peak_mb