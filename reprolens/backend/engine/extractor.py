"""Metric extraction from experiment output."""
import re
from typing import Optional


def extract_metric(exp_id: str, stdout: str) -> Optional[float]:
    """Extract metric value from experiment stdout."""
    matches = re.findall(r"Test accuracy:\s+([\d.]+)", stdout)
    return float(matches[-1]) if matches else None


def extract_metric_by_pattern(exp_id: str, stdout: str, pattern: str = None) -> Optional[float]:
    """Extract metric using a specific pattern."""
    if pattern is None:
        pattern = r"Test accuracy:\s+([\d.]+)"
    matches = re.findall(pattern, stdout)
    return float(matches[-1]) if matches else None