# Script to onboard an AWS account into divvycloud via key/secret

import json
import requests
import getpass

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# Info about the cloud you're onboarding. If you don't put in the secret, you'll be prompted for it and it'll be hidden
api_key = ""
api_secret = ""
if not api_secret:
    api_secret = getpass.getpass('API Secret:')

account_name = "" # Whatever you call this account (Alex-sandbox, divvy-prod, etc.)
account_number = ""


# API URL
base_url = ""

# Param validation
if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password


if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

# Full URL
login_url = base_url + '/v2/public/user/login'

# Shorthand helper function
def get_auth_token():
    response = requests.post(
        url=login_url,
        data=json.dumps({"username": username, "password": passwd}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        })
    return response.json()['session_id']

auth_token = get_auth_token()

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': auth_token
}

# Get Org info
def onboard_aws(account_name,account_number,api_key,api_secret):
    data = {
        "creation_params": {		
            "cloud_type":"AWS",
            "authentication_type":"standard",
            "name":account_name,
            "account_number":account_number,
            "api_key":api_key,
            "secret_key":api_secret
        }
    }

    response = requests.post(
        url=base_url + '/v2/prototype/cloud/add',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Create the pack
print("Onboarding AWS account into DivvyCloud via API key/secret")
onboard_output = onboard_aws(account_name,int(account_number),api_key,api_secret)
print(onboard_output)
# Successful output:
# {'status': 'REFRESH', 'group_resource_id': 'divvyorganizationservice:1', 'name': 'test', 'resource_id': 'divvyorganizationservice:1', 'cloud_type_id': 'AWS', 'creation_time': '2019-07-11 02:40:51.443796', 'id': 1}
