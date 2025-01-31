import os
import json
from linkedin_api import Linkedin

LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin('markothengo@gmail.com', LINKEDIN_PASSWORD)

search_parameters = ["deepseek", "claude", "llama"]

#for parameter in search_parameters:
params = {
    "keywords": "call center outsourcing",
    "includeWebMetadata" : False
    }
search = api.search(params, limit = 1, offset = 0)
summary_search = list(map(lambda x: (x["summary"], x["title"]), search))
result_list = []
for item in summary_search:
    single_post = list(mini_item["text"] for mini_item in item if mini_item is not None)
    with open("results.txt", "w", encoding="utf-8") as file:
        file.write(f"{single_post}\n")
    print("That went well")
print("Done!")
