# Script to list all organizations in DivvyCloudf

import json
import requests
import getpass

# Username/password to authenticate against the API
username = "alexc"
password = "9srZMS%0PxlY" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URL
base_url = "https://sales-demo.divvycloud.com"

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
def get_org():
    data = {}

    response = requests.get(
        url=base_url + '/v2/public/resource/instance:1:us-east-1:i-043bf6d79334e53e4:/tags/list',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Create the pack
response = get_org()
tags_list = (response['resource_tags'])

for tags in tags_list:
    print("Key: " + tags['key'] + " | Value: " + tags['value'])
