"""
AI module for INTELLI-CREDIT
Provides Gemini API integration, web crawling, ML decisioning, and Databricks connectivity
"""
from .llm_client import LLMClient
from .gemini_client import GeminiClient
from .web_crawler import WebCrawler, run_web_research
from .ml_decisioning import CreditDecisionEngine
from .databricks_connector import DatabricksConnector, fetch_multi_source_data

__all__ = [
    'LLMClient',
    'GeminiClient',
    'WebCrawler',
    'run_web_research',
    'CreditDecisionEngine',
    'DatabricksConnector',
    'fetch_multi_source_data'
]
