# Test Data Guide

## 📁 Test Data Files

All test data is in the `test_data/` directory:

### 1. Shakti Steel Private Limited (Complete Company Profile)

**Company Details:**
- Name: Shakti Steel Private Limited
- Sector: Manufacturing (Steel)
- Location: Pune, Maharashtra
- GSTIN: 27AABCS1234F1Z5
- Revenue: ₹245.50 Crores
- Loan Requested: ₹15 Crores

**Files:**
- `shakti_steel_annual_report.txt` - Complete financial statements
- `shakti_steel_bank_statement.csv` - 3 months banking transactions
- `shakti_steel_gst_data.csv` - 12 months GST filings
- `shakti_steel_legal_notice.txt` - Labor dispute case details

---

## 🚀 Quick Test Flow

### Step 1: Upload Documents

```bash
# Via UI
1. Go to http://127.0.0.1:8000
2. Click "Upload" tab
3. Fill form:
   - Company Name: Shakti Steel Private Limited
   - Sector: manufacturing
4. Upload all 4 files from test_data/
5. Click "Upload Documents"
```

```bash
# Via API
curl -X POST "http://127.0.0.1:8000/upload-documents" \
  -F "company_name=Shakti Steel Private Limited" \
  -F "sector=manufacturing" \
  -F "files=@test_data/shakti_steel_annual_report.txt" \
  -F "files=@test_data/shakti_steel_bank_statement.csv" \
  -F "files=@test_data/shakti_steel_gst_data.csv" \
  -F "files=@test_data/shakti_steel_legal_notice.txt"
```

### Step 2: Run Analysis

```bash
# Via UI
1. Go to "Analysis" tab
2. Select "Shakti Steel Private Limited"
3. Click "Run Analysis"
4. Wait 30-60 seconds
```

```bash
# Via API
curl -X POST "http://127.0.0.1:8000/analyze-company" \
  -H "Content-Type: application/json" \
  -d '{"company_id":"comp-001"}'
```

### Step 3: Review Results

**Expected ML Decision:**
- Decision: APPROVE
- PD: ~8-12% (Low Risk)
- Recommended Limit: ₹12-15 Cr
- Interest Rate: ~10-11%
- Risk Class: Low

**Key Metrics:**
- Current Ratio: 1.84 ✅
- Debt-to-Equity: 0.70 ✅
- Interest Coverage: 4.14 ✅
- ROE: 13.89% ✅
- Operating Margin: 14.34% ✅

**Five Cs Scores:**
- Character: High (strong management, no fraud)
- Capacity: High (good ratios, profitable)
- Capital: Good (positive equity, low leverage)
- Collateral: Adequate (assets > loan)
- Conditions: Favorable (sector stable, one minor legal case)

### Step 4: Explore Research

**Research Tab will show:**
- 15+ news articles about steel sector
- Sentiment analysis (mostly positive/neutral)
- Risk indicators: 1 (labor dispute)
- Positive signals: Export growth, capacity expansion
- Sector outlook: Stable to positive

**Click on news sources** to verify authenticity

### Step 5: Check Explainability

**Explainability Tab shows:**
- Why APPROVE decision was made
- ML features used (all 8 ratios)
- PD calculation breakdown
- Risk premium justification
- Lending conditions

### Step 6: Download CAM

**CAM Tab:**
- Click "Download CAM PDF"
- Professional report with all details
- Evidence chain included
- Ready for credit committee

---

## 🎯 Expected Analysis Results

### Financial Health
```
✅ Strong Liquidity (CR: 1.84)
✅ Manageable Leverage (D/E: 0.70)
✅ Good Debt Servicing (IC: 4.14)
✅ Profitable Operations (ROE: 13.89%)
✅ Healthy Margins (OM: 14.34%)
```

### Risk Assessment
```
✅ No fraud indicators
✅ Clean credit history
✅ Consistent GST filings
✅ Positive cash flows
⚠️ One minor labor dispute (₹12L)
```

### ML Decision
```
Decision: APPROVE
Confidence: 85%+
PD: 8-12% (Low Risk)
Limit: ₹12-15 Cr
Rate: 10-11% (Prime category)
```

### Conditions
```
1. Quarterly financial monitoring
2. Maintain current ratio > 1.2x
3. Standard terms and conditions
```

---

## 🧪 Additional Test Scenarios

### Test 2: Train ML Models

```bash
# Train on sample data
python ai/train_models.py test_data/training_data_sample.csv

# Expected output:
# PD Model AUC: ~0.85
# Limit Model MAE: ~80-100 lakhs
# 25 training samples
```

### Test 3: Officer Inputs

```bash
# Via UI
1. Go to Analysis tab
2. After analysis, add officer inputs:
   - Factory Utilization: 72%
   - Management Quality: "Strong leadership, experienced team"
   - Site Visit: "Clean facility, good safety practices"
3. Re-run analysis
4. See adjusted scores
```

```bash
# Via API
curl -X POST "http://127.0.0.1:8000/submit-officer-input" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id":"comp-001",
    "factory_utilization_pct":72,
    "management_quality_notes":"Strong leadership with 25 years experience",
    "site_visit_observations":"Well-maintained facility, good safety standards"
  }'
```

### Test 4: Research Details

```bash
# Get detailed research
curl "http://127.0.0.1:8000/research-details/comp-001"

# Expected: JSON with news articles, sources, sentiment
```

### Test 5: Explainability

```bash
# Get decision explainability
curl "http://127.0.0.1:8000/explainability/comp-001"

# Expected: Complete decision breakdown
```

---

## 📊 Test Data Characteristics

### Shakti Steel Profile

**Strengths:**
- ✅ Profitable (₹18.75 Cr net profit)
- ✅ Growing (18% YoY revenue growth)
- ✅ Export-oriented (25% revenue)
- ✅ Strong management (experienced board)
- ✅ Clean auditor opinion
- ✅ Consistent GST compliance

**Weaknesses:**
- ⚠️ One labor dispute (minor, ₹12L)
- ⚠️ Capacity utilization 72% (room for improvement)

**Neutral:**
- Moderate leverage (0.70 D/E)
- Standard working capital needs
- Typical manufacturing sector risks

---

## 🎬 Demo Script

### For Hackathon Judges

**1. Introduction (1 min)**
"Intelli-Credit automates credit appraisal for Indian corporates using AI, ML, and live web research."

**2. Upload Demo (1 min)**
- Show multi-format upload
- Mention: "Handles PDFs, CSVs, scanned documents"

**3. Analysis Demo (2 min)**
- Run analysis on Shakti Steel
- Show ML decision: "APPROVE at ₹12.5 Cr, 10% rate"
- Highlight: "30 seconds vs 2 weeks manual process"

**4. Research Tab (2 min)**
- Show 15+ news articles with sources
- Click through to original source
- Highlight: "Live web crawling, not mock data"

**5. Explainability (2 min)**
- Show decision breakdown
- Explain: "Every decision fully justified"
- Show ML features used
- Highlight: "No black box"

**6. CAM Download (1 min)**
- Download PDF
- Show professional format
- Mention: "Ready for credit committee"

**7. Unique Features (1 min)**
- Dynamic ML training
- Indian context (GST, Five Cs)
- Production-ready code
- Complete audit trail

**Total: 10 minutes**

---

## 🔍 Validation Checklist

After running test:

### Data Ingestion ✅
- [ ] All 4 files uploaded successfully
- [ ] Financial data extracted correctly
- [ ] GST data parsed properly
- [ ] Legal notice identified

### Analysis ✅
- [ ] ML decision generated
- [ ] PD calculated (8-12%)
- [ ] Credit limit recommended (₹12-15 Cr)
- [ ] Interest rate calculated (~10%)
- [ ] Five Cs scored

### Research ✅
- [ ] News articles found (15+)
- [ ] Sources clickable
- [ ] Sentiment analyzed
- [ ] Risk keywords detected
- [ ] Sector outlook generated

### Explainability ✅
- [ ] Decision reason shown
- [ ] ML features displayed
- [ ] Conditions listed
- [ ] Evidence chain complete

### CAM ✅
- [ ] PDF generated
- [ ] All sections included
- [ ] Professional format
- [ ] Downloadable

---

## 🐛 Troubleshooting

### No news articles found
- Check internet connection
- Gemini API key configured?
- Wait longer (web crawling takes 15-30s)

### ML decision not showing
- Check if analysis completed
- Look for errors in console
- Verify all dependencies installed

### PDF download fails
- WeasyPrint installed?
- Check storage/cam/ directory
- HTML version available as fallback

---

## 📞 Support

If test fails:
1. Check server logs
2. Verify .env configuration
3. Ensure all dependencies installed
4. Try with sample_data/ files first

---

**Ready to test? Start with Step 1! 🚀**
