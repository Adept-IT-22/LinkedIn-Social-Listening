#This module scores a company's industry
from fuzzywuzzy import fuzz

#industry scores
industry_scores = {
    "high": 25,
    "above_average": 20,
    "average": 15,
    "below_average": 10
}


def score_company_industry(company_industry: str, icp_details: dict) -> int:
    if not company_industry or "industries" not in icp_details:
        return 0
    
    #score
    company_industry_score = 0

    #industry match
    matched_company_industry = None

    #highest matched score
    highest_score = 0

    #fuzzy matching
    for industry in icp_details["industries"]:
        current_score = fuzz.partial_ratio(industry.lower(), company_industry.lower())
        if current_score > highest_score:
            matched_company_industry = industry

    if highest_score < 70:
        return 0
    
    #rank industries
    lowercase_industry = matched_company_industry.lower()
    if any(keyword in lowercase_industry for keyword in ["manufacturing"]):
       return industry_scores["high"] 
    elif any(keyword in lowercase_industry for keyword in ["retail"]):
       return industry_scores["above_average"]
    elif any(keyword in lowercase_industry for keyword in ["education", "health care", "finance"]):
       return industry_scores["average"]
    elif any(keyword in lowercase_industry for keyword in ["technology", "education", "nonprofit"]):
       return industry_scores["below_average"]
     