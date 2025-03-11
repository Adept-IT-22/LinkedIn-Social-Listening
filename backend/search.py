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
from io import BytesIO
from datetime import date
from fuzzywuzzy import fuzz
from flask_cors import CORS
from linkedin_api import Linkedin
from fake_useragent import UserAgent
from flask import Flask, jsonify, request, Response, stream_with_context, send_file
import requests.cookies

#Create Flask object
app = Flask(__name__)
CORS(app)

#create session
session = requests.Session()

#Authentication Cookies & Headers
cookies = {
        "li_at": "AQEDAVDHmcQEYhxUAAABlX87uiAAAAGVo0g-IE4AvXBob9udp9P6I9qVPBnaJAQLepCAWX-FLvuiL2sJ4dcEJ8DJXrwPnEIrrOgyV3GyEHLs8CBIDMKvoDRc_eXGp2l9zUUK4V6DH50iP6XoM3Es3cVZ",
        "JSESSIONID" : "ajax:1317021214470204667" 
        }

#Change cookie dictionary to RequestsCookieJar
cookie_jar = requests.cookies.RequestsCookieJar()
for name,value in cookies.items():
    cookie_jar.set(name, value)

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
session.cookies.update(cookie_jar)
session.headers.update(get_header())

#Create client
api = Linkedin(username="m10mathenge@gmail.com", password="markothengo99", cookies=cookie_jar)

#Locations
locations ={
    #North American Countries
    "North American Countries": { "united states", "canada"},
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
    "employees": {"range": (201, 1000)},
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
page_size = 3 #number of authors to fetch per page
max_pages = 1 #number of pages to fetch

#Search Paramters
params = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": " OR ".join(keywords),
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

#Global variable to store authors
all_authors_cache = []

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

#Get authors
def get_authors(): 
    logging.info("Getting authors...")
    start_offset = 0 #where search should start from
    yield_counter = 0 #number of authors yielded
    seen_authors = set() #set of seen authors

    #run this loop max_pages number of times
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
            if person not in seen_authors:
                logging.info(f"NEW AUTHOR FOUND: {person}") #CHANGE BACK TO NAME NOT PERSON
                yield person
                yield_counter += 1
                seen_authors.add(person)
        
        #change start offset and go again
        start_offset += page_size
        #delay to make it feel like real time streaming
        time.sleep(random.uniform(5,10))

    #number of authors yielded
    logging.info(f"Total authors yielded: {yield_counter}")


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
            experience = experience[0] if isinstance(experience, list) else experience

    #Find Company Name
    company_name = experience.get("companyName") 
    if not company_name:
        company_name = "Company Name Not Found"

    #Find Company Location
    company_location = experience.get("geoLocationName")
    if not company_location:
        company_location = "Location Not Found"

    #Find Company Industry
    company_industry = experience.get("company", {}).get("industries", [])
    company_industry = company_industry[0] if company_industry else "Company Not Found"
    if not company_industry:
        company_industry = "Industry Not Found"

    #Find Company Size
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
    company_details = f"{company_name} - {company_location} - {company_industry} - {employee_range}"
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
        company_industry = parts[3].strip() if len(parts) > 3 and parts[3].strip() else "Industry Not Found"
        company_location = parts[4].strip() if len(parts) > 4 and parts[4].strip() else "Location Not Found"
        employee_count = parts[5].strip() if len(parts) > 5 and parts[5].strip() else "Employee Range Not Found"
        
        #regex pattern to find min employees
        pattern = r"(\d+)\s*to\s*(\d+)"
        match = re.search(pattern, employee_count.strip())
        left_number = int(match.group(1)) if match else None
        right_number = int(match.group(2)) if match else None

        #check if author matches ICP
        job_title_match = any(fuzz.partial_ratio(word, job_title) > 70 for word in icp["job title"] ) 
        location_match = any(location.lower() in company_location.lower() for location in icp["locations"] )

        #employee match logic
        employee_match = False
        if "max" in icp["employees"]: #we're looking for max employees
            employee_match = left_number is not None and left_number <= icp["employees"]["max"]
        elif "min" in icp["employees"]: #we're looking for min employees
            employee_match = right_number is not None and right_number >= icp["employees"]["min"]
        elif "range" in icp["employees"]: #we're looking for a range of employees
            min_employees, max_employees = icp["employees"]["range"]
            employee_match = left_number is not None and right_number is not None and left_number >= min_employees and right_number <= max_employees

        #if all matches, add to qualified authors
        if job_title_match and location_match and employee_match:
            logging.info(f"Qualified Author Found: {name}, {company_location}")
            qualified_authors.append(author)

    return qualified_authors

#Save data to excel
def save_to_excel(data_for_dataframe: list):
    # Parse the data into structured format
    parsed_data = []
    for row in data_for_dataframe:
        # Split by ' - ' and handle cases where there might be extra dashes in the text
        parts = row.split(' - ')
        if len(parts) >= 5:  # Ensure we have enough parts
            name = parts[0].strip()
            job_title= parts[1].strip()
            company_name = parts[2].strip()
            company_industry = parts[3].strip()
            company_location = parts[4].strip()
            employee_count = parts[5].strip() if len(parts) > 5 else 'Unknown'

            parsed_data.append([name, job_title, company_name, company_industry, company_location, employee_count])
    
    # Create DataFrame with specific columns
    df = pd.DataFrame(parsed_data, columns=["Name", "Job Title", "Company Name", "Company Industry" "Company Location", "Employee Count"])
    
    #Write dataframe to a ByteIO object
    today = str(date.today())
    output = BytesIO()
    with pd.ExcelWriter(output ,engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=today)
    output.seek(0) #Move the file pointer to the beginning of the stream

    logging.info(f"Data saved in Excel!")
    return output

#Add flask routes
@app.route('/all-authors', methods = ['GET'])
def get_all_authors():
    global all_authors_cache
    
    #Reset the cache so all-authors always starts w/a fresh list of authors
    all_authors_cache = [] 

    #generator function to yield authors
    def generate():
        try:
            #fetch all authors and yield each one
            all_authors = get_authors()
            for author in all_authors:
                all_authors_cache.append(author)
                yield f"data: {json.dumps({"author": author})}\n\n"
        
        #if the fetch fails yield an error message
        except Exception as e:
            yield f"data: {json.dumps({"error": str(e)})}"
    
    #stream the authors as they roll in
    return Response(stream_with_context(generate()), content_type='text/event-stream')


@app.route('/get-qualified-leads', methods=['GET'])
def generate_qualified_leads():
    try:
        #get the icp in the request parameters
        selected_icp = requests.args.get('icp', 'all')
        icp = icps.get(selected_icp)

        #if icp is all fetch all authors
        if icp == "all":
            all_authors = get_authors(icp)
            return jsonify({
                "status": "success",
                "message": f"Found {len(all_authors)} authors",
                "allAuthors": all_authors
            })
        else:
            #otherwise fetch qualified leads based on icp
            qualified_leads = icp_match()
            return jsonify({
                "status" : "success",
                "message" : f"Found {len(qualified_leads)} qualified leads",
                "qualifiedLeads" : qualified_leads
            })
    #if it fails return an error
    except Exception as e:
        return jsonify({
            "status": "error",
            "message" : str(e)
        }), 500

#Download Excel File
@app.route('/download-excel', methods=['GET'])
def download_excel():
    try:
        downloadable_excel_file = "Social Listening Results.xlsx"

        #Get qualified leads
        qualified_leads = all_authors_cache

        #save qualified leads to excel
        saved_file = save_to_excel(qualified_leads)

        #Make file downloadable
        return send_file(
            saved_file,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            as_attachment=True,
            download_name=downloadable_excel_file
            )
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message" : str(e)
        }), 500
    

#run the program
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, 
                        encoding="utf-8",
                        format = "%(asctime)s - %(levelname)s - %(message)s")
    app.run(debug = True)
