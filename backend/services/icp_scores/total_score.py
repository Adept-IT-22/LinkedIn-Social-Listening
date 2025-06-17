#This module calculates the total icp score for an author

#find the icp -> calculate each score -> add them together
#-> return the score
import logging
from utils import icp
from services.icp_scores.find_icp import find_icp
from services.icp_scores.job_title_score import score_job_title
from services.icp_scores.company_size_score import score_company_size
from services.icp_scores.company_industry_score import score_company_industry
from services.icp_scores.company_location_score import score_company_location

logger = logging.getLogger(__name__)

class icp_scorer:
    def __init__(self):
        #import the icps
        self.icps = icp.icps

    def get_icp(self, employee_count:str) -> tuple:
        return find_icp(employee_count)

    def total_score(self, author_data: dict) -> int:
        if not author_data:
            return 0

        #get total score
        logger.info("Calculating total score...\n",)

        try:
            #get the icp
            icp_key, icp_details = self.get_icp(author_data["employee_count"])  
            if not icp_details:
                return 0

            title_score = score_job_title(author_data["job_title"], icp_details)
            industry_score = score_company_industry(author_data["company_industry"], icp_details)
            location_score = score_company_location(author_data["company_location"], icp_details)
            size_score = score_company_size(icp_details)

            total_score = (
                title_score + industry_score + location_score + size_score
            )

            logger.info("Total Score is: %d", total_score)
            logger.info(
                "Title Score: %d\n, Industry Score: %d\n, Location Score: %d\n, Size Score: %d\n", 
                title_score, industry_score, location_score, size_score
            )

            return total_score
        
        except Exception as e:
            logger.error("Error calculating total score: %s", e)
            return 0
