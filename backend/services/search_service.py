#This module will handle searching for posts on linkedin

import json
import time
import random
import logging
from fuzzywuzzy import fuzz
from utils.keywords import KEYWORDS
from utils.negative_keywords import NEGATIVE_KEYWORDS
from services.linkedin_service import get_linkedin_client
from tenacity import(
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_log,
    after_log
)

#initialize module logger
logger = logging.getLogger(__name__)

#initialize keywords
keywords = [word.strip().lower() for words in KEYWORDS.values() for word in words]

@retry(
        stop = stop_after_attempt(5),
        wait=wait_exponential_jitter(
            initial=5, #start with 5 seconds
            max=300, #dont wait more than 5 minutes
            jitter=10 #add 10 seconds randomness
        ),
        retry=retry_if_exception_type(
            (ConnectionError)
        ),
        before_sleep=before_log(
            logger=logger,
            log_level=30
        ),
        after=after_log(
            logger=logger,
            log_level=30,
            sec_format="%0.3f"
        )
)

#search function wrapper
def linkedin_search(api, params):
    time.sleep(random.uniform(3, 5))
    return api.search(params, limit=10)
    
#Search for posts based on keywords
def search_posts(params: dict) -> list:
    all_results = [] #stores all results
    api = get_linkedin_client()

    try:
        #Split the 90 keywords into 15 groups of 6
        for i in range(0, len(keywords), 6):
            keyword_group = keywords[i:i+6]
            combined_keywords = " OR ".join(keyword_group)
            logger.info(f"Search for {combined_keywords} starting...")

            #Create copy of params for each group
            current_params = params.copy()
            current_params["keywords"] = combined_keywords

            #Connect to linkedin & Run the search
            search_results = linkedin_search(api, current_params)

            #Add results to all_results
            if search_results:
                previous_length = len(all_results)
                all_results.extend(search_results)
                logger.info(f"Found {len(all_results) - previous_length} people for group {keyword_group}")
            else:
                logger.info(f"No results for {combined_keywords}")

            #time between searches
            time.sleep(random.uniform(20, 60))

        logger.info(f"Total qualified results: {len(all_results)}")
        return all_results

    except Exception as e:
        logger.error("Error fetching search results: %s", str(e))
        return []

#check if post contains any negative keywords
def check_for_neg_keywords(post: str, negative_keywords: dict, threshold: int = 80) -> bool:
    post = post.lower()
    
    #Get keyword from negative keywords dictionary
    for keywords in negative_keywords.values():
        for keyword in keywords:
            keyword = keyword.lower()

            #Match keyword to post
            similarity = fuzz.partial_ratio(keyword, post)
            if similarity > threshold:
                return True

    return False

#filter for intent phrases
def check_for_intent(post: str, intent_phrases: dict, threshold:int = 50) -> bool:
    post = post.lower()

    #get phrases from intent phrases dictionary
    for phrases in intent_phrases.values():
        for phrase in phrases:
            phrase = phrase.lower()

            #Match phrase to post
            similarity = fuzz.partial_ratio(phrase, post)
            if similarity >= threshold:
                return True
    
    return False
