from __future__ import annotations

import json
import os
import shutil
import uuid
from typing import Iterable, List, Optional

import pandas as pd

from .models import DocumentInfo, IngestResult

RAW_STORAGE_DIR = "storage/raw"


def _ensure_dirs() -> None:
    os.makedirs(RAW_STORAGE_DIR, exist_ok=True)


def detect_file_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".csv"):
        if "gst" in lower:
            return "gst_csv"
        if "bank" in lower or "statement" in lower:
            return "bank_statement_csv"
        return "structured_csv"
    if lower.endswith(".pdf"):
        if "annual" in lower or "report" in lower:
            return "annual_report_pdf"
        if "legal" in lower or "notice" in lower:
            return "legal_notice_pdf"
        return "unstructured_pdf"
    if lower.endswith(".txt"):
        if "annual" in lower or "report" in lower:
            return "annual_report_text"
        if "legal" in lower or "notice" in lower:
            return "legal_notice_text"
        return "unstructured_text"
    return "unknown"


def _store_file(company_id: str, filename: str, file_obj) -> str:
    _ensure_dirs()
    company_dir = os.path.join(RAW_STORAGE_DIR, company_id)
    os.makedirs(company_dir, exist_ok=True)
    dest_path = os.path.join(company_dir, filename)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file_obj, f)
    return dest_path


def _extract_csv_rows(path: str) -> List[dict]:
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_csv(path, encoding="latin-1")
    df = df.fillna("")
    return df.to_dict(orient="records")


def ingest_files(company_id: str, files: Iterable) -> IngestResult:
    documents: List[DocumentInfo] = []

    for upload in files:
        filename = upload.filename
        doc_type = detect_file_type(filename)
        document_id = str(uuid.uuid4())
        path = _store_file(company_id, filename, upload.file)

        extracted_rows = None
        if doc_type.endswith("_csv") or doc_type == "structured_csv":
            extracted_rows = _extract_csv_rows(path)

        meta = {
            "doc_type": doc_type,
            "source": "upload",
            "rows": len(extracted_rows) if extracted_rows else 0,
        }

        documents.append(
            DocumentInfo(
                document_id=document_id,
                company_id=company_id,
                filename=filename,
                doc_type=doc_type,
                path=path,
                extracted_rows=extracted_rows,
                meta=meta,
            )
        )

    return IngestResult(company_id=company_id, documents=documents)
