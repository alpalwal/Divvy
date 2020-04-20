## BOT STATE == paused
## TRIGGER Bot == disabled
### Pack_ID needs to be updated

# Script to create a bot for all insights in a pack
import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False in the request throws a security error otherwise

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
pack_id = "custom:167"
pack_split = pack_id.split(":")
pack_number = int(pack_split[1])
backoffice_or_custom = pack_split[0]

# Shorthand helper function
def get_auth_token():
    response = requests.post(
        url=login_url,
        verify=False,
        data=json.dumps({"username": username, "password": passwd}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        })
    return response.json()['session_id']

def get_packs():
    response = requests.get(
        url=base_url + '/v2/public/insights/packs/list',
        verify=False,
        headers=headers
        )
    return response.json()

def get_insights():
    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        verify=False,
        headers=headers
        )
    return response.json()    

def make_bot(insight):
    bot_name = insight['name'] + " - ServiceNow"
    bot_message = "Security issue found. Name: *" + insight['name'] + "* Resource Name: *{{resource.name}}*"
 
    data = {
        "name": bot_name,
        "description": "ServiceNow Integration",
        "severity": "low",
        "category": "Security",
        "ondemand_enabled": True,
        "state": "PAUSED",
        "instructions": {
            "resource_types": insight['resource_types'],
            "groups": [],
            "filters": insight['filters'],
            "schedule": None,
            "schedule_description": None,
            #All cloud accounts
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
                "config": {
                "description": bot_name,
                "urgency": "1",
                "comments": bot_message
            },
                "name": "servicenow.action.create_incident"
            }
            ]
        }
    }
    response = requests.post(
        url=base_url + '/v2/public/botfactory/bot/create',
        verify=False,
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

def trigger_bot( bot_id):
    response = requests.post(
        url=base_url + '/v2/public/botfactory/' + bot_id + '/ondemand',
        verify=False,
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
found_pack = False
for pack in pack_response:
    if pack['pack_id'] == pack_number:
        if pack['source'] == backoffice_or_custom:
            found_pack = True
            print("Found matching pack. Name: " + pack['name'])
            backoffice_insights = pack['backoffice'] # Normal insights are in the backoffice array        
            custom_insights = (pack['custom']) # Custom insights are in the custom array. Add them to  backoffice
            break  

if not found_pack:
    print("No pack found matching \"" + pack_id + "\". Exiting.")
    exit()

# Get the info from the insights in the pack
insights_response = get_insights() 

# look through the insights for a matching ID
# if we find it - create a bot
print("\n == Creating bots from backoffice insights")
for backoffice_insight in backoffice_insights:
    for insight in insights_response:
        if insight['source'] == "backoffice":
            if insight['insight_id'] == backoffice_insight:
                new_bot = make_bot(insight)
                print("Made a new bot: " + new_bot['name'])
                
                # bot_trigger = trigger_bot( new_bot['resource_id'])
                # print("Triggered bot")
                break

print("\n == Creating bots from custom insights")
for custom_insight in custom_insights:
    for insight in insights_response:
        if insight['source'] == "custom":
            if insight['insight_id'] == custom_insight:
                new_bot = make_bot(insight)
                print("Made a new bot: " + new_bot['name'])
                
                # bot_trigger = trigger_bot( new_bot['resource_id'])
                # print("Triggered bot")
                break
