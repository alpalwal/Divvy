# Script to list all exemptions in DivvyCloud
import json
import requests
import getpass
import csv

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URL
base_url = ""

#### TESTING 
username = "alexc"
password = "q%)P3hX>8JuyoRnjc"
base_url = "https://sales-demo.divvycloud.com"
####

# Param validation
if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

exemptions_file = "exemption_list.csv"

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
def get_exemptions(page):
    data = {}
    response = requests.post(
        url=base_url + '/v2/public/exemptions/list?page=' + str(page) + '&page_size=500',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Get the first page of exemptions
page = 1
exemption_list = []
exemption_response = get_exemptions(page)
exemption_list = exemption_list + exemption_response['data']

''' Need to fix pagination. In the meantime, just cheat and bump the page size up higher
# If there's more pages, get them too
pages_left = int(exemption_response['total_count'] / 50)
print("pages left:")
print(str(pages_left))

print(range(pages_left))
if pages_left > 0:
    pages_left += 1 # Add one so the range can start on page 2 instead of page 0
    for page in range(1,pages_left):
        page += 1
        print(page)
        get_exemptions(page)
        exemption_list = exemption_list + exemption_response['data']
'''

with open(exemptions_file, 'w') as outfile:
    headers = ['exemption_id','resource_type', 'resource_name', 'provider_id', 'insight_id', 'insight_source', 'creator_name', 'owner_name', 'approver', 'create_date', 'start_date', 'expiration_date', 'enabled', 'insight_name']
    writer = csv.writer(outfile)
    writer.writerow(headers)

    for exemption in exemption_list:
        cells = [exemption['exemption_id'],exemption['resource_type'],exemption['resource_name'],exemption['provider_id'],exemption['insight_id'],exemption['insight_source'],exemption['creator_name'],exemption['owner_name'],exemption['approver'],exemption['create_date'],exemption['start_date'],exemption['expiration_date'],exemption['enabled'],exemption['insight_name']]
        writer.writerow(cells)
outfile.close()

# SAMPLE INFO
#   'exemption_id': 8,
#   'resource_id': 'divvyorganizationservice:29',
#   'resource_type': 'divvyorganizationservice',
#   'resource_name': 'AWS Master',
#   'provider_id': '29',
#   'insight_id': 9,
#   'insight_source': 'backoffice',
#   'creator_name': 'Chris DeRamus',
#   'owner_name': 'Chris DeRamus',
#   'approver': 'DivvyCloud migration scripts',
#   'create_date': '2020-02-06T22:01:30Z',
#   'start_date': '2020-02-06T00:00:00Z',
#   'expiration_date': None,
#   'enabled': False,
#   'insight_name': 'Cloud Root Account API Access Key Present'