#This module scores the authors job title
import logging
from fuzzywuzzy import fuzz


#initialize module logger
logger = logging.getLogger(__name__)

#default job titles in case icp is not found and fallback icp is returned
DEFAULT_JOB_TITLES = {
    #Tier 1 (25 pts)
    "Manager", "Head of", "Senior Manager", "Customer Support Manager",
    "Operations Manager", "Contact Center Manager", "Service Delivery Manager",
    "Consultant", "Consultancy", "BPO", "Business Process Outsourcing",

    #Tier 2 (20 pts) => Important but less accessible than managers.
    "Director", "VP", "Vice President", "Senior Director",
    "Managing Director", "Regional Director", "Executive Manager",
    "Country Director", "Director of Operations", "Customer Support Director",
    "VP of Global Services", "Director of IT Services", "Lead",

    #Tier 3 (15 pts) => Low win rate. Often delegate
    "Founder", "CEO", "CTO", "COO", "CFO", "Chief Executive Officer",
    "Chief Operations Officer", "Chief Technology Officer",
    "Chief Financial Officer",

    #Tier 4 (10 pts) => Rarely decision makers.
    "Specialist", "Coordinator"
}

def score_job_title(job_title: str, icp_details: dict) -> int:
    if not job_title or not icp_details:
        return 0

    logger.info("Calculating job title score ...\n")

    #get job titles
    job_titles = icp_details.get("job_titles", DEFAULT_JOB_TITLES)
    logger.debug(f"Job titles to match against: {job_titles}", exc_info=True)

    #title that passes fuzzy matching
    matched_job_title = None

    #score for best matching title
    highest_score = 0

    #fuzzy matching
    for title in job_titles:
        current_score = fuzz.token_set_ratio(title.lower(), job_title.lower())
        logger.debug(f"Matching: {title} vs {job_title} = {current_score}", exc_info=True)
        if current_score > highest_score:
            matched_job_title = title
            highest_score = current_score
            logger.info(f"Matched Job Title: {job_title}, Current Score: {current_score}")

    #if fuzzy score > 60 a valid job title has been found
    logger.info("Matching done. Highest score is: %d\n", highest_score)
    if highest_score < 60:
        logger.info("No strong match found. Best score was %d\n", highest_score)
        return 0

    logger.info(f"Matched Job Title: {matched_job_title}, Highest Score: {highest_score}\n")

    #rank the job title
    lowercase_title = matched_job_title.lower()

    if any(keyword.lower() in lowercase_title for keyword in ["Manager", "Head of", "Senior Manager", "Customer Support Manager",
    "Operations Manager", "Contact Center Manager", "Service Delivery Manager",
    "Consultant", "Consultancy", "BPO", "Business Process Outsourcing"]):
        logger.info("Job Title Score is 25\n")
        return 25

    elif any(keyword.lower() in lowercase_title for keyword in ["Director", "VP", "Vice President", "Senior Director",
    "Managing Director", "Regional Director", "Executive Manager","Country Director", "Director of Operations", 
    "Customer Support Director", "VP of Global Services", "Director of IT Services", "Lead"]):
        logger.info("Job Title Score is 20\n")
        return 20

    elif any(keyword.lower() in lowercase_title for keyword in ["Founder", "CEO", "CTO", "COO", "CFO", "Chief Executive Officer",
    "Chief Operations Officer", "Chief Technology Officer", "Chief Financial Officer"]):
        logger.info("Job Title Score is 15\n")
        return 15

    elif any(keyword.lower() in lowercase_title for keyword in ["Specialist", "Coordinator"]):
        logger.info("Job Title Score is 10\n")
        return 10

    else:
        logger.info("Job Title Score is 5\n")
        return 5
