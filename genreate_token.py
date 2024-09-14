import hashlib
import requests
import json
client_Id='FK9E8YPI2C-100'
secret_Key='4Z24S0WRKI'
combined=f"{client_Id}:{secret_Key}"

appidhash=hashlib.sha256(combined.encode()).hexdigest()
print(appidhash)
url = 'https://api-t1.fyers.in/api/v3/validate-refresh-token'
headers={
    'Content-Type':'application/json',
}
with open('Dependency_File/refresh_token.txt', 'r') as refresh:
    refresh_token = refresh.read()
data={
    "grant_type": "refresh_token",
    "appIdHash":f"{appidhash}",
    "refresh_token":f"{refresh_token}",
    "pin":"1998"
}
response=requests.post(url,headers=headers,data=json.dumps(data))
response=response.json()
print(response['access_token'])
access_token=response['access_token']
with open('Dependency_File/access.txt', 'w') as w:
    w.write(access_token)
