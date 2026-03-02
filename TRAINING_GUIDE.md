# ML Model Training Guide

## Train Models on Real Data

### Option 1: Command Line (Recommended)

```bash
# Activate environment
source .venv/bin/activate

# Train with your CSV file
python ai/train_models.py path/to/your_loan_history.csv

# Or generate sample data and train
python ai/train_models.py
```

### Option 2: API Endpoint

```bash
# Generate sample training data
curl -X POST "http://127.0.0.1:8000/generate-sample-data?n_samples=1000" \
  -o training_data.csv

# Upload and train
curl -X POST "http://127.0.0.1:8000/train-models" \
  -F "file=@training_data.csv"
```

### Option 3: Python Script

```python
from ai.train_models import ModelTrainer

trainer = ModelTrainer()
results = trainer.train_from_csv("your_data.csv")

print(f"PD Model AUC: {results['pd_auc']:.3f}")
print(f"Limit Model MAE: {results['limit_mae']:.2f} lakhs")
```

---

## Required CSV Format

Your CSV must have these columns:

### Features (8 columns):
- `current_ratio` - Current Assets / Current Liabilities
- `debt_to_equity` - Total Debt / Total Equity
- `interest_coverage` - EBIT / Interest Expense
- `roe` - Return on Equity (decimal, e.g., 0.15 for 15%)
- `operating_margin` - Operating Profit / Revenue (decimal)
- `revenue_growth` - YoY growth rate (decimal, e.g., 0.10 for 10%)
- `management_score` - Score from 1-10
- `sector_risk` - Risk factor 0-1 (0=low, 1=high)

### Targets (2 columns):
- `defaulted` - 0 (no default) or 1 (defaulted)
- `approved_limit_lakhs` - Credit limit in lakhs (50-5000)

### Example CSV:

```csv
current_ratio,debt_to_equity,interest_coverage,roe,operating_margin,revenue_growth,management_score,sector_risk,defaulted,approved_limit_lakhs
1.8,1.2,4.5,0.18,0.12,0.15,7.0,0.2,0,1250
1.2,2.8,2.1,0.08,0.06,0.05,5.0,0.5,1,450
2.5,0.8,8.2,0.25,0.18,0.22,9.0,0.1,0,2800
```

---

## Prepare Your Data

### From Databricks

```python
from ai.train_models import ModelTrainer

trainer = ModelTrainer()
results = trainer.train_from_databricks()
```

### From Excel

```python
import pandas as pd

# Load Excel
df = pd.read_excel("loan_history.xlsx")

# Calculate features if needed
df['current_ratio'] = df['current_assets'] / df['current_liabilities']
df['debt_to_equity'] = df['total_debt'] / df['total_equity']
# ... calculate other features

# Save as CSV
df.to_csv("training_data.csv", index=False)
```

### From Multiple Sources

```python
import pandas as pd

# Load from different sources
financials = pd.read_csv("financials.csv")
outcomes = pd.read_csv("loan_outcomes.csv")

# Merge
df = financials.merge(outcomes, on='loan_id')

# Save
df.to_csv("training_data.csv", index=False)
```

---

## Training Process

1. **Load Data**: Reads CSV and validates columns
2. **Split Data**: 80% training, 20% testing
3. **Train PD Model**: Random Forest for default prediction
4. **Train Limit Model**: Gradient Boosting for credit limits
5. **Evaluate**: Shows AUC, MAE, and feature importance
6. **Save Models**: Backs up old models, saves new ones

### Output Example:

```
Training on 1000 loans...
Default rate: 18.50%

Training PD model...
PD Model AUC: 0.847

Classification Report:
              precision    recall  f1-score   support
           0       0.89      0.94      0.91       163
           1       0.76      0.63      0.69        37

Training Credit Limit model...
Limit Model MAE: 87.34 lakhs

Feature Importance (PD Model):
  interest_coverage: 0.284
  debt_to_equity: 0.221
  roe: 0.178
  current_ratio: 0.142
  operating_margin: 0.098
  management_score: 0.047
  revenue_growth: 0.021
  sector_risk: 0.009

✓ Models saved to storage/models/
✓ Backups created with timestamp 20260302_104500
```

---

## After Training

1. **Restart Server**: New models load on startup
   ```bash
   # Stop server (Ctrl+C)
   uvicorn api.main:app --reload
   ```

2. **Test New Models**: Run analysis on test company

3. **Monitor Performance**: Track actual vs predicted defaults

---

## Best Practices

### Data Quality
- Minimum 500 loans (1000+ recommended)
- Include both defaults and non-defaults
- Recent data (last 2-3 years)
- Clean data (no extreme outliers)

### Feature Engineering
- Calculate ratios consistently
- Handle missing values (median imputation)
- Normalize extreme values
- Use domain knowledge for management scores

### Model Validation
- Check AUC > 0.75 for PD model
- Check MAE < 100 lakhs for limit model
- Review feature importance
- Test on holdout set

### Retraining Schedule
- **Monthly**: If high loan volume (>100/month)
- **Quarterly**: For moderate volume
- **Annually**: Minimum requirement
- **Ad-hoc**: After major economic changes

---

## Troubleshooting

### "Missing required columns"
Ensure CSV has all 10 required columns with exact names

### "No data returned"
Check CSV file path and format

### Low AUC score
- Need more training data
- Check data quality
- Review feature calculations

### High MAE
- Limit predictions too variable
- May need more features
- Check for outliers in approved_limit_lakhs

---

## Advanced: Custom Features

Edit `ai/ml_decisioning.py` to add features:

```python
def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
    feature_vector = [
        features.get('current_ratio', 1.5),
        features.get('debt_to_equity', 1.0),
        # ... existing features
        features.get('your_new_feature', 0.0),  # Add here
    ]
    return np.array(feature_vector).reshape(1, -1)
```

Then retrain with CSV including the new column.

---

## Quick Start

```bash
# Generate sample data and train
python ai/train_models.py

# Or with your data
python ai/train_models.py your_loan_history.csv

# Restart server
uvicorn api.main:app --reload
```

Models are now trained on real data and ready to use!
