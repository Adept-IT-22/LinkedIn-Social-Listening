#This module will handle searching for posts on linkedin

import time
import random
import logging
from config import app_config
from services.linkedin_service import get_linkedin_client
from tenacity import(
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_sleep_log
)

#initialize module logger
logger = logging.getLogger(__name__)

#initialize keywords
keywords = [keyword.strip() for keyword in app_config.KEYWORDS.split(',') if keyword.strip()]

#retry decorator
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
        before_sleep=before_sleep_log(
            logger,
            logging.WARNING
        )
)

#search function wrapper
def robust_search(api, params):
    return api.search(params, limit=10)

#Search for posts based on keywords
def search_posts(params: dict) -> list:
    all_results = [] #stores all results
    api = get_linkedin_client()

    try:
        for i in range(0, len(keywords), 3):
            #Get next 3 keywords or remaining if less than 3
            keyword_group = keywords[i:i+3]
            combined_keywords = " OR ".join(keyword_group)

            logger.info(f"Search for {combined_keywords} starting...")

            #Create copy of params for each group
            current_params = params.copy()
            current_params["keywords"] = combined_keywords

            #Connect to linkedin & Run the search
            
            search_results = robust_search(api, current_params)
            
            #Add results to all_results
            if search_results:
                all_results.extend(search_results)
                logger.info(f"Found {len(search_results)} people for group {keyword_group}")
            else:
                logger.info(f"No results for {combined_keywords}")

            #time between searches
            time.sleep(random.uniform(5, 10))
            
        return all_results

    except Exception as e:
        logger.error("Error fetching search results: %s", str(e))
        return []