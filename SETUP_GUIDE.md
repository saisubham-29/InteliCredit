# INTELLI-CREDIT Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://makersuite.google.com/app/apikey
```

Edit `.env`:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Test Setup
```bash
python test_setup.py
```

You should see:
```
✓ All tests passed! System is ready.
```

### 4. Run the Server
```bash
uvicorn api.main:app --reload
```

### 5. Open Dashboard
Navigate to: `http://127.0.0.1:8000`

---

## Operating Modes

### Enhanced Mode (Recommended)
**Requirements**: Gemini API key

**Features**:
- ✅ Live web crawling for company news
- ✅ AI-powered company analysis
- ✅ ML-based credit decisioning
- ✅ Automated risk premium calculation
- ✅ Probability of Default (PD) modeling

**Setup**:
1. Get Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env`: `GEMINI_API_KEY=your_key`
3. Restart server

### Basic Mode (Fallback)
**Requirements**: None

**Features**:
- ✅ Document parsing and analysis
- ✅ Financial ratio calculation
- ✅ Five-Cs scoring
- ✅ CAM generation
- ⚠️ Uses synthetic data for research
- ⚠️ Rule-based decisioning only

---

## Optional: Databricks Integration

### Why Databricks?
- Fetch financial data from centralized data warehouse
- Access credit bureau scores (CIBIL, Experian)
- Pull GST filing records
- Query legal case databases
- Analyze banking transactions

### Setup Steps

1. **Create Databricks Workspace**
   - Sign up at [Databricks](https://databricks.com/)
   - Create a SQL warehouse

2. **Generate Access Token**
   - Go to User Settings → Access Tokens
   - Generate new token
   - Copy token securely

3. **Configure Environment**
   ```bash
   DATABRICKS_HOST=https://your-workspace.databricks.com
   DATABRICKS_TOKEN=your_token_here
   DATABRICKS_WAREHOUSE_ID=your_warehouse_id
   ```

4. **Prepare Data Tables**
   Create these tables in Databricks:
   - `financial_data` - Company financials
   - `credit_bureau_data` - Credit scores
   - `banking_transactions` - Bank statements
   - `gst_data` - GST filings
   - `legal_cases` - Litigation records

5. **Test Connection**
   ```python
   from ai.databricks_connector import DatabricksConnector
   connector = DatabricksConnector()
   print(connector.enabled)  # Should be True
   ```

---

## Demo Walkthrough

### Step 1: Upload Documents
1. Click "Upload Documents"
2. Select company: "Shakti Steel Pvt Ltd"
3. Upload files:
   - `sample_data/annual_report_1.txt`
   - `sample_data/bank_statement.csv`
   - `sample_data/gst_data.csv`

### Step 2: Run Analysis
1. Select company from dropdown
2. Click "Run Analysis"
3. Wait for AI processing (30-60 seconds)

### Step 3: Review Results
You'll see:
- **Financial Analysis**: Ratios, trends, AI insights
- **Research Report**: News, sentiment, sector outlook
- **Risk Scoring**: Five-Cs breakdown with evidence
- **ML Decision**: PD, credit limit, risk premium
- **Recommendation**: Approve/Reject with conditions

### Step 4: Submit Officer Inputs
1. Add field observations:
   - Factory utilization: 68%
   - Management quality: "Strong governance"
   - Site visit notes: "Clean operations"
2. Re-run analysis to see adjusted scores

### Step 5: Download CAM
1. Click "Download CAM PDF"
2. Review comprehensive credit memo
3. Share with credit committee

---

## API Usage Examples

### Upload Documents
```bash
curl -X POST "http://127.0.0.1:8000/upload-documents" \
  -F "company_name=Shakti Steel Pvt Ltd" \
  -F "sector=manufacturing" \
  -F "files=@sample_data/annual_report_1.txt" \
  -F "files=@sample_data/bank_statement.csv"
```

### Run Analysis
```bash
curl -X POST "http://127.0.0.1:8000/analyze-company" \
  -H "Content-Type: application/json" \
  -d '{"company_id":"comp-001"}'
```

### Get Risk Report
```bash
curl "http://127.0.0.1:8000/risk-report/comp-001"
```

### Submit Officer Input
```bash
curl -X POST "http://127.0.0.1:8000/submit-officer-input" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id":"comp-001",
    "factory_utilization_pct":68,
    "management_quality_notes":"Strong governance"
  }'
```

---

## Understanding ML Decisions

### Probability of Default (PD)
- **Model**: Random Forest Classifier
- **Inputs**: 8 financial and qualitative features
- **Output**: PD score (0-1) and risk class

**Risk Classes**:
- Very Low: PD < 5%
- Low: PD 5-15%
- Medium: PD 15-30%
- High: PD 30-50%
- Very High: PD > 50%

### Credit Limit Recommendation
- **Model**: Gradient Boosting Regressor
- **Range**: 50 lakhs to 50 crores
- **Factors**: Financial ratios, collateral, management quality

### Risk Premium Calculation
- **Base Rate**: 8% (configurable)
- **Premium**: 1-8% based on PD
- **Adjustments**: Collateral coverage, sector risk

**Example**:
```json
{
  "base_rate_pct": 8.0,
  "risk_premium_pct": 2.0,
  "total_rate_pct": 10.0,
  "rate_category": "Prime"
}
```

---

## Troubleshooting

### "AI modules not available"
**Cause**: Missing dependencies

**Fix**:
```bash
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
**Cause**: Environment not configured

**Fix**:
1. Create `.env` file: `cp .env.example .env`
2. Add your API key
3. Restart server

### Web crawling is slow
**Cause**: Network latency or rate limiting

**Fix**:
1. Adjust timeout in `.env`: `CRAWL_TIMEOUT=60`
2. Reduce pages: `MAX_CRAWL_PAGES=5`

### Databricks connection fails
**Cause**: Invalid credentials or network issue

**Fix**:
1. Verify credentials in `.env`
2. Test warehouse is running
3. Check firewall/VPN settings

### PDF generation fails
**Cause**: WeasyPrint dependencies missing

**Fix**:
```bash
# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu/Debian
sudo apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0

# Windows
# Download GTK+ runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

---

## Production Deployment

### Security Checklist
- [ ] Rotate API keys regularly
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Encrypt sensitive data at rest

### Performance Optimization
- [ ] Cache web crawl results (Redis)
- [ ] Batch document processing
- [ ] Use async workers (Celery)
- [ ] Load balance API servers
- [ ] Monitor ML model performance

### ML Model Retraining
1. Collect historical loan performance data
2. Prepare training dataset with features + outcomes
3. Retrain models:
   ```python
   from ai.ml_decisioning import CreditDecisionEngine
   engine = CreditDecisionEngine()
   # Add retraining logic with your data
   ```
4. Validate on holdout set
5. Deploy updated models

---

## Support

### Documentation
- API Docs: `http://127.0.0.1:8000/docs`
- README: `README.md`
- This guide: `SETUP_GUIDE.md`

### Common Issues
- Check logs in console output
- Review `storage/` directory for generated files
- Test with sample data first

### Getting Help
1. Review troubleshooting section
2. Check API documentation
3. Examine error messages in logs
4. Test individual components with `test_setup.py`

---

## Next Steps

### Immediate
1. ✅ Complete setup and run demo
2. ✅ Test with sample data
3. ✅ Review generated CAM reports

### Short-term
1. Configure Databricks integration
2. Add real company data
3. Customize risk scoring weights
4. Train ML models on historical data

### Long-term
1. Integrate credit bureau APIs
2. Add MCA data fetching
3. Implement portfolio monitoring
4. Build stress testing module
5. Add automated alerts

---

**Ready to start? Run `python test_setup.py` to verify your installation!**
