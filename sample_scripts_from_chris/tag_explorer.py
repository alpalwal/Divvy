import json
import requests

# Username/password to authenticate against the API
username = "chris@divvycloud.com"
password = ""

# API URLs
base_url = 'http://localhost:8001'
login_url = base_url + '/v2/public/user/login'
tag_configurations_url = base_url + '/v2/public/resources/tags/saved_configs/list'

# Change this to the name of the tagging report you want to pull
TAG_REPORT = 'DivvyCloud Tagging Policy'

def get_auth_token():
    response = requests.post(
        url=login_url,
        data=json.dumps({"username": username, "password": password}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        })
    return response.json()['session_id']

def get_tag_configurations(auth_token):
    response = requests.post(
        url=tag_configurations_url,
        data={},
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        })
    return response.json()['resources']


def get_resources(auth_token, configuration):
    data = {
        'tag_keys': configuration['tag_keys'],
        'resource_types': configuration['resource_types'],
        'contains_all': configuration['contains_all'],
        'missing_all': configuration['missing_all']
    }

    if configuration.get('scopes'):
        data['organization_services'] = configuration['scopes']

    response = requests.post(
        url=base_url + '/v2/public/resources/tags/search',
        data=json.dumps(data),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        })

    return response.json()['resources']

# Get our session token
auth_token = get_auth_token()

# Make an inital response to load the parameters into the session prior to
# pulling down the JSON.
for item in get_tag_configurations(auth_token):
    if item['name'] == TAG_REPORT:
        for resource in get_resources(auth_token, item['configuration']):
            print resource

