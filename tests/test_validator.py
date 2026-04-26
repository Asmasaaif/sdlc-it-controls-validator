"""
Unit tests for the SDLC IT Controls Validator.
Run: python -m pytest tests/ -v
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validator import evaluate_controls, classify_risk, load_json


CONTROLS = [
    {"id": "CODE_REVIEW_APPROVED", "name": "Code Review", "field": "code_review_approved",
     "field_type": "boolean", "sdlc_phase": "Development", "framework": "SOX-ITGC",
     "risk_weight": 20, "description": "", "remediation": ""},
    {"id": "SECURITY_SCAN_COMPLETED", "name": "Security Scan", "field": "security_scan_completed",
     "field_type": "boolean", "sdlc_phase": "Testing", "framework": "SOX-ITGC",
     "risk_weight": 30, "description": "", "remediation": ""},
    {"id": "NO_CRITICAL_VULNERABILITIES", "name": "No Critical CVEs", "field": "critical_vulnerabilities",
     "field_type": "zero_check", "sdlc_phase": "Testing", "framework": "SOX-ITGC",
     "risk_weight": 50, "description": "", "remediation": ""},
]

ALL_PASS_RELEASE = {
    "release_id": "TEST-001", "application_name": "Test App", "version": "1.0",
    "release_owner": "test@test.com", "sox_in_scope": True,
    "contains_ai_components": False,
    "code_review_approved": True, "security_scan_completed": True,
    "critical_vulnerabilities": 0,
}

ALL_FAIL_RELEASE = {
    **ALL_PASS_RELEASE,
    "code_review_approved": False, "security_scan_completed": False,
    "critical_vulnerabilities": 3,
}


class TestClassifyRisk:
    def test_high_risk(self):
        assert classify_risk(75) == "HIGH"
        assert classify_risk(60) == "HIGH"

    def test_medium_risk(self):
        assert classify_risk(59) == "MEDIUM"
        assert classify_risk(30) == "MEDIUM"

    def test_low_risk(self):
        assert classify_risk(29) == "LOW"
        assert classify_risk(0) == "LOW"


class TestEvaluateControls:
    def test_all_pass(self):
        report = evaluate_controls(ALL_PASS_RELEASE, CONTROLS)
        assert report["risk_score"] == 0
        assert report["compliance_score"] == 100
        assert report["risk_level"] == "LOW"
        assert all(r["status"] == "PASS" for r in report["control_results"])

    def test_all_fail(self):
        report = evaluate_controls(ALL_FAIL_RELEASE, CONTROLS)
        assert report["risk_score"] == 100
        assert report["compliance_score"] == 0
        assert report["risk_level"] == "HIGH"
        assert all(r["status"] == "FAIL" for r in report["control_results"])

    def test_partial_fail_medium(self):
        release = {**ALL_PASS_RELEASE, "security_scan_completed": False}
        report = evaluate_controls(release, CONTROLS)
        # security scan = 30% weight → risk score = 30 → MEDIUM
        assert report["risk_score"] == 30
        assert report["risk_level"] == "MEDIUM"

    def test_critical_vuln_zero_check(self):
        release = {**ALL_PASS_RELEASE, "critical_vulnerabilities": 5}
        report = evaluate_controls(release, CONTROLS)
        vuln_result = next(r for r in report["control_results"]
                           if r["control_id"] == "NO_CRITICAL_VULNERABILITIES")
        assert vuln_result["status"] == "FAIL"

    def test_missing_field_fails(self):
        release = {k: v for k, v in ALL_PASS_RELEASE.items()
                   if k != "code_review_approved"}
        report = evaluate_controls(release, CONTROLS)
        code_review = next(r for r in report["control_results"]
                           if r["control_id"] == "CODE_REVIEW_APPROVED")
        assert code_review["status"] == "FAIL"
        assert code_review["error"] is not None

    def test_failures_grouped_by_phase(self):
        release = {**ALL_PASS_RELEASE, "security_scan_completed": False}
        report = evaluate_controls(release, CONTROLS)
        assert "Testing" in report["failures_by_phase"]

    def test_report_contains_required_keys(self):
        report = evaluate_controls(ALL_PASS_RELEASE, CONTROLS)
        required = {"release_id", "risk_level", "risk_score", "compliance_score",
                    "control_results", "recommendation", "generated_at"}
        assert required.issubset(report.keys())

    def test_recommendation_contains_approved_on_low(self):
        report = evaluate_controls(ALL_PASS_RELEASE, CONTROLS)
        assert "APPROVED" in report["recommendation"]

    def test_recommendation_block_on_high(self):
        report = evaluate_controls(ALL_FAIL_RELEASE, CONTROLS)
        assert "BLOCK" in report["recommendation"]
