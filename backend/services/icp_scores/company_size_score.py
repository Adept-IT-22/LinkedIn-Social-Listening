#This module scores the company size
import logging


#initialize module logger
logger = logging.getLogger(__name__)

def score_company_size(icp_details: dict) -> int:
    if not icp_details or "employees" not in icp_details:
        logger.info("ICP Not Found. Defaulting to 20")
        return 20

    #<50 employees
    if "max" in icp_details["employees"]:
        if icp_details["employees"]["max"] <= 50:
            logger.info("Company Size is <50 employees")
            return 15 

    #51-250 employees
    if "range" in icp_details["employees"]:
        try:
            min_range, max_range = icp_details["employees"]["range"]

            if min_range >= 51 and max_range <= 250:
                logger.info("Company Size is 51-250 employees")
                return 25
                
        except Exception as e:
            logger.error("Invalid Range Format: %s\n", str(e))
            return 20

    #>250 employees
    if "min" in icp_details["employees"]:
        if icp_details["employees"]["min"] >= 250: 
            logger.info("Company Size is >250 employees")
            return 20
    