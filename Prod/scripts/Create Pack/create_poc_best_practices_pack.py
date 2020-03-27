# Script to create a "best practices pack" and add insights to it
# Update packaged_insight_ids with the IDs of existing insights. 
# Add new filters to the insight_configs array

# How to run:
# This can be ran from any system that has access to the DivvyCloud instance (including the one that's running Divvy)
# sudo pip3 install requests
# curl -o create_best_practices_pack.py https://raw.githubusercontent.com/alpalwal/Divvy/master/Prod/scripts/Create%20Pack/create_poc_best_practices_pack.py
# python3 create_best_practices_pack.py


import json
import requests
import getpass

# Username/password to authenticate against the API
username = "alexc"
password = "alexcalexcalexc1!Q" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URL
base_url = "https://54.183.29.131"

# PARAMS
pack_name = "Best Practices, Cost Control, and Governance"
pack_description = "Custom checks, cost controls, and overall best practices"
packaged_insight_ids = [281, 8, 11, 13, 15, 23, 41, 54, 60, 71, 141, 17, 90, 63, 98, 109, 117, 123, 130, 175, 2, 9, 165, 20, 21, 34, 37, 49, 59, 80, 85, 94, 142]

# Param validation

if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

if not pack_name:
    pack_name = input("Name for the new pack: ")

if not pack_description:
    pack_description = input("Description for the new pack: (required) ")

# Full URL
login_url = base_url + '/v2/public/user/login'

### Custom insights to add
insight_configs = []

# Instances running in unapproved regions
insight_configs.append({
    "name": "Resources running in unapproved regions (outside of USA)",
    "description": "Resources running outside of US AWS Regions",
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
            "us-east-2",
            "us-west-1",
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
})

# Instances above 4 cores 
insight_configs.append({
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
})

# Instance or database does not have \"team\" tag key
insight_configs.append({
    "name": "Instance or database does not have \"team\" tag key",
    "description": "## Required key: team\nThe team responsible for the tagged resource (GRO group name).",
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
})

# Instance or database does not have \"env\" tag or approved values
insight_configs.append({
    "name": "Instance or database does not have \"env\" tag or approved values",
    "description": "## Required Key: env \n\n## Approved Values: \n* trn, dev, dev-noshutdown, tst, stg, stg-noshutdown, prd",
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
})

# Database Instance With Zero Connections
insight_configs.append({
  "name": "Cost - Databases Without Connections for 14 Days",
  "description": "Pulled from Trusted Advisor. Checking for unused databases",
  "resource_types": [
    "dbinstance"
  ],
  "filters": [
    {
      "name": "divvy.query.databases_with_zero_connections",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
})

# Unused SGs   
insight_configs.append({
  "name": "Housekeeping - Orphaned Security Groups",
  "description": "Unused security groups (excluding default SGs)",
  "resource_types": [
    "resourceaccesslist"
  ],
  "filters": [
    {
      "name": "divvy.filter.access_list_type",
      "config": {
        "access_list_types": [
          "security_group"
        ]
      },
      "collections": {}
    },
    {
      "name": "divvy.filter.orphaned_security_groups",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": "OR"
})

# empty launch wizard SGs
insight_configs.append({
  "name": "Housekeeping - Orphaned Launch-Wizard-* Security Groups",
  "description": "Orphaned SGs with the launch-wizard-* name",
  "resource_types": [
    "resourceaccesslist"
  ],
  "filters": [
    {
      "name": "divvy.filter.access_list_type",
      "config": {
        "access_list_types": [
          "security_group"
        ]
      },
      "collections": {}
    },
    {
      "name": "divvy.filter.orphaned_security_groups",
      "config": {},
      "collections": {}
    },
    {
      "name": "divvy.filter.resource_name_regex",
      "config": {
        "regex": "launch-wizard-"
      },
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": "OR"
})

# internet gateway orphaned 
insight_configs.append({
  "name": "Housekeeping - Orphaned Internet Gateways",
  "description": "Orphaned IGWs",
  "resource_types": [
    "internetgateway"
  ],
  "filters": [
    {
      "name": "divvy.filter.orphaned_internet_gateways",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
})

# load balancer orphaned
insight_configs.append({
  "name": "Cost - Orphaned Load Balancers",
  "description": "Cost - Orphaned Load Balancers",
  "resource_types": [
    "loadbalancer"
  ],
  "filters": [
    {
      "name": "divvy.filter.any_orphaned_elb_sans_instances",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
}) 

# network interface orphaned 
insight_configs.append({
  "name": "Housekeeping - Orphaned Network Interface",
  "description": "Orphaned Network Interface",
  "resource_types": [
    "networkinterface"
  ],
  "filters": [
    {
      "name": "divvy.filter.orphaned_network_interfaces",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
})

# public ip orphaned 
insight_configs.append({
  "name": "Cost - Orphaned Public IP",
  "description": "Unused EIPs",
  "resource_types": [
    "publicip"
  ],
  "filters": [
    {
      "name": "divvy.filter.orphaned_ip_network_or_instances",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
})

# volume orphaned 
insight_configs.append({
  "name": "Cost - Orphaned Volumes",
  "description": "Orphaned Volumes",
  "resource_types": [
    "volume"
  ],
  "filters": [
    {
      "name": "divvy.filter.orphaned_volume",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
})

# web application firewall orphaned
insight_configs.append({
  "name": "Cost - Orphaned Web Application Firewall (WAF)",
  "description": "Orphaned Web Application Firewall (WAF)",
  "resource_types": [
    "waf"
  ],
  "filters": [
    {
      "name": "divvy.query.waf_orphaned",
      "config": {},
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": None
})

# GPU instances
insight_configs.append({
  "name": "Cost - Instances running GPU Instance types (AWS)",
  "description": "https://aws.amazon.com/ec2/instance-types/",
  "resource_types": [
    "instance"
  ],
  "filters": [
    {
      "name": "divvy.filter.instance_type",
      "config": {
        "instance_types": [
          "P2",
          "P3",
          "Inf1",
          "G4",
          "G3",
          "F1"
        ],
        "wildcard_search": True
      },
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": [
    {
      "value": "amazon web services",
      "key": "system.cloud_type"
    }
  ],
  "badge_filter_operator": None
})

# Snapshots past retention
insight_configs.append({
  "name": "Cost - Snapshots older than 90 days",
  "description": "Snapshots older than company defined retention period",
  "resource_types": [
    "snapshot"
  ],
  "filters": [
    {
      "name": "divvy.query.resource_age_exceeds_threshold",
      "config": {
        "unit_type": "days",
        "number_of_units": 90
      },
      "collections": {}
    }
  ],
  "scopes": [],
  "severity": 1,
  "owner_resource_id": None,
  "template_id": None,
  "tags": None,
  "badges": None,
  "badge_filter_operator": "OR"
})

# insight_configs.append()


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


# Create the pack
print("Creating a new pack: " + pack_name)
pack_info = create_pack()
print("Pack created. Name: " + pack_info['name'] + " Pack ID: " + str(pack_info['pack_id']))

print("Creating custom insights and adding them to the new pack")
# Loop through insight_configs and add a filter for each
custom_insight_ids = []

for insight in insight_configs:
    print("Creating new insight: " + insight['name'])
    new_insight_info = create_insight(insight)
    custom_insight_ids.append(new_insight_info['insight_id'])

    # Add notes to the insight
    add_insight_notes(new_insight_info['insight_id'],insight['description'])  

# Add all insights to the pack
print("Adding insights to the pack")
pack_update_output = add_insight_to_pack(pack_info, custom_insight_ids)

print("Finished creating pack: " + pack_name)