"""
Enhanced Data Collection Agent - Simplified MVP
Provides enhanced startup analysis through intelligent content parsing and context enhancement.
Future versions will include external data sources with proper API integrations.
"""

import re
from typing import List, Dict, Optional, Any
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
    """Enhanced startup analysis through intelligent content parsing and context enhancement"""
    
    def __init__(self):
        self.market_keywords = {
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'AI', 'ML'],
            'fintech': ['financial technology', 'payments', 'banking', 'cryptocurrency', 'blockchain', 'fintech'],
            'healthtech': ['healthcare', 'medical', 'health tech', 'biotech', 'pharma', 'telemedicine'],
            'edtech': ['education technology', 'learning', 'e-learning', 'edtech', 'educational'],
            'saas': ['software as a service', 'SaaS', 'cloud', 'platform', 'subscription'],
            'ecommerce': ['e-commerce', 'marketplace', 'retail', 'online shopping', 'commerce']
        }
        
        self.funding_indicators = [
            'seed funding', 'series a', 'series b', 'venture capital', 'vc funding',
            'angel investment', 'fundraising', 'investment', 'valuation', 'pre-seed'
        ]
        
        self.traction_indicators = [
            'customers', 'users', 'revenue', 'growth', 'mrr', 'arr', 'gmv',
            'daily active users', 'monthly active users', 'downloads', 'partnerships'
        ]
    
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
    
    def analyze_market_segment(self, text: str) -> Dict[str, Any]:
        """Analyze market segment and industry from text content"""
        text_lower = text.lower()
        market_analysis = {
            'primary_market': 'general',
            'market_keywords_found': [],
            'market_confidence': 0.5
        }
        
        # Check for market keywords
        for market, keywords in self.market_keywords.items():
            found_keywords = [kw for kw in keywords if kw.lower() in text_lower]
            if found_keywords:
                market_analysis['market_keywords_found'].extend(found_keywords)
                if len(found_keywords) >= 2:  # Strong indicator
                    market_analysis['primary_market'] = market
                    market_analysis['market_confidence'] = 0.8
                elif len(found_keywords) == 1:
                    market_analysis['primary_market'] = market
                    market_analysis['market_confidence'] = 0.6
        
        return market_analysis
    
    def analyze_funding_stage(self, text: str) -> Dict[str, Any]:
        """Analyze funding stage and investment indicators"""
        text_lower = text.lower()
        funding_analysis = {
            'funding_stage': 'unknown',
            'funding_indicators': [],
            'funding_confidence': 0.3
        }
        
        # Check for funding indicators
        found_indicators = [ind for ind in self.funding_indicators if ind in text_lower]
        if found_indicators:
            funding_analysis['funding_indicators'] = found_indicators
            funding_analysis['funding_confidence'] = 0.7
            
            # Determine likely stage
            if any(stage in text_lower for stage in ['series b', 'series c']):
                funding_analysis['funding_stage'] = 'growth'
            elif any(stage in text_lower for stage in ['series a']):
                funding_analysis['funding_stage'] = 'early'
            elif any(stage in text_lower for stage in ['seed', 'angel']):
                funding_analysis['funding_stage'] = 'seed'
        
        return funding_analysis
    
    def analyze_traction_metrics(self, text: str) -> Dict[str, Any]:
        """Extract and analyze traction metrics"""
        traction_analysis = {
            'traction_indicators': [],
            'metrics_found': [],
            'traction_confidence': 0.4
        }
        
        # Look for specific metrics
        metric_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?[kmb]?)\s*(?:users|customers|downloads)',
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?[kmb]?)\s*(?:revenue|mrr|arr)',
            r'(\d+(?:\.\d+)?%)\s*(?:growth|conversion)'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text.lower())
            traction_analysis['metrics_found'].extend(matches)
        
        # Check for traction indicators
        found_indicators = [ind for ind in self.traction_indicators if ind in text.lower()]
        if found_indicators:
            traction_analysis['traction_indicators'] = found_indicators
            traction_analysis['traction_confidence'] = 0.6
        
        return traction_analysis
    
    # Removed external scraping functions for production security
    # Future versions will use proper API integrations with rate limiting and security controls
    
    def collect_comprehensive_data(self, initial_text: str) -> Dict[str, Any]:
        """Enhanced analysis through intelligent content parsing and context generation"""
        
        # Extract company information from initial text
        company_info = self.extract_company_info(initial_text)
        
        # Perform enhanced analysis
        market_analysis = self.analyze_market_segment(initial_text)
        funding_analysis = self.analyze_funding_stage(initial_text)
        traction_analysis = self.analyze_traction_metrics(initial_text)
        
        # Generate enhanced context data sources
        data_sources = []
        
        # Create context-based data sources
        if company_info['company_names']:
            primary_company = company_info['company_names'][0]
            
            # Market context source
            if market_analysis['market_confidence'] > 0.6:
                market_context = f"Market Analysis: {primary_company} operates in the {market_analysis['primary_market']} sector. "
                market_context += f"Key indicators: {', '.join(market_analysis['market_keywords_found'][:3])}"
                
                data_sources.append(DataSource(
                    source_type='market_analysis',
                    url='internal://market-intelligence',
                    title=f"{market_analysis['primary_market'].title()} Market Context",
                    content=market_context,
                    confidence=market_analysis['market_confidence']
                ))
            
            # Funding context source
            if funding_analysis['funding_confidence'] > 0.6:
                funding_context = f"Funding Analysis: Company shows indicators of {funding_analysis['funding_stage']} stage. "
                funding_context += f"Funding signals: {', '.join(funding_analysis['funding_indicators'][:2])}"
                
                data_sources.append(DataSource(
                    source_type='funding_analysis',
                    url='internal://funding-intelligence',
                    title=f"{funding_analysis['funding_stage'].title()} Stage Analysis",
                    content=funding_context,
                    confidence=funding_analysis['funding_confidence']
                ))
            
            # Traction context source
            if traction_analysis['traction_confidence'] > 0.5:
                traction_context = f"Traction Analysis: Found metrics and indicators suggesting business traction. "
                if traction_analysis['metrics_found']:
                    traction_context += f"Metrics: {', '.join(traction_analysis['metrics_found'][:3])}"
                
                data_sources.append(DataSource(
                    source_type='traction_analysis',
                    url='internal://traction-intelligence',
                    title="Business Traction Analysis",
                    content=traction_context,
                    confidence=traction_analysis['traction_confidence']
                ))
        
        collected_data = {
            'extracted_info': company_info,
            'data_sources': data_sources,
            'enhanced_analysis': {
                'market': market_analysis,
                'funding': funding_analysis,
                'traction': traction_analysis
            }
        }
        
        # Create summary
        total_sources = len(data_sources)
        collected_data['summary'] = {
            'total_sources_found': total_sources,
            'high_confidence_sources': len([s for s in data_sources if s.confidence > 0.7]),
            'source_types': list(set([s.source_type for s in data_sources])),
            'data_collection_success': total_sources > 0,
            'enhancement_type': 'intelligent_analysis'
        }
        
        return collected_data

# Global instance
data_collector = EnhancedDataCollector()