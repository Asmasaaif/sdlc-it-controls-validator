# SDLC IT Controls Validator

Automated IT General Controls (ITGC) validation tool that evaluates software releases against SOX compliance requirements, EU AI Act regulations, and GDPR standards — producing risk scores and audit-ready reports.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Framework](https://img.shields.io/badge/Framework-SOX--ITGC-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-12%20passing-brightgreen?style=flat-square)

---

## What is this?

In enterprise IT environments, every software release must pass a set of **IT General Controls (ITGCs)** before going live — especially for systems in scope of **SOX (Sarbanes-Oxley Act)**. These controls ensure that:

- Code is reviewed and approved before deployment
- Security scans are completed with no critical vulnerabilities
- Access controls (RBAC) are validated
- Audit logging is enabled
- No single person can both write and approve a change (Segregation of Duties)

This tool automates that validation process. You provide a release manifest (a JSON file describing the release), and the validator checks it against a configurable set of controls — then generates a risk score, a compliance score, and a detailed audit report.

---

## Why this matters

Manual IT controls testing is time-consuming and error-prone. This tool:

- Saves audit time by automating repetitive control checks
- Standardises risk scoring across all releases
- Produces audit-ready reports that can be attached to release packages
- Integrates with CI/CD pipelines — exits with code `1` on HIGH risk to block deployments automatically
- Covers emerging regulations like the EU AI Act, flagging AI components that need risk classification

---

## Project Structure

```
sdlc-it-controls-validator/
│
├── config/
│   ├── controls.json          # All control definitions (edit here to add/remove controls)
│   └── sample_release.json    # Example release manifest input
│
├── core/
│   └── validator.py           # Core evaluation engine — config-driven, no hardcoded logic
│
├── reports/
│   └── html_reporter.py       # Generates a self-contained HTML audit report
│
├── tests/
│   └── test_validator.py      # 12 unit tests covering all risk scenarios
│
└── main.py                    # CLI entry point — run this to validate a release
```

---

## How It Works

### 1. You provide a release manifest

A simple JSON file describing the release state:

```json
{
  "release_id": "APP-2026-001",
  "application_name": "Customer Portal",
  "version": "1.0.0",
  "release_owner": "team@company.com",
  "sox_in_scope": true,
  "contains_ai_components": false,
  "code_review_approved": true,
  "security_scan_completed": false,
  "critical_vulnerabilities": 0,
  "deployment_approved": true,
  "rbac_validated": false,
  "logging_enabled": true,
  "sod_enforced": true,
  "data_privacy_assessed": true,
  "ai_risk_assessed": false
}
```

### 2. The validator checks each control

Each control has a risk weight — how much it contributes to the overall risk score if it fails. The engine evaluates every control and calculates:

- **Risk Score** — percentage of weighted controls that failed
- **Compliance Score** — 100 minus the risk score
- **Risk Level** — HIGH, MEDIUM, or LOW based on thresholds

### 3. You get two reports

- **Terminal output** — colour-coded summary with pass/fail per control and remediation steps
- **HTML report** — professional audit document you can open in any browser

---

## Controls Framework

| Control | Framework | SDLC Phase | Risk Weight |
|---|---|---|---|
| Code Review Approval | SOX-ITGC | Development | 15% |
| Security Scan Completed | SOX-ITGC | Testing | 20% |
| No Critical Vulnerabilities | SOX-ITGC | Testing | 25% |
| Deployment Approval (CAB) | SOX-ITGC | Deployment | 15% |
| RBAC / Access Control Validation | SOX-ITGC | Operations | 10% |
| Logging and Monitoring Enabled | SOX-ITGC | Operations | 10% |
| Segregation of Duties | SOX-ITGC | Development | 10% |
| Data Privacy Impact Assessment | GDPR | Design | 5% |
| AI Risk Classification | EU AI Act | Design | N/A* |

*The AI Risk Classification control is optional — it is only evaluated when `contains_ai_components` is set to `true` in the release manifest.

---

## Risk Scoring Logic

| Risk Score | Risk Level | Recommendation |
|---|---|---|
| 60% or above | HIGH | Block deployment. Escalate to IT Risk and Compliance. |
| 30% to 59% | MEDIUM | Conditional release. Document compensating controls. |
| Below 30% | LOW | Approved. Proceed with standard change management. |

---

## Getting Started

### Prerequisites

- Python 3.10 or later — download at [python.org](https://python.org/downloads)
- Git (optional, for cloning)

### Installation

Clone the repository:

```bash
git clone https://github.com/Asmasaaif/sdlc-it-controls-validator.git
cd sdlc-it-controls-validator
```

Install dependencies:

```bash
pip install pytest
```

No other dependencies required.

### Running the validator

```bash
python main.py
```

This validates `config/sample_release.json` against `config/controls.json` and produces:

- A colour-coded report in your terminal
- `report_APP-2026-001.json` — machine-readable audit report
- `report_APP-2026-001.html` — open in your browser for the full visual report

### Custom release path

```bash
python main.py --release path/to/your_release.json --controls config/controls.json --out ./reports
```

### CI/CD integration

```bash
python main.py && echo "Safe to deploy" || echo "Deployment blocked — HIGH risk"
```

The tool exits with code `1` on HIGH risk and `0` otherwise, making it straightforward to integrate into GitHub Actions, Jenkins, GitLab CI, or any other pipeline.

---

## Running the Tests

```bash
python -m pytest tests/ -v
```

Expected output:

```
tests/test_validator.py::TestClassifyRisk::test_high_risk        PASSED
tests/test_validator.py::TestClassifyRisk::test_medium_risk      PASSED
tests/test_validator.py::TestClassifyRisk::test_low_risk         PASSED
tests/test_validator.py::TestEvaluateControls::test_all_pass     PASSED
tests/test_validator.py::TestEvaluateControls::test_all_fail     PASSED
12 passed in 0.09s
```

The test suite covers all risk thresholds, partial failures, missing fields, zero-check controls, phase grouping, report structure, and recommendation logic.

---

## Adding a New Control

All controls are data-driven in `config/controls.json` — no Python code changes required. Add a new object to the `controls` array:

```json
{
  "id": "PENETRATION_TEST_COMPLETED",
  "name": "Penetration Test Completed",
  "field": "pentest_completed",
  "field_type": "boolean",
  "sdlc_phase": "Testing",
  "framework": "SOX-ITGC",
  "risk_weight": 10,
  "description": "An annual penetration test must be completed for in-scope systems.",
  "remediation": "Schedule and complete a penetration test. Attach findings report."
}
```

Then add the corresponding field to your release manifest and run the validator.

---

## Roadmap

- GitHub Actions workflow for automated CI/CD gating
- Multi-release batch validation
- Excel export for audit workpapers
- Web dashboard UI
- NIST CSF and ISO 27001 control mappings

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

**Asma Saif**  
Cybersecurity and IT Risk | SOX-ITGC | EU AI Act | SDLC Compliance

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Asma%20Saif-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/asmasaifcyber/)
[![GitHub](https://img.shields.io/badge/GitHub-Asmasaaif-181717?style=flat-square&logo=github)](https://github.com/Asmasaaif)
