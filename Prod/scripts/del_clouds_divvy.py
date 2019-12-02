#!/usr/local/bin/python

import boto3
import time
import urllib
import urllib2
import json
import ssl
import gzip
from botocore.exceptions import ClientError
from StringIO import StringIO

client = boto3.client('organizations')
# Get a list of accounts to add
currentDivvyAccounts = {}

# Account variables
# Bypass SSL cert check
context = ssl._create_unverified_context()
divvyHost = 'https://YOUR-URL-HERE'
divvyLogin = '%s/v2/public/user/login' % (divvyHost)
divvyUser = 'YOUR-USERNAME-HERE'
divvyPass = 'YOUR-PASSWORD-HERE'
loginData = {'username':'%s' % (divvyUser), 'password':'%s' % (divvyPass)}
accountPaginationLimit = 25
accountPaginationOffset = 0
accountListData = {'limit':accountPaginationLimit,'offset':accountPaginationOffset,'order_by':'name','filters':[]}
divvyListAccount = '%s/v2/public/clouds/list' % (divvyHost)
xAuthToken = ''
accountName = ''
accountNumber = ''

# Login to DivvyCloud and get token
try:
	req = urllib2.Request(divvyLogin, json.dumps(loginData), {'Content-Type': 'application/json'})
	f = urllib2.urlopen(req, context=context)
	httpResponse = f.read()
	httpResponse = json.loads(httpResponse)
	xAuthToken = httpResponse['session_id']
	f.close()

except urllib2.URLError as e:
	print "An error %s " %e

# Get a list of all AWS accounts already in DivvyCloud
try:
	print "Getting a list of existing accounts..."
	nextPage = True
	accountPaginationLimit = 25
	accountPaginationOffset = 0

	while nextPage:
		accountListData = {'limit':accountPaginationLimit,'offset':accountPaginationOffset,'order_by':'name','filters':[]}

		req = urllib2.Request(divvyListAccount, json.dumps(accountListData), {'Accept-Encoding': 'gzip, deflate, br', 'Content-Type': 'application/json;charset=UTF-8', \
		'Accept': 'application/json, text/plain, */*', 'X-Auth-Token': '%s' % (xAuthToken)})

		f = urllib2.urlopen(req, context=context)
		buffer = StringIO( f.read() )
		gzipResponse = gzip.GzipFile(fileobj=buffer)
		gzipResponse = gzipResponse.read()
		httpResponse = json.loads(gzipResponse)
		f.close()
		accountTotal = httpResponse['total_count']

		# Add known accounts to dict
		for item in httpResponse['clouds']:
			if item['cloud_type_id'] == 'GCE':
				try:
					currentDivvyAccounts[item['resource_id']] = item['name']
				except KeyError:
					pass

		accountPaginationOffset += accountPaginationLimit
		#time.sleep(1)

		if accountTotal < (accountPaginationLimit + accountPaginationOffset):
			nextPage = False

			accountListData = {'limit':accountPaginationLimit,'offset':accountPaginationOffset,'order_by':'name','filters':[]}

			req = urllib2.Request(divvyListAccount, json.dumps(accountListData), {'Accept-Encoding': 'gzip, deflate, br', 'Content-Type': 'application/json;charset=UTF-8', \
			'Accept': 'application/json, text/plain, */*', 'X-Auth-Token': '%s' % (xAuthToken)})

			f = urllib2.urlopen(req, context=context)
			buffer = StringIO( f.read() )
			gzipResponse = gzip.GzipFile(fileobj=buffer)
			gzipResponse = gzipResponse.read()
			httpResponse = json.loads(gzipResponse)
			f.close()

			# Add known accounts to dict
			for item in httpResponse['clouds']:
				if item['cloud_type_id'] == 'GCE':
					try:
						currentDivvyAccounts[item['name']] = item['resource_id']
					except KeyError:
						pass
			#time.sleep(1)

	print 'Found %s accounts listed in DivvyCloud, %i unique' % (accountTotal,len(currentDivvyAccounts))

except urllib2.URLError as e:
	print "An error %s " %e


# Iterate through accounts and create appropriate data payload
httpData = {}
for k,v in currentDivvyAccounts.iteritems():
	divvyDelAccount = '%s/v2/public/cloud/%s/delete' % (divvyHost,k)
	print divvyDelAccount

	try:
		req = urllib2.Request(divvyDelAccount, json.dumps(httpData), {'Accept-Encoding': 'gzip, deflate, br', 'Content-Type': 'application/json;charset=UTF-8', \
		'Accept': 'application/json, text/plain, */*', 'X-Auth-Token': '%s' % (xAuthToken)})

		f = urllib2.urlopen(req, context=context)
		f.close()
		#time.sleep(1)

	except urllib2.URLError as e:
		print "An error %s " %e
		#time.sleep(1)