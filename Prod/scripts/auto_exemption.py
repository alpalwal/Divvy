# Script to create an exception for a resource programmatically 

# Sample Slack Notification:
# An insecure storage container was identified with public permissions to the world.
# Name: `supersecretdatabucket123`
# The details of this resource are:
# ```{
#   "website": false,
#   "object_count": 0,
#   "total_size": 0.0,
#   "creation_date": "2019-05-14 22:01:51",
#   "common": {
#     "account": "AWS Sales Account",
#     "resource_name": "supersecretdatabucket123",
#     "organization_service_id": 1,
#     "account_id": "014578312761",
#     "resource_id": "storagecontainer:1:us-west-1:supersecretdatabucket123:",
#     "region": "us-west-1",
#     "modified_timestamp": "2019-05-14 22:02:05",
#     "discovered_timestamp": "2019-04-15 00:47:05",
#     "cloud": "AWS",
#     "creation_timestamp": "2019-04-15 00:46:10",
#     "resource_type": "storagecontainer"
#   },
#   "policy_encryption": false,
#   "public": true
# }```
# .
# The container has been quarantined to prevent data exposure

### Sample Jinja2:
# An insecure storage container was identified with public permissions to the world.
# Name: `{{resource.name}}`
# The details of this resource are:
# Bot ID: *{{event.bot_id}}*
# ```{{resource.serialize(indent=2)}}```.
# The container has been quarantined to prevent data exposure

# Insight fires w/ issue and sends to slack
# Slack message has the divvy ID of the resource and bot in it 
# Add the params of the resource ID, bot ID, resource group name, and description

import json
import requests
import getpass

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URLs
base_url = 'https://sales-demo.divvycloud.com'
login_url = base_url + '/v2/public/user/login'

# Inputs:
resource_id = ""
resource_group_name = ""
resource_group_description = ""
bot_id = ""

## Parameter validation:


if not username:
    username = input("Please add a username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not resource_id:
    resource_id = input("Please add a resource ID. (Ex: storagecontainer:1:us-west-1:databucket123:): ")

if not resource_group_name:
    resource_group_name = input("Please add a resource group name: ")

if not resource_group_description:
    resource_group_description = input("Please add a resource group description: ")

if not bot_id:
    bot_id = input("Please input bot ID (Ex: 1458): ")

if not bot_id or not resource_group_name or not resource_group_description or not resource_id or not username:
    print ("All parameters are required. Please ensure there are no blank params and try again")
    exit()     
    
# Resource IDs have a trailing colon that's easy to leave off
if not resource_id.endswith(':'):
    print ("Please ensure that the resource_id has a trailing colon. \nEx: storagecontainer:1:us-west-1:supersecretdatabucket123:")
    exit()
if len(resource_group_name) > 64:
    print ("Max length for the resource group name is 64 characters. Please shorten and try again")
    exit()
if len(resource_group_description) > 255:
    print ("Max length for the resource group description is 255 characters. Please shorten and try again")
    exit()       

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

# Create a new resource group
def create_resource_group():
    data = {
        "group_name": resource_group_name,
        "group_owner_type": "organization",
        "group_description": resource_group_description
    }

    response = requests.post(
        url=base_url + '/v2/public/resourcegroup/create',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    
# Sample Response 
# {
#   "category": "system",
#   "resource_group_id": 83,
#   "description": "new resource group",
#   "creation_time": "2019-05-14 21:58:01",
#   "nested_resource_groups": [],
#   "owner_type": "organization",
#   "id": "resourcegroup:83:",
#   "group_type": "user",
#   "name": "deleteme"
# }

# Add resource to group
def add_resource_to_group(resource_group_full_id):
    data = {
        "resource_group_ids":[resource_group_full_id],
        "resource_ids":[resource_id]
    }
 
    response = requests.post(
        url=base_url + '/v2/prototype/resourcegroups/resources/add',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    
# Sample Response 
# {
#   "resource_ids": [
#     "instance:17:asia-northeast1:mongodb-instance:"
#   ]
# }

# Get info about the insight the bot is created from 
def get_bot_info(bot_id):
    response = requests.get(
        url=base_url + '/v2/public/botfactory/divvybot:1:' + bot_id + '/get',
        headers=headers
        )
    return response.json()    

# Get list of insight exception resource groups 
def get_insight_info(source,insight_number):
    response = requests.get(
        url=base_url + '/v2/public/insights/' + insight_number + '/' + source,
        headers=headers
        )
    return response.json()    


# Add exception to insight
def add_exemption(exemption_list,source):
    # Split insight ID into backoffice/custom and the ID

    data = {
        "source":source,
        "groups":exemption_list
    }

    # Sample: {"source":"backoffice","groups":[118]}

    response = requests.post(
        url=base_url + '/v2/public/insights/' + insight_number + '/set_exemptions',
        data=json.dumps(data),
        headers=headers
        )
    return response    
# Sample Response 
# <none>

# Get list of scheduled events
def get_scheduled_events(bot_id):
    full_bot_id = 'divvybot:1:' + bot_id
    data = {
        "filters": [
            {
            "field_name": "creation_resource_id",
            "filter_type": "EXACT",
            "filter_value": full_bot_id
            }
        ],
        "limit": 50,
        "offset": 0,
        "order_by": "creation_time DESC"
        }
        # Sample: 
        # {
        #   "filters": [
        #     {
        #       "field_name": "creation_resource_id",
        #       "filter_type": "EXACT",
        #       "filter_value": "divvybot:1:1468"
        #     }
        #   ],
        #   "limit": 50,
        #   "offset": 0,
        #   "order_by": "creation_time DESC"
        # }

    response = requests.post(
        url=base_url + '/v2/prototype/scheduled_events/get',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()
# Sample Response 
# Out:
# {
#   "total": 1,
#   "events": [
#     {
#       "provider_id": "supersecretdatabucket123",
#       "target_resource_id": "storagecontainer:1:us-west-1:supersecretdatabucket123:",
#       "event_type": "divvy.cleanup_storage_container_permissions",
#       "last_run_status": "SUCCESS",
#       "event_id": 75309,
#       "description": "Event Scheduled by bot.",
#       "next_scheduled_run": null,
#       "creation_time": "05/15/2019 22:13:19",
#       "account": "AWS Sales Account",
#       "schedule": "Once @ 2019-05-15 22:19:19",
#       "bot_name": "DEMO - S3 Bucket Data Exposure (supersecretbucket123)",
#       "cloud": "AWS",
#       "event_state": "INACTIVE",
#       "scheduled_by": "Alex Corstorphine",
#       "resource_type": "storagecontainer",
#       "name": "supersecretdatabucket123"
#     }
#   ]
# }

# Remove the scheduled events (if there are any)
def remove_scheduled_events(events_to_remove):
    data = {
        "action": "delete",
        "event_ids": events_to_remove
    }
    # Sample: 
    # {
    #   "action": "delete",
    #   "event_ids": [
    #     75309
    #   ]
    # }

    response = requests.post(
        url=base_url + '/v2/prototype/scheduled_events/execute_action',
        data=json.dumps(data),
        headers=headers
        )
    return response
# Sample Response 
# None

#### Do work starting here ####

print ("Creating resource group. Name: " + resource_group_name + "\nDescription:" + resource_group_description)
resource_group_response = create_resource_group()

if 'error_message' in resource_group_response:
    print("Error creating the resource group. Exiting. Error:")
    print (resource_group_response['error_message'])
    exit()

resource_group_full_id = resource_group_response['id']
resource_group_short_id = resource_group_response['resource_group_id']

print ("Adding resource to new resource group. Resource ID: " + resource_id)
add_resource_to_group(resource_group_full_id)

print("Getting the insight ID that this bot was created from")
insight_info = get_bot_info(bot_id)
insight_number = str(insight_info['insight_id'])
source = insight_info['source']

print("Getting current list of exemptions on the insight")
# We need to do this because we can't just append a new group to the insight without removing the ones that are already on there
insight_info = get_insight_info(source,insight_number)
current_exemptions = insight_info['resource_group_blacklist']

exemption_list = [resource_group_short_id]
# current_exemptions can be none, an empty list, or a list with values. If there's something useful, add it to the exemptions list
if type(current_exemptions) is list:
    exemption_list = exemption_list + current_exemptions

print("Adding resource group to the exceptions list for insight id: " + source + ":" + insight_number)
add_exemption(exemption_list,source)

print("Exception added")

print("Checking for scheduled events to remove on this insight")

# Remove all scheduled events for the resource in question
scheduled_events = get_scheduled_events(bot_id)
events_to_remove = []
for event in scheduled_events['events']:
    if event['target_resource_id'] == resource_id:
        events_to_remove.append(event['event_id'])

if len(events_to_remove) > 0:
    print("Removing scheduled events")
    remove_scheduled_events(events_to_remove)
else:
    print("No scheduled events to remove")
                

print("Done")
