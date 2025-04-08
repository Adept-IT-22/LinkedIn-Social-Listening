#This module scores authors based on icp
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from utils.icp import icps
from services.get_authors_service import get_authors
from services.icp_scores import find_icp, job_title_score, company_industry_score, company_location_score, company_size_score


#initialize module logger
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
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

    #if parts doesnt even have name and job title return none
    if len(parts) < 2:
        return None

    #if there are missing values add empty quotes 
    parts += [""] * (6 - len(parts))

    #store each part in a variable and return 
    return Author (
        name = parts[0],
        job_title = parts[1].lower() if len(parts) > 1 and parts[1] else "Job Title Not Found",
        company_name = parts[2] if len(parts) > 2 and parts[2] else "Company Not Found",
        company_location = parts[3] if len(parts) > 3 and parts[3] else "Location Not Found",
        company_industry = parts[4] if len(parts) > 4 and parts[4] else "Industry Not Found",
        employee_count = parts[5] if len(parts) > 5 and parts[5] else "Employee Count Not Found"       
    )
    
#method to do icp scoring
def icp_scoring(min_score: int = 0) -> List[Dict[str, Union[Dict, str, int]]]:
    logger.info("Icp Scoring Starting...")

    #set to store authors whose score is >50
    qualified_authors = {}

    #get all the authors
    try:
        authors = get_authors()
    except Exception as e:
        logger.error("Couldn't fetch authors: %s", e)
        yield {"error": "Failed to fetch authors"}
        return

    #parse author string
    for author in authors:
        try:
            author = parse_authors(author)
            if not author:
                continue

            #find icp of author
            found_icp = find_icp.find_icp(author.employee_count)
            if not found_icp:
                logger.error("ICP Not Found for %s", author.name)
                continue

            #initialize the key and value of found icp
            icp_key = list(found_icp.keys())[0]
            author_icp = list(found_icp.values())[0]

            #log values of each field
            logger.info("Job Title: %s, Industry: %s, Location: %s, ICP: %s", author.job_title, author.company_industry, author.company_location, icp_key)

            #calculate icp score
            title_score= job_title_score.score_job_title(author.job_title, author_icp) or 0 
            industry_score= company_industry_score.score_company_industry(author.company_industry, author_icp) or 0
            location_score= company_location_score.score_company_location(author.company_location, author_icp) or 0
            size_score= company_size_score.score_company_size(author_icp) or 0

            #calculate total score
            total_score = min(
                title_score + industry_score + location_score + size_score,
                100
            )

            logger.info(
                "Title Score: %d, Insustry Score: %d, Location Score: %d, Size Score: %d", 
                title_score, industry_score, location_score, size_score
            )

            #if score > 50 add author to qualified authors
            if total_score >= min_score:
                yield {
                    "author": {
                        "name": author.name,
                        "job_title": author.job_title,
                        "company": author.company_name,
                        "location": author.company_location,
                        "employee_count": author.employee_count
                    },
                    "icp": next((key for key, value in icps.items() if value == author_icp), "Unknown"),
                    "score": total_score
                }
                logger.info(f"Qualified: {author.name}, {total_score}")

        except Exception as e:
            logger.error(f"Error processing author {author}: {str(e)}")
            yield{"error": f"Failed to process author: {str(e)}"}

    logger.info(f"Found {len(qualified_authors)} Qualified Authors!")
    logger.info("ICP Scoring Completed")
    