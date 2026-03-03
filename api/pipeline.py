from __future__ import annotations

import json
import os
import uuid
import math
from typing import Dict, List

from ai import LLMClient
from ai.gnn_fraud_detector import run_fraud_analysis
from cam_generator import generate_cam_json, generate_cam_pdf
from document_parser import parse_document
from financial_analyzer import analyze_financials
from research_agent import run_research
from risk_engine import apply_human_inputs, classify_risk_band, compute_five_cs

# Import enhanced AI modules
try:
    from ai.ml_decisioning import CreditDecisionEngine
    from ai.databricks_connector import fetch_multi_source_data
    from ai.gemini_client import GeminiClient
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False
    print("Warning: ML decisioning modules not available. Using basic mode.")


SAMPLE_COMPANIES_PATH = os.path.join("sample_data", "companies.json")


def _clean_value(val, fallback: float) -> float:
    """Ensures value is a valid float, not NaN or None"""
    if val is None:
        return fallback
    try:
        fval = float(val)
        return fallback if math.isnan(fval) else fval
    except (ValueError, TypeError):
        return fallback


def load_company_profile(company_id: str) -> Dict[str, object]:
    if os.path.exists(SAMPLE_COMPANIES_PATH):
        with open(SAMPLE_COMPANIES_PATH, "r", encoding="utf-8") as f:
            companies = json.load(f)
        for company in companies:
            if company.get("id") == company_id:
                return company
    return {
        "id": company_id,
        "name": f"Company {company_id[:6]}",
        "sector": "manufacturing",
        "loan_requested": 15.0,
        "collateral_value": 25.0,
        "net_worth": 18.0,
        "annual_principal_repayment": 2.5,
    }


def parse_documents(documents: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    parsed: Dict[str, Dict[str, object]] = {}
    for doc in documents:
        doc_type = doc.get("doc_type")
        path = doc.get("path")
        if doc_type in {"annual_report_pdf", "annual_report_text", "unstructured_pdf"}:
            parsed["annual_report"] = parse_document(path, doc_type)
        if doc_type in {"legal_notice_pdf", "legal_notice_text"}:
            parsed["legal_notice"] = parse_document(path, doc_type)
    return parsed


def load_structured_docs(documents: List[Dict[str, object]]) -> Dict[str, List[dict]]:
    structured: Dict[str, List[dict]] = {}
    for doc in documents:
        doc_type = doc.get("doc_type")
        path = doc.get("path")
        if doc_type in {"bank_statement_csv", "gst_csv", "structured_csv"}:
            try:
                import pandas as pd

                df = pd.read_csv(path)
                rows = df.fillna("").to_dict(orient="records")
            except Exception:
                rows = []
            structured.setdefault(doc_type, []).extend(rows)
    return structured


def build_recommendation(company: Dict[str, object], financials: Dict[str, object], total_score: float) -> Dict[str, object]:
    loan_requested = company.get("loan_requested", 0.0)
    collateral_value = company.get("collateral_value", 0.0)
    bank_credits = financials.get("bank_credits", 0.0)

    # PD Calculation (Heuristic based on score)
    # Higher score = higher risk. 0-25 is Low risk.
    probability_of_default = min(0.99, round((total_score / 100.0) ** 2, 4))
    
    # Risk Grade (A-D)
    if total_score <= 25: grade = "A"
    elif total_score <= 45: grade = "B"
    elif total_score <= 65: grade = "C"
    else: grade = "D"

    eligibility = min(
        loan_requested,
        collateral_value * 0.75 if collateral_value else loan_requested,
        (bank_credits / 12) * 8 if bank_credits else loan_requested,
    )

    base_rate = 9.5 # Competitive market rate
    premium = (total_score / 100.0) * 10.0 # Risk premium up to 10%
    interest_rate = round(base_rate + premium, 2)

    decision_tag = "Approve"
    if grade == "C":
        decision_tag = "Approve with Conditions"
    if grade == "D":
        decision_tag = "Reject"

    rationale = f"Risk Grade {grade} assigned based on Five-Cs score of {total_score}. Interest rate includes a risk premium of {round(premium, 2)}%."

    return {
        "eligible_amount": round(eligibility, 2),
        "interest_rate": interest_rate,
        "decision_tag": decision_tag,
        "rationale": rationale,
        "risk_grade": grade,
        "probability_of_default": probability_of_default,
    }


def run_analysis(
    company_id: str,
    documents: List[Dict[str, object]],
    officer_inputs: Dict[str, object],
) -> Dict[str, object]:
    company_profile = load_company_profile(company_id)

    # Step 1: Fetch multi-source data from Databricks (if configured)
    if ML_ENABLED:
        print("Fetching multi-source data from Databricks...")
        databricks_data = fetch_multi_source_data(
            company_id, 
            company_profile.get("name", ""),
            company_profile.get("gstin")
        )
        if databricks_data.get("source") == "databricks":
            # Merge Databricks data into company profile
            if databricks_data.get("credit_bureau"):
                company_profile["credit_bureau"] = databricks_data["credit_bureau"]
            if databricks_data.get("legal"):
                company_profile["legal_cases"] = databricks_data["legal"]

    structured_docs = load_structured_docs(documents)
    parsed_docs = parse_documents(documents)

    if "annual_report" in parsed_docs:
        fields = parsed_docs["annual_report"].get("fields", {})
        for key in ["revenue", "ebitda", "debt"]:
            value = fields.get(key, {}).get("value")
            if value is not None:
                company_profile[key] = value

    llm = LLMClient()
    company_profile["business_overview"] = llm.summarize_business(company_profile)

    financials = analyze_financials(structured_docs, parsed_docs, company_profile)
    research = run_research(company_profile)

    # Step 2: GNN-based Fraud Analysis
    fraud_signals = run_fraud_analysis(
        company_id, 
        company_profile.get("name", "Unknown"),
        structured_docs.get("bank_statement_csv", [])
    )

    # Step 3: Enhanced financial analysis with Gemini (if available)
    if ML_ENABLED:
        try:
            gemini = GeminiClient()
            financial_ai_analysis = gemini.analyze_financial_ratios(financials)
            financials["ai_analysis"] = financial_ai_analysis
        except Exception as e:
            print(f"Gemini financial analysis failed: {e}")

    risk_report = compute_five_cs(financials, research, company_profile, officer_inputs)

    # Pillar 2: Integrate qualitative user input (e.g., factory at 40% capacity)
    qualitative_adjustments = []
    factory_util = officer_inputs.get("factory_utilization_pct")
    if factory_util is not None and factory_util < 50:
        # Penalty for underutilization of capacity
        risk_report["scores"]["capacity"] += 5
        qualitative_adjustments.append(f"Capacity penalty: Low factory utilization ({factory_util}%)")
    
    adjusted_total = round(sum(risk_report["scores"].values()), 2)
    risk_report["total_score"] = adjusted_total
    risk_report["risk_band"] = classify_risk_band(adjusted_total)
    if qualitative_adjustments:
        risk_report.setdefault("drivers", []).extend(qualitative_adjustments)

    # Step 4: ML-based credit decisioning (if enabled)
    if ML_ENABLED:
        try:
            decision_engine = CreditDecisionEngine()
            
            # Prepare features for ML model
            metrics = financials.get('metrics', {})
            ml_features = {
                'current_ratio': _clean_value(metrics.get('current_ratio'), 1.5),
                'debt_to_equity': _clean_value(metrics.get('debt_to_ebitda'), 1.0),
                'interest_coverage': _clean_value(metrics.get('interest_coverage_ratio'), 3.0),
                'roe': _clean_value(metrics.get('roe'), 0.15),
                'operating_margin': _clean_value(metrics.get('ebitda_margin'), 0.10),
                'revenue_growth': _clean_value(metrics.get('revenue_growth'), 0.10),
                'management_score': _clean_value(research.get('ai_analysis', {}).get('management_score'), 5.0) if isinstance(research.get('ai_analysis'), dict) else 5.0,
                'sector_risk': 0.3 if research.get('sector_outlook', '').lower() in ['negative', 'cautious'] else 0.1,
                'collateral_coverage': (company_profile.get('collateral_value') or 0.0) / max(company_profile.get('loan_requested') or 1.0, 1.0)
            }
            
            # Get ML-based lending decision
            ml_decision = decision_engine.make_lending_decision(
                ml_features,
                requested_limit=company_profile.get('loan_requested')
            )
            
            risk_report["ml_decision"] = ml_decision
            risk_report["recommendation"] = {
                "eligible_amount": ml_decision['recommended_limit']['recommended_limit_cr'],
                "interest_rate": ml_decision['pricing']['total_rate_pct'],
                "decision_tag": ml_decision['final_decision'],
                "rationale": ml_decision['reason'],
                "conditions": ml_decision['conditions'],
                "probability_of_default": ml_decision['probability_of_default'],
                "risk_class": ml_decision['risk_class'],
                "ml_confidence": ml_decision['ml_confidence'],
                "ml_explanation": ml_decision.get('ml_explanation') # Added XAI
            }
        except Exception as e:
            print(f"ML decisioning failed: {e}. Using basic recommendation.")
            risk_report["recommendation"] = build_recommendation(
                company_profile, financials, risk_report["total_score"]
            )
    else:
        risk_report["recommendation"] = build_recommendation(
            company_profile, financials, risk_report["total_score"]
        )

    risk_report["missing_data_warnings"] = list(
        set(financials.get("missing", []) + research.get("missing", []))
    )
    
    # Add fraud signals to the report
    risk_report["fraud_analysis"] = fraud_signals

    extraction_confidence = {}
    if "annual_report" in parsed_docs:
        extraction_confidence = {
            k: v.get("confidence")
            for k, v in parsed_docs["annual_report"].get("fields", {}).items()
        }

    risk_report["evidence"] = {
        "supporting_sources": [
            "Bank statement CSV",
            "GST data CSV",
            "Annual report",
            "News dataset",
            "Web Research" if research.get("mode") == "enhanced" else None,
            "Databricks" if ML_ENABLED else None
        ],
        "extraction_confidence": extraction_confidence,
        "document_excerpts": {
            k: v.get("text_excerpt") for k, v in parsed_docs.items()
        },
        "news_snippets": research.get("news_hits", [])[:5],
    }
    
    # Remove None values from supporting sources
    risk_report["evidence"]["supporting_sources"] = [s for s in risk_report["evidence"]["supporting_sources"] if s]

    cam_json = generate_cam_json(company_profile, financials, research, risk_report, officer_inputs)
    cam_pdf_path = generate_cam_pdf(cam_json, company_id)

    return {
        "company": company_profile,
        "financials": financials,
        "research": research,
        "risk_report": risk_report,
        "cam_json": cam_json,
        "cam_pdf_path": cam_pdf_path,
    }
