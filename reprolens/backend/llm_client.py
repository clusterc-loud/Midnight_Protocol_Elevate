#!/usr/bin/env python
"""Google Gemini LLM client for ReproLens.

Critical design principle: E3 (LLM note) evidence must NEVER become the
reproducibility verdict. Final verdicts must be grounded in E1/E2 evidence.
The LLM is used for:
  - Generating human-readable explanations grounded in specific evidence
  - Summarizing discrepancies between reported and reproduced results
  - Interpreting evidence chunks for the UI evidence drawer
"""

import os
import json
import logging
from dotenv import load_dotenv
load_dotenv()
from typing import Optional, Dict, Any, List

# Load from .env or environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

if not GEMINI_API_KEY:
    logging.warning(
        "GEMINI_API_KEY not set. LLM functionality disabled. "
        "Set the environment variable or add it to .env"
    )

# Google Generative AI client
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    _GEMINI_CLIENT_AVAILABLE = True
except Exception:
    _GEMINI_CLIENT_AVAILABLE = False


class LLMRater:
    """LLM-powered explanation generator that grounds explanations in E1/E2 evidence.

    Critical design principle: E3 (LLM note) must NEVER become the
    reproducibility verdict. Final verdicts must be grounded in E1/E2 evidence.
    The LLM is used ONLY for generating human-readable explanations;
    verdicts come from the deterministic comparison engine.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model or GEMINI_MODEL
        self._available = _GEMINI_CLIENT_AVAILABLE

        if not self._available:
            logging.warning("Gemini not available - LLM explanation disabled")
        else:
            try:
                self._model = genai.GenerativeModel(self.model_name)
                logging.info(f"Gemini model initialized: {self.model_name}")
            except Exception as e:
                logging.error(f"Failed to init Gemini model: {e}")
                self._available = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def explain_discrepancy(
        self,
        *,
        model_name: str,
        reported: float,
        reproduced: float,
        abs_diff: float,
        rel_pct: Optional[float],
        evidence: List[Dict[str, Any]],
        execution_mode: str = "live",
    ) -> Optional[str]:
        """Generate a human-readable explanation grounded in E1/E2 evidence.

        Returns None if LLM is unavailable or evidence is insufficient.
        The verdict itself (near_exact/partial/significant/insufficient)
        MUST come from the deterministic comparison engine, not the LLM.
        """
        if not self._available:
            return None

        evidence_summary = self._summarize_evidence(evidence)

        prompt = f"""You are a reproducibility auditor for a machine learning paper reproduction project.

Papers claims reported results; we executed the claimed code and got different results.
Your job is to EXPLAIN the discrepancy, NOT to decide the verdict.

HARD EVIDENCE (E1/E2) - MUST Ground Your Explanation:
- Model: {model_name}
- Reported accuracy: {reported:.4f}
- Reproduced accuracy: {reproduced:.4f}
- Absolute difference: {abs_diff:.4f}
- Relative difference: {rel_pct:.2f}% if available
- Execution mode: {execution_mode}
- Evidence summary: {evidence_summary}

INSTRUCTIONS:
1. Summarize what the evidence tells us about why the difference might exist.
2. Note any suspicious signals (e.g., exit code != 0, missing packages, version mismatches).
3. Keep it concise (2-3 sentences).
4. DO NOT assign a verdict (near_exact/partial/significant/insufficient).
5. DO NOT make up numbers or claim exact reproducibility if the evidence does not support it.

Return just the explanation text, no formatting, no verdict.
"""

        try:
            response = self._model.generate_content(prompt)
            text = (response.text or "").strip()
            # Sanity check: ensure we didn't get a verdict embedded
            verdict_keywords = ["near_exact", "partial", "significant", "insufficient", "verdict"]
            lower = text.lower()
            found_verdict = [v for v in verdict_keywords if v in lower]
            if found_verdict:
                logging.warning(
                    f"LLM response contained verdict keywords (bad): {found_verdict}. "
                    f"Response: {text[:100]}"
                )
            return text if text else None
        except Exception as e:
            logging.error(f"Gemini API error in explain_discrepancy: {e}")
            return None

    def explain_claim(
        self,
        *,
        claim_name: str,
        claim_metric: str,
        reported_value: float,
        evidence: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Generate an explanation for a single claim's result.

        Grounded in E1/E2 evidence. Returns None if LLM unavailable.
        """
        if not self._available:
            return None

        ev_summary = self._summarize_evidence(evidence)

        prompt = f"""You are a reproducibility auditor.

Claim: {claim_name}
Metric: {claim_metric}
Reported value: {reported_value}

EVIDENCE (E1/E2 only):
{ev_summary}

Provide a 2-3 sentence explanation of what the evidence shows. 
Keep it factual. Do NOT assign a verdict (near_exact/partial/significant/insufficient).
Return just the explanation text, no formatting, no verdict.
"""

        try:
            response = self._model.generate_content(prompt)
            text = (response.text or "").strip()
            verdict_keywords = ["near_exact", "partial", "significant", "insufficient"]
            lower = text.lower()
            found_verdict = [v for v in verdict_keywords if v in lower]
            if found_verdict:
                logging.warning(
                    f"LLM response contained verdict keywords (bad): {found_verdict}"
                )
            return text if text else None
        except Exception as e:
            logging.error(f"Gemini API error in explain_claim: {e}")
            return None

    def discrepancy_analysis(
        self,
        *,
        model_name: str,
        reported: float,
        reproduced: float,
        abs_diff: float,
        rel_pct: Optional[float],
        evidence: List[Dict[str, Any]],
        execution_mode: str = "live",
    ) -> Dict[str, Any]:
        """Analyze the root causes of a discrepancy based on E1/E2 evidence.

        Returns a dict with categorized root causes and confidence scores.
        This grounded analysis (E1/E2) is distinct from E3 LLM interpretation.
        """
        if not self._available:
            return {"root_causes": [], "confidence": 0.0, "analysis": "LLM unavailable",
                   "evidence_analyzed": 0, "execution_mode": execution_mode}

        # Categorize root causes from evidence
        causes = []
        confidence_sum = 0.0
        evidence_count = 0

        for ev in evidence:
            tier = ev.get("tier", "E?")
            kind = ev.get("kind", "?")
            excerpt = ev.get("excerpt", "")

            if tier in ("E1", "E2"):
                evidence_count += 1
                if kind == "exit_code":
                    exit_val = int(excerpt.split(":")[-1].strip()) if ":" in excerpt else 0
                    if exit_val != 0:
                        causes.append({
                            "cause": "container_exit_failure",
                            "description": f"Container exited with code {exit_val}",
                            "evidence": f"exit_code:{exit_val}",
                            "confidence": 0.9,
                        })
                    else:
                        causes.append({
                            "cause": "container_successful_exit",
                            "description": "Container exited successfully",
                            "evidence": "exit_code:0",
                            "confidence": 0.8,
                        })
                elif kind == "image_digest":
                    causes.append({
                        "cause": "docker_image_mismatch",
                        "description": "Docker image may differ from expected",
                        "evidence": excerpt,
                        "confidence": 0.7,
                    })
                elif kind == "repo_commit":
                    causes.append({
                        "cause": "repository_commit_mismatch",
                        "description": "Repository commit may differ from expected",
                        "evidence": excerpt,
                        "confidence": 0.75,
                    })
                elif kind == "package_version":
                    causes.append({
                        "cause": "dependency_version_mismatch",
                        "description": "Package versions may differ from expected",
                        "evidence": excerpt,
                        "confidence": 0.8,
                    })
                elif kind == "log_line":
                    if "error" in excerpt.lower() or "fail" in excerpt.lower():
                        causes.append({
                            "cause": "execution_error",
                            "description": "Errors detected in execution log",
                            "evidence": excerpt,
                            "confidence": 0.75,
                        })
                    else:
                        causes.append({
                            "cause": "normal_execution",
                            "description": "Execution appeared normal",
                            "evidence": excerpt,
                            "confidence": 0.85,
                        })
                elif kind == "calculated_diff":
                    causes.append({
                        "cause": "metric_calculation_difference",
                        "description": "Metric calculation may differ",
                        "evidence": excerpt,
                        "confidence": 0.6,
                    })

        # Also consider the magnitude of the difference
        if rel_pct is not None and abs(rel_pct) > 5.0:
            causes.append({
                "cause": "significant_result_difference",
                "description": f"Large difference reported ({rel_pct:.1f}%) vs reproduced",
                "evidence": f"rel_pct:{rel_pct:.1f}%",
                "confidence": 0.9,
            })

        # Sort by confidence
        causes.sort(key=lambda x: x["confidence"], reverse=True)

        # Build summary analysis text
        primary_causes = [c["description"] for c in causes[:3]]
        analysis_text = "; ".join(primary_causes) if primary_causes else "No significant E1/E2 root causes identified"

        result = {
            "root_causes": causes,
            "confidence": sum(c["confidence"] for c in causes) / max(evidence_count, 1) if evidence_count else 0.0,
            "analysis": analysis_text,
            "evidence_analyzed": evidence_count,
            "execution_mode": execution_mode,
        }

        return result

    def _summarize_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Convert the evidence list into a concise text summary."""
        if not evidence:
            return "No evidence available."

        lines = []
        for ev in evidence[:8]:  # Cap to first 8 items
            tier = ev.get("tier", "E?")
            kind = ev.get("kind", "?")
            ref = ev.get("ref", "")
            excerpt = ev.get("excerpt", "")
            lines.append(f"[{tier}] {kind}: {excerpt}")
        return "\n".join(lines)