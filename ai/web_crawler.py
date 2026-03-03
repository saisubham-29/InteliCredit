"""
Web crawler for live company research, news, and sector analysis
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta

class WebCrawler:
    def __init__(self, user_agent: str = "IntelliCredit/1.0", timeout: int = 30):
        self.user_agent = user_agent
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}
    
    async def search_company_news(self, company_name: str, sector: str) -> List[Dict]:
        """Search for recent company news and articles"""
        results = []
        
        # Search queries
        queries = [
            f"{company_name} financial news India",
            f"{company_name} credit rating",
            f"{company_name} promoter news litigation",
            f"{company_name} regulatory penalties SEBI RBI",
            f"{company_name} court cases NCLT",
            f"{sector} sector India outlook 2026"
        ]
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [self._search_query(session, query) for query in queries]
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in search_results:
                if isinstance(result, list):
                    results.extend(result)
        
        return results[:20]  # Limit to top 20 results
    
    async def _search_query(self, session: aiohttp.ClientSession, query: str) -> List[Dict]:
        """Perform web search using DuckDuckGo HTML (no API key needed)"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_search_results(html, query)
        except Exception as e:
            print(f"Search failed for '{query}': {e}")
        return []
    
    def _parse_search_results(self, html: str, query: str) -> List[Dict]:
        """Parse search results from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result'):
            try:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'query': query,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                continue
        
        return results
    
    async def fetch_company_details(self, company_name: str, urls: List[str]) -> Dict[str, object]:
        """Fetch and extract key details from company-related URLs"""
        details = {
            'financial_mentions': [],
            'risk_indicators': [],
            'positive_signals': [],
            'management_info': []
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [self._fetch_url_content(session, url) for url in urls[:5]]
            contents = await asyncio.gather(*tasks, return_exceptions=True)
            
            for content in contents:
                if isinstance(content, str):
                    self._extract_signals(content, details)
        
        return details
    
    async def _fetch_url_content(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch content from a URL"""
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # Extract main text content
                    for script in soup(["script", "style"]):
                        script.decompose()
                    return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
        return None
    
    def _extract_signals(self, text: str, details: Dict):
        """Extract financial and risk signals from text"""
        text_lower = text.lower()
        
        # Financial keywords
        financial_patterns = [
            r'revenue.*?(\d+\.?\d*)\s*(crore|lakh|million|billion)',
            r'profit.*?(\d+\.?\d*)\s*(crore|lakh|million|billion)',
            r'turnover.*?(\d+\.?\d*)\s*(crore|lakh|million|billion)',
        ]
        
        for pattern in financial_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                details['financial_mentions'].extend([f"{m[0]} {m[1]}" for m in matches[:3]])
        
        # Risk indicators (Hackathon Pillar 2)
        risk_keywords = ['default', 'litigation', 'fraud', 'penalty', 'investigation', 
                        'bankruptcy', 'insolvency', 'npa', 'restructuring', 
                        'promoter pledge', 'regulatory action', 'sebi probe', 'rbi penalty']
        for keyword in risk_keywords:
            if keyword in text_lower:
                # Extract sentence containing the keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        details['risk_indicators'].append(sentence.strip()[:200])
                        break
        
        # Positive signals
        positive_keywords = ['award', 'expansion', 'growth', 'profit', 'innovation',
                           'certification', 'partnership', 'contract win']
        for keyword in positive_keywords:
            if keyword in text_lower:
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        details['positive_signals'].append(sentence.strip()[:200])
                        break
    
    async def get_sector_trends(self, sector: str) -> Dict[str, object]:
        """Get sector-specific trends and outlook"""
        query = f"{sector} sector India trends 2026 outlook"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            results = await self._search_query(session, query)
            
            return {
                'sector': sector,
                'news_count': len(results),
                'recent_articles': results[:10],
                'last_updated': datetime.now().isoformat()
            }


def run_web_research(company_name: str, sector: str) -> Dict[str, object]:
    """Synchronous wrapper for web research"""
    crawler = WebCrawler()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run async tasks
        news = loop.run_until_complete(crawler.search_company_news(company_name, sector))
        sector_trends = loop.run_until_complete(crawler.get_sector_trends(sector))
        
        # Extract URLs for detailed crawling
        urls = [item['url'] for item in news[:5] if item.get('url')]
        company_details = loop.run_until_complete(crawler.fetch_company_details(company_name, urls))
        
        return {
            'news_articles': news,
            'sector_trends': sector_trends,
            'company_details': company_details,
            'crawl_timestamp': datetime.now().isoformat()
        }
    finally:
        loop.close()
