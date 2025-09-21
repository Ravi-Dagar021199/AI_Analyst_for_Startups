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
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


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
        # Return a default analysis structure if AI fails
        return StartupAnalysis(
            founder_profile={
                "experience": "Analysis failed - please try again",
                "founder_market_fit": "Unable to assess",
                "strengths": [],
                "concerns": ["Analysis error occurred"]
            },
            market_opportunity={
                "problem_description": "Unable to analyze",
                "market_size": "Unknown",
                "competitive_landscape": "Not assessed",
                "market_validation": "Unable to validate"
            },
            unique_differentiator={
                "core_innovation": "Analysis incomplete",
                "competitive_advantages": [],
                "defensibility": "Not assessed"
            },
            business_metrics={
                "revenue_model": "Not provided",
                "traction": "Unable to assess",
                "growth_metrics": "No data available",
                "unit_economics": "Not analyzed"
            },
            overall_score=0,
            key_insights=[f"Analysis failed: {str(e)}"],
            risk_flags=["Technical analysis error - manual review required"]
        )