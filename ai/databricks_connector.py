"""
Databricks integration for multi-source data ingestion with Unity Catalog support
"""
import os
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

class DatabricksConnector:
    def __init__(self):
        self.host = os.getenv("DATABRICKS_HOST")
        self.token = os.getenv("DATABRICKS_TOKEN")
        self.warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        # Unity Catalog Namespacing
        self.catalog = os.getenv("DATABRICKS_CATALOG", "main")
        self.schema = os.getenv("DATABRICKS_SCHEMA", "default")
        
        if not all([self.host, self.token, self.warehouse_id]):
            print("Warning: Databricks credentials not configured. Using local data only.")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
    
    def get_table_path(self, table_name: str) -> str:
        """Returns fully qualified Unity Catalog path"""
        return f"`{self.catalog}`.`{self.schema}`.`{table_name}`"

    def execute_query(self, query: str) -> Optional[List[Dict]]:
        """Execute SQL query on Databricks warehouse"""
        if not self.enabled:
            return None
        
        url = f"{self.host}/api/2.0/sql/statements"
        
        payload = {
            "warehouse_id": self.warehouse_id,
            "statement": query,
            "wait_timeout": "30s"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=35)
            response.raise_for_status()
            
            result = response.json()
            if result.get("status", {}).get("state") == "SUCCEEDED":
                return self._parse_results(result)
            else:
                print(f"Query failed: {result.get('status', {}).get('error')}")
                return None
        except Exception as e:
            print(f"Databricks query error: {e}")
            return None
    
    def fetch_company_financials(self, company_id: str, company_name: str) -> Optional[Dict]:
        """Fetch company financial data from Databricks"""
        table = self.get_table_path("financial_data")
        query = f"""
        SELECT 
            fiscal_year, revenue, net_profit, total_assets, total_liabilities,
            current_assets, current_liabilities, debt, equity, operating_profit, interest_expense
        FROM {table}
        WHERE company_id = '{company_id}' OR company_name LIKE '%{company_name}%'
        ORDER BY fiscal_year DESC
        LIMIT 3
        """
        
        results = self.execute_query(query)
        if results:
            return {"source": "databricks", "data": results}
        return None
    
    def fetch_credit_bureau_data(self, company_id: str) -> Optional[Dict]:
        """Fetch credit bureau data (CIBIL, Experian, etc.)"""
        table = self.get_table_path("credit_bureau_data")
        query = f"""
        SELECT 
            bureau_name, credit_score, total_exposure, overdue_amount,
            dpd_30_plus, dpd_90_plus, last_updated
        FROM {table}
        WHERE company_id = '{company_id}'
        ORDER BY last_updated DESC
        LIMIT 1
        """
        
        results = self.execute_query(query)
        if results:
            return {"source": "databricks", "data": results[0] if results else {}}
        return None
    
    def fetch_banking_transactions(self, company_id: str, months: int = 12) -> Optional[List[Dict]]:
        """Fetch banking transaction data"""
        table = self.get_table_path("banking_transactions")
        query = f"""
        SELECT 
            transaction_date, credit_amount, debit_amount, balance,
            transaction_type, counterparty
        FROM {table}
        WHERE company_id = '{company_id}'
        AND transaction_date >= DATE_SUB(CURRENT_DATE(), {months * 30})
        ORDER BY transaction_date DESC
        """
        
        results = self.execute_query(query)
        if results:
            return results
        return None
    
    def fetch_gst_data(self, gstin: str) -> Optional[Dict]:
        """Fetch GST filing and compliance data"""
        table = self.get_table_path("gst_data")
        query = f"""
        SELECT 
            filing_period, total_sales, total_purchases, tax_paid,
            filing_status, filing_date
        FROM {table}
        WHERE gstin = '{gstin}'
        ORDER BY filing_period DESC
        LIMIT 12
        """
        
        results = self.execute_query(query)
        if results:
            return {"source": "databricks", "data": results}
        return None
    
    def fetch_legal_cases(self, company_id: str, company_name: str) -> Optional[List[Dict]]:
        """Fetch legal cases and litigation data"""
        table = self.get_table_path("legal_cases")
        query = f"""
        SELECT 
            case_number, case_type, filing_date, status, court_name, amount_involved
        FROM {table}
        WHERE company_id = '{company_id}' OR company_name LIKE '%{company_name}%'
        ORDER BY filing_date DESC
        """
        
        results = self.execute_query(query)
        return results if results else None
    
    def _parse_results(self, result: Dict) -> List[Dict]:
        """Parse Databricks SQL results into list of dicts"""
        try:
            manifest = result.get("manifest", {})
            chunks = result.get("result", {}).get("data_ptr", []) # Updated for modern SQL API if applicable
            
            # Simple fallback to result.get("rows") if it exists
            if "rows" in result:
                return result["rows"]
                
            # Full parsing logic
            schema = result.get("manifest", {}).get("schema", {}).get("columns", [])
            columns = [col["name"] for col in schema]
            
            rows = []
            # This is a simplified parser; experimental Unity Catalog results often come in 'rows'
            if "result" in result and "data" in result["result"]:
                for row in result["result"]["data"]:
                    rows.append(dict(zip(columns, row)))
            
            return rows
        except Exception as e:
            print(f"Error parsing Databricks results: {e}")
            return []


def fetch_multi_source_data(company_id: str, company_name: str, gstin: Optional[str] = None) -> Dict[str, object]:
    """Fetch data from multiple sources via Databricks"""
    connector = DatabricksConnector()
    
    if not connector.enabled:
        return {
            "source": "local",
            "message": "Databricks not configured, using local data only"
        }
    
    return {
        "financials": connector.fetch_company_financials(company_id, company_name),
        "credit_bureau": connector.fetch_credit_bureau_data(company_id),
        "banking": connector.fetch_banking_transactions(company_id),
        "gst": connector.fetch_gst_data(gstin) if gstin else None,
        "legal": connector.fetch_legal_cases(company_id, company_name),
        "source": "databricks",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
