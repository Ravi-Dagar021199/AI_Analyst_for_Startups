"""
Enhanced Data Collection Agent
Automatically gathers data from multiple sources including:
- Company websites and digital footprints
- News articles and press releases
- Social media mentions (where possible)
- Public company information
"""

import asyncio
import aiohttp
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import trafilatura
from bs4 import BeautifulSoup
import json
import re
from dataclasses import dataclass

@dataclass
class DataSource:
    """Represents a collected data source"""
    source_type: str  # 'website', 'news', 'social_media', 'press_release'
    url: str
    title: str
    content: str
    confidence: float  # 0-1, how relevant this data is
    date_published: Optional[str] = None
    author: Optional[str] = None

class EnhancedDataCollector:
    """Collects comprehensive data about startups from multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_company_info(self, text_content: str) -> Dict[str, Any]:
        """Extract company name, founders, and key terms from the initial text"""
        
        # Simple extraction patterns - can be enhanced with NLP
        company_patterns = [
            r'(?:Company|Startup|Business):\s*([A-Za-z0-9\s&]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|LLC|Corp|Limited|Ltd)',
            r'At\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)[,\s]',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(?:a|an|the)'
        ]
        
        founder_patterns = [
            r'(?:Founder|CEO|Co-founder|Founded by):\s*([A-Za-z\s,]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s*\([^)]*\))?\s+(?:founded|started|created)',
            r'(?:by|Founded by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        # Extract company names
        company_names = []
        for pattern in company_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            company_names.extend([match.strip() for match in matches if len(match.strip()) > 2])
        
        # Extract founder names
        founder_names = []
        for pattern in founder_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            founder_names.extend([match.strip() for match in matches if len(match.strip()) > 3])
        
        # Extract key business terms
        business_keywords = re.findall(
            r'\b(?:AI|artificial intelligence|machine learning|SaaS|platform|marketplace|e-commerce|fintech|healthtech|edtech|blockchain|cryptocurrency|mobile app|web app|API|software|technology|startup|innovation|disruption)\b',
            text_content, re.IGNORECASE
        )
        
        return {
            'company_names': list(set(company_names))[:3],  # Top 3 most likely
            'founder_names': list(set(founder_names))[:5],  # Top 5 most likely  
            'business_keywords': list(set([kw.lower() for kw in business_keywords]))[:10]
        }
    
    def search_company_website(self, company_name: str) -> Optional[DataSource]:
        """Search for and scrape the company's official website"""
        try:
            # Try common website patterns
            common_domains = [
                f"https://www.{company_name.lower().replace(' ', '')}.com",
                f"https://{company_name.lower().replace(' ', '')}.com",
                f"https://www.{company_name.lower().replace(' ', '-')}.com",
                f"https://{company_name.lower().replace(' ', '-')}.com"
            ]
            
            for url in common_domains:
                try:
                    response = self.session.get(url, timeout=5)
                    if response.status_code == 200:
                        # Extract text content using trafilatura
                        text_content = trafilatura.extract(response.text)
                        if text_content and len(text_content) > 100:
                            return DataSource(
                                source_type='website',
                                url=url,
                                title=f"{company_name} Official Website",
                                content=text_content[:2000],  # Limit content
                                confidence=0.9
                            )
                except:
                    continue
                    
        except Exception as e:
            print(f"Error searching company website: {e}")
        
        return None
    
    def search_news_articles(self, company_name: str, founders: List[str]) -> List[DataSource]:
        """Search for news articles about the company and founders"""
        news_sources = []
        
        try:
            # Search terms
            search_terms = [company_name] + founders[:2]  # Company + top 2 founders
            
            for term in search_terms:
                if not term or len(term) < 3:
                    continue
                    
                # Use DuckDuckGo search (no API key required)
                search_query = f"{term} startup funding news"
                search_url = f"https://duckduckgo.com/html/?q={search_query}"
                
                try:
                    response = self.session.get(search_url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract search results
                        results = soup.find_all('a', {'class': 'result__a'})[:3]  # Top 3 results
                        
                        for result in results:
                            try:
                                title = result.get_text(strip=True)
                                link = result.get('href')
                                
                                if link and 'http' in link:
                                    # Try to extract article content
                                    article_response = self.session.get(link, timeout=5)
                                    if article_response.status_code == 200:
                                        article_content = trafilatura.extract(article_response.text)
                                        
                                        if article_content and len(article_content) > 200:
                                            confidence = 0.7 if company_name.lower() in article_content.lower() else 0.4
                                            
                                            news_sources.append(DataSource(
                                                source_type='news',
                                                url=link,
                                                title=title[:100],
                                                content=article_content[:1500],
                                                confidence=confidence
                                            ))
                            except:
                                continue
                                
                except Exception as e:
                    print(f"Error searching news for {term}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in news search: {e}")
        
        return news_sources[:5]  # Return top 5 relevant articles
    
    def search_social_media_mentions(self, company_name: str, founders: List[str]) -> List[DataSource]:
        """Search for social media mentions and public profiles"""
        social_sources = []
        
        try:
            # Search for LinkedIn company pages and founder profiles
            search_terms = [company_name] + founders[:2]
            
            for term in search_terms:
                if not term or len(term) < 3:
                    continue
                    
                # Search LinkedIn via Google (public data only)
                linkedin_query = f"site:linkedin.com {term}"
                search_url = f"https://duckduckgo.com/html/?q={linkedin_query}"
                
                try:
                    response = self.session.get(search_url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        results = soup.find_all('a', {'class': 'result__a'})[:2]  # Top 2 LinkedIn results
                        
                        for result in results:
                            try:
                                title = result.get_text(strip=True)
                                link = result.get('href')
                                
                                if link and 'linkedin.com' in link:
                                    social_sources.append(DataSource(
                                        source_type='social_media',
                                        url=link,
                                        title=f"LinkedIn: {title[:80]}",
                                        content=f"LinkedIn profile or company page for {term}",
                                        confidence=0.6
                                    ))
                            except:
                                continue
                                
                except Exception as e:
                    print(f"Error searching LinkedIn for {term}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in social media search: {e}")
        
        return social_sources[:3]  # Return top 3 social media sources
    
    def search_crunchbase_data(self, company_name: str) -> Optional[DataSource]:
        """Search for Crunchbase data (public information)"""
        try:
            # Search Crunchbase via Google
            crunchbase_query = f"site:crunchbase.com {company_name}"
            search_url = f"https://duckduckgo.com/html/?q={crunchbase_query}"
            
            response = self.session.get(search_url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('a', {'class': 'result__a'})[:1]  # Top result
                
                if results:
                    result = results[0]
                    title = result.get_text(strip=True)
                    link = result.get('href')
                    
                    if link and 'crunchbase.com' in link:
                        return DataSource(
                            source_type='database',
                            url=link,
                            title=f"Crunchbase: {title[:80]}",
                            content=f"Crunchbase profile for {company_name} with funding and company information",
                            confidence=0.8
                        )
                        
        except Exception as e:
            print(f"Error searching Crunchbase: {e}")
        
        return None
    
    def collect_comprehensive_data(self, initial_text: str) -> Dict[str, Any]:
        """Main method to collect comprehensive data from all sources"""
        
        # Extract company information from initial text
        company_info = self.extract_company_info(initial_text)
        
        collected_data = {
            'extracted_info': company_info,
            'data_sources': []
        }
        
        if not company_info['company_names']:
            # If no company name found, return minimal data
            return collected_data
        
        primary_company = company_info['company_names'][0]
        founders = company_info['founder_names']
        
        print(f"Collecting data for: {primary_company}")
        print(f"Founders: {founders}")
        
        # Collect from various sources
        data_sources = []
        
        # 1. Company website
        website_data = self.search_company_website(primary_company)
        if website_data:
            data_sources.append(website_data)
        
        # 2. News articles
        news_data = self.search_news_articles(primary_company, founders)
        data_sources.extend(news_data)
        
        # 3. Social media mentions
        social_data = self.search_social_media_mentions(primary_company, founders)
        data_sources.extend(social_data)
        
        # 4. Crunchbase data
        crunchbase_data = self.search_crunchbase_data(primary_company)
        if crunchbase_data:
            data_sources.append(crunchbase_data)
        
        collected_data['data_sources'] = data_sources
        
        # Create summary of collected data
        total_sources = len(data_sources)
        high_confidence_sources = len([s for s in data_sources if s.confidence > 0.7])
        
        collected_data['summary'] = {
            'total_sources_found': total_sources,
            'high_confidence_sources': high_confidence_sources,
            'source_types': list(set([s.source_type for s in data_sources])),
            'data_collection_success': total_sources > 0
        }
        
        return collected_data

# Global instance
data_collector = EnhancedDataCollector()