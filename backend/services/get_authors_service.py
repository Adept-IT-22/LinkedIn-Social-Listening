#This module gets author information from the posts

import re
import time
import random
import logging
from config import app_config
from services.search_service import search_posts, check_for_neg_keywords, check_for_intent
from services.get_company import find_company_info
from utils.negative_keywords import NEGATIVE_KEYWORDS
from utils.intent_phrases import INTENT_PHRASES


#initialize module logger
logger = logging.getLogger(__name__)

#imported variables
MAX_PAGES = app_config.MAX_PAGES
SEARCH_PARAMS = app_config.SEARCH_PARAMS
PAGE_SIZE = app_config.PAGE_SIZE

#global module variable
seen_authors = set() #set of seen authors

def get_authors(): 
    try:
        logger.info("Getting authors...")
        start_offset = 0 #where search should start from
        yield_counter = 0 #number of authors yielded

        #run this loop MAX_PAGES number of times
        for _ in range(MAX_PAGES):
            #set start parameter to start_offset and run search_posts
            current_params = SEARCH_PARAMS.copy()
            current_params["start"] = start_offset 
            posts = search_posts(current_params)

            #if posts returns nothing stop.
            if not posts:
                logger.error("No search results found")
                break

            #else get name & job of each author
            for post in posts:
                name = post["title"]["text"]
                job = post["primarySubtitle"]["text"]
                company = post["actorNavigationUrl"]
                post_summary = post.get("summary", {})
                actual_post = post_summary.get("text", "Post Not Found")

                #check if post has negative keywords. Return True if it does.
                if check_for_neg_keywords(actual_post, NEGATIVE_KEYWORDS):
                    logger.warning("SKIPPED DUE TO NEGATIVE KEYWORDS")
                    continue

                #check if post has intent phrases. return True if it does.
                #if not check_for_intent(actual_post, INTENT_PHRASES):
                    #logger.warning("SKIPPED DUE TO LACK OF INTENT PHRASES")
                    #continue

                logger.info("===========================================")
                logger.info("Linkedin Post: %s", actual_post)

                #get urn from actornavigationurl
                company_urn = re.search(r"(?<=/in/)[^?]+", company)
                
                #if urn exists use it to find company name
                if company_urn:
                    shortened_company_urn = str(company_urn.group(0))
                    company_info = find_company_info(shortened_company_urn)
                else:
                    company_info = "Company Not Found"
                
                #create person variable and add person to authors list
                person = name + " - " + job + " - " + company_info + " - " + actual_post
                if person not in seen_authors:
                    logger.info(f"NEW AUTHOR FOUND: {person}") #CHANGE BACK TO NAME NOT PERSON
                    yield person
                    yield_counter += 1
                    seen_authors.add(person)
            
            #change start offset and go again
            start_offset += PAGE_SIZE
            #delay to make it feel like real time streaming
            time.sleep(random.uniform(5,10))

        #number of authors yielded
        logger.info(f"Total authors yielded: {yield_counter}")

    except Exception as e:
        logger.error(f"Error fetching authors: %s", e)
        return
