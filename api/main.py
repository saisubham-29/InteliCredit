from __future__ import annotations

import json
import os
import uuid
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from data_ingestor import ingest_files
from api.pipeline import load_company_profile, run_analysis
from api.schemas import (
    AnalyzeCompanyRequest,
    BasicResponse,
    OfficerInputRequest,
    RiskReportResponse,
    UploadDocumentsResponse,
)
from api.storage import (
    get_analysis,
    get_company,
    get_documents,
    get_officer_inputs,
    init_db,
    save_analysis,
    save_company,
    save_documents,
    save_officer_inputs,
)


app = FastAPI(title="INTELLI-CREDIT API", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/")
def root() -> HTMLResponse:
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("INTELLI-CREDIT API is running.")


@app.get("/companies")
def list_companies() -> List[dict]:
    sample_path = os.path.join("sample_data", "companies.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.post("/upload-documents", response_model=UploadDocumentsResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    company_id: str | None = Form(None),
    company_name: str | None = Form(None),
    sector: str | None = Form(None),
):
    company_id = company_id or str(uuid.uuid4())
    company_name = company_name or f"Borrower {company_id[:6]}"

    save_company(company_id, company_name, sector)

    result = ingest_files(company_id, files)
    documents = []
    for doc in result.documents:
        documents.append(
            {
                "document_id": doc.document_id,
                "filename": doc.filename,
                "doc_type": doc.doc_type,
                "path": doc.path,
                "meta": doc.meta,
            }
        )
    save_documents(company_id, documents)

    return {
        "company_id": company_id,
        "documents": [
            {
                "document_id": doc["document_id"],
                "filename": doc["filename"],
                "doc_type": doc["doc_type"],
                "meta": doc["meta"],
            }
            for doc in documents
        ],
    }


@app.post("/analyze-company", response_model=RiskReportResponse)
async def analyze_company(payload: AnalyzeCompanyRequest):
    company = get_company(payload.company_id)
    if not company:
        company = load_company_profile(payload.company_id)
        save_company(company["id"], company["name"], company.get("sector"))

    documents = get_documents(payload.company_id)
    officer_inputs = get_officer_inputs(payload.company_id)

    result = run_analysis(payload.company_id, documents, officer_inputs)
    save_analysis(payload.company_id, result["risk_report"], result["cam_json"])

    return {
        "company_id": payload.company_id,
        "risk_report": result["risk_report"],
    }


@app.post("/submit-officer-input", response_model=BasicResponse)
async def submit_officer_input(payload: OfficerInputRequest):
    save_officer_inputs(payload.company_id, payload.model_dump())
    return {"status": "ok", "details": "Officer inputs saved."}


@app.get("/risk-report/{company_id}", response_model=RiskReportResponse)
async def get_risk_report(company_id: str):
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    return {"company_id": company_id, "risk_report": analysis["risk_report"]}


@app.get("/research-details/{company_id}")
async def get_research_details(company_id: str):
    """Get detailed research with news sources for officer review"""
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    research = analysis.get("research", {})
    
    return {
        "company_id": company_id,
        "news_articles": research.get("news_hits", []),
        "sector_outlook": research.get("sector_outlook", ""),
        "risk_heatmap": research.get("risk_heatmap", {}),
        "ai_analysis": research.get("ai_analysis", {}),
        "web_crawl_stats": research.get("web_crawl_stats", {}),
        "mode": research.get("mode", "basic")
    }


@app.get("/explainability/{company_id}")
async def get_decision_explainability(company_id: str):
    """Get complete decision explainability chain"""
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    risk_report = analysis.get("risk_report", {})
    ml_decision = risk_report.get("ml_decision", {})
    
    return {
        "company_id": company_id,
        "final_decision": ml_decision.get("final_decision", "N/A"),
        "decision_reason": ml_decision.get("reason", "N/A"),
        "probability_of_default": ml_decision.get("probability_of_default", 0),
        "risk_class": ml_decision.get("risk_class", "Unknown"),
        "five_cs_breakdown": {
            "character": risk_report.get("character", {}),
            "capacity": risk_report.get("capacity", {}),
            "capital": risk_report.get("capital", {}),
            "collateral": risk_report.get("collateral", {}),
            "conditions": risk_report.get("conditions", {})
        },
        "ml_features_used": {
            "current_ratio": analysis.get("financials", {}).get("current_ratio"),
            "debt_to_equity": analysis.get("financials", {}).get("debt_to_equity"),
            "interest_coverage": analysis.get("financials", {}).get("interest_coverage"),
            "roe": analysis.get("financials", {}).get("roe"),
            "operating_margin": analysis.get("financials", {}).get("operating_margin")
        },
        "evidence": risk_report.get("evidence", {}),
        "conditions": ml_decision.get("conditions", []),
        "pricing_breakdown": ml_decision.get("pricing", {})
    }


@app.get("/download-cam/{company_id}")
async def download_cam(company_id: str):
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")

    cam_pdf_path = os.path.join("storage", "cam", f"cam_{company_id}.pdf")
    cam_html_path = os.path.join("storage", "cam", f"cam_{company_id}.html")
    if os.path.exists(cam_pdf_path):
        return FileResponse(cam_pdf_path, media_type="application/pdf", filename=f"CAM_{company_id}.pdf")
    if os.path.exists(cam_html_path):
        return FileResponse(cam_html_path, media_type="text/html", filename=f"CAM_{company_id}.html")
    raise HTTPException(status_code=404, detail="CAM output not found")


@app.post("/train-models")
async def train_models(file: UploadFile = File(...)):
    """
    Train ML models on historical loan data
    Upload CSV with columns: current_ratio, debt_to_equity, interest_coverage, roe, 
    operating_margin, revenue_growth, management_score, sector_risk, defaulted, approved_limit_lakhs
    """
    from ai.train_models import ModelTrainer
    
    # Save uploaded file
    csv_path = os.path.join("storage", "uploads", f"training_data_{file.filename}")
    with open(csv_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Train models
    try:
        trainer = ModelTrainer()
        results = trainer.train_from_csv(csv_path)
        return {
            "status": "success",
            "message": "Models trained successfully. Restart server to load new models.",
            "metrics": {
                "pd_auc": round(results['pd_auc'], 3),
                "limit_mae": round(results['limit_mae'], 2),
                "samples": results['samples'],
                "default_rate": round(results['default_rate'] * 100, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Training failed: {str(e)}")


@app.post("/generate-sample-data")
async def generate_sample_data(n_samples: int = 500):
    """Generate sample training data for testing"""
    from ai.train_models import create_sample_training_data
    
    output_path = create_sample_training_data(n_samples=n_samples)
    return FileResponse(output_path, media_type="text/csv", filename="sample_training_data.csv")
