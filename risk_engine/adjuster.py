from __future__ import annotations

from typing import Dict, Tuple


def apply_human_inputs(base_score: float, officer_inputs: Dict[str, object]) -> Tuple[float, list]:
    adjustments = []
    score = base_score

    utilization = officer_inputs.get("factory_utilization_pct")
    if utilization is not None:
        try:
            utilization = float(utilization)
        except Exception:
            utilization = None
    if utilization is not None:
        if utilization < 50:
            score += 5
            adjustments.append("Low factory utilization (<50%)")
        elif utilization < 70:
            score += 2
            adjustments.append("Moderate factory utilization (50-70%)")
        elif utilization > 85:
            score -= 2
            adjustments.append("High factory utilization (>85%)")

    site_notes = (officer_inputs.get("site_visit_observations") or "").lower()
    if any(word in site_notes for word in ["risk", "issue", "delay", "concern"]):
        score += 3
        adjustments.append("Site visit flagged operational concerns")
    if any(word in site_notes for word in ["clean", "orderly", "compliant"]):
        score -= 1
        adjustments.append("Positive site visit observations")

    return score, adjustments
