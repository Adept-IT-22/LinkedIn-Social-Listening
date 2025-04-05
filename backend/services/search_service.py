#This module will handle searching for posts on linkedin

import time
import random
import logging
from config import app_config
from sentiment_service import sentiment_analysis
from linkedin_service import get_linkedin_client

#initialize keywords
keywords = app_config.KEYWORDS

#Search for posts based on keywords
def search_posts(params: dict) -> list:
    all_results = [] #stores all results
    all_posts = [] #stores posts of all results before sentiment analysis
    positive_results = [] #stores results of +ve posts
    try:
        for i in range(0, len(keywords), 3):
            #Get next 3 keywords or remaining if less than 3
            keyword_group = keywords[i:i+3]
            combined_keywords = " OR ".join(keyword_group)

            logging.info(f"Search for {combined_keywords} starting...")

            #Create copy of params for each group
            current_params = params.copy()
            current_params["keywords"] = combined_keywords

            #Connect to linkedin & Run the search
            api = get_linkedin_client()
            search_results = api.search(current_params, limit=10)
            
            #log results
            if search_results:
                logging.info(f"Found {len(search_results)} people for group {keyword_group}")

                #Extract posts from results
                for result in search_results:
                    summary = result.get("summary")
                    linkedin_post = summary.get("text") if isinstance(summary, dict) else "Post Not Found"
                    if linkedin_post:
                        all_posts.append(linkedin_post)
                        all_results.append(result)
            else:
                logging.info(f"No results for {combined_keywords}")
            
            #wait 5-10 before searching through another group of keywords
            time.sleep(random.uniform(5, 10))

        #Perform sentiment analysis
        analysis = sentiment_analysis(all_posts, keywords)

        #take +ve posts and return the corresponding search result
        if analysis:
            post_index = [i for i, post in enumerate(analysis) if post["label"] == "POSITIVE"]
            positive_results = [all_results[i] for i in post_index]
        
        return positive_results

    except Exception as e:
        logging.error(f"Error during search {e}")
        return []
