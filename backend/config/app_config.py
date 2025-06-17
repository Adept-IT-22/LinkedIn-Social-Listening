import os
from utils.keywords import KEYWORDS
from dotenv import load_dotenv

#load variables in this file into env variables
load_dotenv(override=True)

#Linkedin settings
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
#authentication and session cookies
LINKEDIN_COOKIES = {
    "li_at": os.getenv("LINKEDIN_LI_AT"),
    "JSESSIONID" : os.getenv("LINKEDIN_JSESSIONID") 
}

#Database settings
DB_CONFIG = {
"host" : os.getenv("DB_HOST"),
"name" : os.getenv("DB_NAME"),
"port" : int(os.getenv("DB_PORT")),
"user" : os.getenv("DB_USER"),
"password" : os.getenv("DB_PASSWORD"),
}

#Load password from docker if available. If not, load from db_password.txt
password_file = "/run/secrets/db_password"
if os.path.exists(password_file):
    with open(password_file, "r") as f:
        DB_CONFIG["password"] = f.read().strip() 
else:
    DB_CONFIG["password"] = os.getenv("DB_PASSWORD")

#Search settings
PAGE_SIZE = int(os.getenv("PAGE_SIZE"))
MAX_PAGES = int(os.getenv("MAX_PAGES"))

#Search parameters
keywords = set(kw.strip().lower() for words in KEYWORDS.values() for kw in words)
SEARCH_PARAMS = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": " OR ".join(keywords) + "AND (Kenya OR Nairobi)",
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

#Flask settings
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    
