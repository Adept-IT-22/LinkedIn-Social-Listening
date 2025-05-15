from services.linkedin_service import get_linkedin_client
from services.search_service import linkedin_search
import json
import logging
from utils.negative_keywords import NEGATIVE_KEYWORDS
from utils.intent_phrases import INTENT_PHRASES

logger = logging.getLogger(__name__)

keywords = {
    "CONTACT CENTRE": [
        "call centre", "contact centre", "outsourced call centre", "in-house call centre",
        "contact centre services", "virtual call centre", "inbound call centre", "outbound call centre",
        "BPO services", "call queue", "call center software", "call routing", "IVR system", "ACD",
        "omnichannel contact centre", "voice support", "tele-support", "call abandonment", "call escalation", "live agent"
    ]
}

iterable_keywords = keywords.get("CONTACT CENTRE")

params = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": " OR ".join(iterable_keywords),
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

def search_for_posts(params: dict) -> list:
    api = get_linkedin_client()
    all_results = set()

    #pick 6 keywords at a time out of the whole list of keywords.
    #join the keywords
    #copy the parameters and store the keywords in the parameters
    #use those parameters to search
    try:
        for i in range(0, len(keywords), 6):
            current_keywords = iterable_keywords[i:i+6]
            joined_keywords = " OR ".join(current_keywords)

            copied_params = params.copy()
            copied_params["keywords"] = joined_keywords

            search_results = linkedin_search(api, copied_params)
            for result in search_results:
                post = result.get("summary").get("text")
                logger.info("===================================")
                logger.info("Post before filter: %s", post)
                if any(keyword.lower() in post.lower() for keywords in NEGATIVE_KEYWORDS.values() for keyword in keywords):
                    logger.info("Post failed the filter!")
                    continue 
                else:
                    all_results.add(post)

            logger.info("^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v")
            logger.info("Post after filter....")
            logger.info(json.dumps(list(all_results), indent=4, ensure_ascii=False))
            return all_results

    except Exception as e:
        logger.warning("Search for results failed: %s", str(e))
        return []

search_for_posts(params)