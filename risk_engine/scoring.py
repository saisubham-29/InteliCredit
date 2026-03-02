from __future__ import annotations

from typing import Dict, List, Tuple


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def classify_risk_band(score: float) -> str:
    if score <= 25:
        return "Low"
    if score <= 45:
        return "Moderate"
    if score <= 65:
        return "High"
    return "Very High"


def _score_character(research: Dict[str, object], officer_inputs: Dict[str, object]) -> Tuple[float, List[str]]:
    score = 8.0
    drivers = []

    negative_news = research.get("negative_news_count", 0)
    if negative_news:
        score += min(8, negative_news * 2)
        drivers.append("Adverse media mentions")

    litigation = research.get("litigation_signals", 0)
    if litigation:
        score += min(4, litigation * 2)
        drivers.append("Litigation signals in public sources")

    management_notes = (officer_inputs.get("management_quality_notes") or "").lower()
    if "weak" in management_notes or "concern" in management_notes:
        score += 3
        drivers.append("Management quality concerns from site visit")
    if "strong" in management_notes or "proven" in management_notes:
        score -= 2
        drivers.append("Strong management track record")

    return _clamp(score, 0, 20), drivers


def _score_capacity(financials: Dict[str, object]) -> Tuple[float, List[str]]:
    score = 10.0
    drivers = []
    metrics = financials.get("metrics", {})

    icr = metrics.get("interest_coverage_ratio")
    if icr is not None:
        if icr < 1.5:
            score += 8
            drivers.append("Interest coverage below 1.5x")
        elif icr < 2.5:
            score += 4
            drivers.append("Moderate interest coverage")
        else:
            score -= 2
            drivers.append("Healthy interest coverage")

    dscr = metrics.get("dscr")
    if dscr is not None:
        if dscr < 1.2:
            score += 7
            drivers.append("DSCR below 1.2x")
        elif dscr < 1.5:
            score += 3
            drivers.append("DSCR in borderline range")
        else:
            score -= 1
            drivers.append("Comfortable DSCR")

    return _clamp(score, 0, 30), drivers


def _score_capital(financials: Dict[str, object], company_profile: Dict[str, object]) -> Tuple[float, List[str]]:
    score = 6.0
    drivers = []

    leverage = financials.get("metrics", {}).get("debt_to_ebitda")
    if leverage is not None:
        if leverage > 4:
            score += 8
            drivers.append("Debt/EBITDA above 4x")
        elif leverage > 2.5:
            score += 4
            drivers.append("Moderate leverage")
        else:
            score -= 2
            drivers.append("Conservative leverage")

    net_worth = company_profile.get("net_worth")
    loan_requested = company_profile.get("loan_requested")
    if net_worth and loan_requested and net_worth < (loan_requested * 0.5):
        score += 3
        drivers.append("Thin equity cushion")

    return _clamp(score, 0, 20), drivers


def _score_collateral(financials: Dict[str, object]) -> Tuple[float, List[str]]:
    score = 4.0
    drivers = []
    security_cover = financials.get("metrics", {}).get("security_cover")
    if security_cover is not None:
        if security_cover < 1.2:
            score += 6
            drivers.append("Collateral cover below 1.2x")
        elif security_cover < 1.5:
            score += 3
            drivers.append("Collateral cover marginal")
        else:
            score -= 2
            drivers.append("Strong collateral cover")
    return _clamp(score, 0, 15), drivers


def _score_conditions(research: Dict[str, object]) -> Tuple[float, List[str]]:
    score = 3.0
    drivers = []
    outlook = research.get("sector_outlook")
    if outlook == "Negative":
        score += 6
        drivers.append("Sector outlook negative")
    elif outlook == "Cautious":
        score += 3
        drivers.append("Sector outlook cautious")
    elif outlook == "Positive":
        score -= 1
        drivers.append("Sector outlook positive")
    return _clamp(score, 0, 15), drivers


def compute_five_cs(
    financials: Dict[str, object],
    research: Dict[str, object],
    company_profile: Dict[str, object],
    officer_inputs: Dict[str, object],
) -> Dict[str, object]:
    character, character_drivers = _score_character(research, officer_inputs)
    capacity, capacity_drivers = _score_capacity(financials)
    capital, capital_drivers = _score_capital(financials, company_profile)
    collateral, collateral_drivers = _score_collateral(financials)
    conditions, conditions_drivers = _score_conditions(research)

    total_score = round(character + capacity + capital + collateral + conditions, 2)
    band = classify_risk_band(total_score)

    top_drivers = list({
        *character_drivers,
        *capacity_drivers,
        *capital_drivers,
        *collateral_drivers,
        *conditions_drivers,
        *financials.get("flags", []),
    })

    return {
        "scores": {
            "character": character,
            "capacity": capacity,
            "capital": capital,
            "collateral": collateral,
            "conditions": conditions,
        },
        "total_score": total_score,
        "risk_band": band,
        "drivers": top_drivers,
    }
