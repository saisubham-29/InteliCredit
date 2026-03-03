
import os
import sys
import json

# Add project root to sys.path
sys.path.append(os.getcwd())

from api.pipeline import run_analysis

def test_enhanced_pipeline():
    print("🚀 Starting Enhanced Pipeline Verification...")
    
    # Sample Test Data
    company_id = "comp-001"
    documents = [
        {"doc_type": "bank_statement_csv", "path": "sample_data/bank_statement_1.csv"},
        {"doc_type": "gst_csv", "path": "sample_data/gst_data.csv"},
        {"doc_type": "annual_report_text", "path": "sample_data/annual_report_1.txt"}
    ]
    officer_inputs = {
        "factory_utilization_pct": 45,
        "management_quality_notes": "Experienced but high leverage"
    }

    print("\n--- Running Global Analysis ---")
    try:
        # Mock ML_ENABLED to test the logic path
        import api.pipeline as pipeline
        pipeline.ML_ENABLED = True
        
        result = run_analysis(company_id, documents, officer_inputs)
        
        print("\n✅ Analysis Completed Successfully!")
        
        # Verify XAI
        recommendation = result["risk_report"].get("recommendation", {})
        if "ml_explanation" in recommendation:
            print("✅ XAI: ml_explanation found in recommendation.")
            print(f"   Rationale: {recommendation['rationale']}")
            print(f"   Drivers: {recommendation['ml_explanation'].get('key_drivers')}")
        else:
            print("❌ XAI: ml_explanation MISSING.")

        # Verify GNN
        fraud = result["risk_report"].get("fraud_analysis", {})
        if fraud:
            print(f"✅ GNN: Fraud analysis completed (Score: {fraud.get('fraud_risk_score')})")
            print(f"   Patterns: {fraud.get('detected_patterns')}")
        else:
            print("❌ GNN: Fraud analysis MISSING.")

        # Verify Indian Context
        flags = result["financials"].get("flags", [])
        indian_flags = [f for f in flags if "GST" in f or "round-tripping" in f]
        if indian_flags:
            print(f"✅ Indian Context: Circular trading/GST flags detected: {indian_flags}")
        else:
            print("ℹ️ Indian Context: No specific fraud flags triggered (Expected for clean data).")

    except Exception as e:
        print(f"❌ Pipeline Failure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_pipeline()
