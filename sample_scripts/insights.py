import json
import logging
from requests.exceptions import ConnectionError

from DivvyApp.DivvyApp import DivvyApp
# from DivvyBlueprints.providers import version
from DivvyResource import ResourceType

from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session

logger = logging.getLogger('BackOffice')
sw_version = '18.6'
BASE_URL = 'https://backoffice.divvycloud.com/v1'

def get(url):
    redis = DivvyApp().redis
    response = None
    key = 'backoffice_api:' + url
    cache = redis.get(key)
    if cache is None:
        with Session() as s:
            s.mount(
                'https://backoffice.divvycloud.com/',
                HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[500, 503]))
            )

            try:
                remote_raw = s.get(BASE_URL + url, timeout=(10, 10))
            except ConnectionError:
                logger.error('Unable to connect to BackOffice')
            else:
                response = json.loads(remote_raw.text)
                redis.set(key, remote_raw.text)
                redis.expire(key, 1800)
    else:
        response = json.loads(cache)

    return response

def list_templates():
    response = get('/templates?version={0}'.format(sw_version))
    if response is not None:
        return response['data']

    return []

resource_types_by_cloud = {
    'AWS': {
        ResourceType.API_ACCOUNTING_CONFIG,
        ResourceType.AUTOSCALING_GROUP,
        ResourceType.AVAILABILITY_ZONE,
        ResourceType.AWS_CONFIG,
        ResourceType.AWS_PLACEMENT_GROUP,
        ResourceType.ROUTE,
        ResourceType.ROUTE_TABLE,
        ResourceType.DATABASE_INSTANCE,
        ResourceType.DATABASE_SNAPSHOT,
        ResourceType.DNS_ZONE,
        ResourceType.DNS_RECORD,
        ResourceType.HYPERVISOR,
        ResourceType.INSTANCE,
        ResourceType.INSTANCE_FLAVOR,
        ResourceType.INSTANCE_RESERVATION,
        ResourceType.INSTANCE_STATUS,
        ResourceType.INTERNET_GATEWAY,
        ResourceType.LOAD_BALANCER,
        ResourceType.NETWORK_INTERFACE,
        ResourceType.NETWORK_FLOW_LOG,
        ResourceType.NETWORK_PEER,
        ResourceType.PRIVATE_IMAGE,
        ResourceType.PRIVATE_NETWORK,
        ResourceType.PRIVATE_SUBNET,
        ResourceType.PUBLIC_IMAGE,
        ResourceType.PUBLIC_IP,
        ResourceType.RESOURCE_LIMIT,
        ResourceType.RESOURCE_ACCESS_LIST,
        ResourceType.SECURITY_GROUP,
        ResourceType.SERVICE_REGION,
        ResourceType.SNAPSHOT,
        ResourceType.SSH_KEY_PAIR,
        ResourceType.STORAGE_CONTAINER,
        ResourceType.STORAGE_CONTAINER_FILE,
        ResourceType.VOLUME,
        ResourceType.MEMCACHE_INSTANCE,
        ResourceType.MEMCACHE_SNAPSHOT,
        ResourceType.ELASTICSEARCH_INSTANCE,
        ResourceType.SERVERLESS_FUNCTION,
        ResourceType.SERVICE_GROUP,
        ResourceType.SERVICE_ROLE,
        ResourceType.SERVICE_USER,
        ResourceType.SERVICE_POLICY,
        ResourceType.SERVICE_CERTIFICATE,
        ResourceType.SERVICE_ACCESS_KEY,
        ResourceType.SERVICE_ENCRYPTION_KEY,
        ResourceType.SERVICE_ALARM,
        ResourceType.BIG_DATA_INSTANCE,
        ResourceType.BIG_DATA_SNAPSHOT,
        ResourceType.DIVVY_ORGANIZATION_SERVICE,
        ResourceType.SHARED_FILE_SYSTEM,
        ResourceType.WORKSPACE,
        ResourceType.DISTRIBUTED_TABLE,
        ResourceType.DISTRIBUTED_TABLE_CLUSTER,
        ResourceType.MESSAGE_QUEUE
    },
    'GCP': {
        ResourceType.AVAILABILITY_ZONE,
        ResourceType.DATABASE_INSTANCE,
        ResourceType.DATABASE,
        ResourceType.DATABASE_SNAPSHOT,
        ResourceType.INSTANCE,
        ResourceType.INSTANCE_FLAVOR,
        ResourceType.PRIVATE_IMAGE,
        ResourceType.PRIVATE_NETWORK,
        ResourceType.PRIVATE_SUBNET,
        ResourceType.PUBLIC_IMAGE,
        ResourceType.PUBLIC_IP,
        ResourceType.RESOURCE_LIMIT,
        ResourceType.SNAPSHOT,
        ResourceType.SERVERLESS_FUNCTION,
        ResourceType.SERVICE_CERTIFICATE,
        ResourceType.SERVICE_REGION,
        ResourceType.STORAGE_CONTAINER,
        ResourceType.SSH_KEY_PAIR,
        ResourceType.VOLUME,
        ResourceType.RESOURCE_ACCESS_LIST
    },
    'AZURE': {
        ResourceType.DATABASE_INSTANCE,
        ResourceType.DATABASE,
        ResourceType.DNS_ZONE,
        ResourceType.INSTANCE,
        ResourceType.INSTANCE_FLAVOR,
        ResourceType.MEMCACHE_INSTANCE,
        ResourceType.PRIVATE_NETWORK,
        ResourceType.PRIVATE_SUBNET,
        ResourceType.RESOURCE_ACCESS_LIST,
        ResourceType.RESOURCE_LIMIT,
        ResourceType.SERVICE_REGION,
        ResourceType.SNAPSHOT,
        ResourceType.PRIVATE_IMAGE,
        ResourceType.VOLUME
    }
}

insight_breakdown = {}
for template in list_templates():
    supported_dict = {'AWS': 'N', 'GCP': 'N', 'AZURE': 'N'}
    for cloud, supported_resource_types in resource_types_by_cloud.items():
        supported = False not in [e in supported_resource_types for e in template['resource_types']]
        supported_dict[cloud] = 'Y' if supported else 'N'
    insight_breakdown[template['name']] = supported_dict

# Convert to a CSV
# Store report CSV text here
csv_data = 'Insight,Amazon,Google,Azure\n'
for insight, cloud_breakdown in insight_breakdown.items():
    csv_data += '"{0}", {1}, {2}, {3}\n'.format(
        insight, cloud_breakdown['AWS'], cloud_breakdown['GCP'], cloud_breakdown['AZURE']
    )

print csv_data
