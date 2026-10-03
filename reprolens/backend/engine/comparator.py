"""Comparison logic for ReproLens."""
from typing import Optional, Dict, Any
from .models import VerdictType


VERDICT_THRESHOLDS = {
    "near_exact": 1.0,   # < 1%
    "partial": 5.0,      # < 5%
    # >= 5% = significant
}


def compare(reported: float, reproduced: float) -> dict:
    """
    Compare reported vs reproduced values.
    Returns dict with abs_diff, rel_pct, verdict.
    """
    abs_diff = reproduced - reported
    
    if abs(reported) < 1e-10:
        rel_pct = None
    else:
        rel_pct = (abs_diff / abs(reported)) * 100
    
    if rel_pct is not None and abs(rel_pct) < 1.0:
        verdict = "near_exact"
    elif rel_pct is not None and abs(rel_pct) < 5.0:
        verdict = "partial"
    else:
        verdict = "significant"
    
    return {
        "abs_diff": abs_diff,
        "rel_pct": rel_pct,
        "verdict": verdict
    }