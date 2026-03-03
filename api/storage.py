import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "intelicredit.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            sector TEXT,
            pan_number TEXT,
            gst_number TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            filename TEXT,
            doc_type TEXT,
            storage_path TEXT,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    # Analysis Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            risk_score FLOAT,
            risk_band TEXT,
            recommendation TEXT, -- JSON
            five_cs_breakdown TEXT, -- JSON
            financial_metrics TEXT, -- JSON
            research_summary TEXT, -- JSON
            cam_json TEXT, -- JSON
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)

    # Officer Inputs table (New or restored)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officer_inputs (
            company_id TEXT PRIMARY KEY,
            inputs TEXT, -- JSON
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_company(company_id, name, sector=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO companies (id, name, sector) VALUES (?, ?, ?)",
        (company_id, name, sector)
    )
    conn.commit()
    conn.close()

def get_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_documents(company_id, documents):
    conn = get_db_connection()
    cursor = conn.cursor()
    for doc in documents:
        cursor.execute(
            "INSERT INTO documents (company_id, filename, doc_type, storage_path) VALUES (?, ?, ?, ?)",
            (company_id, doc.get("filename"), doc.get("doc_type"), doc.get("path"))
        )
    conn.commit()
    conn.close()

def get_documents(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE company_id = ?", (company_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_analysis(company_id, risk_report, cam_json=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Flatten risk_report if needed or store as JSON string
    risk_score = risk_report.get("total_score", 0.0)
    risk_band = risk_report.get("risk_band", "Unknown")
    
    cursor.execute(
        "INSERT INTO analysis_results (company_id, risk_score, risk_band, recommendation, five_cs_breakdown, financial_metrics, research_summary, cam_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            company_id, 
            risk_score, 
            risk_band, 
            json.dumps(risk_report.get("recommendation", {})),
            json.dumps(risk_report.get("component_details", {})),
            json.dumps(risk_report.get("financial_metrics", {})),
            json.dumps(risk_report.get("research_summary", {})),
            json.dumps(cam_json) if cam_json else None
        )
    )
    conn.commit()
    conn.close()

def get_analysis(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_results WHERE company_id = ? ORDER BY created_at DESC LIMIT 1", (company_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    res = dict(row)
    # Parse JSON strings back to dicts
    res["risk_report"] = {
        "total_score": res["risk_score"],
        "risk_band": res["risk_band"],
        "recommendation": json.loads(res["recommendation"] or "{}"),
        "component_details": json.loads(res["five_cs_breakdown"] or "{}"),
        "financial_metrics": json.loads(res["financial_metrics"] or "{}"),
        "research_summary": json.loads(res["research_summary"] or "{}"),
    }
    res["cam_json"] = json.loads(res["cam_json"] or "{}")
    return res

def save_officer_inputs(company_id, officer_inputs):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO officer_inputs (company_id, inputs) VALUES (?, ?)",
        (company_id, json.dumps(officer_inputs))
    )
    conn.commit()
    conn.close()

def get_officer_inputs(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT inputs FROM officer_inputs WHERE company_id = ?", (company_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}
