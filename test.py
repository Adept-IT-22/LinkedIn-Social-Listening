from linkedin_api import Linkedin
import json

api = Linkedin("mark.mathenge@riarauniversity.ac.ke", "markothengo99")

results = api.get_profile("ACoAABoTxrEB66kTitTXWQh0IKlPThV0m-qhyqU")

print(json.dumps(results, indent = 4))
