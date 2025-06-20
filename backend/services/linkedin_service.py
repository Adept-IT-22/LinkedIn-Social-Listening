# This module handles LinkedIn login and session management

import random
import requests
import fake_useragent
import requests.cookies
from config import app_config
from linkedin_api import Linkedin

# Authentication Cookies
cookies = app_config.LINKEDIN_COOKIES

# Put Cookies in CookieJar
cookie_jar = requests.cookies.RequestsCookieJar()
for name, value in cookies.items():
    cookie_jar.set(name, value)

# Initialize User Agent
session_user_agent = None

# Get header
def get_header():
    global session_user_agent
    if session_user_agent is None:
        try:
            ua = fake_useragent.UserAgent()
            session_user_agent = ua.random
        except Exception as e:
            session_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    return {"User-Agent": session_user_agent}

# Create client with cookies and headers
linkedin_username = app_config.LINKEDIN_USERNAME
linkedin_password = app_config.LINKEDIN_PASSWORD
headers = get_header()
api = Linkedin(linkedin_username, linkedin_password, cookies=cookie_jar)

# Get Client
def get_linkedin_client():
    return api