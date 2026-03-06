from __future__ import annotations

import json
import os
import uuid
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from data_ingestor import ingest_files
from api.pipeline import load_company_profile, run_analysis
from api import auth_utils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from api.schemas import (
    AnalyzeCompanyRequest,
    BasicResponse,
    OfficerInputRequest,
    RiskReportResponse,
    UploadDocumentsResponse
)
from api.storage import (
    get_analysis,
    get_company,
    get_documents,
    get_officer_inputs,
    init_db as init_storage_db,
    save_analysis,
    save_company,
    save_documents,
    save_officer_inputs,
)

app = FastAPI(title="INTELLI-CREDIT API (Stateless)", version="0.2.1") # Build: 2026-03-06T02:25:00

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase on startup
@app.on_event("startup")
def _startup() -> None:
    auth_utils.init_firebase()
    # init_storage_db() # Storage is now in-memory (stateless)

@app.get("/")
def health():
    return {"status": "IntelliCredit API running"}

@app.middleware("http")
async def log_requests(request, call_next):
    origin = request.headers.get("origin")
    print(f"DEBUG: Request {request.method} {request.url.path} from Origin: {origin}")
    response = await call_next(request)
    return response

# --- Authentication ---

@app.post("/verify-token")
async def verify_token(user: dict = Depends(auth_utils.get_current_user)):
    """Verifies the Firebase ID token and returns simple user info."""
    return {
        "status": "Authenticated",
        "email": user.get("email"),
        "name": user.get("name"),
    }

# --- Core Logic Routes (Protected) ---

@app.get("/companies")
def list_companies(user: dict = Depends(auth_utils.get_current_user)) -> List[dict]:
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
    user: dict = Depends(auth_utils.get_current_user)
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
async def analyze_company(
    payload: AnalyzeCompanyRequest,
    user: dict = Depends(auth_utils.get_current_user)
):
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

@app.get("/risk-report/{company_id}", response_model=RiskReportResponse)
async def get_risk_report(
    company_id: str,
    user: dict = Depends(auth_utils.get_current_user)
):
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    return {"company_id": company_id, "risk_report": analysis["risk_report"]}

@app.get("/research-details/{company_id}")
async def get_research_details(
    company_id: str,
    user: dict = Depends(auth_utils.get_current_user)
):
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    research = analysis.get("research", {})
    return research

@app.get("/explainability/{company_id}")
async def get_decision_explainability(
    company_id: str,
    user: dict = Depends(auth_utils.get_current_user)
):
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    return analysis.get("risk_report", {})

@app.get("/download-cam/{company_id}")
async def download_cam(
    company_id: str,
    user: dict = Depends(auth_utils.get_current_user)
):
    analysis = get_analysis(company_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")

    cam_pdf_path = os.path.join("storage", "cam", f"cam_{company_id}.pdf")
    if os.path.exists(cam_pdf_path):
        return FileResponse(cam_pdf_path, media_type="application/pdf", filename=f"CAM_{company_id}.pdf")
    raise HTTPException(status_code=404, detail="CAM output not found")
