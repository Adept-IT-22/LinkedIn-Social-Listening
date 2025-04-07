from config import logging_config
import os
import re
import ast
import json
import time
import random
import logging
import psycopg
import requests
import pandas as pd
import logging.config
from io import BytesIO
from datetime import date
from fuzzywuzzy import fuzz
from flask_cors import CORS
from linkedin_api import Linkedin
from fake_useragent import UserAgent
from transformers import pipeline, AutoTokenizer
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
#icps = { 
    #"icp1": { 
        #"job title": {
        #"founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        #"customer"
    #},
    #"employees": {"max": 50},
    #"locations": locations
    #},

    #"icp2": { 
        #"job title": {
        #"founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        #"customer"
    #},
    #"employees": {"range": (51, 200)},
    #"locations": locations
    #},

    #"icp3": { 
        #"job title": {
        #"founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        #"customer"
    #},
    #"employees": {"range": (201, 1000)},
    #"locations": locations
    #},

    #"icp4": { 
        #"job title": {
        #"founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
        #"customer"
    #},
    #"employees": {"min": 1001},
    #"locations": locations
    #}
 #}
icps = {
    "Small Businesses (0-50 seats)": {
        "job_titles": {
            "Founder", "CEO", "Marketing Manager", "Customer Service Manager", 
            "Entrepreneur", "Small Business Owner"
        },
        "employees": {"max": 50},
        "revenue": {"max": "Ksh 50M"},
        "industries": {
            "Individuals", "Local start-ups", "Retailers", "Small professionals", 
            "Research companies", "Beverage distributors", "Debt collectors"
        },
        "locations" : locations,
        "pain_points": {
            "Inefficient customer service operations",
            "High operational costs for in-house contact centers",
            "Limited access to advanced analytics"
        },
        "value_proposition": {
            "Omni-channel support solutions",
            "Scalable solutions",
            "Affordable solution within budget",
            "Trusted long-term partner"
        },
        "decision_factors": ["Cost efficiency", "Risk mitigation", "Technology integration"],
        "sales_cycle": "1-3 months",
        "discovery_channels": ["Referrals", "Website", "Email", "LinkedIn", "SME events"]
    },
    
    "Mid-Size Companies (51-250 seats)": {
        "job_titles": {
            "CEO", "CFO", "CTO", "Head of Customer Care", "Operations Manager", 
            "IT Manager", "Customer Experience Manager"
        },
        "employees": {"range": (51, 250)},
        "revenue": {"range": ("Ksh 51M", "Ksh 100M")},
        "industries": {
            "Mid-size e-commerce", "Manufacturing", "Tier 2 healthcare providers",
            "Tier 2 banks", "Tier 2 SACCOs", "Tier 2 insurance", "Fintechs"
        },
        "locations" : locations,
        "pain_points": {
            "Need for efficient customer support",
            "Managing growth and customer expansion",
            "Integration with current systems"
        },
        "value_proposition": {
            "Quality control for high standards",
            "Experience in customer support",
            "Trusted long-term partner",
            "Data solutions integration"
        },
        "decision_factors": ["Experience", "Quality", "Affordable rate", "Speed"],
        "sales_cycle": "3-6 months",
        "discovery_channels": ["Industry expos", "Trade shows", "Tech workshops", "Referrals"]
    },
    
    "Large Enterprises (251+ seats)": {
        "job_titles": {
            "CEO", "CFO", "CTO", "CMO", "IT Security Manager", 
            "VP Customer Experience", "Chief Data Officer"
        },
        "employees": {"min": 251},
        "revenue": {"min": "Ksh 100M"},
        "industries": {
            "Large e-commerce", "Manufacturing & transport", "Tier 1 healthcare",
            "Tier 1 banks", "Tier 1 insurance", "Tier 1 telcos"
        },
        "locations" : locations,
        "pain_points": {
            "Competitive differentiation",
            "High-quality service delivery",
            "Expanding client base needs",
            "System integration challenges"
        },
        "value_proposition": {
            "Quality assurance processes",
            "Trusted partner with compliance",
            "Large-scale operation expertise",
            "Data security and integration"
        },
        "decision_factors": ["Price", "Experience", "Compliance", "Tech support"],
        "sales_cycle": "6+ months",
        "discovery_channels": ["Executive networking", "Industry summits", "RFP responses"]
    },
    
    "BPO Providers (100-1000+ seats)": {
        "job_titles": {
            "Regional Business Development Manager", "Operations Manager",
            "Client Relations Manager", "Chief Operations Officer"
        },
        "employees": {"range": (100, 1000)},
        "revenue": {"min": "$100M"},
        "industries": {"Mid-Large BPOs", "International outsourcing firms"},
        "locations" : locations,
            "pain_points": {
            "Specialized BPO services",
            "Security and data compliance",
            "Quality assurance at scale",
            "Large workforce management"
        },
        "value_proposition": {
            "Specialized BPO services",
            "Security and data compliance",
            "Quality assurance",
            "Large workforce management"
        },
        "decision_factors": ["Compliance", "Team size", "Quality", "Experience"],
        "sales_cycle": "2-6 months",
        "discovery_channels": ["BPO conferences", "Outsourcing summits", "Global networking"]
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

#Global variable to store posts & authors
all_authors_cache = []
icp_score = 0
    
##perform sentiment analysis of each post
#model = "siebert/sentiment-roberta-large-english"
#sentiment_analyzer = pipeline(task="sentiment-analysis", model=model)

#def sentiment_analysis(text, keywords):
    #try:
        ##tokenize the text
        #tokenizer = AutoTokenizer.from_pretrained(model)
        #tokens = tokenizer(
            #text,
            #truncation = True,
            #max_length = 4096,
        #)
        #truncated_text = tokenizer.decode(tokens["input_ids"])

        #analysis = sentiment_analyzer(truncated_text)[0] #analyze the 1st 4096 tokens
        #return {
            #"text": text,
            #"sentiment" : analysis["label"],
            #"score" : analysis["score"],
            #"words_found" : any(keyword in text.lower() for keyword in keywords),
            #"truncated": len(tokens["input_ids"]) >= 4096
        #}
    #except Exception as e:
        #logging.error("Analysis failed for text (first 50 characters): %s | Error %s", text[:50], str(e))
        #return None

#Search for posts based on keywords
def search_posts(params: dict) -> list:
    all_posts = []
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

            #extract the actual linkedin post
            #for result in search_results:
                #summary = result.get("summary")
                #linkedin_post = summary.get("text") if isinstance(summary, dict) else "Post not found" 
                ##perform sentiment analysis on post
                #if linkedin_post:
                    #analysis = sentiment_analysis(linkedin_post, keywords)
                    ##store analysis in all posts
                    #if analysis:
                        #all_posts.append(analysis)

            #Add results to all_results
            if search_results:
                all_results.extend(search_results)
                print(f"Found {len(search_results)} people for group {keyword_group}")
            else:
                print(f"No results for {combined_keywords}")
            time.sleep(random.uniform(5, 10))
            
        return all_results
        #return all_posts

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
def icp_scoring():
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
        if len(parts) < 6:
            continue
        
        #otherwise split author info into pieces
        name = parts[0].strip()
        job_title = parts[1].strip().lower()
        company_name = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Company Not Found"
        company_industry = parts[3].strip() if len(parts) > 3 and parts[3].strip() else "Industry Not Found"
        company_location = parts[4].strip() if len(parts) > 4 and parts[4].strip() else "Location Not Found"
        employee_count = parts[5].strip() if len(parts) > 5 and parts[5].strip() else "Employee Range Not Found"
        
        #define icp based on company size
        chosen_icp = icp_based_on_size(employee_count, icps)

        #job title match
        job_title_match = check_job_title(job_title, chosen_icp)

        #location match
        location_match = check_company_location(company_location, chosen_icp)
       
        #industry match
        industry_match = check_company_industry(company_industry, chosen_icp)

        #size match
        size_match = check_company_size(chosen_icp)

        #if all matches, add to qualified authors
        if job_title_match > 0 and location_match > 0 and industry_match > 0 and size_match > 0:
            logging.info(f"Qualified Author Found: Name: {name}, Job Title: {job_title}, Job Title Score: {job_title_match},"
                         f"Company Name: {company_name}, Company Industry: {company_industry}, Industry Score: {industry_match}," 
                         f"Company Location: {company_location}, Location Score:{location_match}, "
                         f"Company Size: {employee_count}: Size Score: {size_match}")
            qualified_authors.append(author)

    return qualified_authors

#check job title 
def check_job_title(job_title: str, icp: dict) -> int:
    #job title match
    job_title_score = 0

    #job title that has passed fuzzy matching
    matched_title = None

    #get score from fuzzy mactching
    for title in icp["job_titles"]:
        match_score = fuzz.partial_ratio(title.lower(), job_title.lower())

        if match_score > 70:
            matched_title = title
            break

    #if match was found, rank it
    if matched_title:
        if any(keyword in matched_title.lower() for keyword in ["founder", "chief", "ceo", "cto", "cfo"]):
            job_title_score += 25
        elif "director" in matched_title.lower() or "vp" in matched_title.lower() or "head" in matched_title.lower():
            job_title_score += 20
        elif "manager" in matched_title.lower():
            job_title_score += 15
        elif "specialist" in matched_title.lower() or " coordinator" in matched_title.lower():
            job_title_score += 10
        else:
            job_title_score += 5

    #add job title score to overall icp score
    return job_title_score

#check company location 
def check_company_location(company_location: str, icp: dict) -> int:
    company_location_score = 0
    matched_location = None
    
    # Create a flat dictionary of locations mapped to scores
    location_scores = {}

    # Assign predefined scores to each location
    for location in icp["locations"].get("North American Countries", []):
        location_scores[location.lower()] = 25
    for location in icp["locations"].get("U.S. Cities", []):
        location_scores[location.lower()] = 25
    for location in icp["locations"].get("European Countries", []):
        location_scores[location.lower()] = 25
    for location in icp["locations"].get("European Cities", []):
        location_scores[location.lower()] = 25
    for location in icp["locations"].get("African Countries", []):
        location_scores[location.lower()] = 15
    for location in icp["locations"].get("African Cities", []):
        location_scores[location.lower()] = 15

    # Perform fuzzy matching then score
    for loc, score in location_scores.items():
        location_fuzzy_score = fuzz.partial_ratio(loc, company_location.lower())
        if location_fuzzy_score > 70:
            matched_location = loc
            company_location_score = score
            break  # Stop at the first match

    # Default score for non-matching locations
    if not matched_location:
        company_location_score = 5  

    return company_location_score

#check company industry
def check_company_industry(company_industry: str, icp: dict) -> int:
    company_industry_score = 0
    matched_industry = None

    for industry in icp["industries"]:
        fuzzy_industry_score = fuzz.partial_ratio(company_industry.lower(), industry.lower())

        if fuzzy_industry_score > 70:
            matched_industry = industry

    if matched_industry:
        if any(keyword in matched_industry.lower() for keyword in ["Manufacturing", "Telecommunications", "Finance", "Banking", "Healthcare", "Insurance", "Retail", "Energy"]):
            company_industry_score += 25
        elif any(keyword in matched_industry.lower() for keyword in ["Travel", "Hospitality", "Real Estate", "Legal", "Software and IT Services"]):
            company_industry_score += 15
        else:
            company_industry_score += 5

    return company_industry_score

#determine icp based on size
def icp_based_on_size(employee_count: str, icps: dict)->(dict | None):
    #regex pattern to find employee count
    pattern = r"(\d+)\s*to\s*(\d+)"
    match = re.search(pattern, employee_count.strip())

    #if employee count not found return 0
    if not match:
        return None
    
    #else store min and max employee count
    left_number = int(match.group(1)) if match else None
    right_number = int(match.group(2)) if match else None

    for icp_name, icp_details in icps.items():
        #if icp has a max employee count 
        if "max" in icp_details["employees"] and right_number <= icp_details["employees"]["max"]:
            return icp_details
        #if icp has a minimum employee count
        elif "min" in icp_details["employees"] and left_number >= icp_details["employees"]["min"]:
            return icp_details
        #if icp has a range
        elif "range" in icp_details["employees"]:
            min_employees, max_employees = icp_details["employees"]["range"]
            if min_employees <= left_number and max_employees >= right_number:
                return icp_details
    return None

#check company size
def check_company_size(icp: dict) -> int:
    company_size_score = 0
    #if employee count has a max amount
    if "max" in icp["employees"]:
        if icp["employees"]["max"] <= 50:
            company_size_score += 5
    
    #if employee count has a min amount
    elif "min" in icp["employees"]:
        if icp["employees"]["min"] >= 250:
            company_size_score += 20

    #if employee count has a range
    elif "range" in icp["employees"]:
        min_number, max_number = icp["employees"]["range"]
        if max_number >= 1000:
            company_size_score += 25
        elif min_number >= 51 and max_number <= 250:
            company_size_score += 15

    return company_size_score

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

mock_authors = [
    "Alice Johnson - Software Engineer - Google - Tech - Mountain View, CA - 11 to 50",
    "Bob Smith - Data Scientist - Microsoft - Enteretainment - Redmond, WA - 2 to 10",
    "Charlie Brown - Product Manager - Amazon - Sports - Seattle, WA - 501 to 1000",
    "Diana Prince - UX Designer - Meta - Finance - Menlo Park, CA - 51 to 200",
    "Ethan Hunt - DevOps Engineer - Netflix - Agriculture - Los Gatos, CA - 1001 to 5000",
    "Fiona Gallagher - AI Researcher - OpenAI - Tech - San Francisco, CA - 501 to 1000",
    "George Costanza - Marketing Manager - Tesla - Entertainment - Austin, TX - 1001 to 5000",
    "Hannah Baker - Cybersecurity Analyst - IBM - Sports - New York, NY - 11 to 50",
    "Isaac Newton - Machine Learning Engineer - DeepMind - Tech - London, UK - 2 to 10",
    "Jack Sparrow - Software Developer - Spotify - Tech - Stockholm, Sweden - 51 to 200"
]

@app.route('/', methods = ['GET'])
def search():
    return search_posts(params)

@app.route('/get-mocks', methods=['GET'])
def get_mocks():
    with psycopg.connect(conninfo="host=localhost dbname=sl user=postgres port=5432 password=markothengo99") as conn:
        with conn.cursor() as cur:
            for author in mock_authors:
                parts = author.split(" - ")
                name = parts[0].strip()
                title = parts[1].strip()
                company = parts[2].strip()
                industry = parts[3].strip()
                location = parts[4].strip()
                size = parts[5].strip() 
                cur.execute("INSERT INTO companies (name, industry, location, employee_count) VALUES (%s, %s, %s, %s) RETURNING company_id",
                            (company, industry, location, size)           
                            )
                company_id = cur.fetchone()[0]
                cur.execute("INSERT INTO authors (name, title, company_id) VALUES (%s, %s, %s)",
                            (name, title, company_id) 
                            )
        conn.commit()
    conn.close()
    return mock_authors

@app.route('/mock-icp-scoring', methods=['GET'])
def mock_icp_scoring():
    #Log process starting message
    logging.info("Matching Mock ICPs...")

    #List of qualified authors
    qualified_authors = []
    
    #for each author split their name and job
    for author in mock_authors:
        parts = author.split(" - ")

        #if author doesn't have name/job go to next author
        if len(parts) < 6:
            continue
        
        #otherwise split author info into pieces
        name = parts[0].strip()
        job_title = parts[1].strip().lower()
        company_name = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Company Not Found"
        company_industry = parts[3].strip() if len(parts) > 3 and parts[3].strip() else "Industry Not Found"
        company_location = parts[4].strip() if len(parts) > 4 and parts[4].strip() else "Location Not Found"
        employee_count = parts[5].strip() if len(parts) > 5 and parts[5].strip() else "Employee Range Not Found"
        
        #define icp based on company size
        chosen_icp = icp_based_on_size(employee_count, icps)
        
        #job title match
        job_title_match = check_job_title(job_title, chosen_icp)
        print(f"Debug: Job Title Match = {job_title_match}")

        #location match
        location_match = check_company_location(company_location, chosen_icp)
        print(f"Debug: Location Match = {location_match}")
       
        #industry match
        industry_match = check_company_industry(company_industry, chosen_icp)
        print(f"Debug: industry Match = {industry_match}")

        #size match
        size_match = check_company_size(chosen_icp)
        print(f"Debug: size Match = {size_match}")

        #if all matches, add to qualified authors
        if job_title_match > 0 and location_match > 0 and industry_match > 0 and size_match > 0:
            qualified_authors.append(author)

    return qualified_authors

#Add Routes
@app.route('/all-authors', methods = ['GET'])
def get_all_authors():
    global all_authors_cache
    
    #Reset the cache so all-authors always starts w/a fresh list of authors
    all_authors_cache = [] 

    #generator function to yield authors
    def generate():
        try:
            with psycopg.connect(conninfo="host=localhost dbname=sl port=5432 user=postgres password=markothengo99") as conn:
                with conn.cursor() as cur:
                    #fetch all authors and yield each one
                    all_authors = get_authors()
                    for author in all_authors:
                        all_authors_cache.append(author)
                        yield f"data: {json.dumps({"author": author})}\n\n"
                        parts = author.split(" - ")
                        name = parts[0].strip()
                        job_title = parts[1].strip()
                        company_name = parts[2].strip()
                        company_industry = parts[3].strip()
                        company_location = parts[4].strip()
                        employee_size = parts[5].strip()
                        try:
                            cur.execute(
                                "INSERT INTO companies (name, industry, location, employee_count) VALUES (%s, %s, %s, %s) RETURNING company_id",
                                        (company_name, company_industry, company_location, employee_size)
                                    )
                            company_id = cur.fetchone()[0]
                            cur.execute(
                                "INSERT INTO authors (name, title, company_id) VALUES (%s, %s, %s)",
                                        (name, job_title, company_id)
                                    )
                            
                            logging.info("Data inserted into Authors!")
                        except Exception as e:
                            logging.error("Error: ", e)

                conn.commit()
        #if the fetch fails yield an error message
        except Exception as e:
            yield f"data: {json.dumps({"error": str(e)})}"
    
    #stream the authors as they roll in
    return Response(stream_with_context(generate()), content_type='text/event-stream')


@app.route('/get-qualified-leads', methods=['GET'])
def generate_qualified_leads():
    try:
        #get the icp in the request parameters
        selected_icp = request.args.get('icp', 'all')
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
            qualified_leads = icp_scoring()
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
    #initialize logging configurations
    logging_config.configure_logging()

    #run the flask app
    app.run(debug = True)
