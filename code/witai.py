import requests
import json
import os

s = requests.Session()
s.headers.update({
    'authorization': "Bearer {}".format(os.environ['WIT_AI_TOKEN']),
    'accept': "application/vnd.wit.20140620+json",
})


def create_entity():
    payload = {
      "doc": "A city that I hate",
      "id": "favorite_city",
      "values": [
        {
          "value": "Paris",
          "expressions": ["Paris", "City of Light", "Capital of France"]
        }
      ]
    }
    
    r = s.post('https://api-wit-ai-1an7bd2zyeqn.runscope.net/entities',
            data=json.dumps(payload))
    print r.content

def corpus():
    print s.get('https://api-wit-ai-1an7bd2zyeqn.runscope.net/corpus').content

corpus()
