from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd


def _sum_bank_credits(rows: List[dict]) -> Tuple[float, float, float]:
    if not rows:
        return 0.0, 0.0, 0.0
    df = pd.DataFrame(rows)
    amount_col = "amount" if "amount" in df.columns else df.columns[-1]
    type_col = "type" if "type" in df.columns else None

    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)
    if type_col:
        credits = df[df[type_col].str.lower().eq("credit")][amount_col].sum()
        debits = df[df[type_col].str.lower().eq("debit")][amount_col].sum()
    else:
        credits = df[amount_col].sum()
        debits = 0.0

    interest = 0.0
    if "description" in df.columns:
        interest = df[df["description"].str.contains("interest", case=False, na=False)][amount_col].sum()

    return float(credits), float(debits), float(interest)


def _sum_gst_turnover(rows: List[dict]) -> float:
    if not rows:
        return 0.0
    df = pd.DataFrame(rows)
    turnover_col = None
    for col in df.columns:
        if "turnover" in col.lower() or "taxable" in col.lower():
            turnover_col = col
            break
    if turnover_col is None:
        return 0.0
    df[turnover_col] = pd.to_numeric(df[turnover_col], errors="coerce").fillna(0.0)
    return float(df[turnover_col].sum())


def _check_gst_mismatch(gst_rows: List[dict]) -> Tuple[float, List[str]]:
    """Check for mismatch between GSTR-1/3B and 2A (Input Credit)"""
    if not gst_rows:
        return 0.0, []
    
    df = pd.DataFrame(gst_rows)
    # Mocking GSTR-2A vs 3B comparison if columns exist
    if "gstr3b_output" in df.columns and "gstr2a_input" in df.columns:
        total_3b = pd.to_numeric(df["gstr3b_output"], errors="coerce").sum()
        total_2a = pd.to_numeric(df["gstr2a_input"], errors="coerce").sum()
        mismatch = abs(total_3b - total_2a) / total_3b if total_3b else 0
        if mismatch > 0.15:
            return mismatch, [f"High GST mismatch detected: {round(mismatch*100, 2)}% (GSTR-3B vs 2A)"]
    return 0.0, []


def _detect_anomalies(bank_rows: List[dict]) -> List[str]:
    """Detect circular trading or abnormal spikes in cash flow"""
    if not bank_rows:
        return []
    
    df = pd.DataFrame(bank_rows)
    amount_col = "amount" if "amount" in df.columns else df.columns[-1]
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)
    
    flags = []
    # Check for large round-sum transactions (Potential circular trading)
    round_sums = df[df[amount_col] % 100000 == 0][amount_col]
    if len(round_sums) > len(df) * 0.2:
        flags.append("High frequency of round-sum transactions (Potential circular trading)")
    
    # Check for sudden spikes (> 3x mean)
    mean_val = df[amount_col].mean()
    if mean_val > 0:
        spikes = df[df[amount_col] > mean_val * 5]
        if not spikes.empty:
            flags.append(f"Abnormal cash flow spikes detected ({len(spikes)} instances)")
            
    # Indian Banking: Detect round-tripping patterns (Debit followed by Credit of similar amount)
    # This is a basic heuristic for demonstration
    for i in range(len(df) - 1):
        if i > 0:
            prev_tx = df.iloc[i-1]
            curr_tx = df.iloc[i]
            if prev_tx[amount_col] > 500000 and abs(prev_tx[amount_col] - curr_tx[amount_col]) < 5000:
                flags.append(f"Suspicious round-tripping of ₹{curr_tx[amount_col]} detected")
                break
                
    return flags


def _extract_previous_ebitda(text: str) -> float | None:
    if not text:
        return None
    import re

    match = re.search(
        r"EBITDA\s*FY\s*2023\s*[:\-]?\s*₹?\s*([0-9,.]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "").strip())
    except Exception:
        return None


def analyze_financials(
    structured_docs: Dict[str, List[dict]],
    parsed_docs: Dict[str, dict],
    company_profile: Dict[str, object],
) -> Dict[str, object]:
    bank_rows = structured_docs.get("bank_statement_csv", [])
    gst_rows = structured_docs.get("gst_csv", [])

    bank_credits, bank_debits, interest_expense = _sum_bank_credits(bank_rows)
    gst_turnover = _sum_gst_turnover(gst_rows)

    extracted_fields = parsed_docs.get("annual_report", {}).get("fields", {})
    revenue = extracted_fields.get("revenue", {}).get("value")
    ebitda = extracted_fields.get("ebitda", {}).get("value")
    debt = extracted_fields.get("debt", {}).get("value")

    metrics = {}
    missing = []

    if ebitda and interest_expense:
        metrics["interest_coverage_ratio"] = round(ebitda / interest_expense, 2)
    else:
        metrics["interest_coverage_ratio"] = None
        missing.append("interest_coverage_ratio")

    principal_repayment = company_profile.get("annual_principal_repayment")
    if ebitda and (interest_expense or principal_repayment):
        denom = (interest_expense or 0.0) + (principal_repayment or 0.0)
        metrics["dscr"] = round(ebitda / denom, 2) if denom else None
    else:
        metrics["dscr"] = None
        missing.append("dscr")

    if gst_turnover and bank_credits:
        metrics["gst_vs_bank_ratio"] = round(gst_turnover / bank_credits, 2)
    else:
        metrics["gst_vs_bank_ratio"] = None
        missing.append("gst_vs_bank_ratio")

    if revenue and ebitda:
        metrics["ebitda_margin"] = round((ebitda / revenue) * 100, 2)
    else:
        metrics["ebitda_margin"] = None
        missing.append("ebitda_margin")

    annual_text = parsed_docs.get("annual_report", {}).get("text_excerpt", "")
    ebitda_prior = _extract_previous_ebitda(annual_text)
    if ebitda and ebitda_prior:
        change_pct = ((ebitda - ebitda_prior) / ebitda_prior) * 100
        if change_pct > 5:
            metrics["ebitda_trend"] = "Improving"
        elif change_pct < -5:
            metrics["ebitda_trend"] = "Declining"
        else:
            metrics["ebitda_trend"] = "Stable"
    else:
        metrics["ebitda_trend"] = None
        missing.append("ebitda_trend")

    collateral_value = company_profile.get("collateral_value")
    loan_requested = company_profile.get("loan_requested")
    if collateral_value and loan_requested:
        metrics["security_cover"] = round(collateral_value / loan_requested, 2)
    else:
        metrics["security_cover"] = None
        missing.append("security_cover")

    leverage = None
    if debt and ebitda:
        leverage = round(debt / ebitda, 2)
        metrics["debt_to_ebitda"] = leverage
    else:
        metrics["debt_to_ebitda"] = None
        missing.append("debt_to_ebitda")

    flags = []
    gst_mismatch, gst_flags = _check_gst_mismatch(gst_rows)
    flags.extend(gst_flags)
    
    anomaly_flags = _detect_anomalies(bank_rows)
    flags.extend(anomaly_flags)

    if metrics.get("gst_vs_bank_ratio") and metrics["gst_vs_bank_ratio"] > 1.3:
        flags.append("GST vs bank mismatch suggests revenue inflation (Window Dressing)")
    if metrics.get("interest_coverage_ratio") is not None and metrics["interest_coverage_ratio"] < 1.5:
        flags.append("Weak interest coverage ratio")
    if metrics.get("dscr") is not None and metrics["dscr"] < 1.2:
        flags.append("DSCR below comfort")
    if leverage and leverage > 4:
        flags.append("High leverage (Debt/EBITDA > 4x)")

    return {
        "metrics": metrics,
        "flags": flags,
        "missing": missing,
        "bank_credits": bank_credits,
        "bank_debits": bank_debits,
        "gst_turnover": gst_turnover,
        "interest_expense": interest_expense,
    }
