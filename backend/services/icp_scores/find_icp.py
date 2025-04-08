#This module finds a company's ICP based on their employer count

import re
import logging
from utils import icp
from typing import Dict, Optional


#initialize module logger
logger = logging.getLogger(__name__)

#define icps
icps = icp.icps

def find_icp(employee_count: str) -> Optional[Dict[str, dict]]:
    if not employee_count or employee_count == "Employee Count Not Found":
        return None

    #initialize icp to be returned and icp name
    outgoing_icp = {}
    icp_name = None

    # Handle "unknown" cases
    if "unknown" in employee_count.lower():
        # Extract the known number
        known_num = re.search(r"(\d+)\s*to\s*unknown", employee_count.lower())
        if known_num:
            employee_count = known_num.group(1)
        else:
            return None

    # Extract numbers (handles both "X to Y" and single numbers)
    numbers = re.findall(r"\d+", employee_count)
    if not numbers:
        return None

    # Use the first number for comparison
    try:
        emp_count = int(numbers[0])
    except (ValueError, IndexError):
        return None

    # Match against ICP ranges
    for icp_name, icp_details in icps.items():
        employees = icp_details["employees"]
        
        # Check max threshold (Small Businesses)
        if "max" in employees and emp_count <= employees["max"]:
            logger.info(f"ICP Match: {icp_name} (count: {emp_count})")
            outgoing_icp[icp_name] = icp_details
            return outgoing_icp
            
        # Check range (Mid-Size and BPO Providers)
        elif "range" in employees:
            range_min, range_max = employees["range"]
            if range_min <= emp_count <= range_max:
                logger.info(f"ICP Match: {icp_name} (count: {emp_count})")
                outgoing_icp[icp_name] = icp_details
                return outgoing_icp
                
        # Check min threshold (Large Enterprises)
        elif "min" in employees and emp_count >= employees["min"]:
            logger.info(f"ICP Match: {icp_name} (count: {emp_count})")
            outgoing_icp[icp_name] = icp_details
            return outgoing_icp

    logger.warning(f"No ICP match for count: {employee_count}")
    return None


#def find_icp(employee_count: str) -> dict:
    #if not employee_count or employee_count == "Employee Count Not Found":
        #return None

    ##regex pattern to find min to max employees
    #pattern = r"(\d+)\s*to\s*(\d+)"
    #match = re.search(pattern, employee_count.strip())
    #if not match:
        #return None
    #left_number = int(match.group(1)) if match else None
    #right_number = int(match.group(2)) if match else None

    ##match the employee count to an icp
    #for icp_name, icp_details in icps.items():
        #employees = icp_details["employees"]
        #if "min" in employees and left_number >= employees["min"]:
            #logger.info(f"ICP Name: {icp_name}")
            #return icp_details
        #elif "max" in employees and right_number <= employees["max"]:
            #logger.info(f"ICP Name: {icp_name}")
            #return icp_details
        #elif "range" in employees:
            #range_min, range_max = employees["range"]
            #if (left_number >= range_min and right_number <= range_max):
                #logger.info(f"ICP Name: {icp_name}")
                #return icp_details