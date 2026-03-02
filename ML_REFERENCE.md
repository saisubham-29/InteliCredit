# ML Decisioning Engine - Technical Reference

## Overview
The ML-based credit decisioning engine automates lending decisions using machine learning models trained on financial and qualitative features.

## Models

### 1. Probability of Default (PD) Model
**Type**: Random Forest Classifier (100 estimators)

**Input Features** (8):
1. `current_ratio` - Current Assets / Current Liabilities
2. `debt_to_equity` - Total Debt / Total Equity
3. `interest_coverage` - EBIT / Interest Expense
4. `roe` - Return on Equity (Net Income / Equity)
5. `operating_margin` - Operating Profit / Revenue
6. `revenue_growth` - YoY revenue growth rate
7. `management_score` - AI-generated score (1-10)
8. `sector_risk` - Sector-specific risk factor (0-1)

**Output**:
- PD probability (0-1)
- Risk classification (Very Low / Low / Medium / High / Very High)

**Risk Thresholds**:
```python
PD < 0.05  → Very Low Risk
PD < 0.15  → Low Risk
PD < 0.30  → Medium Risk
PD < 0.50  → High Risk
PD >= 0.50 → Very High Risk
```

### 2. Credit Limit Model
**Type**: Gradient Boosting Regressor (100 estimators)

**Input Features**: Same 8 features as PD model

**Output**:
- Recommended credit limit (in lakhs)
- Range: 50 lakhs to 5,000 lakhs (50 Cr)

**Business Rules**:
- If requested ≤ recommended → APPROVE
- If requested ≤ 1.2 × recommended → APPROVE_WITH_CONDITIONS
- If requested > 1.2 × recommended → REJECT (offer 70% of requested or recommended, whichever is lower)

### 3. Risk Premium Calculator
**Type**: Rule-based with ML inputs

**Formula**:
```
Total Rate = Base Rate + Risk Premium + Adjustments
```

**Risk Premium by PD**:
```python
PD < 0.05  → 1.0% premium
PD < 0.15  → 2.0% premium
PD < 0.30  → 3.5% premium
PD < 0.50  → 5.5% premium
PD >= 0.50 → 8.0% premium
```

**Collateral Adjustments**:
- Coverage > 1.5x → 20% reduction in premium
- Coverage < 0.8x → 30% increase in premium

**Sector Adjustments**:
- Configurable sector-specific risk premium (-1% to +2%)

## Feature Engineering

### From Financial Statements
```python
current_ratio = current_assets / current_liabilities
debt_to_equity = total_debt / total_equity
interest_coverage = ebit / interest_expense
roe = net_income / total_equity
operating_margin = operating_profit / revenue
revenue_growth = (current_revenue - prior_revenue) / prior_revenue
```

### From AI Analysis
```python
management_score = gemini_analysis['management_score']  # 1-10 scale
sector_risk = 0.3 if sector_outlook in ['Negative', 'Cautious'] else 0.1
```

### From Company Profile
```python
collateral_coverage = collateral_value / loan_requested
```

## Decision Logic

### Final Lending Decision
```python
if PD > 0.50:
    decision = "DECLINE"
    reason = "PD exceeds 50% threshold"

elif PD > 0.30 and debt_to_equity > 3.0:
    decision = "DECLINE"
    reason = "High PD + excessive leverage"

elif requested_limit > 1.2 × recommended_limit:
    decision = "APPROVE_LOWER_LIMIT"
    reason = "Requested exceeds risk appetite"

elif requested_limit > recommended_limit:
    decision = "APPROVE_WITH_CONDITIONS"
    reason = "Additional collateral required"

else:
    decision = "APPROVE"
    reason = "All parameters within limits"
```

### Lending Conditions
Automatically generated based on risk factors:

```python
if PD > 0.20:
    conditions.append("Quarterly financial monitoring")

if debt_to_equity > 2.0:
    conditions.append("Debt reduction plan required")

if current_ratio < 1.2:
    conditions.append("Maintain minimum current ratio 1.2x")

if interest_coverage < 2.0:
    conditions.append("Improve interest coverage to 2.0x")

if approved_with_conditions:
    conditions.append("Additional collateral coverage 1.5x")
```

## API Response Format

### Complete ML Decision
```json
{
  "final_decision": "APPROVE",
  "reason": "All risk parameters within acceptable limits",
  "probability_of_default": 0.0823,
  "risk_class": "Low",
  "recommended_limit": {
    "recommended_limit_lakhs": 1250.0,
    "recommended_limit_cr": 12.5,
    "min_limit_lakhs": 50.0,
    "max_limit_lakhs": 5000.0,
    "decision": "APPROVE",
    "confidence": 0.85
  },
  "pricing": {
    "base_rate_pct": 8.0,
    "risk_premium_pct": 2.0,
    "total_rate_pct": 10.0,
    "rate_category": "Prime",
    "justification": "PD-based premium for 8.2% default probability; reduced due to strong collateral coverage"
  },
  "conditions": [
    "Quarterly financial monitoring required",
    "Standard terms and conditions apply"
  ],
  "ml_confidence": 0.85
}
```

## Model Training

### Current Status
- Models initialized with synthetic data for demo
- Training data: 1,000 synthetic samples
- Features: 8 financial + qualitative variables

### Production Training
To train on real data:

```python
from ai.ml_decisioning import CreditDecisionEngine
import pandas as pd

# Load historical loan data
df = pd.read_csv('historical_loans.csv')

# Prepare features
X = df[['current_ratio', 'debt_to_equity', 'interest_coverage', 
        'roe', 'operating_margin', 'revenue_growth', 
        'management_score', 'sector_risk']]

# Prepare labels
y_pd = df['defaulted']  # 0 or 1
y_limit = df['approved_limit_lakhs']

# Train models
engine = CreditDecisionEngine()
engine.pd_model.fit(X, y_pd)
engine.limit_model.fit(X, y_limit)

# Save models
import pickle
with open('storage/models/pd_model.pkl', 'wb') as f:
    pickle.dump(engine.pd_model, f)
with open('storage/models/limit_model.pkl', 'wb') as f:
    pickle.dump(engine.limit_model, f)
```

### Required Training Data
Minimum 500 historical loans with:
- Financial ratios at origination
- Loan amount approved
- Default outcome (0/1) after 12-24 months
- Management quality scores
- Sector classifications

### Model Validation
```python
from sklearn.metrics import roc_auc_score, mean_absolute_error

# PD Model
y_pred_proba = engine.pd_model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)
print(f"PD Model AUC: {auc:.3f}")  # Target: > 0.75

# Limit Model
y_pred_limit = engine.limit_model.predict(X_test)
mae = mean_absolute_error(y_test_limit, y_pred_limit)
print(f"Limit Model MAE: {mae:.2f} lakhs")  # Target: < 100 lakhs
```

## Feature Importance

### Typical Feature Rankings (from synthetic data)
1. **interest_coverage** (25%) - Strong predictor of repayment ability
2. **debt_to_equity** (22%) - Leverage risk indicator
3. **roe** (18%) - Profitability signal
4. **current_ratio** (15%) - Liquidity measure
5. **operating_margin** (10%) - Operational efficiency
6. **management_score** (5%) - Qualitative factor
7. **revenue_growth** (3%) - Growth trajectory
8. **sector_risk** (2%) - Macro factor

*Note: Rankings will vary with real training data*

## Confidence Scores

### ML Confidence Calculation
```python
confidence = data_completeness × 0.85

data_completeness = (
    number_of_available_features / 
    total_required_features
)
```

**Interpretation**:
- > 0.80: High confidence, all key data available
- 0.60-0.80: Medium confidence, some data missing
- < 0.60: Low confidence, significant data gaps

## Explainability

### Model Transparency
- Feature importance scores available
- Decision rules documented
- Threshold values explicit
- Confidence scores provided

### Audit Trail
Every decision includes:
1. Input features used
2. Model predictions (PD, limit)
3. Business rules applied
4. Final decision rationale
5. Confidence assessment

## Performance Monitoring

### Key Metrics to Track
1. **PD Model Accuracy**: Compare predicted PD vs actual default rate
2. **Limit Model Error**: MAE between recommended and optimal limits
3. **Decision Override Rate**: % of ML decisions overridden by officers
4. **Portfolio Performance**: Track approved loans' actual performance

### Recommended Monitoring
```python
# Monthly review
- Default rate by risk class
- Average PD vs actual default rate
- Limit utilization patterns
- Pricing adequacy (spread vs losses)

# Quarterly review
- Model recalibration needs
- Feature importance changes
- Decision rule effectiveness
- Portfolio concentration risks
```

## Customization

### Adjusting Risk Thresholds
Edit `ai/ml_decisioning.py`:

```python
# More conservative
if pd < 0.03:  # was 0.05
    risk_class = "Very Low"

# More aggressive pricing
if pd < 0.15:
    risk_premium = 1.5  # was 2.0
```

### Sector-Specific Rules
```python
sector_adjustments = {
    'manufacturing': 0.0,
    'real_estate': 1.5,  # +1.5% premium
    'pharma': -0.5,      # -0.5% discount
    'infrastructure': 1.0
}
```

### Custom Conditions
```python
if company_profile.get('years_in_business', 0) < 3:
    conditions.append("Personal guarantee required for new businesses")

if financials.get('cash_flow_volatility', 0) > 0.3:
    conditions.append("Cash flow stabilization plan required")
```

## Integration Points

### With Gemini AI
```python
# Management score from AI analysis
ai_analysis = gemini.analyze_company_profile(...)
management_score = ai_analysis.get('management_score', 5.0)
```

### With Web Crawler
```python
# Sector risk from news sentiment
research = run_web_research(...)
sector_risk = 0.3 if research['overall_sentiment'] == 'negative' else 0.1
```

### With Databricks
```python
# Credit bureau score integration
credit_bureau = databricks.fetch_credit_bureau_data(...)
if credit_bureau['credit_score'] < 600:
    sector_risk += 0.2  # Increase risk
```

## Best Practices

### Data Quality
- Validate all input features
- Handle missing values appropriately
- Normalize features before prediction
- Check for outliers

### Model Governance
- Version control model files
- Document training data sources
- Track model performance metrics
- Schedule regular retraining

### Risk Management
- Set conservative thresholds initially
- Monitor early warning indicators
- Implement override mechanisms
- Maintain human oversight

---

**For questions or customization needs, refer to the code in `ai/ml_decisioning.py`**
