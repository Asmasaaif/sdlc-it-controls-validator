"""
SDLC IT Controls Validator — Core Engine
Framework: SOX-ITGC | EU AI Act | GDPR
"""

import json
from datetime import datetime, timezone
from typing import Any


# ── Risk thresholds ────────────────────────────────────────────────────────────
RISK_THRESHOLDS = {"HIGH": 60, "MEDIUM": 30, "LOW": 0}


def load_json(filepath: str) -> dict:
    with open(filepath, "r") as fh:
        return json.load(fh)


def classify_risk(score: float) -> str:
    for level, threshold in RISK_THRESHOLDS.items():
        if score >= threshold:
            return level
    return "LOW"


def evaluate_field(release: dict, control: dict) -> tuple[bool, str | None]:
    """
    Config-driven field evaluation — no hardcoded if/elif chains.
    Supports: boolean, zero_check field types.
    Returns (passed, error_message).
    """
    field = control.get("field")
    field_type = control.get("field_type", "boolean")

    # Skip optional controls when the relevant feature is absent
    if control.get("optional"):
        trigger = "contains_ai_components" if control["framework"] == "EU-AI-Act" else None
        if trigger and not release.get(trigger, False):
            return True, None   # not applicable — skip

    if field not in release:
        return False, f"Field '{field}' missing from release manifest"

    value = release[field]

    if field_type == "boolean":
        return bool(value), None
    elif field_type == "zero_check":
        return value == 0, None
    else:
        return False, f"Unknown field_type '{field_type}' for control {control['id']}"


def evaluate_controls(release: dict, controls: list[dict]) -> dict:
    """
    Evaluate all controls and produce a structured audit result.
    """
    results = []
    failed_weight = 0
    applicable_weight = 0

    for control in controls:
        passed, error = evaluate_field(release, control)
        weight = control["risk_weight"]

        # Optional/N-A controls carry 0 weight
        is_applicable = not (control.get("optional") and passed and error is None
                             and weight == 0)

        if is_applicable:
            applicable_weight += weight
            if not passed:
                failed_weight += weight

        results.append({
            "control_id": control["id"],
            "control_name": control["name"],
            "sdlc_phase": control["sdlc_phase"],
            "framework": control["framework"],
            "status": "PASS" if passed else ("N/A" if not is_applicable else "FAIL"),
            "risk_weight": weight,
            "description": control.get("description", ""),
            "remediation": control.get("remediation", "") if not passed else "",
            "error": error,
        })

    risk_score = round((failed_weight / applicable_weight) * 100) if applicable_weight else 0
    compliance_score = 100 - risk_score
    risk_level = classify_risk(risk_score)

    # Group failures by SDLC phase for prioritised remediation
    failures_by_phase: dict[str, list] = {}
    for r in results:
        if r["status"] == "FAIL":
            phase = r["sdlc_phase"]
            failures_by_phase.setdefault(phase, []).append(r["control_name"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_id": release["release_id"],
        "application_name": release["application_name"],
        "version": release["version"],
        "release_owner": release.get("release_owner", "N/A"),
        "sox_in_scope": release.get("sox_in_scope", False),
        "contains_ai_components": release.get("contains_ai_components", False),
        "risk_level": risk_level,
        "risk_score": risk_score,
        "compliance_score": compliance_score,
        "applicable_weight": applicable_weight,
        "failed_weight": failed_weight,
        "failures_by_phase": failures_by_phase,
        "control_results": results,
        "recommendation": _recommend(risk_level, failures_by_phase),
    }


def _recommend(risk_level: str, failures_by_phase: dict) -> str:
    if risk_level == "HIGH":
        return (
            "BLOCK deployment. Critical IT General Controls have failed. "
            "Escalate to IT Risk & Compliance and obtain explicit exception approval "
            "before any production change proceeds."
        )
    elif risk_level == "MEDIUM":
        phases = ", ".join(failures_by_phase.keys())
        return (
            f"CONDITIONAL release. Failures detected in: {phases}. "
            "Document compensating controls and obtain manager sign-off."
        )
    return "APPROVED. All material controls passed. Proceed with standard change management."
