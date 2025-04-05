#This module scores the company size
import logging

def score_company_size(icp_details: dict) -> int:
    if "employees" not in icp_details:
        return 0
    
    #score
    company_size_score = 0

    #rank company size
    #max employee logic
    if "max" in icp_details["employees"]:
        if icp_details["employees"]["max"] <= 50:
            company_size_score += 5

    #min employee logic
    if "min" in icp_details["employees"]:
        if icp_details["employees"]["min"] >= 250:
            company_size_score += 20

    #range logic
    if "range" in icp_details["employees"]:
        try:
            min_range, max_range = icp_details["employees"]["range"]
            if min_range >= 51 and max_range <= 250:
                company_size_score += 15
            elif max_range >= 1000:
                company_size_score += 25
            logging.info(f"Company Size Score: {company_size_score}")
            return company_size_score

        except Exception as e:
            logging.error(f"Error calculating company size score: %s", str(e))
            return 0

    