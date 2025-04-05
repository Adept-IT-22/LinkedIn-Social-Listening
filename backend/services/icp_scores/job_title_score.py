#This module scores the authors job title
import logging
from fuzzywuzzy import fuzz

#ADD WHEN BACK IN OFFICE!
TITLE_SCORES = {
}

def score_job_title(job_title: str, icp_details: dict) -> int:
    if not job_title or not icp_details["job_titles"]:
        return 0

    #score
    job_title_score = 0

    #title that passes fuzzy matching
    matched_job_title = None

    #score for best matching title
    highest_score = 0

    #fuzzy matching
    for title in icp_details["job_titles"]:
        current_score = fuzz.partial_ratio(title.lower(), job_title.lower())
        if current_score > highest_score:
            matched_job_title = title

    #if fuzzy score > 70 a valid job title has been found
    if highest_score < 70:
        return 0

    logging.info(f"Matched Job Title: {matched_job_title} and Highest Score: {highest_score}")

    #rank the job title
    if any(keyword in matched_job_title.lower() for keyword in ["founder", "chief", "ceo", "cto", "cfo"]):
        job_title_score += 25
    elif any(keyword in matched_job_title.lower() for keyword in ["director", "vp", "head"]):
        job_title_score += 20
    elif "manager" in matched_job_title.lower():
        job_title_score += 15
    elif any(keyword in matched_job_title.lower() for keyword in ["specialist", " coordinator"]):
        job_title_score += 10
    else:
        job_title_score += 5

    return job_title_score