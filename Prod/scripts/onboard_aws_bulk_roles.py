'''
Script to onboard multiple AWS accounts via cross account role
Sample onboard_output

[Alex-MBP scripts]$python onboard_aws_bulk_roles.py 
Onboarding AWS accounts into DivvyCloud
Account Name: POCs| Status: Success | Account Number: 625820357955
Account Name: test| Status: Error | Account Number: 625820357958
'''

import json
import requests
import getpass

# For each account you want to add, add a new block in aws_accounts
aws_accounts = [
    {
        "account_name": "Production Acct",
        "account_number": 62512450955,
        "role_arn": "arn:aws:iam::62512450955:role/DivvyCloudCrossAcctRole-Role-SOJ9J0W1B0SO",
        "external_id": "divvycloud"
    },
    {
        "account_name": "Dev Acct",
        "account_number": 12345654,
        "role_arn": "arn:aws:iam::12345654:role/DivvyCloudCrossAcctRole-Role-SOJ9J0W1B0SO",
        "external_id": "divvycloud"
    }
]

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
def onboard_aws(account_name,account_number,role_arn,external_id):
    data = {
        "creation_params": 
        {
            "cloud_type":"AWS",
            "authentication_type":"instance_assume_role",
            "name": account_name,
            "account_number":account_number,
            "role_arn":role_arn,
            "duration":3600,
                "external_id": external_id,
            "session_name":"DivvyCloud"
        }
    }

    response = requests.post(
        url=base_url + '/v2/prototype/cloud/add',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Onboard the accounts
print("Onboarding AWS accounts into DivvyCloud")

for account in aws_accounts:
    account_name = account['account_name']
    account_number = int(account['account_number'])
    role_arn = account['role_arn']
    external_id = account['external_id']

    try:    
        onboard_output = onboard_aws(account_name,account_number,role_arn,external_id)
    except Exception as e:
        print ("An error occurred")

    try:
        if onboard_output['status']:
            onboard_status = "Success"
    except KeyError:    
        if onboard_output['error_message']:
            onboard_status = "Error"

    print("Account Name: " + account_name + "| Status: " + onboard_status + " | Account Number: " + str(account_number))

