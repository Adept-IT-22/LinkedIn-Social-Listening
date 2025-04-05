#This module scores authors based on icp
import logging
from get_authors_service import get_authors

def icp_match(icp: dict):
    #Log process starting message
    logging.info("Matching against ICPs...")

    #List of qualified authors
    qualified_authors = []
    
    #get all authors
    all_authors = get_authors()

    #for each author split their name and job
    for author in all_authors:
        parts = author.split(" - ")

        #if author doesn't have name/job go to next author
        if len(parts) < 6:
            continue
        
        #otherwise split author info into pieces
        name = parts[0].strip()
        job_title = parts[1].strip().lower()
        company_name = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Company Not Found"
        company_industry = parts[3].strip() if len(parts) > 3 and parts[3].strip() else "Industry Not Found"
        company_location = parts[4].strip() if len(parts) > 4 and parts[4].strip() else "Location Not Found"
        employee_count = parts[5].strip() if len(parts) > 5 and parts[5].strip() else "Employee Range Not Found"
        
        #job title match


       #check if location is right 


        #regex pattern to find min employees
        pattern = r"(\d+)\s*to\s*(\d+)"
        match = re.search(pattern, employee_count.strip())
        left_number = int(match.group(1)) if match else None
        right_number = int(match.group(2)) if match else None

        #employee match logic
        employee_match = False
        if "max" in icp["employees"]: #we're looking for max employees
            employee_match = left_number is not None and left_number <= icp["employees"]["max"]
        elif "min" in icp["employees"]: #we're looking for min employees
            employee_match = right_number is not None and right_number >= icp["employees"]["min"]
        elif "range" in icp["employees"]: #we're looking for a range of employees
            min_employees, max_employees = icp["employees"]["range"]
            employee_match = left_number is not None and right_number is not None and left_number >= min_employees and right_number <= max_employees

        #if all matches, add to qualified authors
        if job_title_match and location_match and employee_match:
            logging.info(f"Qualified Author Found: {name}, {company_location}")
            qualified_authors.append(author)

    return qualified_authors