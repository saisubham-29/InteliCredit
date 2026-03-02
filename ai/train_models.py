"""
ML Model Training Module - Train on real historical loan data
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, mean_absolute_error, classification_report
import pickle
import os
from datetime import datetime

class ModelTrainer:
    def __init__(self):
        self.pd_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.limit_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model_path = "storage/models"
        os.makedirs(self.model_path, exist_ok=True)
    
    def train_from_csv(self, csv_path: str):
        """
        Train models from CSV file with historical loan data
        
        CSV should have columns:
        - current_ratio, debt_to_equity, interest_coverage, roe, operating_margin
        - revenue_growth, management_score, sector_risk
        - defaulted (0/1) - target for PD model
        - approved_limit_lakhs - target for limit model
        """
        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        required_features = ['current_ratio', 'debt_to_equity', 'interest_coverage', 
                           'roe', 'operating_margin', 'revenue_growth', 
                           'management_score', 'sector_risk']
        required_targets = ['defaulted', 'approved_limit_lakhs']
        
        missing = [col for col in required_features + required_targets if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Prepare features
        X = df[required_features].fillna(df[required_features].median())
        y_pd = df['defaulted']
        y_limit = df['approved_limit_lakhs']
        
        print(f"Training on {len(df)} loans...")
        print(f"Default rate: {y_pd.mean()*100:.2f}%")
        
        # Train-test split
        X_train, X_test, y_pd_train, y_pd_test, y_limit_train, y_limit_test = train_test_split(
            X, y_pd, y_limit, test_size=0.2, random_state=42
        )
        
        # Train PD model
        print("\nTraining PD model...")
        self.pd_model.fit(X_train, y_pd_train)
        
        # Evaluate PD model
        y_pred_proba = self.pd_model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_pd_test, y_pred_proba)
        print(f"PD Model AUC: {auc:.3f}")
        
        y_pred = self.pd_model.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_pd_test, y_pred))
        
        # Train Limit model
        print("\nTraining Credit Limit model...")
        self.limit_model.fit(X_train, y_limit_train)
        
        # Evaluate Limit model
        y_pred_limit = self.limit_model.predict(X_test)
        mae = mean_absolute_error(y_limit_test, y_pred_limit)
        print(f"Limit Model MAE: {mae:.2f} lakhs")
        
        # Feature importance
        print("\nFeature Importance (PD Model):")
        for feat, imp in sorted(zip(required_features, self.pd_model.feature_importances_), 
                               key=lambda x: x[1], reverse=True):
            print(f"  {feat}: {imp:.3f}")
        
        # Save models
        self.save_models()
        
        return {
            'pd_auc': auc,
            'limit_mae': mae,
            'samples': len(df),
            'default_rate': y_pd.mean()
        }
    
    def train_from_databricks(self, query: str = None):
        """Train models from Databricks historical data"""
        from ai.databricks_connector import DatabricksConnector
        
        connector = DatabricksConnector()
        if not connector.enabled:
            raise ValueError("Databricks not configured")
        
        if query is None:
            query = """
            SELECT 
                current_ratio, debt_to_equity, interest_coverage, roe, 
                operating_margin, revenue_growth, management_score, sector_risk,
                defaulted, approved_limit_lakhs
            FROM loan_history
            WHERE loan_date >= DATE_SUB(CURRENT_DATE(), 730)
            """
        
        print("Fetching data from Databricks...")
        results = connector.execute_query(query)
        
        if not results:
            raise ValueError("No data returned from Databricks")
        
        df = pd.DataFrame(results)
        
        # Save to temp CSV and use existing training logic
        temp_path = "storage/temp_training_data.csv"
        df.to_csv(temp_path, index=False)
        
        return self.train_from_csv(temp_path)
    
    def save_models(self):
        """Save trained models to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        pd_path = f"{self.model_path}/pd_model.pkl"
        limit_path = f"{self.model_path}/limit_model.pkl"
        
        # Backup existing models
        if os.path.exists(pd_path):
            os.rename(pd_path, f"{self.model_path}/pd_model_backup_{timestamp}.pkl")
        if os.path.exists(limit_path):
            os.rename(limit_path, f"{self.model_path}/limit_model_backup_{timestamp}.pkl")
        
        # Save new models
        with open(pd_path, 'wb') as f:
            pickle.dump(self.pd_model, f)
        with open(limit_path, 'wb') as f:
            pickle.dump(self.limit_model, f)
        
        print(f"\n✓ Models saved to {self.model_path}/")
        print(f"✓ Backups created with timestamp {timestamp}")


def create_sample_training_data(output_path: str = "storage/sample_training_data.csv", n_samples: int = 500):
    """
    Create sample training data CSV for demonstration
    Replace this with your actual historical loan data
    """
    np.random.seed(42)
    
    data = {
        'current_ratio': np.random.uniform(0.5, 3.0, n_samples),
        'debt_to_equity': np.random.uniform(0.2, 4.0, n_samples),
        'interest_coverage': np.random.uniform(0.5, 10.0, n_samples),
        'roe': np.random.uniform(-0.1, 0.4, n_samples),
        'operating_margin': np.random.uniform(-0.05, 0.3, n_samples),
        'revenue_growth': np.random.uniform(-0.2, 0.5, n_samples),
        'management_score': np.random.uniform(1, 10, n_samples),
        'sector_risk': np.random.uniform(0, 1, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate realistic default labels
    default_score = (
        -df['interest_coverage'] * 0.3 +
        df['debt_to_equity'] * 0.4 +
        df['sector_risk'] * 0.3 +
        np.random.randn(n_samples) * 0.5
    )
    df['defaulted'] = (default_score > 0.5).astype(int)
    
    # Generate realistic credit limits
    df['approved_limit_lakhs'] = np.clip(
        500 + 
        df['current_ratio'] * 200 + 
        df['roe'] * 1000 - 
        df['debt_to_equity'] * 150 +
        df['management_score'] * 50 +
        np.random.randn(n_samples) * 100,
        50, 5000
    )
    
    df.to_csv(output_path, index=False)
    print(f"Sample training data created: {output_path}")
    print(f"Samples: {n_samples}, Default rate: {df['defaulted'].mean()*100:.1f}%")
    
    return output_path


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("INTELLI-CREDIT ML Model Training")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Train from provided CSV
        csv_path = sys.argv[1]
        print(f"\nTraining from: {csv_path}")
    else:
        # Create and use sample data
        print("\nNo CSV provided. Creating sample training data...")
        csv_path = create_sample_training_data(n_samples=1000)
    
    # Train models
    trainer = ModelTrainer()
    results = trainer.train_from_csv(csv_path)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"PD Model AUC: {results['pd_auc']:.3f}")
    print(f"Limit Model MAE: {results['limit_mae']:.2f} lakhs")
    print(f"Training samples: {results['samples']}")
    print(f"Default rate: {results['default_rate']*100:.2f}%")
    print("\nModels saved and ready to use!")
    print("Restart the API server to load new models.")
