import json

import jinja2
from DivvyBotfactory.event import BotEvent
from DivvyBotfactory.registry import BotFactoryRegistryWrapper
from DivvyBotfactory.scheduling import ScheduledEventTracker, schedule_hours_from_now
from DivvyDb.QueryFilters.cloud_types import CloudType
from DivvyUtils.field_definition import (
    FieldOptions, StringField, Jinja2TextField, FloatField
)

registry = BotFactoryRegistryWrapper()


@registry.action(
    uid='custom.action.instance_publish_to_cloud_topic',
    name='Publish to Cloud Notification Topic',
    bulk_action=True,
    expensive=False,
    description=(
        'Publish a message to a topic from the platform. Note that this topic '
        'must allow access.'
    ),
    author='Customer',
    supported_resources=[],
    supported_clouds=[
        CloudType.AMAZON_WEB_SERVICES
    ],
    settings_config=[
        StringField(
            name='cloud_topic',
            display_name='Cloud Topic',
            options=FieldOptions.REQUIRED,
            description=(
                'The unique ID (e.g. ARN) of the topic to submit a message to. '
                'Note that the account the supplied ARN lives must be '
                'harvested by DivvyCloud, as this action will use the '
                'credentials of the topic\'s account to submit the message.'
            )
        ),
        Jinja2TextField(
            name='message_attributes',
            display_name='Message Attributes (Optional)',
            description=(
                'Optional message attributes. The format must be a dictionary '
                'and adhere to the structure documented via '
                'https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish'
            )
        ),
        StringField(
            name='subject',
            display_name='Subject',
            description='The message subject (Optional)'
        ),
        Jinja2TextField(
            name='message',
            display_name='Topic Message',
            description=(
                'The message payload to send to the topic. Note that Jinja2 templating is supported.'
            )
        ),
        FloatField(
            name='hours',
            display_name='Delay Hours',
            description=(
                'How many hours to wait before taking the action? Zero hours '
                'means the event will be scheduled for one minute out. Decimal '
                'values can be used to specify minutes. For example, to '
                'specify 15 minutes use 0.25.'
            ),
            min_value=0,
            options=FieldOptions.REQUIRED
        )
    ]
)
def instance_publish_to_cloud_topic(bot, settings, matches, _non_matches):
    with ScheduledEventTracker() as context:
        for resource in matches:
            # Stubs event so templates are backwards compatable
            event = BotEvent('hookpoint', resource, bot.bot_id, bot.name)
            message = jinja2.Template(settings.get('message', ''))
            action_data = {
                'cloud_topic': settings['cloud_topic'],
                'message': message.render(event=event, resource=resource),
                'message_attributes': settings.get('message_attributes', ''),
                'subject': settings.get('subject', '')
            }
            context.schedule_bot_event(
                bot=bot,
                resource=resource,
                description='SNS publish event scheduled by bot.',
                event_type='custom.instance_publish_to_cloud_topic',
                schedule_data=schedule_hours_from_now(settings['hours']),
                action_data=json.dumps(action_data)
            )


def load():
    registry.load()
