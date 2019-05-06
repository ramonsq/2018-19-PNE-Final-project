import requests
import sys

# SERVER IP, PORT
SERVER = "http://localhost:8000/"

endpoint = input(SERVER)

if endpoint.find("=") > 0:
    endpoint += "&json=1"
else:
    endpoint += "?json=1"

r = requests.get(SERVER+endpoint, headers={"Content-Type": "application/json"})
 
if not r.ok:
    r.raise_for_status()
    sys.exit()
 
decoded = r.json()
print(repr(decoded))

input()