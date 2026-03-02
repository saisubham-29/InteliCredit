from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_PATH = "storage/db.sqlite"


def _ensure_storage_dir() -> None:
    os.makedirs("storage", exist_ok=True)


def get_conn() -> sqlite3.Connection:
    _ensure_storage_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            company_id TEXT,
            filename TEXT,
            doc_type TEXT,
            path TEXT,
            meta TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            company_id TEXT PRIMARY KEY,
            risk_report TEXT,
            cam_json TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS officer_inputs (
            company_id TEXT PRIMARY KEY,
            data TEXT,
            updated_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_company(company_id: str, name: str, sector: str | None = None) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO companies (id, name, sector, created_at) VALUES (?, ?, ?, ?)",
        (company_id, name, sector, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_company(company_id: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_documents(company_id: str, documents: List[Dict[str, Any]]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    for doc in documents:
        cur.execute(
            "INSERT OR REPLACE INTO documents (id, company_id, filename, doc_type, path, meta) VALUES (?, ?, ?, ?, ?, ?)",
            (
                doc["document_id"],
                company_id,
                doc["filename"],
                doc["doc_type"],
                doc["path"],
                json.dumps(doc.get("meta", {})),
            ),
        )
    conn.commit()
    conn.close()


def get_documents(company_id: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE company_id = ?", (company_id,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    for row in rows:
        row["meta"] = json.loads(row.get("meta") or "{}")
    return rows


def save_analysis(company_id: str, risk_report: Dict[str, Any], cam_json: Dict[str, Any]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO analyses (company_id, risk_report, cam_json, updated_at) VALUES (?, ?, ?, ?)",
        (
            company_id,
            json.dumps(risk_report),
            json.dumps(cam_json),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_analysis(company_id: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analyses WHERE company_id = ?", (company_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "risk_report": json.loads(row["risk_report"]),
        "cam_json": json.loads(row["cam_json"]),
        "updated_at": row["updated_at"],
    }


def save_officer_inputs(company_id: str, data: Dict[str, Any]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO officer_inputs (company_id, data, updated_at) VALUES (?, ?, ?)",
        (company_id, json.dumps(data), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_officer_inputs(company_id: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM officer_inputs WHERE company_id = ?", (company_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return json.loads(row[0])
