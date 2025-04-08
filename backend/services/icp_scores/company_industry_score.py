from utils.industries import industries
from fuzzywuzzy import fuzz, process
from typing import Optional, Dict, Set

# Industry scores with consistent case (all lowercase)
INDUSTRY_SCORES = {
    "score_25": {
        "manufacturing", "finance", "retail", "telecommunications", 
        "software and it services", "transportation and logistics"
    },
    "score_20": {
        "healthcare", "energy and mining", "real estate", "hospitality", 
        "consumer goods", "insurance", "utilities"
    },
    "score_15": {
        "education", "entertainment", "legal", "government administration", 
        "construction", "recreation and travel", "automotive"
    },
    "score_10": {
        "design", "public safety", "agriculture", "nonprofit"
    },
    "score_5": {
        "textiles", "arts", "think tanks", "museums & institutions", 
        "libraries", "wine and spirits"
    }
}

def score_company_industry(company_industry: Optional[str], icp_details: Dict) -> int:
    """Score a company's industry based on ICP preferences."""
    if not company_industry or not icp_details or "industries" not in icp_details:
        return 0
    
    # Find industry with fuzzy matching
    matched_industry = find_industry(company_industry)
    if not matched_industry:
        return 0
    
    # Get score (all comparisons in lowercase)
    industry_key = matched_industry.lower()
    
    if industry_key in INDUSTRY_SCORES["score_25"]:
        return 25
    if industry_key in INDUSTRY_SCORES["score_20"]:
        return 20
    if industry_key in INDUSTRY_SCORES["score_15"]:
        return 15
    if industry_key in INDUSTRY_SCORES["score_10"]:
        return 10
    if industry_key in INDUSTRY_SCORES["score_5"]:
        return 5
    
    return 0

def find_industry(input_industry: str, threshold: int = 70) -> Optional[str]:
    """Fuzzy match an industry string to our canonical list."""
    if not input_industry.strip():
        return None
    
    # Flatten industry mapping
    industry_mapping = {}
    for industry_key, sub_industries in industries.items():
        for sub in sub_industries:
            industry_mapping[sub] = industry_key
    
    # Get best match
    match, score = process.extractOne(input_industry, industry_mapping.keys())
    return industry_mapping[match] if score >= threshold else None