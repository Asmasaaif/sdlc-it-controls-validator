# SDLC IT Controls Validator v2.0

> Automated IT General Controls (ITGC) validation for SOX-scoped software releases.
> Aligned with: **SOX-ITGC**, **EU AI Act**, and **GDPR** frameworks.

## Overview

This tool validates release packages against a configurable set of IT controls, produces a risk score, and generates professional audit-ready reports — JSON and HTML. Designed to support SOX compliance programmes and SDLC governance workflows.

## Project Structure

```
sdlc-it-controls-validator/
├── config/
│   ├── controls.json          # Control definitions (SOX-ITGC, EU AI Act, GDPR)
│   └── sample_release.json    # Example release manifest
├── core/
│   └── validator.py           # Config-driven evaluation engine
├── reports/
│   └── html_reporter.py       # HTML audit report generator
├── tests/
│   └── test_validator.py      # Unit tests (12 cases)
└── main.py                    # CLI entry point
```

## Quick Start

```bash
# Run against sample release
python main.py

# Custom paths
python main.py --release path/to/release.json --controls path/to/controls.json --out ./reports

# CI/CD usage (exits 1 on HIGH risk, 0 otherwise)
python main.py --no-html && echo "Safe to deploy"
```

## Release Manifest Schema

```json
{
  "release_id": "APP-2026-001",
  "application_name": "Customer Portal",
  "version": "1.0.0",
  "release_owner": "team@company.com",
  "sox_in_scope": true,
  "contains_ai_components": false,
  "code_review_approved": true,
  "security_scan_completed": true,
  "critical_vulnerabilities": 0,
  "deployment_approved": true,
  "rbac_validated": true,
  "logging_enabled": true,
  "sod_enforced": true,
  "data_privacy_assessed": true,
  "ai_risk_assessed": false
}
```

## Controls Framework

| Control | Framework | Phase | Weight |
|---|---|---|---|
| Code Review Approval | SOX-ITGC | Development | 15% |
| Security Scan Completed | SOX-ITGC | Testing | 20% |
| No Critical Vulnerabilities | SOX-ITGC | Testing | 25% |
| Deployment Approval (CAB) | SOX-ITGC | Deployment | 15% |
| RBAC Validation | SOX-ITGC | Operations | 10% |
| Logging & Monitoring | SOX-ITGC | Operations | 10% |
| Segregation of Duties | SOX-ITGC | Development | 10% |
| Data Privacy (DPIA) | GDPR | Design | 5% |
| AI Risk Classification | EU AI Act | Design | N/A* |

*Optional — only evaluated when `contains_ai_components: true`

## Risk Scoring

| Risk Score | Level | Recommendation |
|---|---|---|
| ≥ 60% | HIGH | **BLOCK** — escalate to IT Risk & Compliance |
| 30–59% | MEDIUM | **CONDITIONAL** — document compensating controls |
| < 30% | LOW | **APPROVED** — proceed with standard change management |

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Adding Controls

All controls are data-driven in `config/controls.json`. No code changes required.
Supported `field_type` values: `boolean`, `zero_check`.

```json
{
  "id": "MY_CONTROL",
  "name": "My New Control",
  "field": "my_field_in_release_json",
  "field_type": "boolean",
  "sdlc_phase": "Testing",
  "framework": "SOX-ITGC",
  "risk_weight": 10,
  "description": "What this control checks.",
  "remediation": "What to do if it fails."
}
```
