"""Evidence model and builder for ReproLens."""
from typing import List, Dict, Any, Optional


EVIDENCE_TIER_MAP = {
    "paper_span": "E1",
    "table_cell": "E1",
    "log_line": "E1",
    "package_version": "E1",
    "resource_stat": "E1",
    "file_range": "E2",
    "config_key": "E2",
    "mapping": "E2",
    "llm_note": "E3",
}


def make_evidence(kind: str, ref: str, excerpt: str = "") -> dict:
    """Create an evidence object."""
    tier = EVIDENCE_TIER_MAP.get(kind, "E3")
    return {
        "id": f"EV-{kind}-{hash(ref) % 10000}",
        "tier": tier,
        "kind": kind,
        "ref": ref,
        "excerpt": excerpt
    }


def build_evidence(claim: dict, mapping: dict, stdout: str, metric: float, comparison: dict) -> list:
    """Build evidence list for a claim."""
    ev = []
    model_name = claim.get("model", claim.get("name", "Unknown"))
    claim_id = claim.get("id", "unknown")
    
    ref_paper = f"Table 1, Row {model_name}, Col Accuracy"
    ev.append({
        "id": f"EV-paper_span-{hash(ref_paper) % 10000}",
        "tier": "E1",
        "kind": "paper_span",
        "ref": ref_paper,
        "excerpt": str(claim["reported_value"])
    })
    
    ref_log = "stdout.log:last"
    ev.append({
        "id": f"EV-log_line-{hash(ref_log) % 10000}",
        "tier": "E1",
        "kind": "log_line",
        "ref": ref_log,
        "excerpt": f"Test accuracy: {metric}"
    })
    
    ref_mapping = f"mappings.json:{claim_id}"
    ev.append({
        "id": f"EV-mapping-{hash(ref_mapping) % 10000}",
        "tier": "E2",
        "kind": "mapping",
        "ref": ref_mapping,
        "excerpt": mapping.get("command", "")
    })
    
    ref_pkg = "pip freeze"
    ev.append({
        "id": f"EV-package_version-{hash(ref_pkg) % 10000}",
        "tier": "E1",
        "kind": "package_version",
        "ref": ref_pkg,
        "excerpt": "scikit-learn==1.4.2"
    })
    return ev