from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DocumentInfo:
    document_id: str
    company_id: str
    filename: str
    doc_type: str
    path: str
    extracted_rows: Optional[List[Dict[str, Any]]] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestResult:
    company_id: str
    documents: List[DocumentInfo]
