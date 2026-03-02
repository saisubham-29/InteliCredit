"""
Research agent: performs secondary research on company, sector, and management
Enhanced with Gemini AI and live web crawling
"""
from __future__ import annotations
import json
import os
from typing import Dict, List
from datetime import datetime

# Import AI modules
try:
    from ai.gemini_client import GeminiClient
    from ai.web_crawler import run_web_research
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Warning: AI modules not available. Running in basic mode.")

RISK_KEYWORDS = {
    "default": ["default", "delayed", "overdue"],
    "litigation": ["litigation", "court", "tribunal", "nclt"],
    "fraud": ["fraud", "probe", "investigation", "cbi", "sfio"],
    "regulatory": ["rbi", "sebi", "penalty", "show cause"],
}

POSITIVE_WORDS = {"growth", "award", "expansion", "profit", "strong", "order"}
NEGATIVE_WORDS = {"loss", "default", "litigation", "penalty", "probe", "delay"}

SECTOR_OUTLOOK = {
    "manufacturing": "Stable",
    "infrastructure": "Cautious",
    "real estate": "Negative",
    "pharma": "Positive",
    "textiles": "Cautious",
    "logistics": "Stable",
}


def _load_news_dataset() -> List[dict]:
    path = os.path.join("sample_data", "news_dataset.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _classify_sentiment(text: str) -> str:
    words = set(text.lower().split())
    pos_hits = len(words & POSITIVE_WORDS)
    neg_hits = len(words & NEGATIVE_WORDS)
    if neg_hits > pos_hits:
        return "Negative"
    if pos_hits > neg_hits:
        return "Positive"
    return "Neutral"


def _detect_risk_keywords(text: str) -> List[str]:
    hits = []
    lower = text.lower()
    for category, keywords in RISK_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            hits.append(category)
    return hits


def run_research(company_profile: Dict[str, object]) -> Dict[str, object]:
    """
    Perform secondary research on the company.
    Enhanced with live web crawling and Gemini AI analysis when available.
    """
    if ENHANCED_MODE:
        try:
            return _run_enhanced_research(company_profile)
        except Exception as e:
            print(f"Enhanced research failed: {e}. Falling back to basic mode.")
    
    return _run_basic_research(company_profile)


def _run_enhanced_research(company_profile: Dict[str, object]) -> Dict[str, object]:
    """Enhanced research with AI and web crawling"""
    company_name = company_profile.get("name", "Unknown")
    sector = (company_profile.get("sector") or "").lower()
    
    # Step 1: Live web crawling
    print(f"Crawling web for {company_name}...")
    web_data = run_web_research(company_name, sector)
    
    # Step 2: Process news articles
    news_articles = web_data.get('news_articles', [])
    evidence = []
    all_text = ""
    heatmap = {key: 0 for key in RISK_KEYWORDS.keys()}
    negative_hits = 0
    
    for article in news_articles[:15]:
        text = article.get('title', '') + ' ' + article.get('snippet', '')
        sentiment = _classify_sentiment(text)
        risk_keywords = _detect_risk_keywords(text)
        
        for keyword in risk_keywords:
            heatmap[keyword] += 1
        if sentiment == "Negative":
            negative_hits += 1
        
        evidence.append({
            "title": article.get('title', 'Unknown'),
            "snippet": article.get('snippet', '')[:200],
            "source": article.get('url', ''),
            "date": article.get('timestamp', datetime.now().isoformat()),
            "sentiment": sentiment,
            "risk_keywords": risk_keywords,
        })
        all_text += text + ' '
    
    # Step 3: Gemini AI analysis
    print(f"Running Gemini AI analysis...")
    gemini = GeminiClient()
    
    company_details = web_data.get('company_details', {})
    research_summary = {
        'revenue': company_details.get('financial_mentions', ['Not available'])[0] if company_details.get('financial_mentions') else 'Not available',
        'profit': 'See financial analysis',
        'assets': 'See financial analysis',
        'news_summary': '\n'.join([f"- {e['title']}: {e['snippet'][:100]}" for e in evidence[:5]]),
        'sector_outlook': web_data.get('sector_trends', {})
    }
    
    ai_analysis = gemini.analyze_company_profile(company_profile, research_summary)
    sector_outlook_text = gemini.generate_sector_outlook(sector, news_articles)
    
    return {
        "sector_outlook": sector_outlook_text or SECTOR_OUTLOOK.get(sector, "Stable"),
        "news_hits": evidence,
        "risk_heatmap": heatmap,
        "litigation_signals": heatmap.get("litigation", 0),
        "negative_news_count": negative_hits,
        "ai_analysis": ai_analysis,
        "web_crawl_stats": {
            "articles_found": len(news_articles),
            "risk_indicators": len(company_details.get('risk_indicators', [])),
            "positive_signals": len(company_details.get('positive_signals', []))
        },
        "research_timestamp": datetime.now().isoformat(),
        "mode": "enhanced",
        "missing": [] if evidence else ["news_data"]
    }


def _run_basic_research(company_profile: Dict[str, object]) -> Dict[str, object]:
    """Basic research with local/synthetic data (fallback)"""
    company_name = company_profile.get("name", "")
    promoter = company_profile.get("promoter", "")
    sector = (company_profile.get("sector") or "").lower()

    news = _load_news_dataset()
    relevant = [
        item
        for item in news
        if company_name.lower() in item.get("company_name", "").lower()
        or promoter.lower() in item.get("company_name", "").lower()
    ]

    evidence = []
    heatmap = {key: 0 for key in RISK_KEYWORDS.keys()}
    negative_hits = 0

    for item in relevant:
        text = f"{item.get('title', '')} {item.get('snippet', '')}"
        sentiment = item.get("sentiment") or _classify_sentiment(text)
        risk_keywords = _detect_risk_keywords(text)
        for keyword in risk_keywords:
            heatmap[keyword] += 1
        if sentiment == "Negative":
            negative_hits += 1

        evidence.append(
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "date": item.get("date"),
                "source": item.get("source"),
                "sentiment": sentiment,
                "risk_keywords": risk_keywords,
            }
        )

    outlook = SECTOR_OUTLOOK.get(sector, "Stable")
    litigation_signals = heatmap.get("litigation", 0)

    return {
        "sector_outlook": outlook,
        "news_hits": evidence,
        "risk_heatmap": heatmap,
        "litigation_signals": litigation_signals,
        "negative_news_count": negative_hits,
        "mode": "basic",
        "missing": [] if relevant else ["news_data"],
    }
