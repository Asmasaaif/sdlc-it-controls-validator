# SDLC IT Controls Validator

A Python tool that automates IT General Controls (ITGC) validation for software releases — producing risk scores and audit-style reports. Built as a learning project to explore how SOX controls, SDLC governance, and risk assessment work in practice.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Framework](https://img.shields.io/badge/Inspired%20by-SOX--ITGC-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-12%20passing-brightgreen?style=flat-square)

---

## What is this?

Before a software release goes live, IT teams typically run through a checklist of controls — was the code reviewed? Was a security scan completed? Does anyone have access they shouldn't? This process is especially important for systems in scope of **SOX (Sarbanes-Oxley Act)**, where IT General Controls must be documented and tested.

This tool simulates that process. You provide a release manifest (a JSON file describing the state of a release), and the validator checks it against a set of configurable controls — then calculates a risk score and generates a report.

Includes simplified control mappings inspired by SOX ITGC, GDPR principles, and emerging AI risk frameworks such as the EU AI Act.

---

## What I implemented

- Designed the control evaluation logic and risk scoring model from scratch
- Built a config-driven validation engine — controls are defined in JSON, no hardcoded logic in Python
- Implemented a CLI interface with flexible arguments for custom release paths and output directories
- Developed an HTML report generator for audit-style outputs
- Wrote 12 unit tests covering risk classification, partial failures, missing fields, and edge cases

---

## Why I built this

I wanted to understand how IT risk and compliance teams actually work — specifically how controls are tested, how risk is quantified, and what an audit package looks like. Building this tool forced me to think through real questions: what makes a control fail? How do you weight different risks against each other? What does a useful remediation step look like?

---

## Project Structure

```
sdlc-it-controls-validator/
│
├── config/
│   ├── controls.json          # Control definitions — edit here to add or remove controls
│   └── sample_release.json    # Example release manifest used as input
│
├── core/
│   └── validator.py           # Evaluation engine — config-driven, no hardcoded field logic
│
├── reports/
│   └── html_reporter.py       # Generates a self-contained HTML audit report
│
├── tests/
│   └── test_validator.py      # Unit tests covering all risk scenarios
│
└── main.py                    # CLI entry point
```

---

## How It Works

### 1. You provide a release manifest

A JSON file describing the current state of a release:

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

Each control has a risk weight — how much it contributes to the overall risk score if it fails. The engine calculates:

- **Risk Score** — percentage of weighted controls that failed
- **Compliance Score** — 100 minus the risk score
- **Risk Level** — HIGH, MEDIUM, or LOW

### 3. You get two reports

- **Terminal output** — colour-coded pass/fail per control with remediation guidance
- **HTML report** — audit-style document you can open in any browser

---

## Controls

| Control | Inspired by | SDLC Phase | Risk Weight |
|---|---|---|---|
| Code Review Approval | SOX-ITGC | Development | 15% |
| Security Scan Completed | SOX-ITGC | Testing | 20% |
| No Critical Vulnerabilities | SOX-ITGC | Testing | 25% |
| Deployment Approval (CAB) | SOX-ITGC | Deployment | 15% |
| RBAC / Access Control Validation | SOX-ITGC | Operations | 10% |
| Logging and Monitoring Enabled | SOX-ITGC | Operations | 10% |
| Segregation of Duties | SOX-ITGC | Development | 10% |
| Data Privacy Impact Assessment | GDPR principles | Design | 5% |
| AI Risk Classification | EU AI Act frameworks | Design | N/A* |

*The AI control is optional — only evaluated when `contains_ai_components` is `true`.

---

## Risk Scoring

| Risk Score | Level | Output |
|---|---|---|
| 60% or above | HIGH | Block deployment. Escalate to IT Risk and Compliance. |
| 30% to 59% | MEDIUM | Conditional release. Document compensating controls. |
| Below 30% | LOW | Approved. Proceed with standard change management. |

---

## Getting Started

### Prerequisites

- Python 3.10 or later — [python.org](https://python.org/downloads)

### Installation

```bash
git clone https://github.com/Asmasaaif/sdlc-it-controls-validator.git
cd sdlc-it-controls-validator
pip install pytest
```

### Run the validator

```bash
python main.py
```

Produces a terminal report plus two files: a JSON report and an HTML report.

### Custom paths

```bash
python main.py --release path/to/release.json --controls config/controls.json --out ./reports
```

### CI/CD integration

```bash
python main.py && echo "Safe to deploy" || echo "Deployment blocked"
```

Exits with code `1` on HIGH risk, `0` otherwise.

---

## Running the Tests

```bash
python -m pytest tests/ -v
```

```
tests/test_validator.py::TestClassifyRisk::test_high_risk        PASSED
tests/test_validator.py::TestClassifyRisk::test_medium_risk      PASSED
tests/test_validator.py::TestClassifyRisk::test_low_risk         PASSED
tests/test_validator.py::TestEvaluateControls::test_all_pass     PASSED
tests/test_validator.py::TestEvaluateControls::test_all_fail     PASSED
12 passed in 0.09s
```

---

## Adding a New Control

Controls are defined in `config/controls.json` — no Python changes needed. Add an object to the array:

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

Then add the field to your release manifest and run.

---

## Limitations

This tool simulates IT control validation using simplified inputs. It does not replace real audit procedures, evidence collection, or regulatory compliance assessments. The control mappings are inspired by real frameworks but are not a substitute for formal compliance programmes.

---

## Roadmap

- GitHub Actions workflow for automated CI/CD gating
- Multi-release batch validation
- Excel export for audit workpapers
- NIST CSF and ISO 27001 control mappings

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

**Asma Saif**  
Cybersecurity and IT Risk | SOX-ITGC | SDLC Compliance | GRC

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Asma%20Saif-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/asmasaifcyber/)
[![GitHub](https://img.shields.io/badge/GitHub-Asmasaaif-181717?style=flat-square&logo=github)](https://github.com/Asmasaaif)
