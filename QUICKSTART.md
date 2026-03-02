# 🚀 INTELLI-CREDIT Quick Start

## One-Command Setup

```bash
./quickstart.sh
```

This will:
1. ✅ Create virtual environment
2. ✅ Install all dependencies
3. ✅ Create .env configuration file
4. ✅ Set up storage directories
5. ✅ Run system tests
6. ✅ Start the server

## Manual Setup (3 Steps)

### Step 1: Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get your Gemini API key: https://makersuite.google.com/app/apikey

### Step 3: Run
```bash
uvicorn api.main:app --reload
```

Open: http://127.0.0.1:8000

---

## What You Get

### 🤖 AI-Powered Analysis
- **Gemini AI**: Intelligent company and financial analysis
- **Web Crawler**: Live news and sector research
- **ML Models**: Automated credit decisioning

### 📊 Credit Decisioning
- **PD Calculation**: Probability of Default modeling
- **Credit Limits**: ML-based limit recommendations (50L - 50Cr)
- **Risk Pricing**: Automated premium calculation (1-8%)
- **Final Decision**: Approve/Conditional/Decline with reasoning

### 📄 CAM Generation
- **Professional Reports**: PDF and JSON formats
- **Evidence-Based**: Complete audit trail
- **Explainable**: Transparent scoring and decisions

---

## Demo Walkthrough (5 Minutes)

### 1. Upload Documents
Navigate to http://127.0.0.1:8000

Upload sample files:
- `sample_data/annual_report_1.txt`
- `sample_data/bank_statement.csv`
- `sample_data/gst_data.csv`

### 2. Run Analysis
- Select company: "Shakti Steel Pvt Ltd"
- Click "Run Analysis"
- Wait 30-60 seconds for AI processing

### 3. Review Results
You'll see:
- ✅ Financial ratios and trends
- ✅ AI-generated insights
- ✅ Live news and sentiment
- ✅ ML credit decision
- ✅ Risk scoring breakdown
- ✅ Lending recommendation

### 4. Download CAM
Click "Download CAM PDF" for the complete credit memo

---

## Operating Modes

### 🌟 Enhanced Mode (Recommended)
**Requires**: Gemini API key

**Features**:
- ✅ Live web crawling
- ✅ AI-powered analysis
- ✅ ML-based decisioning
- ✅ Real-time news
- ✅ Automated pricing

**Setup**: Add `GEMINI_API_KEY` to `.env`

### 📦 Basic Mode (Fallback)
**Requires**: Nothing

**Features**:
- ✅ Document parsing
- ✅ Financial analysis
- ✅ Five-Cs scoring
- ✅ CAM generation
- ⚠️ Synthetic research data
- ⚠️ Rule-based decisions

**Setup**: Works out of the box

---

## API Quick Reference

### Upload Documents
```bash
curl -X POST "http://127.0.0.1:8000/upload-documents" \
  -F "company_name=Shakti Steel Pvt Ltd" \
  -F "sector=manufacturing" \
  -F "files=@sample_data/annual_report_1.txt"
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

### Download CAM
```bash
curl -O "http://127.0.0.1:8000/download-cam/comp-001"
```

Full API docs: http://127.0.0.1:8000/docs

---

## ML Decision Example

```json
{
  "final_decision": "APPROVE",
  "probability_of_default": 0.0823,
  "risk_class": "Low",
  "recommended_limit": {
    "recommended_limit_cr": 12.5,
    "confidence": 0.85
  },
  "pricing": {
    "base_rate_pct": 8.0,
    "risk_premium_pct": 2.0,
    "total_rate_pct": 10.0
  },
  "conditions": [
    "Quarterly financial monitoring required"
  ]
}
```

---

## Troubleshooting

### "AI modules not available"
```bash
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
1. Create `.env`: `cp .env.example .env`
2. Add your API key
3. Restart server

### Web crawling is slow
Edit `.env`:
```bash
CRAWL_TIMEOUT=60
MAX_CRAWL_PAGES=5
```

### PDF generation fails
Install system dependencies:

**macOS**:
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Ubuntu/Debian**:
```bash
sudo apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
```

---

## Documentation

- 📖 **Full README**: `README.md`
- 🛠️ **Setup Guide**: `SETUP_GUIDE.md`
- 🤖 **ML Reference**: `ML_REFERENCE.md`
- 🏗️ **Architecture**: `ARCHITECTURE.md`
- 📝 **Enhancement Summary**: `ENHANCEMENT_SUMMARY.md`

---

## Next Steps

### Immediate
1. ✅ Complete setup
2. ✅ Test with sample data
3. ✅ Review generated CAM

### Short-term
1. Configure Databricks (optional)
2. Add real company data
3. Train ML models on historical data

### Long-term
1. Integrate credit bureau APIs
2. Add portfolio monitoring
3. Implement stress testing

---

## Support

### Test Your Setup
```bash
python test_setup.py
```

### Check Logs
Server logs show detailed error messages

### API Documentation
http://127.0.0.1:8000/docs

### File Issues
Review documentation or check console logs

---

## Key Features

✅ **Multi-source Data**: PDFs, CSVs, Databricks
✅ **Live Research**: Real-time web crawling
✅ **AI Analysis**: Gemini-powered insights
✅ **ML Decisioning**: PD modeling + limit calculation
✅ **Risk Scoring**: Explainable Five-Cs framework
✅ **CAM Generation**: Professional PDF reports
✅ **Audit Trail**: Complete evidence chain
✅ **Transparency**: Confidence scores + justifications

---

## System Requirements

- **Python**: 3.9 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 500MB for dependencies
- **Network**: Required for enhanced mode
- **API Key**: Gemini API (free tier available)

---

## Quick Commands

```bash
# Setup
./quickstart.sh

# Or manually
source .venv/bin/activate
uvicorn api.main:app --reload

# Test
python test_setup.py

# Stop server
Ctrl + C
```

---

**Ready to start? Run `./quickstart.sh` now!** 🚀
