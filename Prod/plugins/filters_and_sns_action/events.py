import boto3
import json
import traceback
from datetime import datetime

from DivvyCloudProviders.Common.Frontend.frontend import get_cloud_type_by_organization_service_id
from DivvyDb import DivvyDbObjects
from DivvyDb.DivvyCloudGatewayORM import DivvyCloudGatewayORM
from DivvyDb.DivvyDb import SharedSessionScope
from DivvyWorkers.Processors.ScheduledEvents import ScheduledEventManager
from DivvyWorkers.ScheduledWorkers.base import ScheduledEventJob
from worker.registry import Router
from DivvyWorkers.Processors.ScheduledEvents import cast_scheduled_event_args


@ScheduledEventManager.register('custom.instance_publish_to_cloud_topic')
class InstancePublishToCloudTopic(ScheduledEventJob):

    def __init__(
        self, resource_id, user_resource_id, scheduled_event_id,
        scheduled_event_type, cloud_topic, message, subject, message_attributes
    ):
        super(InstancePublishToCloudTopic, self).__init__(
            resource_id=resource_id,
            user_resource_id=user_resource_id,
            scheduled_event_id=scheduled_event_id,
            scheduled_event_type=scheduled_event_type
        )

        self.cloud_topic = cloud_topic
        self.message = message
        self.message_attributes = message_attributes
        self.subject = subject

    @SharedSessionScope(DivvyCloudGatewayORM)
    def run(self):
        start_time = datetime.utcnow()

        # Get a mapping of topic ARNs to organization service IDs
        db = DivvyCloudGatewayORM()
        org_svc_mapping = dict(
            db.session.query(
                DivvyDbObjects.NotificationTopic.arn,
                DivvyDbObjects.NotificationTopic.organization_service_id
            )
        )
        org_svc_id = org_svc_mapping.get(self.cloud_topic)
        if not org_svc_id:
            raise ValueError('Unable to identify organization service ID')
        region = self.cloud_topic.split(':')[3]
        frontend = get_cloud_type_by_organization_service_id(org_svc_id)
        backend = frontend.get_cloud_gw(region_name=region)
        client = backend.client('sns')

        try:
            params = {
                'TopicArn': self.cloud_topic,
                'Message': self.message
            }
            if self.message_attributes:
                params['MessageAttributes'] = json.loads(str(self.message_attributes))
            if self.subject:
                params['Subject'] = self.subject

            client.publish(**params)
            status = 'SUCCESS'
            result_data = None

        except Exception:
            status = 'ERROR'
            result_data = traceback.format_exc()

        self.store_event_history(
            start_time=start_time,
            finish_time=datetime.utcnow(),
            status=status,
            result_data=result_data
        )


def load():
    Router.add_scheduled_event_job(
        'custom.instance_publish_to_cloud_topic',
        InstancePublishToCloudTopic,
        cast_scheduled_event_args
    )


def unload():
    pass
