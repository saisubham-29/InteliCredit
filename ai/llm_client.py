from __future__ import annotations

import os
from typing import Dict


class LLMClient:
    """Mockable LLM wrapper for summaries and narrative generation."""

    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "mock")

    def summarize_business(self, company: Dict[str, object]) -> str:
        if self.provider == "mock":
            sector = company.get("sector", "manufacturing")
            return (
                f"The borrower operates in the {sector} sector with diversified customers "
                "and stable operating history. Management reports steady order book and "
                "moderate expansion plans over the next 12 months."
            )
        return "LLM provider not configured in demo mode."
