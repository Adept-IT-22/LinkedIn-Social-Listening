import logging.config
import os
import re
import json
import time
import logging
import pandas as pd
from linkedin_api import Linkedin

#set log.info to be the default logging status
#logging.basicConfig(level=logging.INFO)

rate_limit_seconds = 1

#Create client
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin('mark.mathenge@riarauniversity.ac.ke', LINKEDIN_PASSWORD)

#Ideal Customer Profile
icp = ["founder", "ceo", "leader", "manager", "specialist"]
company_icp = []

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
def search_posts(params: dict) -> list:
    try:
        print("Search starting...")
        search = api.search(params, limit = 10)
        print("Search ended!")
        time.sleep(rate_limit_seconds)
        return search
    except Exception as e:
        logging.error(f"Error during search {e}")
        return []

#Get authors
def get_authors():
    print("Getting authors...")
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

            #get urn from actornavigationurl
            company_urn = re.search(r"(?<=/in/)[^?]+", company)
            
            #if urn exists use it to find company name
            if company_urn:
                shortened_company_urn = str(company_urn.group(0))
                company_name = find_company_name(shortened_company_urn)
            else:
                company_name = "Company Not Found"
            
            #create person variable and add person to authors list
            person = name + " - " + job + " - " + company_name
            authors.add(person)
        
        #change start offset and go again
        start_offset += page_size

    #store info in authors.txt file
    df_authors = pd.DataFrame(authors)
    authors_csv_filename = "authors.csv"
    if not os.path.exists(authors_csv_filename):
        df_authors.to_csv(authors_csv_filename, index=False)
    else:
        df_authors.to_csv(authors_csv_filename, mode='a', header=False, index=False)

    print("Authors saved to CSV!")
    return list(authors)

#Find Company Name
def find_company_name(name: str) -> str:
    #get company name & location from person's profile
    individual_profile = api.get_profile(name)

    #company info is located in experience dictionary
    experience = individual_profile["experience"][0]
    company_name = experience["companyName"]
    company_location = experience.get("geoLocationName")
    if not company_location:
        company_location = "Location Not Found"

    #return company details
    company_details = company_name + ", " + company_location
    return company_details

#Match with ICPs
def icp_role_match():
    print("Matching against ICPs...")
    qualified_authors = []
    authors_in_right_locations = []
    right_location_right_job = []

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
        company_location = parts[2].strip()

        #check if job is in america, europe or africa
        correct_location = ["United States", "Nigeria", "South Africa", "Kenya", "Egypt"]
        for location in correct_location:
            if re.search(r"\b" + re.escape(location) + r"\b", company_location, flags=re.IGNORECASE):
                authors_in_right_locations.append(name + " - " + job + " - " + company_location)
                break

    #save authors in right locations in csv
    df_right_location = pd.DataFrame(authors_in_right_locations)
    right_location_filename = "correct_location.csv"
    if not os.path.exists(right_location_filename):
        df_right_location.to_csv(right_location_filename, index=False)
    else:
        df_right_location.to_csv(right_location_filename, mode='a', index=False, header=False)

    logging.info("Authors in right location saved to CSV!")

    #filter authors from right location based on job
    for role in icp:
        if re.search(r"\b" + re.escape(role) + r"\b", str(authors_in_right_locations), flags=re.IGNORECASE):
            right_location_right_job.append(name)
            break

    df_right_location_right_job = pd.DataFrame(right_location_right_job)
    right_location_right_job_filename = "right_location_right_job.csv"
    if not os.path.exists(right_location_right_job_filename):
        df_right_location_right_job.to_csv(right_location_right_job_filename, index=False)
    else:
        df_right_location_right_job.to_csv(right_location_right_job_filename, mode='a', index=False, header=False)
        
    logging.info("Authors in right location with right job saved to CSV!")

    return right_location_right_job

    #check if role in icp is in author's job
    # for role in icp:
    #     if re.search(r"\b" + re.escape(role) + r"\b", job, flags=re.IGNORECASE):
    #         qualified_authors.append(name) #add author to qualified authors list
    #         break #stop checking once match is found

    # #save qualified authors in csv
    # df_qualified_authors = pd.DataFrame(qualified_authors)

    # #if csv already exists, append. else, create new one
    # qualified_authors_csv_filename = "qualified_authors.csv"
    # if not os.path.exists(qualified_authors_csv_filename):
    #     df_qualified_authors.to_csv(qualified_authors_csv_filename, index=False)
    # else:
    #     df_qualified_authors.to_csv(qualified_authors_csv_filename, mode='a', header=False, index=False)

    # print("Qualified Authors saved to CSV!")
    # print(f"Qualified Authors: {qualified_authors}")
    # return df_qualified_authors

icp_role_match()