# Provisioning Local Account Permissions
This will set up a role that your DivvyCloud instance will assume in order to collect data about the local account and assume roles into other accounts. 
Decide if you want to provision “Standard User” or “Power User” permissions. 

[<img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png">](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=DivvyCloudInstanceRole&templateURL=https://s3.amazonaws.com/get.divvycloud.com/cft/Divvy-CFT-IAR.yaml)

### Parameters:
**Standard or Power user** - The policies for both are linked below

### Standard user policies:
* http://get.divvycloud.com/policies/ReadOnlyPolicy1.json
* http://get.divvycloud.com/policies/ReadOnlyPolicy2.json
* http://get.divvycloud.com/policies/STSPolicy.json

### Power user policies:
* http://get.divvycloud.com/policies/PowerUserPolicy.json
* http://get.divvycloud.com/policies/STSPolicy.json



# Provisioning Cross Account Permissions 
(for all accounts besides the one that is running the DivvyCloud instance):
This will set up a role that your DivvyCloud instance will assume in order to collect data about the local account and assume roles into other accounts. 

[<img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png">](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=DivvyCloudInstanceRole&templateURL=https://s3.amazonaws.com/get.divvycloud.com/cft/Divvy-CFT-cross-account.yaml)

### Parameters:
**Standard or Power user** - The policies for both are linked below  
**SourceAccountID** - This is the account ID of the account that is running the DivvyCloud instance  
**ExternalId** - (Optional) The external ID that is attached to the assume role trust policy  

### Standard user policies:
* http://get.divvycloud.com/policies/ReadOnlyPolicy1.json
* http://get.divvycloud.com/policies/ReadOnlyPolicy2.json
* http://get.divvycloud.com/policies/STSPolicy.json

### Power user policies:
* http://get.divvycloud.com/policies/PowerUserPolicy.json
* http://get.divvycloud.com/policies/STSPolicy.json




*************************************************************************************************************************************************  
*************************************************************************************************************************************************  
*************************************************************************************************************************************************  
*************************************************************************************************************************************************  
# Templates below here aren't ready
*************************************************************************************************************************************************  
*************************************************************************************************************************************************  
*************************************************************************************************************************************************  


# Provisioning EDH Consumer
This will attach permissions to your DivvyCloud role that will allow EDH to be configured and run. If you don't already have a CloudTrail configured, one will be created. 
 
[<img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png">](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=DivvyCloudInstanceRole&templateURL=https://s3.amazonaws.com/get.divvycloud.com/cft/Divvy-CFT-cross-account.yaml)

### Parameters:
**OrgId** - REQUIRED - ID of the organization this account is in. Ex. o-6ovjaffaj3  
**RoleName** - REQUIRED - Name of the existing DivvyCloud role the permissions for EDH will be attached to.  

**ExistingTrail** - Is there an existing CloudTrail to use? If so, skil LogGroupName and S3BucketName  
**LogGroupName** - Name of the CloudWatch Log Group that will be created for CloudTrail will log to  
**S3BucketName** - Name of a new S3 bucket that will be created that CloudTrail wil log to (don't forget that bucket names are global)  



# Provisioning EDH Producer
This will attach permissions to your DivvyCloud role that will allow EDH to be configured and run. If you don't already have a CloudTrail configured, one will be created. 
 
[<img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png">](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=DivvyCloudInstanceRole&templateURL=https://s3.amazonaws.com/get.divvycloud.com/cft/Divvy-CFT-cross-account.yaml)

### Parameters:
**RoleName** - REQUIRED - Name of the existing DivvyCloud role the permissions for EDH will be attached to.  

**ExistingTrail** - Is there an existing CloudTrail to use? If so, skil LogGroupName and S3BucketName  
**LogGroupName** - Name of the CloudWatch Log Group that will be created for CloudTrail will log to  
**S3BucketName** - Name of a new S3 bucket that will be created that CloudTrail wil log to (don't forget that bucket names are global)  
