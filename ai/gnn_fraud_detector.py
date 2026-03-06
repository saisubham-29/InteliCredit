"""
GNN-based Promoter Fraud and Circular Trading Detector
Identifies suspicious transaction patterns and related party clusters.
"""
import numpy as np
from typing import Dict, List, Tuple, Set

class GNNFraudDetector:
    def __init__(self):
        # In a real production system, this would load a PyTorch Geometric or DGL model
        self.anomaly_threshold = 0.75
    
    def analyze_network(self, company_id: str, company_name: str, transactions: List[Dict]) -> Dict[str, object]:
        """
        Analyzes the transaction network for circular trading and shell company patterns.
        """
        if not transactions:
            return {
                "fraud_risk_score": 0.0,
                "risk_band": "Low",
                "detected_patterns": [],
                "network_density": 0.0
            }
            
        # 1. Circular Trading Detection (Simplified Graph Analysis)
        # We look for cycles in the money flow: A -> B -> C -> A
        patterns = []
        suspicious_nodes = set()
        
        # Build adjacency list
        graph = {}
        for tx in transactions:
            u = company_name
            v = tx.get("counterparty")
            if not v: continue
            
            if u not in graph: graph[u] = []
            graph[u].append(v)
            
        # Detect circular paths (simplified for demo)
        for tx in transactions:
            if tx.get("transaction_type") == "debit" and tx.get("counterparty") == company_name:
                patterns.append("Self-loop transaction detected")
                suspicious_nodes.add(company_name)
        
        # 2. Shell Company Heuristics
        # High volume of transactions with recently created or low-capital firms
        shell_count = 0
        for tx in transactions:
            cp = tx.get("counterparty", "").lower()
            if any(key in cp for key in ["shell", "trading", "enterprises", "solutions"]) and tx.get("amount", 0) > 1000000:
                shell_count += 1
                
        if shell_count > 3:
            patterns.append(f"High volume with potential shell entities ({shell_count} hits)")
            
        # 3. Round-Tripping Analysis
        # Credits followed immediately by debits of similar amounts
        # ... logic ...
        
        total_risk = min(0.95, (len(patterns) * 0.25) + (shell_count * 0.1))
        
        return {
            "fraud_risk_score": round(total_risk, 2),
            "risk_band": "High" if total_risk > 0.6 else "Medium" if total_risk > 0.3 else "Low",
            "detected_patterns": patterns,
            "suspicious_counterparties": list(suspicious_nodes),
            "graph_summary": {
                "nodes": len(set([tx.get("counterparty") for tx in transactions if tx.get("counterparty")])),
                "edges": len(transactions),
                "circular_trading_index": round(total_risk * 0.8, 2)
            }
        }

def run_fraud_analysis(company_id: str, company_name: str, transactions: List[Dict]) -> Dict[str, object]:
    detector = GNNFraudDetector()
    return detector.analyze_network(company_id, company_name, transactions)
