import os
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
"port" : os.getenv("DB_PORT"),
"user" : os.getenv("DB_USER"),
"password" : os.getenv("DB_PASSWORD"),
}

#Search settings
KEYWORDS = os.getenv("KEYWORDS")
PAGE_SIZE = int(os.getenv("PAGE_SIZE"))
MAX_PAGES = int(os.getenv("MAX_PAGES"))

#Search parameters
SEARCH_PARAMS = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": " OR ".join(KEYWORDS),
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

#Flask settings
DEBUG = os.getenv("DEBUG")

    