# Script to create an exception for a resource programmatically 
# Sample Slack Event:
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

import json
import requests
import getpass

# Username/password to authenticate against the API
username = "alex_test"
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

# API URLs
base_url = 'https://sales-demo.divvycloud.com'
login_url = base_url + '/v2/public/user/login'

# Inputs:
resource_id = "storagecontainer:1:us-west-1:supersecretdatabucket123:"
## Do all resources have trailing :s? If so - add error handling / regex
resource_group_name = "S3_public_exception1"
resource_group_description = "Exception ID: 1 for s3 exposure"
# Add check to make sure resource group description is less than 255 characters / 64 for name
bot_id = "1468"

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
    print(data)
    # Sample: {"source":"backoffice","groups":[118]}

    response = requests.post(
        url=base_url + '/v2/public/insights/' + insight_number + '/set_exemptions',
        data=json.dumps(data),
        headers=headers
        )
    return response    
# Sample Response 
# <none>


#### Do work starting here ####

print ("Creating resource group. Name:" + resource_group_name + "\nDescription:" + resource_group_description)
resource_group_response = create_resource_group()
## Add in error handling here - 
# Response - {'error_message': 'A resource group with this name already exists. Please try a different name.', 'error_type': 'Exception'}
resource_group_full_id = resource_group_response['id']
resource_group_short_id = resource_group_response['resource_group_id']

print ("Adding resource to new resource group. Resource ID:" + resource_id)
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

print("Adding resource group to the exceptions list for insight id:" + source + ":" + insight_number)
add_exemption(exemption_list,source)

print("Exception added")

