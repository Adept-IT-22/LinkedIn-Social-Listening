from services.linkedin_service import get_linkedin_client
import json
keywords = ["call center","contact center", "call center outsourcing", 
            "customer service", "customer support", 
            "customer service outsourcing", "customer service automation", 
            "customer service software"
            ]
params = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": " OR ".join(keywords),
    "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

api = get_linkedin_client()

def get_profile():
    print("Search starting...")
    try:
        all_results = []
        print("Fetching results...")
        results = api.search(params, limit = 3)
        print(f"Results: {results}")
        for result in results:
            post = result.get("summary").get("text")
            print(f"Post: {post} \n")
            all_results.append(post)
        return all_results
    except Exception as e:
        print(f"That shit failed! {e}")
        return

x = get_profile()
print(x)