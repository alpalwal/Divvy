# Check if a resource has showed up in DivvyCloud. If it has, check to see if there are any compliance violations on it. 
# Currently this looks for any insights but filtering in check_for_violations() can pull out specific insights if needed

import json
import requests
import getpass
import time

# Instance ID and region for the instance
instance_id = "i-003014f07c517c6abc"
instance_region = "us-east-1"


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

# Get Reource info
def check_for_resource(resource_id):
    data = {}
    response = requests.get(
        url=base_url + '/v2/public/resource/' + resource_id + '/detail',
        data=json.dumps(data),
        headers=headers
        )
    
    # If the resource isn't seen, it'll return a 404. If we see it (200), return success
    if response.status_code != 200:
        return
    else:
        return True

# Get Instance violation info. It'll be returned in an array if there are any
def check_for_violation(resource_id):
    data = {}
    response = requests.get(
        url=base_url + '/v2/public/insights/' + resource_id + '/violations/get',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    


resource_id = "instance:1:" + instance_region + ":" + instance_id + ":"

# Check if the resource is showing in divvycloud yet
while True:
    found_resource = check_for_resource(resource_id)

    if found_resource:
        print("Found resource. Checking for compliance")
        break
    else:
        print("Resource not found yet. Sleeping for 60")
        time.sleep(60)


# Check for insight violations
instance_violations = check_for_violation(resource_id)

if instance_violations:
    print("======== Violations found for the insight ========")
    for violation in instance_violations:
        print(violation['name'])

if not instance_violations:
    print("No violations found on the instance")