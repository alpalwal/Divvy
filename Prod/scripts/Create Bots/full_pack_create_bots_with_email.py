# Script to create a bot for all insights in a pack
# Currently set up for slack

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
base_url = ''
login_url = base_url + '/v2/public/user/login'

# PARAMS
pack_name = "Top Security Concerns"

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

def get_packs():
    response = requests.get(
        url=base_url + '/v2/public/insights/packs/list',
        headers=headers
        )
    return response.json()

def get_insights():
    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        headers=headers
        )
    return response.json()    

def make_bot(insight):
    bot_name = "Email - " + insight['name']
    bot_message = "Security issue found. Name: *" + insight['name'] + "* Resource Name: *{{resource.name}}*"

    data = {
        "name": bot_name,
        "description": "Demo",
        "severity": "low",
        "category": "Security",
        "ondemand_enabled": True,
        "state": "RUNNING",
        "scope": ["divvyorganizationservice:1"],
        "instructions": {
            "resource_types": insight['resource_types'],
            "groups": ["divvyorganizationservice:1"],
            "filters": insight['filters'],
            "schedule": None,
            "schedule_description": None,
            "badges": [
            {
                "key": "system.resource_type",
                "value": "cloud"
            }
            ],
            "ondemand_enabled": True,
            "hookpoints": [   
                "divvycloud.resource.created",
                "divvycloud.resource.modified"
            ],
            "actions": [
            {
                "run_when_result_is": True,
                "config": {},
                "name": "divvy.action.mark_non_compliant"
            },
            {
                "run_when_result_is": True,
                "config": {
                "message_body": "Security issue found\nResource data: {{resource.serialize(indent=2)}}",
                "html_message": False,
                "recipient_list": [
                "alex.corstorphine+securityalias@divvycloud.com"
                ],
                "recipient_badge_keys": [],
                "message_subject": "DivvyCloud - " + insight['name'],
                "hours": 0,
                "recipient_tag_keys": [
                "email_owner"
                ],
                "skip_duplicates": False
                },
                "name": "divvy.action.send_delayed_email"
            }
            ]
        }
    }


    response = requests.post(
        url=base_url + '/v2/public/botfactory/bot/create',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

def trigger_bot( bot_id):
    response = requests.post(
        url=base_url + '/v2/public/botfactory/' + bot_id + '/ondemand',
        headers=headers
        )
    return response.json()   
    
auth_token = get_auth_token()

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': auth_token
}

# Get the list of packs to loop through and look for the one that was defined
pack_response = get_packs()

# Get the pack ID
for pack in pack_response:
    if pack['name'] == pack_name:
        print ("FOUND PACK")
        break   

# Normal insights are in the backoffice array
backoffice = pack['backoffice']

# Custom insights are in the custom array. Add them to  backoffice
backoffice.extend(pack['custom'])

# Get the info from the insights in the pack
insights_response = get_insights() 
for insight in backoffice:
    # look through the insights for a matching ID
    # if we find it - create a bot
    for response in insights_response:
        if response['insight_id'] == insight:
            print("Creating bot")
            new_bot = make_bot(response)
            print("Made a new bot: " + new_bot['name'])
            # bot_trigger = trigger_bot(new_bot['resource_id'])
            # print("Triggered bot")
            break
