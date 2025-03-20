#This module will handle searching for posts on linkedin

import time
import random
import logging
from config import app_config
from linkedin_service import get_linkedin_client

#initialize keywords
keywords = app_config.Config.KEYWORDS

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
            api = get_linkedin_client()
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