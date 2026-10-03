"""Report generation for ReproLens."""
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def render_report(
    claims: list,
    results: list,
    all_evidence: list,
    replay_mode: bool = False,
    paper_title: str = "Fashion-MNIST Benchmark",
    paper_arxiv: str = "arXiv:1708.07747",
    repo_url: str = "https://github.com/zalandoresearch/fashion-mnist",
    repo_commit: str = "a1b2c3d",
    image_digest: str = "sha256:abc123...",
    python_version: str = "3.11",
    sklearn_version: str = "1.4.2",
    limitations: list = None,
) -> str:
    """Render HTML report using Jinja2 template."""
    if limitations is None:
        limitations = [
            "Single seed - variance not estimated",
            "Human-curated mapping",
            "CPU-only execution",
            "sklearn version not stated in paper"
        ]

    summary = {
        "near_exact": sum(1 for r in results if r.get("comparison", {}).get("verdict") == "near_exact"),
        "partial": sum(1 for r in results if r.get("comparison", {}).get("verdict") == "partial"),
        "significant": sum(1 for r in results if r.get("comparison", {}).get("verdict") == "significant"),
        "not_executable": sum(1 for r in results if r.get("comparison", {}).get("verdict") == "not_executable"),
        "insufficient": sum(1 for r in results if r.get("comparison", {}).get("verdict") == "insufficient"),
    }

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("report_template.html")

    return template.render(
        paper_title=paper_title,
        paper_arxiv=paper_arxiv,
        repo_url=repo_url,
        repo_commit=repo_commit,
        image_digest=image_digest,
        python_version=python_version,
        sklearn_version=sklearn_version,
        claims=claims,
        results=results,
        evidence=all_evidence,
        replay_mode=replay_mode,
        summary=summary,
        limitations=limitations
    )