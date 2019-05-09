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
base_url = 'https://sales-demo.divvycloud.com'
login_url = base_url + '/v2/public/user/login'

# PARAMS
pack_name = "Cost Control"
slack_channel = "#botalerts"

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
    bot_name = "Slack - " + insight['name']
    bot_message = "Security issue found. Name: *" + insight['name'] + "* Resource Name: *{{resource.name}}*"

    data = {
        "name": bot_name,
        "description": "Demo",
        "severity": "low",
        "category": "Security",
        "ondemand_enabled": True,
        "state": "RUNNING",
        "instructions": {
            "resource_types": insight['resource_types'],
            "groups": [],
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
                "username": "DivvyCloud",
                "recipient_badge_keys": [],
                "recipient_tag_keys": [],
                "message": bot_message,
                "channel": slack_channel,
                "skip_duplicates": False
                },
                "name": "slack.action.send_slack_message"
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
i = 0
while i < len(pack_response):
    if pack_response[i]['name'] == pack_name:
        print ("FOUND PACK")
        break
    i += 1    

# Normal insights are in the backoffice array
backoffice = pack_response[i]['backoffice']

# Custom insights are in the custom array. Add them to  backoffice
backoffice.extend(pack_response[i]['custom'])

# Get the info from the insights in the pack
insights_response = get_insights() 

j = 0
while j < len(backoffice):
    # look through the insights for a matching ID
    # if we find it - create a bot
    k=0
    while k < len(insights_response):
        if insights_response[k]['insight_id'] == backoffice[j]:
            print("Creating bot")
            new_bot = make_bot(insights_response[k])
            print("Made a new bot: " + new_bot['name'])
            bot_trigger = trigger_bot( new_bot['resource_id'])
            print("Triggered bot")
            break
        else:
            k += 1
    j += 1    
    
