import json
import os
from datetime import datetime

# In-memory storage to satisfy "stateless (no database)" requirement
# Note: Data will be lost on server restart. 
_storage = {
    "companies": {},      # company_id -> dict
    "documents": {},      # company_id -> list of dicts
    "analysis_results": {}, # company_id -> list of dicts (ordered by created_at)
    "officer_inputs": {},   # company_id -> dict
}

def init_db():
    """No-op for in-memory storage"""
    pass

def save_company(company_id, name, sector=None):
    _storage["companies"][company_id] = {
        "id": company_id,
        "name": name,
        "sector": sector,
        "created_at": datetime.now().isoformat()
    }

def get_company(company_id):
    return _storage["companies"].get(company_id)

def save_documents(company_id, documents):
    if company_id not in _storage["documents"]:
        _storage["documents"][company_id] = []
    
    for doc in documents:
        _storage["documents"][company_id].append({
            "company_id": company_id,
            "filename": doc.get("filename"),
            "doc_type": doc.get("doc_type"),
            "storage_path": doc.get("path"),
            "uploaded_at": datetime.now().isoformat()
        })

def get_documents(company_id):
    return _storage["documents"].get(company_id, [])

def save_analysis(company_id, risk_report, cam_json=None):
    if company_id not in _storage["analysis_results"]:
        _storage["analysis_results"][company_id] = []
    
    analysis_entry = {
        "company_id": company_id,
        "risk_score": risk_report.get("total_score", 0.0),
        "risk_band": risk_report.get("risk_band", "Unknown"),
        "recommendation": json.dumps(risk_report.get("recommendation", {})),
        "five_cs_breakdown": json.dumps(risk_report.get("component_details", {})),
        "financial_metrics": json.dumps(risk_report.get("financial_metrics", {})),
        "research_summary": json.dumps(risk_report.get("research_summary", {})),
        "cam_json": json.dumps(cam_json) if cam_json else None,
        "created_at": datetime.now().isoformat()
    }
    _storage["analysis_results"][company_id].append(analysis_entry)

def get_analysis(company_id):
    results = _storage["analysis_results"].get(company_id)
    if not results:
        return None
    
    # Get the latest result
    res = results[-1]
    
    # Reconstruct the format expected by the API
    return {
        "company_id": res["company_id"],
        "risk_report": {
            "total_score": res["risk_score"],
            "risk_band": res["risk_band"],
            "recommendation": json.loads(res["recommendation"] or "{}"),
            "component_details": json.loads(res["five_cs_breakdown"] or "{}"),
            "financial_metrics": json.loads(res["financial_metrics"] or "{}"),
            "research_summary": json.loads(res["research_summary"] or "{}"),
        },
        "cam_json": json.loads(res["cam_json"] or "{}"),
        "created_at": res["created_at"]
    }

def save_officer_inputs(company_id, officer_inputs):
    _storage["officer_inputs"][company_id] = {
        "inputs": json.dumps(officer_inputs),
        "updated_at": datetime.now().isoformat()
    }

def get_officer_inputs(company_id):
    entry = _storage["officer_inputs"].get(company_id)
    return json.loads(entry["inputs"]) if entry else {}
