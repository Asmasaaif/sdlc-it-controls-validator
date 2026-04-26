"""
SDLC IT Controls Validator — CLI Entry Point
Usage: python main.py [--release <path>] [--controls <path>] [--out <dir>]
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent))

from core.validator import load_json, evaluate_controls
from reports.html_reporter import generate_html_report


ANSI = {
    "RED": "\033[91m", "GREEN": "\033[92m", "YELLOW": "\033[93m",
    "BLUE": "\033[94m", "CYAN": "\033[96m", "BOLD": "\033[1m",
    "DIM": "\033[2m", "RESET": "\033[0m",
}

RISK_COLOR = {"HIGH": "RED", "MEDIUM": "YELLOW", "LOW": "GREEN"}


def c(text: str, *keys: str) -> str:
    codes = "".join(ANSI[k] for k in keys)
    return f"{codes}{text}{ANSI['RESET']}"


def print_report(report: dict) -> None:
    risk_col = RISK_COLOR.get(report["risk_level"], "CYAN")

    print()
    print(c("━" * 60, "DIM"))
    print(c("  SDLC IT Controls Validation Report", "BOLD", "CYAN"))
    print(c("━" * 60, "DIM"))
    print(f"  {c('Release:', 'DIM')}     {report['release_id']}")
    print(f"  {c('Application:', 'DIM')} {report['application_name']} v{report['version']}")
    print(f"  {c('Owner:', 'DIM')}       {report['release_owner']}")
    print(f"  {c('Generated:', 'DIM')}   {report['generated_at'][:19]} UTC")
    print(c("━" * 60, "DIM"))
    print()
    print(f"  Risk Level:       {c(report['risk_level'], 'BOLD', risk_col)}")
    print(f"  Risk Score:       {c(str(report['risk_score']) + '%', risk_col)}")
    print(f"  Compliance Score: {c(str(report['compliance_score']) + '%', 'GREEN' if report['compliance_score'] >= 70 else 'YELLOW')}")
    print()
    print(c("  Control Results", "BOLD"))
    print()

    for r in report["control_results"]:
        if r["status"] == "PASS":
            icon = c("✔", "GREEN")
        elif r["status"] == "FAIL":
            icon = c("✘", "RED")
        else:
            icon = c("–", "DIM")

        status_str = c(f"[{r['status']:<4}]", "GREEN" if r["status"] == "PASS" else ("RED" if r["status"] == "FAIL" else "DIM"))
        weight = c(f"({r['risk_weight']}%)", "DIM")
        print(f"  {icon} {status_str} {r['control_name']} {weight}")
        if r["status"] == "FAIL" and r.get("remediation"):
            print(f"        {c('→ ' + r['remediation'][:72], 'YELLOW')}")

    print()
    print(c("  Recommendation", "BOLD"))
    print()
    # Word-wrap recommendation at 56 chars
    words = report["recommendation"].split()
    line = "  "
    for word in words:
        if len(line) + len(word) > 58:
            print(c(line, risk_col))
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(c(line, risk_col))
    print()
    print(c("━" * 60, "DIM"))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="SDLC IT Controls Validator"
    )
    parser.add_argument("--release",  default="config/sample_release.json",
                        help="Path to release manifest JSON")
    parser.add_argument("--controls", default="config/controls.json",
                        help="Path to controls config JSON")
    parser.add_argument("--out",      default=".",
                        help="Output directory for reports")
    parser.add_argument("--no-html",  action="store_true",
                        help="Skip HTML report generation")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    controls = load_json(args.controls)["controls"]
    release = load_json(args.release)

    report = evaluate_controls(release, controls)

    # Console output
    print_report(report)

    # JSON report
    json_path = out_dir / f"report_{report['release_id']}.json"
    with open(json_path, "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"  JSON report → {json_path}")

    # HTML report
    if not args.no_html:
        html_path = out_dir / f"report_{report['release_id']}.html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(generate_html_report(report))
        print(f"  HTML report → {html_path}")

    print()

    # Exit code for CI/CD pipelines
    sys.exit(1 if report["risk_level"] == "HIGH" else 0)


if __name__ == "__main__":
    main()
