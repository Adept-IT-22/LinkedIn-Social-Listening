import os
import re
import ast
import json
import time
import random
import logging
import requests
import pandas as pd
import logging.config
from fuzzywuzzy import fuzz
from flask_cors import CORS
from linkedin_api import Linkedin
from fake_useragent import UserAgent
from flask import Flask, jsonify, request

#Create Flask object
app = Flask(__name__)
CORS(app)

#create session
session = requests.Session()

#Authentication Cookies & Headers
cookies = {
        "li_at": "AQEDAVDHmcQFX63iAAABlSfcq4EAAAGVS-kvgU4ABJVuzulfMAmE-H6V080_aaQ7cwJRnMmcdFVzy3GlpiRC0esxHMXppqaUc-AsobphBJpIXUq8Qnfvj6ImWNW2WG_H9p6om3JE4QkNCStVUutadgAz"
        }

#Initialize Session User Agent
session_user_agent = None

#get header for the session
def get_header():
    global session_user_agent
    if session_user_agent is None:
        ua = UserAgent()
        session_user_agent = ua.random
    return {"User-Agent": session_user_agent}

#inject cookies & headers into session
session.cookies.update(cookies)
session.headers.update(get_header())

#Create client
linkedin_email = "m10mathenge@gmail.com"
linkedin_password = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin(linkedin_email, linkedin_password)

#Locations
locations ={
    #North American Countries
    "North American Countries": {
    "united states", "canada"},
    
    #African Countries
    "African Countries": {
    "algeria", "angola", "benin", "botswana", "burkina faso", 
    "burundi", "cabo verde", "cameroon", "central african republic",
    "chad", "comoros", "democratic republic of the congo", "djibouti",
    "egypt", "equatorial guinea", "eritrea", "eswatini", "ethiopia",
    "gabon", "gambia", "ghana", "guinea", "guinea-bissau", "ivory coast",
    "kenya", "lesotho", "liberia", "libya", "madagascar", "malawi",
    "mali", "mauritania", "mauritius", "morocco", "mozambique",
    "namibia", "niger", "nigeria", "republic of the congo", "rwanda",
    "sao tome and principe", "senegal", "seychelles", "sierra leone",
    "somalia", "south africa", "south sudan", "sudan", "tanzania",
    "togo", "tunisia", "uganda", "zambia", "zimbabwe"},
    
    #African Cities
    "African Cities": {
    "lagos", "cairo", "kinshasa", "johannesburg", "nairobi",
    "addis ababa", "dar es salaam", "alexandria", "abidjan", "casablanca",
    "cape town", "accra", "algiers", "luanda", "dakar",
    "khartoum", "kigali", "tunis", "kampala", "lusaka",
    "maputo", "pretoria", "yaoundé", "bamako", "harare",
    "mogadishu", "port harcourt", "ibadan", "ouagadougou", "antananarivo",
    "brazzaville", "windhoek", "gaborone", "freetown", "bujumbura"},
    
    #European Countries
    "European Countries": {
    "austria", "belgium", "bulgaria", "croatia", "cyprus",
    "czech republic", "denmark", "estonia", "finland", "france",
    "germany", "greece", "hungary", "ireland", "italy", "latvia",
    "lithuania", "luxembourg", "malta", "netherlands", "poland",
    "portugal", "romania", "slovakia", "slovenia", "spain", "sweden",
    "albania", "andorra", "belarus", "bosnia and herzegovina",
    "iceland", "kosovo", "liechtenstein", "moldova", "monaco",
    "montenegro", "north macedonia", "norway", "san marino", "serbia",
    "switzerland", "ukraine", "united kingdom", "vatican city"},

    #European Cities
    "European Cities": {
    "london", "paris", "berlin", "madrid", "rome",
    "vienna", "amsterdam", "brussels", "stockholm", "oslo",
    "copenhagen", "helsinki", "lisbon", "prague", "budapest",
    "warsaw", "athens", "dublin", "zurich", "barcelona",
    "munich", "milan", "hamburg", "frankfurt", "bucharest",
    "sofia", "zagreb", "belgrade", "riga", "vilnius",
    "tallinn", "luxembourg", "ljubljana", "sarajevo", "bratislava",
    "reykjavik", "valletta", "podgorica", "skopje", "tirana"},
    
    #U.S. Cities
    "U.S. Cities": {
    "new york city", "los angeles", "chicago", "houston", "phoenix",
    "philadelphia", "san antonio", "san diego", "dallas", "san jose",
    "austin", "jacksonville", "fort worth", "columbus", "charlotte",
    "san francisco", "indianapolis", "seattle", "denver",
    "washington, d.c.", "boston", "el paso", "nashville", "detroit",
    "oklahoma city", "portland", "las vegas", "memphis", "louisville",
    "baltimore", "milwaukee", "albuquerque", "tucson", "fresno",
    "sacramento", "kansas city", "mesa", "atlanta", "omaha",
    "colorado springs", "raleigh", "miami", "long beach",
    "virginia beach", "oakland", "minneapolis", "tulsa", "tampa",
    "arlington", "new orleans"}
}

#Ideal Customer Profile
icps = { 
    "icp1": { 
        "job title": {
        "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        "customer"
    },
    "employees": {"max": 50},
    "locations": locations
    },

    "icp2": { 
        "job title": {
        "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        "customer"
    },
    "employees": {"range": (51, 200)},
    "locations": locations
    },

    "icp3": { 
        "job title": {
        "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        "customer"
    },
    "employees": {"min": 201},
    "locations": locations
    },

    "icp4": { 
        "job title": {
        "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        "customer"
    },
    "employees": {"min": 1001},
    "locations": locations
    }
 }

#Search settings
keywords = ["call center","contact center", "call center outsourcing", 
            "customer service", "customer support", 
            "customer service outsourcing", "customer service automation", 
            "customer service software"
            ]
page_size = 10
max_pages = 10

#Search Paramters
params = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": " OR ".join(keywords),
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

#Search for posts based on keywords
def search_posts(params: dict) -> list:
    all_results = []
    try:
        for i in range(0, len(keywords), 3):
            #Get next 3 keywords or remaining if less than 3
            keyword_group = keywords[i:i+3]
            combined_keywords = " OR ".join(keyword_group)

            logging.info(f"Search for {combined_keywords} starting...")

            #Create copy of params for each group
            current_params = params.copy()
            current_params["keywords"] = combined_keywords

            #Run the search
            search_results = api.search(current_params, limit=10)

            #Add results to all_results
            if search_results:
                all_results.extend(search_results)
                print(f"Found {len(search_results)} people for group {keyword_group}")
            else:
                print(f"No results for {combined_keywords}")
            time.sleep(random.uniform(5, 10))
            
        return all_results
    except Exception as e:
        logging.error(f"Error during search {e}")
        return []

#Get companies
def get_companies() -> list:
    logging.info("Getting companies...")
    companies = []
    results = api.search_companies(keywords=keywords)
    companies.append(results)
    return companies

#Get authors
def get_authors() -> list:
    logging.info("Getting authors...")
    authors = []
    start_offset = 0 #where search should start from

    #run this loop max_pages(5) number of times
    for _ in range(max_pages):
        #set start parameter to start_offset and run search_posts
        params["start"] = start_offset 
        posts = search_posts(params)

        #if posts returns nothing stop.
        if not posts:
            logging.error("No search results found")
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
            logging.info(f"NEW AUTHOR FOUND: {name}")
            authors.append(person)
        
        #change start offset and go again
        start_offset += page_size

    #store info in authors.csv file
    save_to_excel(authors, "Thursday.xlsx", "All Authors")
    logging.info("Authors saved to Excel!")
    return list(authors)

#Find Company Info
def find_company_info(name: str) -> str:
    #get company name & location from person's profile
    individual_profile = api.get_profile(name)

    #company info (located in experience dictionary)
    experience = individual_profile.get("experience")
    if not experience:
        return "Company Not Found"
    else:
        if isinstance(experience, list):
            experience = experience[0]

    company_name = experience.get("companyName") 
    if not company_name:
        company_name = "Company Name Not Found"

    company_location = experience.get("geoLocationName")
    if not company_location:
        company_location = "Location Not Found"

    company_size = experience.get("company")

    #if company size data exists fetch it otherwise return not found 
    if company_size:
        employee_range = company_size.get("employeeCountRange")
        if isinstance(employee_range, dict):
            employee_range = f"{employee_range.get('start', 'Unknown')} to {employee_range.get('end', 'Unknown')}"
        else:
            employee_range = str(employee_range)
    else:
        employee_range = "Employee Range Not Found"

    #return company details
    company_details = f"{company_name} - {company_location} - {employee_range}"
    return company_details

#Match author with ICPs
def icp_match(icp: dict):
    #Log process starting message
    logging.info("Matching against ICPs...")

    #List of qualified authors
    qualified_authors = []
    
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
        job_title = parts[1].strip().lower()
        company_name = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Company Not Found"
        company_location = parts[3].strip() if len(parts) > 3 and parts[3].strip() else "Location Not Found"
        employee_count = parts[4].strip() if len(parts) > 4 and parts[4].strip() else "Employee Range Not Found"
        
        #regex pattern to find max employees
        pattern = r"(\d+)$"
        right_match = re.search(pattern, employee_count.strip())
        num_employees = int(right_match.group(1)) if right_match else None

        #regex pattern to find min employees
        pattern = r"^\d+"
        left_match = re.search(pattern, employee_count.strip())
        num_employees = int(left_match.group(1)) if left_match else None

        #check if author matches ICP
        job_title_match = any(fuzz.partial_ratio(word, job_title) > 70 for word in icp["job title"] ) 
        location_match = any(location.lower() in company_location.lower() for location in icp["locations"] )
        #employee match logic
        employee_match = False
        if "max" in icp["employees"]: #we're looking for max employees
            employee_match = num_employees is not None and num_employees <= icp["employees"]["max"]
        elif "min" in icp["employees"]: #we're looking for min employees
            employee_match = num_employees is not None and num_employees >= icp["employees"]["min"]
        elif "range" in icp["employees"]: #we're looking for a range of employees
            min_employees, max_employees = icp["employees"]["range"]
            employee_match = num_employees is not None and min_employees <= num_employees <= max_employees

        #if all matches, add to qualified authors
        if job_title_match and location_match and employee_match:
            logging.info(f"Qualified Author Found: {name}, {company_location}")
            qualified_authors.append(author)

    #Save qualified authors to csv
    save_to_excel(qualified_authors, "Thursday.xlsx", "Qualified Authors")
    logging.info("Qualified authors saved to Excel!")
    return qualified_authors

#Save data to excel
def save_to_excel(data_for_dataframe: list, storage_filename: str, sheet_name: str = 'Sheet1') -> None:
    # Convert filename to .xlsx if it doesn't already have the extension
    if not storage_filename.endswith('.xlsx'):
        storage_filename = storage_filename.rsplit('.', 1)[0] + '.xlsx'
    
    # Parse the data into structured format
    parsed_data = []
    for row in data_for_dataframe:
        # Split by ' - ' and handle cases where there might be extra dashes in the text
        parts = row.split(' - ')
        if len(parts) >= 4:  # Ensure we have enough parts
            parsed_row = {
                'Name': parts[0].strip(),
                'Job Title': parts[1].strip(),
                'Company Name': parts[2].strip(),
                'Company Location': parts[3].strip(),
                'Company Employee Count': parts[4].strip() if len(parts) > 4 else 'Unknown'
            }
            parsed_data.append(parsed_row)
    
    # Create DataFrame with specific columns
    df = pd.DataFrame(parsed_data)
    
    if not os.path.exists(storage_filename):
        df.to_excel(storage_filename, index=False)
    else:
        with pd.ExcelWriter(storage_filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

    logging.info(f"Data saved to {storage_filename} in sheet {sheet_name}!")

#mockup, not the real thing
def mockup_search():
    return [
        "John - CEO - Google - Mountain View - 10000",
        "Jane - CTO - Facebook - Menlo Park - 50",
        "Jim - VP of Sales - Apple - Cupertino - 20",
        "Jill - Director of Marketing - Amazon - Seattle - 20000"
    ]

#Add flask routes
@app.route('/all-authors', methods = ['GET'])
def get_all_authors():
    try:
        all_authors = get_authors()
        return jsonify({
            "status": "success",
            "message": f"Found {len(all_authors)} authors",
            "allAuthors": all_authors
        })
    except Exception as e:
        return jsonify({
            "status": "Error",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
#def generate_mockup_leads():
    #try:
        #leads = mockup_search()
        #return jsonify({
            #"status": "success",
            #"message": f"Found {len(leads)} mockup leads",
            #"Qualified Leads": leads
        #})
    #except Exception as e:
        #return jsonify({
            #"status": "Error",
            #"message": f"The following error was encountered: {str(e)}"
        #}), 500
def generate_qualified_leads():
    try:
        selected_icp = requests.args.get('icp', 'all')
        icp = icps.get(selected_icp)

        if icp == "all":
            all_authors = get_authors(icp)
            return jsonify({
                "status": "success",
                "message": f"Found {len(all_authors)} authors",
                "allAuthors": all_authors
            })
        else:
            qualified_leads = icp_match()
            return jsonify({
                "status" : "success",
                "message" : f"Found {len(qualified_leads)} qualified leads",
                "qualifiedLeads" : qualified_leads
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message" : str(e)
        }), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, 
                        encoding="utf-8",
                        format = "%(asctime)s - %(levelname)s - %(message)s")
    app.run(debug = True)

