import json
import requests
import boto3
from DivvyBotfactory.registry import BotFactoryRegistryWrapper
from DivvyBotfactory.event import BotEvent
from DivvyUtils.field_definition import FieldOptions, StringField, TextField

registry = BotFactoryRegistryWrapper()

@registry.action(
	uid='custom.action.post_to_sns',
	name='Post To SNS',
	bulk_action=True,
	admin_only=True,
	expensive=False,
	description=(
		'Post a message to SNS '
	),
	author='DivvyCloud',
	supported_resources=[],
	settings_config=[]
)

def post_to_sns(bot, settings, matches, non_matches):

	topic_arn="arn:aws:sns:us-west-2:014578312761:divvyNotifications"
	split_topic = topic_arn.split(":")
	topic_account_id = split_topic[4]
	region = split_topic[3]
	
	message_subject="Test Subject"
	message_body="Test Body"	

	for match in matches:
		account = match.get_organization_service().account_id

		if account != topic_account_id:
			#creating a divvy session to assume role into the violating resource's account
			boto_sts = boto3.client('sts')
			stsresponse = boto_sts.assume_role(
				RoleArn = 'arn:aws:iam::'+account+':role/DivvyCloud',
				RoleSessionName = 'DivvySession'
			)
			#saving the creds from the assume role
			newsession_id = stsresponse['Credentials']['AccessKeyId']
			newsession_key = stsresponse['Credentials']['SecretAccessKey']
			newsession_token = stsresponse['Credentials']['SessionToken']
			#create a client with the new session creds
			sns_assumed_client = boto3.client(
				'sns',
				region_name = region,
				aws_access_key_id = newsession_id,
				aws_secret_access_key = newsession_key,
				aws_session_token = newsession_token
			)
		else:
			sns_assumed_client = boto3.client('sns', region_name = region) 

		response = sns_assumed_client.publish(
			TopicArn=topic_arn,
			Message=message_body,
			Subject=message_subject
		)

def load():
	registry.load()