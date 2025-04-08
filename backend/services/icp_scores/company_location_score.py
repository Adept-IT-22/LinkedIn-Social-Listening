#This module scores the author's company location
from fuzzywuzzy import fuzz

def score_company_location(company_location:str, icp_details:dict) -> int:
    if not icp_details:
        return 0

    company_location_score = 0
    matched_company_location = None
    
    # Create a flat dictionary of locations mapped to scores
    location_scores = {}

    # Assign predefined scores to each location
    for location in icp_details["locations"].get("North American Countries", []):
        location_scores[location.lower()] = 25
    for location in icp_details["locations"].get("U.S. Cities", []):
        location_scores[location.lower()] = 25
    for location in icp_details["locations"].get("European Countries", []):
        location_scores[location.lower()] = 25
    for location in icp_details["locations"].get("European Cities", []):
        location_scores[location.lower()] = 25
    for location in icp_details["locations"].get("African Countries", []):
        location_scores[location.lower()] = 15
    for location in icp_details["locations"].get("African Cities", []):
        location_scores[location.lower()] = 15

    # Perform fuzzy matching then score
    for loc, score in location_scores.items():
        location_fuzzy_score = fuzz.partial_ratio(loc, company_location.lower())
        if location_fuzzy_score > 70:
            matched_company_location = loc
            company_location_score = score
            break  # Stop at the first match

    # Default score for non-matching locations
    if not matched_company_location:
        company_location_score = 5  

    return company_location_score