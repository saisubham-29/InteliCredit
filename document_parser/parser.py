from __future__ import annotations

import os
import re
from typing import Dict, Tuple

from pypdf import PdfReader

FIELD_PATTERNS = {
    "revenue": [
        r"Revenue\s*from\s*Operations\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Total\s*Revenue\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Revenue\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Turnover\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr"
    ],
    "ebitda": [
        r"EBITDA\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Operating\s*Profit\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"EBITDA\s*Margin\s*[:\-]?\s*([0-9,.]+)%"
    ],
    "pat": [
        r"Profit\s*After\s*Tax\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Net\s*Profit\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"PAT\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr"
    ],
    "debt": [
        r"Total\s*Debt\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Total\s*Borrowings\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Long\s*Term\s*Borrowings\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr"
    ],
    "net_worth": [
        r"Net\s*Worth\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Shareholder's?\s*Funds\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr",
        r"Total\s*Equity\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr"
    ],
    "auditor_remarks": [r"Auditor(?:'s)?\s*Remarks\s*[:\-]?\s*(.+)"],
    "contingent_liabilities": [r"Contingent\s*Liabilities\s*[:\-]?\s*₹?\s*([0-9,.]+)\s*Cr"],
}


def _read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n".join(texts)


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _run_ocr_stub(path: str) -> Tuple[str, str]:
    """
    OCR stub: tries pytesseract if available and the file is an image.
    Returns (text, method).
    """
    lower = path.lower()
    if not any(lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
        return "", "ocr_unavailable"

    try:
        import pytesseract
        from PIL import Image

        text = pytesseract.image_to_string(Image.open(path))
        return text, "pytesseract"
    except Exception:
        return "", "ocr_failed"


def extract_text(path: str, doc_type: str) -> Tuple[str, str]:
    if path.lower().endswith(".pdf"):
        text = _read_pdf_text(path)
        if text.strip():
            return text, "pdf_text"
        ocr_text, method = _run_ocr_stub(path)
        return ocr_text, method
    if path.lower().endswith(".txt"):
        return _read_text_file(path), "text_read"

    ocr_text, method = _run_ocr_stub(path)
    return ocr_text, method


def _normalize_number(value: str) -> float:
    return float(value.replace(",", "").strip())


def extract_key_fields(text: str) -> Dict[str, Dict[str, object]]:
    results: Dict[str, Dict[str, object]] = {}
    for field, patterns in FIELD_PATTERNS.items():
        match_value = None
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                match_value = match.group(1).strip()
                break
        
        if match_value is None:
            results[field] = {"value": None, "confidence": 0.0, "evidence": None}
            continue

        if field == "auditor_remarks":
            results[field] = {"value": match_value[:500], "confidence": 0.9, "evidence": match_value}
        else:
            try:
                numeric = _normalize_number(match_value)
                # Deterministic validation logic
                confidence = 0.95 if "Cr" in text[match.start():match.end()+10] else 0.85
                results[field] = {"value": numeric, "confidence": confidence, "evidence": match_value}
            except Exception:
                results[field] = {"value": None, "confidence": 0.0, "evidence": match_value}
    
    # Cross-field validation (Deterministic constraint)
    rev = results.get("revenue", {}).get("value")
    pat = results.get("pat", {}).get("value")
    if rev and pat and pat > rev:
        # Potential hallucination/mis-extraction: PAT cannot exceed Revenue
        results["pat"]["confidence"] *= 0.1
        results["pat"]["warning"] = "PAT exceeds Revenue - likely extraction error"
        
    return results


def _rule_based_fallback(path: str) -> str:
    try:
        with open(path, "rb") as f:
            raw = f.read()
        return raw.decode("latin-1", errors="ignore")
    except Exception:
        return ""


def parse_document(path: str, doc_type: str) -> Dict[str, object]:
    text, method = extract_text(path, doc_type)
    if not text.strip():
        text = _rule_based_fallback(path)
        method = "rule_fallback"
    fields = extract_key_fields(text)
    missing = [k for k, v in fields.items() if v["value"] is None]

    return {
        "doc_type": doc_type,
        "method": method,
        "text_excerpt": text[:500],
        "fields": fields,
        "missing_fields": missing,
    }
