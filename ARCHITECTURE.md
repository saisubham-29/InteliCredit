# INTELLI-CREDIT System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Web Dashboard / API)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Upload     │  │   Analyze    │  │   Download   │         │
│  │  Documents   │  │   Company    │  │     CAM      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│                      (pipeline.py)                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Data Ingestion → 2. Parsing → 3. Analysis           │  │
│  │  4. Research → 5. ML Decision → 6. CAM Generation       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   DATA       │    │   AI/ML      │    │   OUTPUT     │
│   SOURCES    │    │   ENGINES    │    │  GENERATION  │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Detailed Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Uploaded   │  │  Databricks  │  │  Web Crawler │         │
│  │  Documents   │  │  Connector   │  │   (Live)     │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • PDFs       │  │ • Financials │  │ • News       │         │
│  │ • CSVs       │  │ • Credit     │  │ • Sector     │         │
│  │ • Text       │  │   Bureau     │  │   Trends     │         │
│  │              │  │ • GST Data   │  │ • Risk       │         │
│  │              │  │ • Legal      │  │   Signals    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Document Parser                             │  │
│  │  • PDF text extraction                                   │  │
│  │  • OCR (optional)                                        │  │
│  │  • Field extraction with confidence                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Financial Analyzer                             │  │
│  │  • Ratio calculation                                     │  │
│  │  • Trend analysis                                        │  │
│  │  • Missing data detection                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Research Agent                                │  │
│  │  • Web crawling (DuckDuckGo)                             │  │
│  │  • Sentiment analysis                                    │  │
│  │  • Risk keyword detection                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Gemini AI Client                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Company Profile Analysis                          │  │  │
│  │  │  • Management quality (1-10)                       │  │  │
│  │  │  • Business model viability                        │  │  │
│  │  │  • Market position assessment                      │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Financial Ratio Analysis                          │  │  │
│  │  │  • Health score                                    │  │  │
│  │  │  • Liquidity assessment                            │  │  │
│  │  │  • Leverage risk evaluation                        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Sector Outlook Generation                         │  │  │
│  │  │  • Trends analysis                                 │  │  │
│  │  │  • Growth prospects                                │  │  │
│  │  │  • Risk factors                                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         ML Credit Decision Engine                        │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  PD Model (Random Forest)                          │  │  │
│  │  │  Input: 8 features                                 │  │  │
│  │  │  Output: PD (0-1) + Risk Class                     │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Limit Model (Gradient Boosting)                   │  │  │
│  │  │  Input: 8 features                                 │  │  │
│  │  │  Output: Recommended limit (50L-50Cr)              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Risk Premium Calculator                           │  │  │
│  │  │  Input: PD + Collateral + Sector                   │  │  │
│  │  │  Output: Total rate (8-16%)                        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Decision Logic                                    │  │  │
│  │  │  Output: APPROVE / APPROVE_WITH_CONDITIONS /       │  │  │
│  │  │          APPROVE_LOWER_LIMIT / DECLINE             │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RISK ASSESSMENT LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Five-Cs Scoring Engine                      │  │
│  │  ┌────────────┬────────────┬────────────┬──────────┐    │  │
│  │  │ Character  │  Capacity  │  Capital   │Collateral│    │  │
│  │  │  (0-20)    │   (0-30)   │   (0-25)   │  (0-15)  │    │  │
│  │  └────────────┴────────────┴────────────┴──────────┘    │  │
│  │  ┌────────────┐                                          │  │
│  │  │ Conditions │  Total Score: 0-100                      │  │
│  │  │   (0-10)   │  Risk Band: Low/Moderate/High/Very High  │  │
│  │  └────────────┘                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Officer Input Adjuster                         │  │
│  │  • Factory utilization adjustments                       │  │
│  │  • Management quality notes                              │  │
│  │  • Site visit observations                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              CAM Generator                               │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  JSON CAM                                          │  │  │
│  │  │  • Complete structured data                        │  │  │
│  │  │  • Evidence chain                                  │  │  │
│  │  │  • ML decision details                             │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  PDF CAM (via WeasyPrint)                          │  │  │
│  │  │  • Professional formatting                         │  │  │
│  │  │  • Charts and tables                               │  │  │
│  │  │  • Executive summary                               │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────┐
│   Upload    │
│  Documents  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Ingestion                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   PDFs   │  │   CSVs   │  │Databricks│             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       └─────────────┼─────────────┘                    │
└─────────────────────┼──────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Document Parsing                           │
│  • Text extraction                                      │
│  • Field identification                                 │
│  • Confidence scoring                                   │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Financial   │ │   Research   │ │   Company    │
│   Analysis   │ │    Agent     │ │   Profile    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                ▼                │
       │         ┌──────────────┐        │
       │         │ Web Crawler  │        │
       │         │ (Live News)  │        │
       │         └──────┬───────┘        │
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Gemini AI      │
              │   Analysis       │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Feature         │
              │  Engineering     │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  ML Decision     │
              │  Engine          │
              ├──────────────────┤
              │ • PD Model       │
              │ • Limit Model    │
              │ • Pricing        │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Five-Cs         │
              │  Scoring         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Officer         │
              │  Adjustments     │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Risk Report     │
              │  Generation      │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  CAM Generation  │
              │  (JSON + PDF)    │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   Download       │
              │   CAM Report     │
              └──────────────────┘
```

## ML Model Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT FEATURES (8)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Financial Ratios (5)          Qualitative (3)                 │
│  ┌──────────────────┐          ┌──────────────────┐           │
│  │ • Current Ratio  │          │ • Management     │           │
│  │ • Debt/Equity    │          │   Score (AI)     │           │
│  │ • Interest Cov.  │          │ • Sector Risk    │           │
│  │ • ROE            │          │ • Collateral     │           │
│  │ • Operating Mgn  │          │   Coverage       │           │
│  │ • Revenue Growth │          │                  │           │
│  └──────────────────┘          └──────────────────┘           │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PD Model    │    │ Limit Model  │    │   Pricing    │
│  (RF 100)    │    │  (GBR 100)   │    │  Calculator  │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ Input: 8     │    │ Input: 8     │    │ Input: PD +  │
│ Output: PD   │    │ Output: Amt  │    │   Features   │
│   + Class    │    │   + Decision │    │ Output: Rate │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Decision Logic   │
                  ├──────────────────┤
                  │ • PD > 50%?      │
                  │ • Limit OK?      │
                  │ • Leverage OK?   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Final Decision   │
                  ├──────────────────┤
                  │ • APPROVE        │
                  │ • APPROVE_COND   │
                  │ • APPROVE_LOWER  │
                  │ • DECLINE        │
                  └──────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  Gemini API      │  │  DuckDuckGo      │                   │
│  │  (Google)        │  │  Search          │                   │
│  ├──────────────────┤  ├──────────────────┤                   │
│  │ • Company        │  │ • News articles  │                   │
│  │   analysis       │  │ • Sector trends  │                   │
│  │ • Financial      │  │ • Risk signals   │                   │
│  │   insights       │  │                  │                   │
│  │ • Sector outlook │  │                  │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  Databricks      │  │  Future: Credit  │                   │
│  │  (Optional)      │  │  Bureau APIs     │                   │
│  ├──────────────────┤  ├──────────────────┤                   │
│  │ • Financials     │  │ • CIBIL          │                   │
│  │ • Credit bureau  │  │ • Experian       │                   │
│  │ • GST data       │  │ • Equifax        │                   │
│  │ • Legal cases    │  │ • CRIF           │                   │
│  │ • Banking txns   │  │                  │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION SETUP                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Load Balancer                         │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         │                 │                 │                  │
│         ▼                 ▼                 ▼                  │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐            │
│  │ FastAPI  │      │ FastAPI  │      │ FastAPI  │            │
│  │ Server 1 │      │ Server 2 │      │ Server 3 │            │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘            │
│       └─────────────────┼─────────────────┘                   │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Shared Storage                         │ │
│  │  • ML Models (storage/models/)                           │ │
│  │  • CAM Reports (storage/cam/)                            │ │
│  │  • Uploaded Docs (storage/uploads/)                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                External Services                         │ │
│  │  • Gemini API                                            │ │
│  │  • Databricks                                            │ │
│  │  • Web Crawling                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: Authentication & Authorization                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • API key validation                                     │  │
│  │ • Role-based access control (future)                     │  │
│  │ • Session management                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Layer 2: Data Protection                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Environment variable encryption                        │  │
│  │ • Secure credential storage                              │  │
│  │ • TLS/HTTPS for all external calls                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Layer 3: Input Validation                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • File type validation                                   │  │
│  │ • Size limits                                            │  │
│  │ • SQL injection prevention                               │  │
│  │ • XSS protection                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Layer 4: Audit & Logging                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Complete decision trail                                │  │
│  │ • User action logging                                    │  │
│  │ • Error tracking                                         │  │
│  │ • Performance monitoring                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ML**: scikit-learn (Random Forest, Gradient Boosting)
- **AI**: Google Gemini API
- **Web Scraping**: BeautifulSoup4, aiohttp
- **PDF**: WeasyPrint, pypdf
- **Data**: pandas, numpy

### External Services
- **LLM**: Google Gemini Pro
- **Search**: DuckDuckGo HTML
- **Data Warehouse**: Databricks (optional)

### Storage
- **Local**: File system (storage/)
- **Models**: Pickle files
- **Documents**: PDF, CSV, TXT
- **Reports**: JSON, PDF

### Frontend
- **UI**: HTML, CSS, JavaScript
- **API Docs**: FastAPI auto-generated (Swagger)

---

## Scalability Considerations

### Horizontal Scaling
- Multiple FastAPI instances behind load balancer
- Shared storage for models and reports
- Stateless API design

### Vertical Scaling
- ML model optimization
- Async processing for web crawling
- Caching for repeated analyses

### Performance Optimization
- Model pre-loading at startup
- Connection pooling for Databricks
- Rate limiting for external APIs
- Result caching (Redis future)

---

**For detailed implementation, see the code in respective modules.**
