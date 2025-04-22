#This module scores the authors job title
import logging
from fuzzywuzzy import fuzz


#initialize module logger
logger = logging.getLogger(__name__)

#default job titles in case icp is not found and fallback icp is returned
DEFAULT_JOB_TITLES = {
    "Founder", "CEO", "CTO", "CFO", "COO", "Director", "Customer Service"
    "Manager", "Team Lead", "VP", "Head of Department"    
}

def score_job_title(job_title: str, icp_details: dict) -> int:
    if not job_title or not icp_details:
        return 0

    logger.info("Calculating job title score ...\n")

    #get job titles
    job_titles = icp_details.get("job_titles", set())

    #if they don't exist set them to default job titles
    if not job_titles:
        logger.warning("No job titles found. Setting them to Default.")
        job_titles = DEFAULT_JOB_TITLES

    #title that passes fuzzy matching
    matched_job_title = None

    #score for best matching title
    highest_score = 0

    #fuzzy matching
    for title in job_titles:
        current_score = fuzz.token_set_ratio(title.lower(), job_title.lower())
        if current_score > highest_score:
            matched_job_title = title
            highest_score = current_score
            logger.info(f"Trying match: '{title}' vs '{job_title}' = {current_score}")

    #if fuzzy score > 70 a valid job title has been found
    logging.info("Highest score is: %d\n", highest_score)
    if highest_score < 50:
        return 0

    logging.info(f"Matched Job Title: {matched_job_title} and Highest Score: {highest_score}\n")

    #rank the job title
    lowercase_title = matched_job_title.lower()
    if any(keyword in lowercase_title for keyword in ["founder", "chief", "ceo", "cto", "cfo"]):
        logger.info("Job Title Score is 25\n")
        return 25
    elif any(keyword in lowercase_title for keyword in ["director", "vp", "head"]):
        logger.info("Job Title Score is 20\n")
        return 20
    elif "manager" or "lead" or "customer" in lowercase_title:
        logger.info("Job Title Score is 15\n")
        return 15
    elif any(keyword in lowercase_title for keyword in ["specialist", " coordinator"]):
        logger.info("Job Title Score is 10\n")
        return 10
    else:
        logger.info("Job Title Score is 5\n")
        return 5