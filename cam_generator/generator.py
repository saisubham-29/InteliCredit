from __future__ import annotations

import os
from datetime import datetime
from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

CAM_STORAGE_DIR = "storage/cam"
TEMPLATE_DIR = os.path.join("cam_generator", "templates")


def _ensure_dirs() -> None:
    os.makedirs(CAM_STORAGE_DIR, exist_ok=True)


def _format_money_cr(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"₹ {value:,.2f} Cr"


def generate_cam_json(
    company_profile: Dict[str, object],
    financials: Dict[str, object],
    research: Dict[str, object],
    risk_report: Dict[str, object],
    officer_inputs: Dict[str, object],
) -> Dict[str, object]:
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "company": company_profile,
        "executive_summary": {
            "risk_band": risk_report.get("risk_band"),
            "total_score": risk_report.get("total_score"),
            "recommendation": risk_report.get("recommendation"),
        },
        "financial_analysis": financials,
        "research": research,
        "five_cs": risk_report.get("scores"),
        "risk_drivers": risk_report.get("drivers"),
        "officer_inputs": officer_inputs,
    }


def _render_html(cam_json: Dict[str, object]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("cam_template.html")

    return template.render(
        company=cam_json.get("company", {}),
        executive_summary=cam_json.get("executive_summary", {}),
        financials=cam_json.get("financial_analysis", {}),
        research=cam_json.get("research", {}),
        five_cs=cam_json.get("five_cs", {}),
        report_date=datetime.now().strftime("%d %b %Y"),
        format_money=_format_money_cr,
    )


def generate_cam_pdf(cam_json: Dict[str, object], company_id: str) -> str:
    _ensure_dirs()
    html = _render_html(cam_json)
    html_path = os.path.join(CAM_STORAGE_DIR, f"cam_{company_id}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    pdf_path = os.path.join(CAM_STORAGE_DIR, f"cam_{company_id}.pdf")
    try:
        from weasyprint import HTML

        HTML(string=html).write_pdf(pdf_path)
        return pdf_path
    except Exception:
        # Fallback: keep HTML as artifact if PDF conversion is unavailable.
        return html_path
