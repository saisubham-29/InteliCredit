from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    document_id: str
    filename: str
    doc_type: str
    meta: Dict[str, Any]


class UploadDocumentsResponse(BaseModel):
    company_id: str
    documents: List[DocumentOut]


class AnalyzeCompanyRequest(BaseModel):
    company_id: str


class OfficerInputRequest(BaseModel):
    company_id: str
    factory_utilization_pct: Optional[float] = None
    management_quality_notes: Optional[str] = None
    site_visit_observations: Optional[str] = None


class RiskReportResponse(BaseModel):
    company_id: str
    risk_report: Dict[str, Any]


class BasicResponse(BaseModel):
    status: str = Field(default="ok")
    details: Optional[str] = None
