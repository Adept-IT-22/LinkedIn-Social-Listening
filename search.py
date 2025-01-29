import os
import json
from linkedin_api import Linkedin

LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
api = Linkedin('markothengo@gmail.com', LINKEDIN_PASSWORD)

search_parameters = ["deepseek", "claude", "llama"]

for parameter in search_parameters:
    params = {
        "keywords": parameter,
        "filters": ""
        }
    search = api.search(params, limit = 1)
    search = json.dumps(search, indent=4)
    print(search)
    with open("results.txt", "w") as file:
        file.write(search)
    print(f"{parameter} results saved in file.")