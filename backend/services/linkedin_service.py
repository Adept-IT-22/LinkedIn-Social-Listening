# This module handles LinkedIn login and session management

import random
import requests
import fake_useragent
from config import app_config
from linkedin_api import Linkedin

# Authentication Cookies
cookies = app_config.Config.LINKEDIN_COOKIES

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
        ua = fake_useragent.UserAgent()
        session_user_agent = ua.random
    return {"User-Agent": session_user_agent}

# Create client with cookies and headers
linkedin_username = app_config.Config.LINKEDIN_USERNAME
linkedin_password = app_config.Config.LINKEDIN_PASSWORD
headers = get_header()
api = Linkedin(linkedin_username, linkedin_password, cookies=cookie_jar, headers=headers)

# Get Client
def get_linkedin_client():
    return api