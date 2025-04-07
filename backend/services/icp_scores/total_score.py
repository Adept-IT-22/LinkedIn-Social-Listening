#This module calculates the total icp score for an author

#find the icp -> calculate each score -> add them together
#-> return the score
from utils import icp
from find_icp import find_icp
from job_title_score import score_job_title
from company_size_score import score_company_size
from company_industry_score import score_company_industry
from company_location_score import score_company_location

class icp_scorer:
    def __init__(self):
        #import the icps
        self.icps = icp.icps

    def get_icp(self, employee_count:str) -> dict:
        return find_icp(employee_count)

    def total_score(self, author_data: dict) -> int:
        if not author_data:
            return 0
        
        #get the icp
        icp_details = self.get_icp(author_data["employees"])  

        if not icp_details:
            return 0
        
        #get total score
        total_score = (
            score_job_title()
        )
