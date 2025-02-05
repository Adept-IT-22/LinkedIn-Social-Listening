import os
import re
import json
from linkedin_api import Linkedin

#Create client
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin('markothengo@gmail.com', LINKEDIN_PASSWORD)

#Ideal Customer Profile
icp = ["founder", "ceo", "leader", "manager", "specialist"]

#Search Keywords
keywords = ["call center"]
page_size = 10
max_pages = 5

#Search Paramters
params = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": keywords,
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

#Search for posts based on keywords
def search_posts(params):
    search = api.search(params, limit = 10)
    return search

#Get authors
def get_authors()->list:
    authors = set([])
    start_offset = 0 #where search should start from

    #run this loop max_pages(5) number of times
    for _ in range(max_pages):
        #set start parameter to start_offset and run search_posts
        params["start"] = start_offset 
        posts = search_posts(params)

        #if posts returns nothing stop.
        if not posts:
            break

        #else get name & job of each author
        for post in posts:
            name = post["title"]["text"]
            job = post["primarySubtitle"]["text"]
            company = post["actorNavigationUrl"]
            company_urn = re.search(r"(?<=/in/)[^?]+", company)
            if company_urn:
                shortened_company_urn = str(company_urn.group(0))
            company_name = find_company_name(shortened_company_urn)
            person = name + " - " + job + " - " + company_name 
            authors.add(person)
        start_offset += page_size
    
    return list(authors)

#Find Company Name
def find_company_name(name: str) -> str:
    #if company not found return message
    if name is None:
        return "Company Not Found"
    individual_profile = api.get_profile(name)
    company_name = individual_profile["experience"][0]["companyName"]
    company_location = individual_profile["experience"][0]["geoLocationName"]
    company_details = company_name + ", " + company_location
    print(company_details)
    return company_name

#Match with ICPs
def icp_role_match()->list:
    qualified_authors = []

    #get all authors
    all_authors = get_authors()

    #for each author split their name and job
    for author in all_authors:
        parts = author.split(" - ")

        #if author doesn't have name/job go to next author
        if len(parts) < 2:
            continue
        
        #otherwise split name & job
        name = parts[0].strip()
        job = parts[1].strip()

        #check if role in icp is in author's job
        for role in icp:
            if re.search(r"\b" + re.escape(role) + r"\b", job, flags=re.IGNORECASE):
                qualified_authors.append(name) #add author to qualified authors list
                break #stop checking once match is found

    return qualified_authors

#Get companies for authors
get_authors()
