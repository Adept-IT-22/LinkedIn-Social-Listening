import os
import json
from linkedin_api import Linkedin

LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin('markothengo@gmail.com', LINKEDIN_PASSWORD)

icp = {
    
}

params = {
    "start": 0,
    "origin": "GLOBAL_SEARCH_HEADER",
    "keywords": "call center",
        "filters": "List((key:resultType,value:List(CONTENT)),(key:contentType,value:List(STATUS_UPDATE)))"
}

search = api.search(params, limit = 50)
with open("matokeo.txt", "w", encoding="utf-8") as file:
    search = json.dumps(search, indent=4)
    file.write(search)
print("Done!")
# summary_search = list(map(lambda x: (x["summary"], x["title"]), search))

# result_list = []
# for item in summary_search:
#     single_post = list(mini_item["text"] for mini_item in item if mini_item is not None)
#     result_list.append(single_post)

# for each_list in result_list:
#     with open("results.txt", "w", encoding="utf-8") as file:
#         each_list = str(each_list)
#         file.write(each_list)
#     print("Done!")

