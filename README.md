# INTELICREDIT: Next-Gen AI Corporate Credit Appraisal Engine

InteliCredit is a state-of-the-art enterprise lending platform designed for the Indian corporate market. It combines **Deep Explainable AI (XAI)**, **Graph Neural Networks (GNN)**, and **Databricks Unity Catalog** integration to automate the preparation of high-fidelity Credit Appraisal Memos (CAM).

## 🚀 Next-Gen Pillars (Phase 6 & 7)

### 1. Deep Explainable AI (XAI)

- **Neural Logic**: Transparent ML decisioning using Gradient Boosting Regressors.
- **Feature Attribution**: Bar chart visualizations showing the contribution of each financial cluster (Liquidity, Leverage, etc.) to the Probability of Default (PD).
- **Automated Justification**: Natural language risk drivers generated per-entity.

### 2. GNN Promoter Fraud Detection

- **Network Analysis**: Uses Graph Neural Networks to detect circular trading patterns and promoter money loops.
- **Shell Company Guard**: Identifies suspicious transaction clusters and round-tripping activities.

### 3. Indian Financial Context

- **GST vs Bank Analysis**: Heuristics to detect "Window Dressing" by cross-validating GST filings against actual bank flows.
- **GST-3B vs 2A Mismatch**: Built-in logic for GST governance checks.

### 4. Databricks Unity Catalog

- **Enterprise Data Sovereignty**: Native support for three-level namespaces (`catalog.schema.table`).
- **Unified Governance**: Secure ingestion from governed SQL warehouses and data lakes.

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.12, PyPDF, WeasyPrint, Scikit-Learn.
- **Frontend**: Next.js 16 (Turbopack), Tailwind CSS, Recharts, Framer Motion.
- **Identity**: Firebase Google Auth (Stateless ID Token Verification).
- **Intelligence**: Google Gemini API (LLM), DuckDuckGo (Research).

## 📂 Project Structure

```
/InteliCredit
|-- ai/                          # AI/ML Core (XAI, GNN, Gemini)
|-- api/                         # FastAPI Services & Pipeline (Stateless)
|-- cam_generator/               # Jinja2 PDF Templates & Logic
|-- document_parser/             # PDF/CSV Extraction
|-- financial_analyzer/          # Indian Context Heuristics (GST & Bank)
|-- frontend-nextjs/             # Next.js Dashboard
|-- risk_engine/                 # 5Cs Scoring Logic
|-- storage/                     # In-memory session data & CAM Output
```

## 🚀 Quick Start

### 1. Install Backend

```bash
pip install -r requirements.txt
cp .env.example .env
# Set GEMINI_API_KEY and FIREBASE_SERVICE_ACCOUNT_JSON
uvicorn api.main:app --reload
```

### 2. Install Frontend

```bash
cd frontend-nextjs
npm install
npm run dev
```

## 📊 Verification

Run the integrated verification suite:

```bash
python verify_phase6.py
```

This validates the end-to-end pipeline from Databricks ingestion to XAI report generation.

## ⚖️ License

MIT License - Developed for the Intelli-Credit Challenge 2026.
