"""
Test script to verify AI module setup and functionality
"""
import os
import sys

def test_imports():
    """Test if all AI modules can be imported"""
    print("Testing AI module imports...")
    
    try:
        from ai.gemini_client import GeminiClient
        print("✓ Gemini client imported successfully")
    except ImportError as e:
        print(f"✗ Gemini client import failed: {e}")
        return False
    
    try:
        from ai.web_crawler import WebCrawler, run_web_research
        print("✓ Web crawler imported successfully")
    except ImportError as e:
        print(f"✗ Web crawler import failed: {e}")
        return False
    
    try:
        from ai.ml_decisioning import CreditDecisionEngine
        print("✓ ML decisioning engine imported successfully")
    except ImportError as e:
        print(f"✗ ML decisioning engine import failed: {e}")
        return False
    
    try:
        from ai.databricks_connector import DatabricksConnector, fetch_multi_source_data
        print("✓ Databricks connector imported successfully")
    except ImportError as e:
        print(f"✗ Databricks connector import failed: {e}")
        return False
    
    return True


def test_ml_models():
    """Test ML model initialization"""
    print("\nTesting ML model initialization...")
    
    try:
        from ai.ml_decisioning import CreditDecisionEngine
        engine = CreditDecisionEngine()
        print("✓ ML models initialized successfully")
        
        # Test PD calculation
        test_features = {
            'current_ratio': 1.8,
            'debt_to_equity': 1.2,
            'interest_coverage': 4.5,
            'roe': 0.18,
            'operating_margin': 0.12,
            'revenue_growth': 0.15,
            'management_score': 7.0,
            'sector_risk': 0.2
        }
        
        pd, risk_class = engine.calculate_pd(test_features)
        print(f"✓ PD calculation works: {pd:.4f} ({risk_class})")
        
        limit = engine.calculate_credit_limit(test_features)
        print(f"✓ Credit limit calculation works: {limit['recommended_limit_cr']} Cr")
        
        return True
    except Exception as e:
        print(f"✗ ML model test failed: {e}")
        return False


def test_env_config():
    """Test environment configuration"""
    print("\nChecking environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        print("✓ GEMINI_API_KEY is configured")
    else:
        print("⚠ GEMINI_API_KEY not configured (enhanced mode will be disabled)")
    
    databricks_host = os.getenv("DATABRICKS_HOST")
    if databricks_host and databricks_host != "your_databricks_host":
        print("✓ Databricks is configured")
    else:
        print("⚠ Databricks not configured (will use local data only)")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("INTELLI-CREDIT AI Module Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n✗ Import tests failed. Please run: pip install -r requirements.txt")
    
    # Test ML models
    if not test_ml_models():
        all_passed = False
    
    # Test environment
    test_env_config()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Configure GEMINI_API_KEY in .env for enhanced mode")
        print("2. Run: uvicorn api.main:app --reload")
        print("3. Open: http://127.0.0.1:8000")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
