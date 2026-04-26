"""
HTML Report Generator — produces a self-contained audit report.
"""

from datetime import datetime


RISK_COLORS = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#22c55e"}
STATUS_COLORS = {"PASS": "#22c55e", "FAIL": "#ef4444", "N/A": "#6b7280"}
PHASE_ICONS = {
    "Design": "📐", "Development": "💻", "Testing": "🧪",
    "Deployment": "🚀", "Operations": "⚙️",
}


def generate_html_report(report: dict) -> str:
    risk_color = RISK_COLORS.get(report["risk_level"], "#6b7280")
    controls_rows = _build_control_rows(report["control_results"])
    failures_html = _build_failures_section(report["failures_by_phase"])
    ai_badge = (
        '<span class="badge badge-ai">🤖 AI Components</span>'
        if report["contains_ai_components"] else ""
    )
    sox_badge = (
        '<span class="badge badge-sox">SOX In-Scope</span>'
        if report["sox_in_scope"] else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IT Controls Report — {report['release_id']}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

  :root {{
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1c2536;
    --border: #2d3748;
    --text: #e2e8f0;
    --muted: #64748b;
    --accent: #3b82f6;
    --pass: #22c55e;
    --fail: #ef4444;
    --warn: #f59e0b;
    --risk: {risk_color};
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'IBM Plex Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 2rem;
  }}

  .header {{
    border-left: 4px solid var(--accent);
    padding-left: 1.5rem;
    margin-bottom: 2.5rem;
  }}

  .header h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }}

  .header .meta {{
    color: var(--muted);
    font-size: 0.85rem;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 0.4rem;
  }}

  .badges {{ display: flex; gap: 0.5rem; margin-top: 0.8rem; flex-wrap: wrap; }}

  .badge {{
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
  }}

  .badge-sox {{ background: #1e3a5f; color: #60a5fa; border: 1px solid #2563eb; }}
  .badge-ai  {{ background: #2d1b4e; color: #c084fc; border: 1px solid #7c3aed; }}

  .scorecard {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }}

  .score-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
  }}

  .score-card .label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 600;
  }}

  .score-card .value {{
    font-size: 2.25rem;
    font-weight: 700;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.1;
    margin-top: 0.3rem;
  }}

  .risk-badge {{
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    background: var(--risk);
    color: #fff;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 0.4rem;
  }}

  .recommendation {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--risk);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
    font-size: 0.9rem;
  }}

  .recommendation strong {{ display: block; margin-bottom: 0.4rem; color: var(--risk); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }}

  section {{ margin-bottom: 2rem; }}
  h2 {{ font-size: 1rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-bottom: 1rem; font-weight: 600; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}

  thead tr {{ background: var(--surface2); }}
  thead th {{ padding: 0.75rem 1rem; text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 600; }}

  tbody tr {{ border-top: 1px solid var(--border); transition: background 0.15s; }}
  tbody tr:hover {{ background: var(--surface); }}
  tbody td {{ padding: 0.75rem 1rem; vertical-align: top; }}

  .status-pill {{
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.05em;
  }}

  .status-PASS {{ background: #14532d; color: #4ade80; }}
  .status-FAIL {{ background: #450a0a; color: #f87171; }}
  .status-NA   {{ background: #1e2a3a; color: #64748b; }}

  .phase-tag {{ font-size: 0.75rem; color: var(--muted); }}

  .remediation {{ font-size: 0.8rem; color: var(--warn); margin-top: 0.25rem; }}

  .failures-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 0.75rem;
  }}

  .phase-block {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
  }}

  .phase-block h3 {{ font-size: 0.8rem; color: var(--muted); margin-bottom: 0.5rem; }}
  .phase-block ul {{ padding-left: 1rem; font-size: 0.85rem; color: #f87171; }}
  .phase-block li {{ margin-bottom: 0.2rem; }}

  .footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
  }}

  .weight-bar {{
    width: 100%;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    margin-top: 0.4rem;
  }}

  .weight-bar-fill {{
    height: 100%;
    border-radius: 2px;
    background: var(--accent);
  }}
</style>
</head>
<body>

<div class="header">
  <h1>IT Controls Validation Report</h1>
  <div class="meta">
    {report['release_id']} &nbsp;·&nbsp; {report['application_name']} v{report['version']}
    &nbsp;·&nbsp; {report['generated_at'][:19].replace('T', ' ')} UTC
  </div>
  <div class="badges">{sox_badge}{ai_badge}</div>
</div>

<div class="scorecard">
  <div class="score-card">
    <div class="label">Risk Level</div>
    <div class="value" style="color: var(--risk);">{report['risk_level']}</div>
    <span class="risk-badge">{report['risk_score']}% risk score</span>
  </div>
  <div class="score-card">
    <div class="label">Compliance Score</div>
    <div class="value" style="color: var(--pass);">{report['compliance_score']}%</div>
    <div class="weight-bar"><div class="weight-bar-fill" style="width:{report['compliance_score']}%; background: {'var(--pass)' if report['compliance_score'] >= 70 else 'var(--warn)'};"></div></div>
  </div>
  <div class="score-card">
    <div class="label">Controls</div>
    <div class="value">{sum(1 for c in report['control_results'] if c['status'] == 'PASS')} / {sum(1 for c in report['control_results'] if c['status'] != 'N/A')}</div>
    <div class="phase-tag">passed</div>
  </div>
  <div class="score-card">
    <div class="label">Release Owner</div>
    <div class="value" style="font-size:1rem; padding-top:0.5rem;">{report['release_owner']}</div>
  </div>
</div>

<div class="recommendation">
  <strong>Recommendation</strong>
  {report['recommendation']}
</div>

{"" if not report['failures_by_phase'] else f'''
<section>
  <h2>Failures by SDLC Phase</h2>
  <div class="failures-grid">{failures_html}</div>
</section>
'''}

<section>
  <h2>Control Results</h2>
  <table>
    <thead>
      <tr>
        <th>Control</th>
        <th>Phase</th>
        <th>Framework</th>
        <th>Status</th>
        <th>Weight</th>
      </tr>
    </thead>
    <tbody>
      {controls_rows}
    </tbody>
  </table>
</section>

<div class="footer">
  Generated by sdlc-it-controls-validator v2.0 &nbsp;·&nbsp; Framework: SOX-ITGC + EU-AI-Act + GDPR
</div>

</body>
</html>"""


def _build_control_rows(results: list[dict]) -> str:
    rows = []
    for r in results:
        status_class = {"PASS": "PASS", "FAIL": "FAIL", "N/A": "NA"}.get(r["status"], "NA")
        phase_icon = PHASE_ICONS.get(r["sdlc_phase"], "")
        remediation_html = (
            f'<div class="remediation">⚠ {r["remediation"]}</div>'
            if r["remediation"] else ""
        )
        rows.append(f"""
        <tr>
          <td>
            <div><strong>{r['control_name']}</strong></div>
            <div class="phase-tag" style="margin-top:0.2rem;">{r['description'][:80]}{'…' if len(r['description']) > 80 else ''}</div>
            {remediation_html}
          </td>
          <td><span class="phase-tag">{phase_icon} {r['sdlc_phase']}</span></td>
          <td><span class="phase-tag">{r['framework']}</span></td>
          <td><span class="status-pill status-{status_class}">{r['status']}</span></td>
          <td><span style="font-family:'IBM Plex Mono',monospace;">{r['risk_weight']}%</span></td>
        </tr>""")
    return "\n".join(rows)


def _build_failures_section(failures_by_phase: dict) -> str:
    if not failures_by_phase:
        return ""
    blocks = []
    for phase, items in failures_by_phase.items():
        icon = PHASE_ICONS.get(phase, "")
        items_html = "".join(f"<li>{i}</li>" for i in items)
        blocks.append(f"""
        <div class="phase-block">
          <h3>{icon} {phase}</h3>
          <ul>{items_html}</ul>
        </div>""")
    return "\n".join(blocks)
