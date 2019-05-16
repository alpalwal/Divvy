# Script to create a "best practices pack" and add insights to it
# Update packaged_insight_ids with the IDs of existing insights. 
# Add new filters to the insight_configs array

import json
import requests
import getpass

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URLs
base_url = "https://sales-demo.divvycloud.com"
login_url = base_url + '/v2/public/user/login'

# PARAMS
pack_name = "Cost Control and Governance"
pack_description = "Cost management and governance best practices"
packaged_insight_ids = [95, 48, 51, 67, 56, 30]

# Param validation

if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: https://sales-demo.divvycloud.com or http://74.34.166.184): ")

if not pack_name:
    pack_name = input("Name for the new pack: ")

if not pack_description:
    pack_description = input("Description for the new pack: (required) ")


# Custom insight configs
insight_configs = [
    {
        "name": "Instances running in unapproved regions",
        "description": "Instances running outside of:\n* us-east-1\n* us-west-2",
        "resource_types": [
            "instance",
            "sharedfilesystem",
            "bigdatasnapshot",
            "emailservicedomain",
            "autoscalinglaunchconfiguration",
            "autoscalinggroup",
            "distributedtablecluster",
            "servicelimit",
            "servicealarm",
            "searchcluster",
            "serviceencryptionkey",
            "serverlessfunction",
            "privateimage",
            "natgateway",
            "networkinterface",
            "mcsnapshot",
            "distributedtable",
            "notificationtopic",
            "servicecertificate",
            "serviceloggroup",
            "networkflowlog",
            "privatenetwork",
            "privatesubnet",
            "publicip",
            "secret",
            "stacktemplate",
            "resourceaccesslist",
            "resourceaccesslistrule",
            "messagequeue",
            "storagecontainer",
            "instancereservation",
            "notificationsubscription",
            "volume",
            "internetgateway",
            "spanner",
            "bigdatainstance",
            "dbinstance",
            "spannerdatabase",
            "datastream",
            "deliverystream",
            "mcinstance",
            "dbsnapshot",
            "routetable",
            "mapreducecluster",
            "snapshot",
            "workspace",
            "servicedetector",
            "sshkeypair",
            "esinstance",
            "loadbalancer"
        ],
        "filters": [
            {
            "name": "divvy.query.resource_not_in_regions",
            "config": {
                "regions_list": [
                "us-east-1",
                "us-west-2"
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
        "description": "Instances that have more than 4 cores",
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
    },
    {
        "name": "Compute or Database Instance Monthly Cost >$1000",
        "description": "Compute or Database Instances where the monthly cost is >$1000",
        "resource_types": [
            "instance",
            "bigdatainstance",
            "dbinstance"
        ],
        "filters": [
            {
            "name": "divvy.filter.monthly_cost_at_least",
            "config": {
                "maximum_monthly_cost": 1000
            }
            }
        ],
        "scopes": [],
        "severity": 2,
        "owner_resource_id": None,
        "template_id": None,
        "tags": None,
        "badges": None,
        "badge_filter_operator": None
    },
    {
        "name": "Instance or database does not have \"team\" tag key",
        "description": "## Required key: team\nThe team responsible for the tagged resource (GRO group name).  \nTo find the GRO group name, go to https://my.byu.edu, login, enter grouss in the Quick URL box, (wait a while), you'll then see the names of all the GRO groups you belong to in the left column in the Groups Memberships row.",
        "resource_types": [
            "instance",
            "dbinstance"
        ],
        "filters": [
                {
                "name": "divvy.query.resource_does_not_have_tag_key",
                "config": {
                    "tag_keys": [
                        "team"
                    ]
                }
            }
        ],
        "scopes": [],
        "severity": 2,
        "owner_resource_id": None,
        "template_id": None,
        "tags": None,
        "badges": None,
        "badge_filter_operator": None
    },
    {
        "name": "Instance or database does not have \"env\" tag or approved values",
        "description": "## Required Key: env \n\n## Approved Values: \n* trn: For training, learning, or experimental efforts \n* dev: For development, learning, or experimental efforts \n* dev-noshutdown: A dev system that shouldn't be automatically shut down \n* tst: Automated testing \n* stg: Staging systems used for QA and User Acceptance Testing\n*stg-noshutdown: A stg system that wont be automatically shut down\n*prd: Production",
        "resource_types": [
            "instance",
            "dbinstance"
        ],
        "filters": [
            {
                "name": "divvy.query.tag_key_value_pair_not_present",
                "config": {
                    "tag_key": "env",
                    "tag_values": [
                        "trn",
                        "dev",
                        "dev-noshutdown",
                        "tst",
                        "stg",
                        "stg-noshutdown",
                        "prd"
                    ]
                }
            }
        ],
        "scopes": [],
        "severity": 2,
        "owner_resource_id": None,
        "template_id": None,
        "tags": None,
        "badges": None,
        "badge_filter_operator": "OR"
    },
    {
        "name": "Instance or database does not have \"data-sensitivity\" tag or approved values",
        "description": "## Required Key: data-sensitivity \n\n## Approved values: \n* public \n* internal \n* confidential (default) \n* highly confidential",
        "resource_types": [
            "instance",
            "dbinstance"
        ],
        "filters": [
            {
                "name": "divvy.query.tag_key_value_pair_not_present",
                "config": {
                    "tag_key": "data-sensitivity",
                    "tag_values": [
                        "public",
                        "internal",
                        "confidential",
                        "highly confidential"
                    ]
                }
            }
        ],
        "scopes": [],
        "severity": 2,
        "owner_resource_id": None,
        "template_id": None,
        "tags": None,
        "badges": None,
        "badge_filter_operator": "OR"
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

# Add notes to insight
def add_insight_notes(insight_id,description):
    data = {
        "notes": description
    }

    response = requests.post(
        url=base_url + '/v2/public/insights/' + str(insight_id) + '/notes/update',
        data=json.dumps(data),
        headers=headers
        )
    return response
# No response expected   


# # Create the pack
# print("Creating a new pack: " + pack_name)
# pack_info = create_pack()
# print("Pack created. Name: " + pack_info['name'] + " Pack ID: " + str(pack_info['pack_id']))

print("Creating custom insights and adding them to the new pack")
# Loop through insight_configs and add a filter for each
custom_insight_ids = []
i = 0
while i < len(insight_configs):
    print("Creating new insight: " + insight_configs[i]['name'])
    new_insight_info = create_insight(insight_configs[i])
    custom_insight_ids.append(new_insight_info['insight_id'])

    # Add notes to the insight
    add_insight_notes(new_insight_info['insight_id'],insight_configs[i]['description'])

    i += 1    


# # Add all insights to the pack
# print("Adding insights to the pack")
# pack_update_output = add_insight_to_pack(pack_info, custom_insight_ids)

# print("Finished creating pack: " + pack_name)


    
