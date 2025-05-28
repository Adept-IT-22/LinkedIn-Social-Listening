#This module is used to find companies and info about them
import logging
from services.linkedin_service import get_linkedin_client


#initialize module logger
logger = logging.getLogger(__name__)

def find_company_info(profile_urn: str) -> str:
    try:
        #connection to linkedin
        api = get_linkedin_client()

        #get company name & location from person's profile
        individual_profile = api.get_profile(profile_urn)

        #company info (located in experience dictionary)
        experience = individual_profile.get("experience")
        if not experience:
            return "Company Not Found"
            
        else:
            experience = experience[0] if isinstance(experience, list) else experience

        #Find Company Name
        company_name = experience.get("companyName", "Company Name Not Found") 

        #Find Company Location
        company_location = experience.get("geoLocationName", "Location Not Found")

        #Find Company Industry
        company_industry = experience.get("company", {}).get("industries", [])
        company_industry = company_industry[0] if company_industry else "Industry Not Found"

        #Find Company Size
        company_size = experience.get("company", "Employee Range Not Found")
        #if company size data exists fetch it otherwise return not found 
        if company_size:
            employee_range = company_size.get("employeeCountRange")
            if isinstance(employee_range, dict):
                start = employee_range.get('start', 'Unknown')
                end = employee_range.get('end', 'Unknown')
                employee_range = f"{start} to {end}"
            else:
                employee_range = str(employee_range)

        #return company details
        company_details = f"{company_name} - {company_location} - {company_industry} - {employee_range}"
        return company_details
    
    except Exception as e:
        logging.error(f"Error getting company info: %s", e)
        return "Company Not Found"