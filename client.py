import requests
import sys

# SERVER IP, PORT
SERVER = "http://localhost:8000/"
print("-----------------------------------------------------------")
print("Enter the endpoint below, press ENTER and wait for 'Result'")
print("-----------------------------------------------------------")
endpoint = input(SERVER)

if endpoint.endswith("json=1"):
    r = requests.get(SERVER+endpoint, headers={ "Content-Type" : "application/json"})
    if not r.ok:
        r.raise_for_status()
        sys.exit()
    try:
        decoded = r.json()
        print("\nResult:\n"+repr(decoded))
    except Exception as e:
        print("\nError: "+str(e.args))
else:
    print("\nError: 'json=1' parameter is missing")


input()
