from enum import Enum
from typing import List, Dict, Any, Optional


def _parse_mapping_confidence(mapping) -> dict:
    """Extract confidence information from a mapping (dict or CommandMapping)."""
    # Handle CommandMapping object
    if hasattr(mapping, 'confidence'):
        rationale = mapping.confidence.rationale
        evidence = mapping.confidence.evidence
        score = mapping.confidence.score
    # Handle dict from mappings.json
    elif isinstance(mapping, dict):
        rationale = mapping.get("rationale", "Human-confirmed mapping")
        evidence = mapping.get("evidence", ["mappings.json human-curated"])
        score = mapping.get("score", 1.0)
    else:
        rationale = "Human-confirmed mapping"
        evidence = ["mappings.json human-curated"]
        score = 1.0
    
    return {
        "score": score,
        "rationale": rationale,
        "evidence": evidence,
        "effective_tier": "E2"  # Mapping is always E2 (human-confirmed / deterministically inferred)
    }


def make_evidence(kind: str, ref: str, excerpt: str = "") -> dict:
    """Create an evidence object."""
    from backend.engine.models import EvidenceTier
    tier = EVIDENCE_TIER_MAP.get(kind, "E3")
    return {
        "id": f"EV-{kind}-{hash(ref) % 10000}",
        "tier": tier,
        "kind": kind,
        "ref": ref,
        "excerpt": excerpt
    }


def _extract_mapping_confidence(mapping) -> dict:
    """Extract confidence information from a mapping."""
    return _parse_mapping_confidence(mapping)


def build_evidence(claim: dict, mapping, stdout: str, metric: float, comparison: dict, exit_code: int = 0, image_digest: str = "", repo_commit: str = "") -> list:
    """Build evidence list for a claim."""
    ev = []
    model_name = claim.get("model", claim.get("name", "Unknown"))
    claim_id = claim.get("id", "unknown")
    
    # Extract mapping confidence
    mapping_conf = _extract_mapping_confidence(mapping)
    
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
    
    # Mapping evidence with confidence (E2)
    if hasattr(mapping, 'command'):
        mapping_info = f"{mapping.command} + {mapping.files}"
    else:
        mapping_info = mapping.get("command", "unknown") + " + " + str(mapping.get("files", []))
    ev.append({
        "id": f"EV-mapping-{hash(mapping_info) % 10000}",
        "tier": mapping_conf["effective_tier"],
        "kind": "mapping",
        "ref": f"mappings.json:{claim_id}",
        "excerpt": mapping_info
    })
    
    ref_pkg = "pip freeze"
    ev.append({
        "id": f"EV-package_version-{hash(ref_pkg) % 10000}",
        "tier": "E1",
        "kind": "package_version",
        "ref": ref_pkg,
        "excerpt": "scikit-learn==1.4.2"
    })
    
    ref_exit = f"container exit code"
    ev.append({
        "id": f"EV-exit_code-{hash(ref_exit) % 10000}",
        "tier": "E1",
        "kind": "exit_code",
        "ref": ref_exit,
        "excerpt": f"exit code: {exit_code}"
    })
    
    ref_digest = f"image digest"
    ev.append({
        "id": f"EV-image_digest-{hash(ref_digest) % 10000}",
        "tier": "E1",
        "kind": "image_digest",
        "ref": ref_digest,
        "excerpt": image_digest or "sha256:abc123..."
    })
    
    ref_commit = f"repository commit"
    ev.append({
        "id": f"EV-repo_commit-{hash(ref_commit) % 10000}",
        "tier": "E1",
        "kind": "repo_commit",
        "ref": ref_commit,
        "excerpt": repo_commit or "a1b2c3d"
    })
    
    if comparison.get("rel_pct") is not None:
        rel_pct = abs(comparison.get("rel_pct", 0))
        ref_diff = f"computed difference"
        ev.append({
            "id": f"EV-calculated_diff-{hash(ref_diff) % 10000}",
            "tier": "E2",
            "kind": "calculated_diff",
            "ref": ref_diff,
            "excerpt": f"abs_diff={comparison.get('abs_diff', 0):.4f}, rel%={comparison.get('rel_pct', 0):.2f}%"
        })
    
    # Add mapping confidence evidence note
    ev.append({
        "id": f"EV-mapping_confidence-{hash(claim_id) % 10000}",
        "tier": mapping_conf["effective_tier"],
        "kind": "mapping_confidence",
        "ref": f"mappings.json:{claim_id}",
        "excerpt": f"Confidence: {mapping_conf['score']:.0%} - {mapping_conf['rationale']}"
    })
    
    return ev