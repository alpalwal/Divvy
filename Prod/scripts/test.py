import json
import os
import requests
# Username/password to authenticate against the API
username = ''
password = ''
# API URLs
base_url = ''
login_url = base_url + '/v2/public/user/login'
# Insight Configuration
PACK_IDS = ['backoffice:6', 'custom:36', 'custom:37']
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
def get_packs(auth_token):
    response = requests.get(
            url=base_url + '/v2/public/insights/packs/list',
        headers={
                'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        }
    )
    return response.json()
def get_cloud_accounts(auth_token):
    """
    Return a mapping of organization service IDs to account names/IDs
    """
    cloud_account_mapping = {}
    response = requests.get(
            url=base_url + '/v2/public/clouds/list',
        headers={
                'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        }
    )
    for cloud in response.json().get('clouds', []):
        cloud_account_mapping[cloud['id']] = {
                'account_id': cloud.get('account_id'),
            'name': cloud['name'],
            'cloud_type_id': cloud['cloud_type_id'],
            'pack_results': {}
        }
    return cloud_account_mapping
def get_insight_data(auth_token):
    response = requests.get(
            url=base_url + '/v2/public/insights/list',
        headers={
                'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        },
        stream=True
    )
    return response.json()
def process_insight_data(cloud_accounts, insight_data, pack):
    for org_svc_id_str, data in insight_data.items():
        org_svc_id = int(org_svc_id_str)
        if org_svc_id in cloud_accounts:
            if pack['name'] not in cloud_accounts[org_svc_id]['pack_results']:
                cloud_accounts[org_svc_id]['pack_results'][pack['name']] = {
                        'compliant': 0,
                    'noncompliant': 0
                }
            d = cloud_accounts[org_svc_id]['pack_results'][pack['name']]
            compliant_count = data['total'] - data['count']
            noncompliant_count = data['count']
            d.update({
                    'compliant': d['compliant'] + compliant_count,
                'noncompliant': d['noncompliant'] + noncompliant_count
            })
def run():
    auth_token = get_auth_token()
    cloud_accounts = get_cloud_accounts(auth_token)
    insight_data = get_insight_data(auth_token)
    # print insight_data
    pack_mapping = {}
    for pack in get_packs(auth_token):
        composite_id = '{0}:{1}'.format(pack['source'], pack['pack_id'])
        pack_mapping[composite_id] = pack
    for pack_id in PACK_IDS:
        # Only generate the data for legit, known packs.
        pack = pack_mapping.get(pack_id)
        if pack:
            backoffice_ids = pack.get('backoffice', [])
            custom_ids = pack.get('custom', [])
            for insight in insight_data:
                if insight['source'] == 'backoffice' and insight['insight_id'] in backoffice_ids:
                    process_insight_data(cloud_accounts, insight['by_cloud'], pack)
                elif insight['source'] == 'custom' and insight['insight_id'] in custom_ids:
                    process_insight_data(cloud_accounts, insight['by_cloud'], pack)
    print json.dumps(cloud_accounts, indent=2)
run()