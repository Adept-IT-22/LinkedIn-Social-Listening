#This module scores the author's company location
from fuzzywuzzy import fuzz
from utils.locations import locations
import logging

#initialize logger for this module
logger = logging.getLogger(__name__)

#use locations from locations.py if icp is not found
DEFAULT_COMPANY_LOCATIONS = set()
for location_group in locations.values():
    DEFAULT_COMPANY_LOCATIONS.update(location_group)

#Calculate the location's score
def score_company_location(company_location:str, icp_details:dict) -> int | None:
    if not company_location or not icp_details:
        return None #Don't score or show

    icp_locations = icp_details.get("locations", set())

    if not icp_locations:
        logger.warning("No location found. Setting to default")
        icp_locations = {"Default": DEFAULT_COMPANY_LOCATIONS}

    # Create a flat dictionary of locations mapped to scores
    location_scores = {}

    # Assign predefined scores to each location
    for location in icp_locations.get("North American Countries", []):
        location_scores[location.lower()] = 25
    for location in icp_locations.get("U.S. Cities", []):
        location_scores[location.lower()] = 25
    for location in icp_locations.get("European Countries", []):
        location_scores[location.lower()] = 25
    for location in icp_locations.get("European Cities", []):
        location_scores[location.lower()] = 25
    for location in icp_locations.get("African Countries", []):
        location_scores[location.lower()] = 15
    for location in icp_locations.get("African Cities", []):
        location_scores[location.lower()] = 15
    #fallback if icp is not found
    for location in icp_locations.get("Default", []):
        location_scores[location.lower()] = 0

    # Perform fuzzy matching then return score
    for loc, score in location_scores.items():
        location_fuzzy_score = fuzz.partial_ratio(loc, company_location.lower())
        if location_fuzzy_score > 80:
            logger.info("Matched location: %s => Score: %d", loc, score)
            return score

    #Dont score or show if match isn't found
    logger.info("Company location isn't in desired location: %s\n", company_location)
    return None