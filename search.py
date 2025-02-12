import os
import re
import json
import time
import logging
import pandas as pd
import logging.config
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
                company_info = find_company_info(shortened_company_urn)
            else:
                company_info = "Company Not Found"
            
            #create person variable and add person to authors list
            person = name + " - " + job + " - " + company_info
            print(f"Person: {person}")
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
def find_company_info(name: str) -> str:
    #get company name & location from person's profile
    individual_profile = api.get_profile(name)

    #company info (located in experience dictionary)
    experience = individual_profile.get("experience")[0]
    company_name = experience.get("companyName") 

    company_location = experience.get("geoLocationName")
    if not company_location:
        company_location = "Location Not Found"

    company_size = experience.get("company")

    #if company size data exists fetch it otherwise return not found 
    if company_size:
        employee_range = str(company_size.get("employeeCountRange"))
    else:
        employee_range = "Employee Range Not Found"

    #return company details
    company_details = company_name + " - " + company_location + " - " + employee_range
    return company_details

#Match author with ICPs
def icp_location_match():
    #Log process starting message
    logging.info("Matching against ICPs...")

    #List of qualified authors
    qualified_authors = []
    
    if len(qualified_authors) <= 20:
            
	#get all authors
        all_authors = get_authors()

        #for each author split their name and job
        for author in all_authors:
            parts = author.split(" - ")

            #if author doesn't have name/job go to next author
            if len(parts) < 2:
                continue
            
            #otherwise split author info into pieces
            name = parts[0].strip()
            job_title = parts[1].strip()
            company_name = parts[2].strip() if len(parts) > 2 else "Company Not Found"
            company_location = parts[3].strip() if len(parts) > 3 else "Location Not Found"
            employee_count = parts[4] if len(parts) > 4 else "Employee Range Not Found"
            print(f"Name: {name}, Job Title: {job_title}, Company Name: {company_name}, Company Location: {company_location}, Employee Count: {employee_count}")
            
            #save author if they have the right job title & company based on location & employee count
            if job_title in icp and company_location == "Kenya" and dict(employee_count).get("end"):
                qualified_authors.append(author) 
                print(f"Qualified Author: {author}")
            else:
                continue 

            #Save qualified authors to csv
            df_qualified_authors = pd.DataFrame(qualified_authors)
            qualified_authors_filename = "qualified_authors.csv"
            if not os.path.exists(qualified_authors_filename):
                df_qualified_authors.to_csv(qualified_authors_filename, index=False)
            else:
                df_qualified_authors.to_csv(qualified_authors_filename, mode='a', index=False, header=False)

    #Log success message
    logging.info("Qualified authors saved to CSV!")

    #Return list of qualified authors
    return qualified_authors

icp_location_match()
