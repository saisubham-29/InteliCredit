"""
ML-based credit decisioning engine with PD model and limit calculation
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple, Optional, List
import pickle
import os

class CreditDecisionEngine:
    def __init__(self):
        self.pd_model = None  # Probability of Default model
        self.limit_model = None  # Credit Limit model
        self.scaler = StandardScaler()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load pre-trained models"""
        model_path = "storage/models"
        os.makedirs(model_path, exist_ok=True)
        
        pd_model_file = f"{model_path}/pd_model.pkl"
        limit_model_file = f"{model_path}/limit_model.pkl"
        
        if os.path.exists(pd_model_file) and os.path.exists(limit_model_file):
            try:
                with open(pd_model_file, 'rb') as f:
                    self.pd_model = pickle.load(f)
                with open(limit_model_file, 'rb') as f:
                    self.limit_model = pickle.load(f)
                return
            except:
                pass
        
        # Initialize with default models (will be trained with real data)
        self.pd_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.limit_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        # Train on synthetic data for demo purposes
        self._train_on_synthetic_data()
    
    def _train_on_synthetic_data(self):
        """Train models on synthetic data for demo"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [current_ratio, debt_to_equity, interest_coverage, roe, 
        #            operating_margin, revenue_growth, management_score, sector_risk]
        X = np.random.randn(n_samples, 8)
        
        # Synthetic PD labels (0=no default, 1=default)
        pd_score = (X[:, 1] * 0.3 - X[:, 2] * 0.4 - X[:, 3] * 0.2 + 
                   X[:, 7] * 0.3 + np.random.randn(n_samples) * 0.1)
        y_pd = (pd_score > 0).astype(int)
        
        # Synthetic credit limits (in lakhs)
        y_limit = np.clip(
            500 + X[:, 0] * 200 + X[:, 3] * 300 - X[:, 1] * 150 + 
            X[:, 6] * 100 + np.random.randn(n_samples) * 50,
            50, 5000
        )
        
        # Train models
        self.pd_model.fit(X, y_pd)
        self.limit_model.fit(X, y_limit)
        self.scaler.fit(X)
    
    def calculate_pd(self, features: Dict[str, float]) -> Tuple[float, str]:
        """Calculate Probability of Default"""
        X = self._prepare_features(features)
        
        if self.pd_model is None:
            return 0.15, "Medium"  # Default fallback
        
        try:
            # Get probability of default (class 1)
            pd_prob = self.pd_model.predict_proba(X)[0][1]
            
            # Classify risk
            if pd_prob < 0.05:
                risk_class = "Very Low"
            elif pd_prob < 0.15:
                risk_class = "Low"
            elif pd_prob < 0.30:
                risk_class = "Medium"
            elif pd_prob < 0.50:
                risk_class = "High"
            else:
                risk_class = "Very High"
            
            return float(pd_prob), risk_class
        except Exception as e:
            print(f"PD calculation failed: {e}")
            return 0.15, "Medium"
    
    def calculate_credit_limit(self, features: Dict[str, float], 
                              requested_limit: Optional[float] = None) -> Dict[str, object]:
        """Calculate recommended credit limit"""
        X = self._prepare_features(features)
        
        if self.limit_model is None:
            recommended = 500.0  # Default 5 Cr
        else:
            try:
                recommended = float(self.limit_model.predict(X)[0])
            except Exception as e:
                print(f"Limit calculation failed: {e}")
                recommended = 500.0
        
        # Apply business rules
        min_limit = 50.0  # 50 lakhs
        max_limit = 5000.0  # 50 Cr
        recommended = np.clip(recommended, min_limit, max_limit)
        
        # If requested limit provided, compare
        decision = "APPROVE"
        if requested_limit:
            if requested_limit <= recommended:
                decision = "APPROVE"
            elif requested_limit <= recommended * 1.2:
                decision = "APPROVE_WITH_CONDITIONS"
            else:
                decision = "REJECT"
                recommended = min(requested_limit * 0.7, recommended)
        
        return {
            'recommended_limit_lakhs': round(recommended, 2),
            'recommended_limit_cr': round(recommended / 100, 2),
            'min_limit_lakhs': round(min_limit, 2),
            'max_limit_lakhs': round(max_limit, 2),
            'decision': decision,
            'confidence': self._calculate_confidence(features)
        }
    
    def calculate_risk_premium(self, pd: float, features: Dict[str, float]) -> Dict[str, object]:
        """Calculate risk-adjusted interest rate premium"""
        # Base rate (assume 8% base rate for India)
        base_rate = 8.0
        
        # Risk premium based on PD
        if pd < 0.05:
            risk_premium = 1.0  # 1% premium
        elif pd < 0.15:
            risk_premium = 2.0  # 2% premium
        elif pd < 0.30:
            risk_premium = 3.5  # 3.5% premium
        elif pd < 0.50:
            risk_premium = 5.5  # 5.5% premium
        else:
            risk_premium = 8.0  # 8% premium (or decline)
        
        # Adjust for collateral
        collateral_coverage = features.get('collateral_coverage', 1.0)
        if collateral_coverage > 1.5:
            risk_premium *= 0.8  # 20% reduction
        elif collateral_coverage < 0.8:
            risk_premium *= 1.3  # 30% increase
        
        # Adjust for relationship and sector
        sector_adjustment = features.get('sector_risk_adjustment', 0.0)
        risk_premium += sector_adjustment
        
        total_rate = base_rate + risk_premium
        
        return {
            'base_rate_pct': base_rate,
            'risk_premium_pct': round(risk_premium, 2),
            'total_rate_pct': round(total_rate, 2),
            'rate_category': self._categorize_rate(total_rate),
            'justification': self._generate_rate_justification(pd, collateral_coverage, sector_adjustment)
        }
    
    def make_lending_decision(self, features: Dict[str, float], 
                             requested_limit: Optional[float] = None) -> Dict[str, object]:
        """Comprehensive lending decision"""
        # Calculate PD
        pd, risk_class = self.calculate_pd(features)
        
        # Calculate credit limit
        limit_decision = self.calculate_credit_limit(features, requested_limit)
        
        # Calculate risk premium
        pricing = self.calculate_risk_premium(pd, features)
        
        # Final decision logic
        if pd > 0.50:
            final_decision = "DECLINE"
            reason = "Probability of default exceeds acceptable threshold (>50%)"
        elif pd > 0.30 and features.get('debt_to_equity', 0) > 3.0:
            final_decision = "DECLINE"
            reason = "High default risk combined with excessive leverage"
        elif limit_decision['decision'] == "REJECT":
            final_decision = "APPROVE_LOWER_LIMIT"
            reason = f"Requested limit exceeds risk appetite. Recommend {limit_decision['recommended_limit_cr']} Cr"
        elif limit_decision['decision'] == "APPROVE_WITH_CONDITIONS":
            final_decision = "APPROVE_WITH_CONDITIONS"
            reason = "Approval subject to additional collateral or guarantees"
        else:
            final_decision = "APPROVE"
            reason = "All risk parameters within acceptable limits"
        
        return {
            'final_decision': final_decision,
            'reason': reason,
            'probability_of_default': round(pd, 4),
            'risk_class': risk_class,
            'recommended_limit': limit_decision,
            'pricing': pricing,
            'conditions': self._generate_conditions(pd, features, limit_decision),
            'ml_confidence': limit_decision['confidence']
        }
    
    def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare feature vector for ML models"""
        feature_vector = [
            features.get('current_ratio', 1.5),
            features.get('debt_to_equity', 1.0),
            features.get('interest_coverage', 3.0),
            features.get('roe', 0.15),
            features.get('operating_margin', 0.10),
            features.get('revenue_growth', 0.10),
            features.get('management_score', 5.0),
            features.get('sector_risk', 0.5)
        ]
        return np.array(feature_vector).reshape(1, -1)
    
    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence score for the decision"""
        # Based on data completeness and model certainty
        completeness = sum(1 for k in ['current_ratio', 'debt_to_equity', 'interest_coverage', 
                                       'roe', 'operating_margin'] if k in features) / 5.0
        return round(completeness * 0.85, 2)  # Max 85% confidence
    
    def _categorize_rate(self, rate: float) -> str:
        """Categorize interest rate"""
        if rate < 10:
            return "Prime"
        elif rate < 12:
            return "Standard"
        elif rate < 15:
            return "Sub-Standard"
        else:
            return "High-Risk"
    
    def _generate_rate_justification(self, pd: float, collateral: float, sector_adj: float) -> str:
        """Generate justification for the rate"""
        parts = [f"PD-based premium for {pd*100:.1f}% default probability"]
        if collateral > 1.5:
            parts.append("reduced due to strong collateral coverage")
        elif collateral < 0.8:
            parts.append("increased due to weak collateral")
        if sector_adj != 0:
            parts.append(f"sector adjustment of {sector_adj:+.1f}%")
        return "; ".join(parts)
    
    def _generate_conditions(self, pd: float, features: Dict, limit_decision: Dict) -> List[str]:
        """Generate lending conditions"""
        conditions = []
        
        if pd > 0.20:
            conditions.append("Quarterly financial monitoring required")
        if features.get('debt_to_equity', 0) > 2.0:
            conditions.append("Debt reduction plan to be submitted")
        if features.get('current_ratio', 2.0) < 1.2:
            conditions.append("Maintain minimum current ratio of 1.2x")
        if limit_decision['decision'] == "APPROVE_WITH_CONDITIONS":
            conditions.append("Additional collateral coverage of 1.5x required")
        if features.get('interest_coverage', 5.0) < 2.0:
            conditions.append("Interest coverage to be improved to minimum 2.0x")
        
        return conditions if conditions else ["Standard terms and conditions apply"]
