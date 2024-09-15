import hashlib
import requests
import json
# Here it generate access token As per API docs when will access token is generated along with this a refresh token is also generated which is valid for 15 days ,by using this access token we will able to generate access token
client_Id='FK9E8YPI2C-100'
secret_Key='4Z24S0WRKI'
combined=f"{client_Id}:{secret_Key}"

appidhash=hashlib.sha256(combined.encode()).hexdigest()  #first need to convert client id + secret key SHA256 as per apidocs
print(appidhash)
url = 'https://api-t1.fyers.in/api/v3/validate-refresh-token'
headers={
    'Content-Type':'application/json',
}
with open('Dependency_File/refresh_token.txt', 'r') as refresh: # here fetching our refresh token from saved file
    refresh_token = refresh.read()
data={
    "grant_type": "refresh_token",
    "appIdHash":f"{appidhash}",
    "refresh_token":f"{refresh_token}",
    "pin":"1998"
}
response=requests.post(url,headers=headers,data=json.dumps(data))   # here i am getting response from fyerAPi and this reponse have data as accesss token
response=response.json()
print(response['access_token'])
access_token=response['access_token']
with open('Dependency_File/access.txt', 'w') as w:
    w.write(access_token)
