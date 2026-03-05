from __future__ import annotations

import os
from typing import Dict

# Import GeminiClient if available for real intelligence
try:
    from ai.gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMClient:
    """Enhanced LLM wrapper for summaries and narrative generation."""

    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "gemini" if GEMINI_AVAILABLE else "mock")

    def summarize_business(self, company: Dict[str, object]) -> str:
        if self.provider == "gemini" and GEMINI_AVAILABLE:
            try:
                gemini = GeminiClient()
                # Using analyze_company_profile as a general summary tool
                analysis = gemini.analyze_company_profile(company, {"mode": "summary_only"})
                return analysis.get("strengths_summary", "Summary generation failed.")
            except Exception as e:
                print(f"Gemini summary failed: {e}. Falling back to mock.")
        
        # Fallback Mock Logic
        sector = company.get("sector", "manufacturing")
        return (
            f"The borrower operates in the {sector} sector with diversified customers "
            "and stable operating history. Management reports steady order book and "
            "moderate expansion plans over the next 12 months."
        )
