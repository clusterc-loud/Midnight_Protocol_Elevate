# ReproLens Engine - Configuration loader
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_json(path: str) -> dict:
    """Load and parse JSON file."""
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_paper_config(paper_dir: Path) -> dict:
    """Load paper configuration from paper directory."""
    paper_json = paper_dir / "paper.json"
    if not paper_json.exists():
        raise FileNotFoundError(f"paper.json not found in {paper_dir}")

    with open(paper_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_claims(claims_path: str) -> List[dict]:
    """Load claims from file path."""
    path = Path(claims_path)
    if not path.exists():
        return []
    return load_json(str(path))


def load_mappings(mappings_path: str) -> List[dict]:
    """Load mappings from file path."""
    path = Path(mappings_path)
    if not path.exists():
        return []
    return load_json(str(path))


def load_paper(paper_dir: Path) -> dict:
    """Load complete paper configuration."""
    paper_config = load_json(paper_dir / "paper.json")
    claims = load_claims(str(paper_dir / "claims.json"))
    mappings = load_mappings(str(paper_dir / "mappings.json"))

    return {
        "paper": paper_config,
        "claims": claims,
        "mappings": mappings
    }


def discover_papers(papers_dir: Path) -> List[dict]:
    """Discover all paper configurations in papers directory."""
    papers = []
    if not papers_dir.exists():
        return []

    for paper_dir in papers_dir.iterdir():
        if paper_dir.is_dir():
            paper_json = paper_dir / "paper.json"
            if paper_json.exists():
                paper_data = load_paper(paper_dir)
                papers.append({
                    "id": paper_dir.name,
                    "config": paper_data
                })
    return papers


def get_paper_dir(paper_id: str, papers_dir: Path) -> Path:
    """Get paper directory path."""
    paper_dir = papers_dir / paper_id
    if not paper_dir.exists():
        raise FileNotFoundError(f"Paper directory not found: {paper_id}")
    return paper_dir


def load_paper_config(paper_id: str, papers_dir: Path) -> dict:
    """Load complete paper configuration."""
    paper_dir = get_paper_dir(paper_id, Path("papers"))
    return load_paper(Path(f"papers/{paper_id}"))