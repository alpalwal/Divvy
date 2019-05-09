# Script to create a "best practices pack" and add insights to it
# Update packaged_insight_ids with the IDs of existing insights. 
# Add new filters to the insight_configs array

import json
import requests
import getpass

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password


# API URLs
base_url = 'https://sales-demo.divvycloud.com'
login_url = base_url + '/v2/public/user/login'

# PARAMS
pack_name = "Alex's best practices"
pack_description = "test pack"
packaged_insight_ids = [95, 48, 51, 67, 56, 30]

# Custom insight configs
insight_configs = [
    {
        "name": "Instances running in unapproved regions",
        "description": "Instances running in unapproved regions",
        "resource_types": [
            "instance"
        ],
        "filters": [
            {
            "name": "divvy.query.resource_not_in_regions",
            "config": {
                "regions_list": [
                "us-east-1"
                ]
            }
            }
        ],
        "scopes": [],
        "severity": 1,
        "owner_resource_id": None,
        "template_id": None,
        "tags": None,
        "badges": None,
        "badge_filter_operator": None
    },
    {
        "name": "Instances above 4 cores",
        "description": "Instances above 4 cores",
        "resource_types": [
            "instance"
        ],
        "filters": [
            {
            "name": "divvy.filter.instance_cores_exceeds_threshold",
            "config": {
                "cores": 4
            }
            }
        ],
        "scopes": [],
        "severity": 1,
        "owner_resource_id": None,
        "template_id": None,
        "tags": None,
        "badges": None,
        "badge_filter_operator": None
    }
]

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


# Create a new pack
def create_pack():
    data = {
        "name": pack_name, 
        "backoffice": [], 
        "badges": [],
        "badge_filter_operator": "OR",
        "custom": [], 
        "description": pack_description
    }

    response = requests.post(
        url=base_url + '/v2/public/insights/pack/create',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    


# Add an insight to the pack
def add_insight_to_pack(pack_info, custom_insight_ids):
    data = {
        "name": pack_info['name'], 
        "badge_filter_operator": None,
        "description": pack_info['description'], 
        "logo_url": None, 
        "backoffice": packaged_insight_ids, 
        "custom": custom_insight_ids,
        "badges": None
    }

    response = requests.post(
        url=base_url + '/v2/public/insights/pack/' + str(pack_info['pack_id']) + '/update',
        data=json.dumps(data),
        headers=headers
        )
    return response#.json()    


# Create a custom insight
def create_insight(insight_config):
    response = requests.post(
        url=base_url + '/v2/public/insights/create',
        data=json.dumps(insight_config),
        headers=headers
        )
    return response.json()        


# Create the pack
print("Creating a new pack: " + pack_name)
pack_info = create_pack()
print("Pack created. Name: " + pack_info['name'] + " Pack ID: " + str(pack_info['pack_id']))

## Insights to create:
# Resource Tagging
# Services Exceeding Cost Allowance
# Services Costing More than Last Month

print("Creating custom insights and adding them to the new pack")
# Loop through insight_configs and add a filter for each
custom_insight_ids = []
i = 0
while i < len(insight_configs):
    print("Creating new insight: " + insight_configs[i]['name'])
    new_insight_info = create_insight(insight_configs[i])
    custom_insight_ids.append(new_insight_info['insight_id'])
    i += 1    


# Add all insights to the pack
print("Adding insights to the pack")
pack_update_output = add_insight_to_pack(pack_info, custom_insight_ids)

print("Finished creating pack: " + pack_name)


    
