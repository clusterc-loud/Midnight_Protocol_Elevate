# Pydantic models for ReproLens data structures.
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class EvidenceTier(str, Enum):
    E1 = "E1"  # Hard evidence - directly observed
    E2 = "E2"  # Auto-inferred - deterministically derived
    E3 = "E3"  # LLM interpretation


class VerdictType(str, Enum):
    NEAR_EXACT = "near_exact"
    PARTIAL = "partial"
    SIGNIFICANT = "significant"
    NOT_EXECUTABLE = "not_executable"
    INSUFFICIENT = "insufficient"


class ExecutionMode(str, Enum):
    LIVE = "live"
    REPLAY = "replay"


class ProvenanceConfig(BaseModel):
    paper: str
    page: int
    table: str
    row: str
    col: str


class CommandMapping(BaseModel):
    command: str
    files: List[str] = []


class Claim(BaseModel):
    id: str
    name: str
    metric: str
    reported_value: float
    provenance: ProvenanceConfig
    mapping: dict

    class Config:
        arbitrary_types_allowed = True


class PaperConfig(BaseModel):
    id: str
    title: str
    authors: List[str] = []
    year: int
    arxiv: str
    paper_url: str = ""
    repo_url: str = ""
    commit: str = ""
    environment: Dict[str, Any] = {}
    dockerfile: str = "Dockerfile"
    claims: List[dict] = []


class Mapping(BaseModel):
    claim_id: str
    command: str
    files: List[str] = []


class Evidence(BaseModel):
    id: str
    tier: EvidenceTier
    kind: str
    ref: str
    excerpt: str = ""


class ComparisonResult(BaseModel):
    abs_diff: float
    rel_pct: Optional[float]
    verdict: str


class ExecutionResult(BaseModel):
    claim_id: str
    model: str
    reported: float
    reproduced: Optional[float]
    comparison: Dict[str, Any]
    evidence: List[dict]
    execution_mode: str = "live"
    wall_time: float = 0.0
    exit_code: int = 0


# Regex patterns for metric extraction
REGEX_PATTERNS = {
    "EXP-001": r"Test accuracy:\s+([\d.]+)",
    "EXP-002": r"Test accuracy:\s+([\d.]+)",
    "EXP-003": r"Test accuracy:\s+([\d.]+)",
    "EXP-004": r"Test accuracy:\s+([\d.]+)",
}