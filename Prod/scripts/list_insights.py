# Script to list all pre-canned insights by cloud. 
# Sample output:
# ================================================================
# ===========================AWS==================================
# ================================================================
# Cloud Account Without Global API Accounting Config
# Instance Has Ephemeral Public IP
# Database Instance Retention Policy Too Low
# Load Balancer Cross Zone Balancing Disabled
# Load Balancer Connection Draining Disabled

import json
import requests
import getpass

# Username/password to authenticate against the API
username = "alexc"
password = "9srZMS%0PxlY" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URL
base_url = "https://sales-demo.divvycloud.com"

# Param validation
if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

# Full URL
login_url = base_url + '/v2/public/user/login'

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

# Get Org info
def get_insights():
    data = {}

    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Create the pack
insight_info_array = get_insights()

#print(insight_info_array)

aws = []
aws_china = []
aws_gov = []
gcp = [] 
azure = []
alicloud = []
k8s = []

for insight in insight_info_array:
    if insight['source'] == 'backoffice':
        name = insight['name']
        # print(clouds_list)
        supported_resources = insight['resource_types']

        clouds_list = insight['supported_clouds']
        if clouds_list:
            for cloud in clouds_list:
                if cloud == 'AWS_GOV':
                    aws_gov.append(name)
                if cloud == 'AWS_CHINA':
                    aws_china.append(name)
                if cloud == 'AWS':
                    aws.append(name)
                if cloud == 'AZURE_ARM':
                    azure.append(name)
                if cloud == 'ALICLOUD':
                    alicloud.append(name)
                if cloud == 'K8S':
                    k8s.append(name)


print("================================================================")                
print("===========================AWS==================================")                
print("================================================================")  
for insight in aws:
    print(insight)              
print("")
print("")

print("================================================================")                
print("===========================AWS-GOV==============================")                
print("================================================================")  
for insight in aws_gov:
    print(insight)  
print("")
print("")

print("================================================================")                
print("===========================AWS-CHINA============================")                
print("================================================================")  
for insight in aws_china:
    print(insight)  
print("")
print("")

print("================================================================")                
print("===========================AZURE================================")                
print("================================================================")  
for insight in azure:
    print(insight)  
print("")
print("")

print("================================================================")                
print("===========================ALICLOUD=============================")                
print("================================================================")  
for insight in alicloud:
    print(insight)  
print("")
print("")

print("================================================================")                
print("===========================K8S==================================")                
print("================================================================")  
for insight in k8s:
    print(insight)  
print("")
print("")


            
#     'name': 'Cloud Account Without Global API Accounting Config',
#     'supported_clouds': ['AWS_GOV', 'AWS_CHINA', 'AWS'],
#     'resource_types': ['divvyorganizationservice'],
#     'insight_id': 2,

#   'favorited': False,
#   'cache_updated_at': '2019-06-12T23:35:56.907724',
#   'description': 'Match instances with an ephemeral public IP address',
#   'resource_group_blacklist': None,
#   'updated_at': '2019-06-11T09:30:22Z',
#   'results': 29,
#   'meta_data': None,
#   'by_type': {
#     'instance': 29
#   'custom_severity': None,
#   'name': 'Instance Has Ephemeral Public IP',
#   'supported_clouds': ['GCE', 'AWS_CHINA', 'AZURE_ARM', 'AZURE_GOV', 'AWS_GOV', 'AWS'],
#   'resource_types': ['instance'],
#   'severity': 1,
#   'insight_id': 4,
#   'inserted_at': '2017-12-07T00:07:15Z',
#   'notes': '## Overview\n\nCompute instances can have static or dynamic (ephemeral) public IP addresses associated with them. Static addresses will remain intact and persist through lifecycle actions such as stop/start. This can be essential when the resource is used for direct connectivity and does not sit behind a load balancer. Ephemeral addresses will commonly change, and can result in a loss of connectivity to the system if it is routinely stopped/started.\n\nFor some workloads such as web servers this may not represent a true problem. These systems are intended to be ephemeral and in many cases should not have a public IP at all. This Insight can be reconfigured to leverage that tagging policy to identify those mission critical systems which should be updated. It is strongly encouraged to leverage a tagging policy to identify scenarios where this is acceptable. \n\n### Remediation\n\nFor production facing/critical workloads which cannot be taken offline, consider attaching an persistent public iP address. This can be done without taking the machine offline. Be aware that when doing this you may need to update DNS to point to the newly reserved IP address.\n\n\n### Compliance Information\n  - SOC 2: C1.2, C1.3, C1.7, CC5.6, A1.1',
#   'source': 'backoffice',

