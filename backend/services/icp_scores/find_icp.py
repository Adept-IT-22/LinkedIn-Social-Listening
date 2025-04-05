#This module finds a company's ICP based on their employer count

import re
from utils import icp

#define icps
icps = icp.icps

def find_icp(employee_count: str) -> dict:
    if not employee_count or employee_count == "Employee Count Not Found":
        return None

    #regex pattern to find min to max employees
    pattern = r"(\d+)\s*to\s*(\d+)"
    match = re.search(pattern, employee_count.strip())
    if not match:
        return None
    left_number = int(match.group(1)) if match else None
    right_number = int(match.group(2)) if match else None

    #match the employee count to an icp
    for icp_name, icp_details in icps.items():
        employees = icp_details["employees"]
        if "min" in employees and left_number >= employees["min"]:
            return icp_details
        elif "max" in employees and right_number <= employees["max"]:
            return icp_details
        elif "range" in employees:
            range_min, range_max = employees["range"]
            if (left_number >= range_min and right_number <= range_max):
                return icp_details