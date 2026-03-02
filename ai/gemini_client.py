"""
AI module for Gemini API integration and LLM-powered analysis
"""
import os
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_company_profile(self, company_data: Dict, research_data: Dict) -> Dict[str, object]:
        """Generate comprehensive company analysis using Gemini"""
        prompt = f"""
Analyze this company for credit risk assessment:

Company: {company_data.get('name', 'Unknown')}
Sector: {company_data.get('sector', 'Unknown')}
Location: {company_data.get('location', 'Unknown')}

Financial Highlights:
- Revenue: {research_data.get('revenue', 'N/A')}
- Profit: {research_data.get('profit', 'N/A')}
- Assets: {research_data.get('assets', 'N/A')}

Recent News & Web Research:
{research_data.get('news_summary', 'No recent news available')}

Sector Outlook:
{research_data.get('sector_outlook', 'No sector data available')}

Provide a structured analysis covering:
1. Management Quality Assessment (score 1-10)
2. Business Model Viability (score 1-10)
3. Market Position & Competitive Advantage
4. Key Risk Factors (list top 3-5)
5. Growth Potential Assessment
6. Overall Credit Worthiness Summary

Format as JSON with keys: management_score, business_model_score, market_position, risk_factors (array), growth_potential, credit_summary
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_gemini_response(response.text)
        except Exception as e:
            return {
                "management_score": 5.0,
                "business_model_score": 5.0,
                "market_position": "Unable to assess",
                "risk_factors": [f"AI analysis failed: {str(e)}"],
                "growth_potential": "Unknown",
                "credit_summary": "Manual review required"
            }
    
    def analyze_financial_ratios(self, financials: Dict) -> Dict[str, object]:
        """Deep financial analysis using Gemini"""
        prompt = f"""
Analyze these financial ratios for credit risk:

Current Ratio: {financials.get('current_ratio', 'N/A')}
Debt-to-Equity: {financials.get('debt_to_equity', 'N/A')}
Interest Coverage: {financials.get('interest_coverage', 'N/A')}
ROE: {financials.get('roe', 'N/A')}
Operating Margin: {financials.get('operating_margin', 'N/A')}

Provide:
1. Financial Health Score (1-10)
2. Liquidity Assessment
3. Leverage Risk Level (Low/Medium/High)
4. Profitability Trend
5. Key Financial Concerns (if any)

Format as JSON with keys: health_score, liquidity, leverage_risk, profitability, concerns (array)
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_gemini_response(response.text)
        except Exception as e:
            return {
                "health_score": 5.0,
                "liquidity": "Unknown",
                "leverage_risk": "Medium",
                "profitability": "Unknown",
                "concerns": [f"Analysis failed: {str(e)}"]
            }
    
    def generate_sector_outlook(self, sector: str, news_data: List[Dict]) -> str:
        """Generate sector-specific outlook using recent news"""
        news_text = "\n".join([f"- {item.get('title', '')}: {item.get('snippet', '')}" 
                               for item in news_data[:5]])
        
        prompt = f"""
Based on recent news and market trends, provide a brief sector outlook for: {sector}

Recent News:
{news_text}

Provide a 2-3 paragraph outlook covering:
- Current sector trends
- Growth prospects
- Key risks and challenges
- Regulatory environment (if applicable for India)
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Sector outlook unavailable: {str(e)}"
    
    def _parse_gemini_response(self, text: str) -> Dict:
        """Parse Gemini response, handling both JSON and text formats"""
        import json
        import re
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try direct JSON parse
        try:
            return json.loads(text)
        except:
            # Fallback: extract key-value pairs from text
            return {"raw_analysis": text, "parsed": False}
