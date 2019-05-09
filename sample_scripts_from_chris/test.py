import json
import requests


# Username/password to authenticate against the API
username = "chris@divvycloud.com"
password = ""

# API URLs
base_url = 'http://localhost:8001'
login_url = base_url + '/v2/public/user/login'


# Shorthand helper function
def get_auth_token():
    response = requests.post(
        url=login_url,
        data=json.dumps({"username": username, "password": password}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        })
    return response.json()['session_id']

def get_resources(auth_token, cursor):
    data = {
        'scopes': [],
        'filters': [],
        'limit': 50,
        'selected_resource_type': 'instance'
    }

    if cursor:
        data['cursor'] = cursor

    response = requests.post(
        url=base_url + '/v3/public/resource/query',
        data=json.dumps(data),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        })

    return response.json()

auth_token = get_auth_token()
cursor = None
count = 0
while True:
    response = get_resources(auth_token, cursor)
    print response
    count += len(response.get('resources', []))
    cursor = response.get('next_cursor', False)
    if not cursor:
        print 'total_processed: {}'.format(count)
        break
