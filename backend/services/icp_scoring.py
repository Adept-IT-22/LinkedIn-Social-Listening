#This module scores authors based on icp
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from services.get_authors_service import get_authors
from services.icp_scores import find_icp, job_title_score, company_industry_score, company_location_score, company_size_score


#initialize module logger
logger = logging.getLogger(__name__)

@dataclass
class Author:
    name: str
    job_title: str
    company_name: str = "Company Not Found"
    company_industry: str = "Industry Not Found"
    company_location: str = "Location Not Found"
    employee_count: str = "Employee Count Not Found"

#method to parse each string
def parse_authors(author_str: str)-> Optional[Author]:
    #split the string 
    parts = [part.strip() for part in author_str.split(" - ")]

    #if parts doesnt even have name & job title return none
    if len(parts) < 2:
        return None

    #if there are missing values add empty quotes 
    parts += ["" * (6 - len(parts))]

    #store each part in a variable and return 
    return Author (
        name = parts[0],
        job_title = parts[1].lower(),
        company_name = parts[2] or "Company Not Found",
        company_industry = parts[3] or "Industry Not Found",
        company_location = parts[4] or "Location Not Found",
        employee_count = parts[5] or "Employee Count Not Found"       
    )
    
#method to do icp scoring
def icp_scoring(min_score: int = 50) -> Dict[str, int]:
    logging.info("Icp Scoring Starting...")

    #set to store authors whose score is >50
    qualified_authors = {}

    #get all the authors
    try:
        authors = get_authors()
    except Exception as e:
        logging.error("Couldn't fetch authors: %s", e)
        return {}

    #parse author string
    for author in authors:
        author = parse_authors(author)
        if not author:
            continue

        #find icp of author
        author_icp = find_icp.find_icp(author.employee_count)
        if not author_icp:
            logging.error("ICP Not Found")

        #calculate icp score
        score = (
            job_title_score.score_job_title(author.job_title, author_icp) 
            + company_industry_score.score_company_industry(author.company_industry, author_icp)
            + company_location_score.score_company_location(author.company_location, author_icp)
            + company_size_score.score_company_size(author.employee_count, author_icp)
        )

        #score cant be above 100
        total_score = min(score, 100)

        #if score > 50 add author to qualified authors
        if total_score >= min_score:
            qualified_authors[author] = score
            logging.info(f"Qualified: {author.name}, {total_score}")

    logging.info(f"Found {len(qualified_authors)} Qualified Authors!")
    return qualified_authors