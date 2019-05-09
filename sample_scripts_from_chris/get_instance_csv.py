import csv
import json
import requests
from contextlib import closing

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
        'badges': [
            {'key': 'environment', 'value': 'development'},
            {'key': 'environment', 'value': 'production'}
        ],
        'filters': [],
        'limit': 50,
        'filters': [
            {'name': 'divvy.query.instances_exposing_public_ssh'}
        ],
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
response = get_resources(auth_token, cursor)

csv_url = '{0}/v2/public/divvy/resources/instance/csv?X-Auth-Token={1}'.format(
    base_url, auth_token
)
with requests.Session() as s:
    download = s.get(csv_url)
    line_iterator = (x.decode('utf-8') for x in download.iter_lines(decode_unicode=True))
    cr = csv.reader(line_iterator, delimiter=',')
    my_list = list(cr)
    for row in my_list:
        print(row)
