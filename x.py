import json 
from linkedin_api import Linkedin

api = Linkedin('m10mathenge@gmail.com', 'markothengo99')

search = api.get_profile('ACoAAAXt9q4BUqKj5FE20TTTfqybJH6d1mpaZ74')

print(json.dumps(search, indent = 4))
