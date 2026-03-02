# INTELLI-CREDIT: AI-Powered Corporate Credit Appraisal Engine

Production-grade system that automates Comprehensive Credit Appraisal Memo (CAM) preparation for Indian corporate lending with ML-based decisioning, live web research, and explainable Five-Cs scoring.

## Key Features

### Core Capabilities
- **Multi-source Data Ingestion**: PDFs, CSVs, and Databricks integration for comprehensive data collection
- **Live Web Research**: Real-time company news, sector analysis, and risk signal detection
- **AI-Powered Analysis**: Gemini API integration for intelligent company and financial analysis
- **ML-Based Decisioning**: 
  - Probability of Default (PD) calculation using Random Forest
  - Credit limit recommendation with Gradient Boosting
  - Risk-adjusted pricing with automated premium calculation
- **Explainable Five-Cs Scoring**: Transparent credit assessment with evidence-based reasoning
- **Automated CAM Generation**: Professional PDF reports with JSON export

### AI & ML Features
- **Gemini AI Integration**: Deep company profile and financial ratio analysis
- **Web Crawler**: Live news aggregation and sentiment analysis from multiple sources
- **Credit Decision Engine**: 
  - PD model with risk classification (Very Low to Very High)
  - Automated credit limit calculation (50L - 50Cr range)
  - Risk premium calculation (1% - 8% based on PD)
  - Lending decision logic (Approve/Approve with Conditions/Decline)
- **Databricks Connector**: Multi-source data fetching (financials, credit bureau, GST, legal cases)

## Folder Structure
```
/Users/saisubhamsahu/InteliCredit
|-- ai/                          # AI & ML modules
|   |-- gemini_client.py         # Gemini API integration
|   |-- web_crawler.py           # Live web research
|   |-- ml_decisioning.py        # ML-based credit decisioning
|   |-- databricks_connector.py  # Databricks integration
|-- api/                         # FastAPI endpoints
|-- cam_generator/               # CAM generation
|-- data_ingestor/               # Data ingestion
|-- document_parser/             # Document parsing
|-- financial_analyzer/          # Financial analysis
|-- frontend/                    # Web UI
|-- research_agent/              # Research & sentiment analysis
|-- risk_engine/                 # Five-Cs scoring
|-- sample_data/                 # Demo data
|-- storage/                     # Data storage
|-- .env.example                 # Environment configuration template
|-- requirements.txt
|-- README.md
```

## Setup

### 1. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

**Required Configuration:**
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Optional Configuration:**
- `DATABRICKS_HOST`: Your Databricks workspace URL
- `DATABRICKS_TOKEN`: Databricks access token
- `DATABRICKS_WAREHOUSE_ID`: SQL warehouse ID

### 4. Run the Server
```bash
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000` for the dashboard.

## Usage

### Web Interface
1. Navigate to `http://127.0.0.1:8000`
2. Upload documents (annual reports, bank statements, GST data)
3. Select company and run analysis
4. Review AI-powered insights and ML-based recommendations
5. Submit officer inputs to adjust scoring
6. Download CAM PDF

### API Endpoints

#### Upload Documents
```bash
curl -X POST "http://127.0.0.1:8000/upload-documents" \
  -F "company_name=Shakti Steel Pvt Ltd" \
  -F "sector=manufacturing" \
  -F "files=@sample_data/annual_report_1.txt" \
  -F "files=@sample_data/bank_statement.csv" \
  -F "files=@sample_data/gst_data.csv"
```

#### Run Analysis (with ML Decisioning)
```bash
curl -X POST "http://127.0.0.1:8000/analyze-company" \
  -H "Content-Type: application/json" \
  -d '{"company_id":"comp-001"}'
```

#### Submit Officer Input
```bash
curl -X POST "http://127.0.0.1:8000/submit-officer-input" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id":"comp-001",
    "factory_utilization_pct":68,
    "management_quality_notes":"Strong governance",
    "site_visit_observations":"Clean operations"
  }'
```

#### Fetch Risk Report
```bash
curl "http://127.0.0.1:8000/risk-report/comp-001"
```

#### Download CAM PDF
```bash
curl -O "http://127.0.0.1:8000/download-cam/comp-001"
```

## ML Decision Output

The ML decisioning engine provides:

```json
{
  "final_decision": "APPROVE",
  "reason": "All risk parameters within acceptable limits",
  "probability_of_default": 0.0823,
  "risk_class": "Low",
  "recommended_limit": {
    "recommended_limit_cr": 12.5,
    "decision": "APPROVE",
    "confidence": 0.85
  },
  "pricing": {
    "base_rate_pct": 8.0,
    "risk_premium_pct": 2.0,
    "total_rate_pct": 10.0,
    "rate_category": "Prime"
  },
  "conditions": [
    "Quarterly financial monitoring required",
    "Standard terms and conditions apply"
  ]
}
```

## AI Features in Action

### 1. Live Web Research
- Crawls DuckDuckGo for company news and sector trends
- Extracts financial mentions, risk indicators, and positive signals
- Performs sentiment analysis on news articles
- Provides evidence-based risk assessment

### 2. Gemini AI Analysis
- **Company Profile Analysis**: Management quality, business model viability, market position
- **Financial Ratio Analysis**: Health score, liquidity assessment, leverage risk
- **Sector Outlook**: AI-generated sector trends and growth prospects

### 3. ML-Based Decisioning
- **PD Calculation**: Random Forest model trained on financial ratios
- **Credit Limit**: Gradient Boosting model for optimal limit recommendation
- **Risk Premium**: Automated pricing based on PD, collateral, and sector risk
- **Final Decision**: Rule-based logic combining ML outputs with business constraints

## Sample Data

Upload these files from `sample_data`:
- `annual_report_1.txt` - Company financial statements
- `annual_report_2.txt` - Historical financial data
- `bank_statement.csv` - Banking transactions
- `gst_data.csv` - GST filing records
- `legal_notice.txt` - Legal compliance documents

## Explainability & Transparency

### Evidence-Based Scoring
- All risk scores include supporting evidence and confidence levels
- News snippets with sentiment analysis and source URLs
- Financial ratio calculations with missing data warnings

### ML Model Transparency
- Feature importance displayed for credit decisions
- Confidence scores for all ML predictions
- Justification for risk premium calculations

### Audit Trail
- Complete evidence chain from source documents to final decision
- Extraction confidence scores for parsed fields
- Officer input adjustments tracked separately

## Architecture

### Data Flow
```
Documents → Parser → Financial Analyzer
                          ↓
Company Profile → Web Crawler → Gemini AI → Research Agent
                          ↓
              ML Decision Engine
                          ↓
              Five-Cs Scoring → Risk Report → CAM Generator
```

### ML Models
- **PD Model**: Random Forest Classifier (100 estimators)
- **Limit Model**: Gradient Boosting Regressor (100 estimators)
- **Training**: Synthetic data for demo; production requires historical loan data

### Databricks Integration
- Fetches financial data, credit bureau scores, GST records, legal cases
- Falls back to local data if Databricks not configured
- Supports SQL queries via Databricks SQL API

## Configuration

### Operating Modes

**Enhanced Mode** (Recommended):
- Requires `GEMINI_API_KEY` in `.env`
- Enables live web crawling and AI analysis
- ML-based credit decisioning active

**Basic Mode** (Fallback):
- Uses synthetic data and rule-based logic
- No external API calls required
- Suitable for testing without API keys

### Databricks Setup (Optional)

1. Create SQL warehouse in Databricks
2. Generate personal access token
3. Configure `.env` with credentials
4. System will automatically fetch multi-source data

## Production Deployment

### Prerequisites
- Python 3.9+
- Gemini API key (required for AI features)
- Databricks workspace (optional, for multi-source data)
- Tesseract OCR (optional, for scanned PDFs)

### Environment Variables
```bash
GEMINI_API_KEY=your_key_here
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=your_token
DATABRICKS_WAREHOUSE_ID=your_warehouse_id
```

### Scaling Considerations
- Web crawler respects rate limits (configurable timeout)
- ML models can be retrained with production data
- Databricks handles large-scale data ingestion
- CAM generation supports batch processing

## Next Steps

### Immediate Enhancements
1. **Train ML Models**: Replace synthetic training data with historical loan performance
2. **OCR Integration**: Add Tesseract for scanned PDF processing
3. **MCA Integration**: Fetch company data from Ministry of Corporate Affairs
4. **Credit Bureau APIs**: Integrate CIBIL, Experian, Equifax

### Advanced Features
1. **Real-time Monitoring**: Track borrower financial health post-disbursement
2. **Portfolio Analytics**: Aggregate risk metrics across loan book
3. **Stress Testing**: Scenario analysis for economic downturns
4. **Automated Alerts**: Flag deteriorating credit quality

## Technical Notes

### PDF Generation
- Uses `weasyprint` for HTML → PDF conversion
- Falls back to HTML CAM if PDF generation fails
- Supports custom templates via Jinja2

### Web Crawling
- Uses DuckDuckGo HTML (no API key required)
- Respects robots.txt and rate limits
- Async implementation for performance

### ML Models
- Stored in `storage/models/` directory
- Automatically initialized with synthetic data
- Can be retrained via API endpoint (future enhancement)

## Troubleshooting

### "AI modules not available"
- Install dependencies: `pip install -r requirements.txt`
- Check `.env` file exists with `GEMINI_API_KEY`

### "Databricks not configured"
- Optional feature; system works without it
- Add Databricks credentials to `.env` to enable

### Web crawling slow
- Adjust `CRAWL_TIMEOUT` in `.env`
- Reduce `MAX_CRAWL_PAGES` for faster results

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation at `http://127.0.0.1:8000/docs`
3. Examine logs in console output
