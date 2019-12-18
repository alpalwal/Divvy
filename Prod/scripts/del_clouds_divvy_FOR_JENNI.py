# Delete all GCP projects that match a certain string

import json
import requests
import getpass

# # Username/password to authenticate against the API
# username = "alex"
# password = "DivvyCloud1!" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# # API URL
# base_url = "http://3.219.214.104:8001"

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

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
def get_clouds():
    data = {}

    response = requests.post(
        url=base_url + '/v2/public/clouds/list',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Get Org info
def remove_account(account_id):
    data = {}
    response = requests.post(
        url=base_url + '/v2/public/cloud/' + account_id + '/delete',
        data=json.dumps(data),
        headers=headers
        )
    return response #.json()        

# list clouds and look for gcp
while True:
    clouds_list = get_clouds()
    if len(clouds_list['clouds']) > 0:
        for cloud in  clouds_list['clouds']: 
            if cloud['cloud_type_id'] == 'GCE':
                if "sys-" in cloud['account_id']:
                    print(cloud)
                    account_id = cloud['group_resource_id']
                    remove_account(account_id)
    else:
        print("All bad projects removed!")
        break




