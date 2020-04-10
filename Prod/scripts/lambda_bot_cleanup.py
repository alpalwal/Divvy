# Bot to run in lambda and cleanup paused divvy bots on sales demo daily

import boto3
import os
import json
from botocore.vendored import requests
from base64 import b64decode

base_url = os.environ['DIVVY_URL']
login_url = base_url + '/v2/public/user/login'

ENCRYPTED_USERNAME = os.environ['USERNAME']
ENCRYPTED_PASSWORD = os.environ['PASSWORD']
# Decrypt code should run once and variables stored outside of the function handler so that these are decrypted once per container
username = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_USERNAME))['Plaintext'].decode('utf-8')
password = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_PASSWORD))['Plaintext'].decode('utf-8')

def lambda_handler(event, context):

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

    
    auth_token = get_auth_token()
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'X-Auth-Token': auth_token
    }

    # Get bot info
    def get_bots():
        data = {"filters":[],"limit":500,"offset":0}

        response = requests.post(
            url=base_url + '/v2/public/botfactory/list',
            data=json.dumps(data),
            headers=headers
            )
        return response.json()

    # archive bots
    def archive_bot(resource_id):
        data = {"resource_ids": [bot['resource_id']]}

        response = requests.post(
            url=base_url + '/v2/public/botfactory/bots/bulk_action/archive',
            data=json.dumps(data),
            headers=headers
            )
        return response

    # list all bots
    bot_info = get_bots()

    for bot in bot_info['bots']:
        if bot['state'] == "PAUSED":
            print("Found paused bot to archive: " + bot['name'])
            
            result = archive_bot(bot['resource_id'])
            print(result)



