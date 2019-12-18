# Script to list all organizations in DivvyCloudf
import csv
import json
import requests
import getpass
import datetime

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

api_headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': auth_token
}

# Get finding info
def get_findings(insight_id):
    data = {}
    response = requests.post(
        url=base_url + '/v2/public/insights/' + str(insight_id) + '/backoffice/resource/history',
        data=json.dumps(data),
        headers=api_headers
        )
    return response.json()    



# Get insights info
def get_insights():
    data = {}
    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        data=json.dumps(data),
        headers=api_headers
        )
    return response.json()    


# Create the pack
insights_info = get_insights()

shortened_insights = {}
for insight in insights_info:

# insight['severity'] = 4
    if insight['severity'] > 3:
        insight_name = insight['name']
        shortened_insights[insight_name] = insight['severity']
        # insight_id = insight['insight_id']
        # source = insight['source']
        # insight_name = insight['name']
        # supported_clouds = insight['supported_clouds']

print(shortened_insights)

#         insight_findings = get_findings(insight_id)
#         for finding in insight_findings:
#             print(finding)
#             account_name = finding['account']
#             account_id = finding['account_id']
#             resource_name = finding['name']

#             cells = ['Divvy', 'No', severity, 'ToDo', '?', account_name, account_id, '?','?',resource_name,'ToDo',insight_name,date.strftime("%Y-%m-%d")]
#             writer.writerow(cells)  

            


# #   {
# #     "provider_id": "OhioLaunchConfig",
# #     "organization_service_id": 22,
# #     "name": "OhioLaunchConfig",
# #     "insight_name": "Storage Container Exposing Access To World",
# #     "state": 0,
# #     "account": "AWS API Test`",
# #     "identified_at": "2019-08-06T04:58:00Z",
# #     "resource_type": "storagecontainer",
# #     "account_id": "050283019178"
# #   },