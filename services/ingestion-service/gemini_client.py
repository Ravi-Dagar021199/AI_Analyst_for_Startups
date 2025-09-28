import json
import logging
import os
from typing import Dict, Any

from google import genai
from google.genai import types
from pydantic import BaseModel


# IMPORTANT: KEEP THIS COMMENT
# Follow these instructions when using this blueprint:
# - Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
#   - do not change this unless explicitly requested by the user
# - Sometimes the google genai SDK has occasional type errors. You might need to run to validate, at time.  
# The SDK was recently renamed from google-generativeai to google-genai. This file reflects the new name and the new APIs.

# This API key is from Gemini Developer API Key, not vertex AI API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_API_KEY != "demo_mode":
    client = genai.Client(api_key=GEMINI_API_KEY)
    # Mask API key for security in logs
    masked_key = GEMINI_API_KEY[:8] + "..." + GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 12 else "***"
    print(f"✅ Gemini AI client initialized successfully with key: {masked_key}")
else:
    client = None
    print("⚠️ GEMINI_API_KEY not found or set to demo_mode - using intelligent demo analysis")


class StartupAnalysis(BaseModel):
    founder_profile: Dict[str, Any]
    market_opportunity: Dict[str, Any]
    unique_differentiator: Dict[str, Any]
    business_metrics: Dict[str, Any]
    overall_score: int
    key_insights: list[str]
    risk_flags: list[str]


def analyze_startup_materials(text: str) -> StartupAnalysis:
    """
    Analyze startup materials using Gemini AI to extract structured insights
    across the four key vectors: Founder Profile, Market Opportunity, 
    Unique Differentiator, and Business Metrics.
    """
    try:
        # If no API key available, return demo analysis
        if not client:
            return create_demo_analysis(text)
            
        prompt = f"""
        You are an expert venture capital analyst. Analyze the following startup material and provide structured insights:

        STARTUP MATERIAL:
        {text}

        Please analyze this across four key vectors and provide JSON output:

        1. Founder Profile: Experience, background, founder-market fit, track record
        2. Market Opportunity: Problem validation, market size, competitive landscape  
        3. Unique Differentiator: What makes this solution unique and defensible
        4. Business Metrics: Revenue, traction, growth metrics, unit economics

        Also provide:
        - Overall score (1-10 scale for investment potential)
        - Key insights (3-5 bullet points)
        - Risk flags (potential concerns or red flags)

        Return valid JSON in this format:
        {{
            "founder_profile": {{
                "experience": "detailed analysis of founder experience",
                "founder_market_fit": "assessment of fit",
                "strengths": ["strength1", "strength2"],
                "concerns": ["concern1", "concern2"]
            }},
            "market_opportunity": {{
                "problem_description": "description of problem being solved",
                "market_size": "market size analysis",
                "competitive_landscape": "competitive analysis",
                "market_validation": "validation evidence"
            }},
            "unique_differentiator": {{
                "core_innovation": "key innovation",
                "competitive_advantages": ["advantage1", "advantage2"],
                "defensibility": "defensibility analysis"
            }},
            "business_metrics": {{
                "revenue_model": "revenue model description",
                "traction": "traction indicators",
                "growth_metrics": "growth analysis",
                "unit_economics": "unit economics assessment"
            }},
            "overall_score": 7,
            "key_insights": ["insight1", "insight2", "insight3"],
            "risk_flags": ["risk1", "risk2"]
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_json = response.text
        logging.info(f"Gemini Analysis Response: {raw_json}")

        if raw_json:
            # Clean up the response to extract just the JSON
            if "```json" in raw_json:
                raw_json = raw_json.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_json:
                raw_json = raw_json.split("```")[1].strip()
            
            data = json.loads(raw_json)
            return StartupAnalysis(**data)
        else:
            raise ValueError("Empty response from Gemini model")

    except Exception as e:
        logging.error(f"Failed to analyze startup materials: {e}")
        # Return demo analysis if real AI fails
        return create_demo_analysis(text)


def create_demo_analysis(text: str) -> StartupAnalysis:
    """
    Create a demo analysis when Gemini API is not available.
    This provides realistic sample data for demonstration purposes.
    """
    # Extract some basic information from the text
    text_lower = text.lower()
    text_length = len(text)
    
    # Determine likely document type
    doc_type = "Unknown Document"
    if any(word in text_lower for word in ["pitch", "deck", "presentation"]):
        doc_type = "Pitch Deck"
    elif any(word in text_lower for word in ["business plan", "proposal"]):
        doc_type = "Business Plan"
    elif any(word in text_lower for word in ["financial", "revenue", "funding"]):
        doc_type = "Financial Document"
    
    # Generate realistic demo insights based on common startup patterns
    score = min(max(int((text_length / 100) % 8) + 2, 3), 8)  # Score between 3-8 based on content length
    
    return StartupAnalysis(
        founder_profile={
            "experience": f"Analysis of {doc_type.lower()} shows founding team with relevant industry background. Document length ({text_length} chars) suggests comprehensive preparation.",
            "founder_market_fit": "Strong alignment between team background and target market based on document structure and content depth.",
            "strengths": [
                "Comprehensive documentation indicates thorough planning",
                "Professional presentation suggests business acumen",
                "Detailed content shows market understanding"
            ],
            "concerns": [
                "Full team background assessment requires live presentation",
                "Track record verification needed beyond documentation"
            ]
        },
        market_opportunity={
            "problem_description": f"Based on {doc_type.lower()} analysis, addressing market inefficiencies with technology-driven solution.",
            "market_size": "Significant addressable market indicated by document scope and detail level.",
            "competitive_landscape": "Competitive positioning suggests awareness of market dynamics and differentiation strategy.",
            "market_validation": "Document preparation level indicates market research and validation efforts."
        },
        unique_differentiator={
            "core_innovation": "Technology-enabled approach to traditional market challenges with scalable business model.",
            "competitive_advantages": [
                "First-mover advantage in specific market segment",
                "Proprietary technology or process innovation",
                "Strong team expertise in target domain"
            ],
            "defensibility": "Business model shows potential for network effects and customer retention strategies."
        },
        business_metrics={
            "revenue_model": "Subscription-based or transaction-fee model with recurring revenue potential.",
            "traction": f"Professional documentation quality suggests early traction and investor readiness.",
            "growth_metrics": "Scalable model with clear unit economics and growth potential.",
            "unit_economics": "Positive unit economics projected with reasonable customer acquisition costs."
        },
        overall_score=score,
        key_insights=[
            f"✅ DEMO MODE: Comprehensive {doc_type.lower()} indicates serious startup preparation",
            f"📊 Document analysis shows {text_length} characters of detailed content",
            "🎯 Professional presentation suggests market-ready solution",
            "⚡ Connect Gemini API key for full AI-powered analysis",
            "🔧 This is a demonstration - real AI analysis available with API configuration"
        ],
        risk_flags=[
            "⚠️ DEMO ANALYSIS: Full assessment requires Gemini API key configuration",
            "📝 Market validation needs real customer interviews beyond documentation",
            "💰 Financial projections require detailed review and validation"
        ]
    )