from utils.industries import industries
from fuzzywuzzy import process
from typing import Optional, Dict, Set
import logging

logger = logging.getLogger(__name__)

# Industry scores with consistent case (all lowercase)
INDUSTRY_SCORES = {
    "score_25": {
        "legal", "healthcare", "nonprofit", "corporate services"
    },
    "score_20": {
        "insurance", "software and it services"
    },
    "score_15": {
        "finance", "telecommunications", "retail"
    },
    "score_10": {
        "manufacturing", "transportation and logistics", "real estate" 
    },
    "score_5": {
        "education", "government administration", "arts", "textiles"
    }
}

#default industries in case icp is not found
DEFAULT_COMPANY_INDUSTRIES = set(industries.keys())

def score_company_industry(company_industry: Optional[str], icp_details: Dict) -> int:
    """Score a company's industry based on ICP preferences."""
    if not company_industry or not icp_details:
        return 0

    logger.info("Company Industry Scoring Starting...")

    #get industries
    icp_industries = icp_details.get("industries", {"Default": DEFAULT_COMPANY_INDUSTRIES})

    # Find industry with fuzzy matching
    matched_industry = find_industry(company_industry)
    if not matched_industry:
        logger.debug("Find_industry method has returned nothing")
        return 0
    
    # Get score (all comparisons in lowercase)
    industry_key = matched_industry.lower()
    logger.info("Scoring matched industry: %s\n", industry_key)
    
    if industry_key in INDUSTRY_SCORES["score_25"]:
        logger.info("Company industry score is 25\n")
        return 25
    elif industry_key in INDUSTRY_SCORES["score_20"]:
        logger.info("Company industry score is 20\n")
        return 20
    elif industry_key in INDUSTRY_SCORES["score_15"]:
        logger.info("Company industry score is 15\n")
        return 15
    elif industry_key in INDUSTRY_SCORES["score_10"]:
        logger.info("Company industry score is 10\n")
        return 10
    elif industry_key in INDUSTRY_SCORES["score_5"]:
        logger.info("Company industry score is 5\n")
        return 5
    
    logger.info("Company Industry Score is 0")
    return 0

def find_industry(input_industry: str, threshold: int = 60) -> Optional[str]:
    """Fuzzy match an industry string to our canonical list."""
    if not input_industry.strip():
        return None
    
    #Check for exact matches against industries
    for industry_key in industries.keys():
        if input_industry.lower() == industry_key.lower():
            return industry_key

    #Check for exact matches against sub industries
    for industry_key, sub_industries in industries.items():
        if any(input_industry.lower() == industry.lower() for industry in sub_industries):
            return industry_key

    #Otherwise do fuzzy matching
    #Flatten industry mapping
    industry_mapping = {}
    for industry_key, sub_industries in industries.items():
        for sub in sub_industries:
            industry_mapping[sub] = industry_key
    
    # Get best match
    match, score = process.extractOne(input_industry, industry_mapping.keys())
    canonical = industry_mapping.get(match)

    logger.info("Matched industry: %s, Canonical: %s => Score: %d", match, canonical, score)
    return canonical if score >= threshold else None