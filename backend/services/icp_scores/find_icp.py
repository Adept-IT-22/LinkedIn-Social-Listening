#This module finds a company's ICP based on their employer count

import re
import logging
from utils import icp
from typing import Dict, Optional


#initialize module logger
logger = logging.getLogger(__name__)

#define icps
icps = icp.icps

#fallback icp in case employee string isn't found
fallback_icp = {
    "job_titles" : set(),
    "industries" : set(),
    "locations" : set(),
    "employee_count" : set(),
}


def find_icp(employee_count: str) -> Optional[tuple[str, dict]]:
    if not employee_count or employee_count == "Employee Count Not Found":
        logger.warning("Missing employee count. ICP not found. Returning fallback ICP.")
        return ("Unknown", fallback_icp)

    #initialize icp to be returned and icp name
    icp_name = None

    # Handle "unknown" cases e.g. employee count is 1 to unknown.
    if "unknown" in employee_count.lower():
        # Extract the known number
        known_num = re.search(r"(\d+)\s*to\s*unknown", employee_count.lower())
        if known_num:
            employee_count = known_num.group(1)
            logger.info("Employee Count: %s", employee_count)
        else:
            return ("Unknown", fallback_icp)

    # Extract numbers (handles both "X to Y" and single numbers)
    numbers = re.findall(r"\d+", employee_count)
    if not numbers:
        return ("Unknown", fallback_icp)

    # Use the first number for comparison
    try:
        emp_count = int(numbers[0])
        logger.info("Emp Count: %d\n", emp_count)
    except ValueError:
        return ("Unknown", fallback_icp)

    # Match against ICP ranges
    for icp_name, icp_details in icps.items():
        employees = icp_details["employees"]
        
        # Check max threshold (Small Businesses)
        if "max" in employees and emp_count <= employees["max"]:
            logger.info(f"ICP Match: {icp_name} (count: {emp_count})")
            return (icp_name, icp_details)
            
        # Check range (Mid-Size and BPO Providers)
        elif "range" in employees:
            range_min, range_max = employees["range"]
            if range_min <= emp_count <= range_max:
                logger.info(f"ICP Match: {icp_name} (count: {emp_count})")
                return (icp_name, icp_details)
                
        # Check min threshold (Large Enterprises)
        elif "min" in employees and emp_count >= employees["min"]:
            logger.info(f"ICP Match: {icp_name} (count: {emp_count})")
            return (icp_name, icp_details)

    logger.warning(f"No ICP match for count: {employee_count}")
    return ("Unknown", fallback_icp)
