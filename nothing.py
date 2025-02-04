from linkedin_api import Linkedin
import re
import json
import os

LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin('markothengo@gmail.com', LINKEDIN_PASSWORD)

name = "ACoAAC6QaK0B06e-5mV568GgO-Sqdu05Ce6E7xk"
pattern = r"(?<=urn:li:fs_miniCompany:)\d+$"

def find_company_name(name:str)->str:
    if name is None:
        return "Company not found"
    author = api.get_profile(name)
    print(json.dumps(author, indent = 4))
    company_urn = author["experience"][0]["companyUrn"]
    refined_company_urn = re.search(pattern, company_urn)
    company_id = str(refined_company_urn.group(0))
    company_name = company_name_from_id(company_id)
    return company_name

def company_name_from_id(id:str)->str:
    company_name = api.get_company(id)
    company_name = company_name["name"]
    return company_name


find_company_name(name)
