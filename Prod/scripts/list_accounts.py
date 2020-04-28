# Script to list all organizations in DivvyCloud

'''
Sample Output:

[Alex-MBP scripts]$python list_accounts.py 
Name | Account_ID | Cloud_Type | Resource_Count | Creation_Time
AWS Sales Account | 014578312761 | AWS | 1157 | 2016-03-29 16:31:48
DivvyCloud QA RO | 050283019178 | AWS | 3692 | 2016-03-30 17:09:27
Acme Corp Development | 212860832355 | AWS | 448 | 2016-04-05 14:52:24
AWS Master | 745948225562 | AWS | 898 | 2017-10-22 11:11:17
Azure Sandbox | 59026a9c-042b-4431-a61f-d03295e5f76e | AZURE_ARM | 315 | 2018-10-19 16:59:40
AliCloud - Dev | 5976820284870875 | ALICLOUD | 95 | 2019-01-31 15:31:26
depthtest-highest | depthtest-highest | GCE | 101 | 2019-02-21 16:16:44

Setup / running the script:
The script can be ran from any system that has access to the divvycloud UI
If your username, password, and base URL aren't provided, it'll prompt you for it. 

'''

import json
import requests
import getpass

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

# Get Acct info
def get_account_list():
    data = {
        "filters": [],
        "limit": 500,
        "offset": 0,
        "order_by": "name"
    }

    response = requests.get(
        url=base_url + '/v2/public/clouds/list',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Parse through the info to pretty print the accounts
account_list = get_account_list()

print("Name | Account_ID | Cloud_Type | Resource_Count | Creation_Time")
for cloud in account_list['clouds']:
    
    account_id = cloud.get("account_id", "None")


    print(cloud['name'] + " | " + str(cloud.get("account_id", "empty")) + " | " + cloud['cloud_type_id'] + " | " + str(cloud['resource_count']) + " | " + cloud['creation_time'])

