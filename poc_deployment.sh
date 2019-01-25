#!/bin/bash

# Usage: ./create_poc <customer> <expected end date of POC>
# Ex: ./create_poc Contoso 8/5/19
# No spaces allowed for customer name
# Keys are sent to /tmp/

aws_profile_name="default"

path_to_cft="file:////Users/alexcorstorphine/Dropbox/code/Divvy/cloudformation_templates/Divvy_hosted_POC.yml"

#Just your name for tagging purposes
user="Alex"

# Where do you want to store your keys (absolute path)
# Using places other than /tmp causes permissions issues. Leave it alone if ya don't want to mess with it. 
key_location="/tmp/"

# Shouldn't need to modify
instance_role_name="Divvy-POC-STS-Assume-Role"

# Check for arguments
if [ $# -ne 2 ]
  then
    echo "Wrong number of arguments. Exiting"
    echo "Usage: ./create_poc <customer>"
    echo "Ex: ./create_poc Contoso 8/5/19"
    exit 1
fi

customer_name=$1
expected_poc_end_date=$2

aws ec2 create-key-pair \
--region us-west-2 \
--key-name $customer_name-poc \
--profile $aws_profile_name \
> $key_location$customer_name-poc.pem

chmod 400 $key_location$customer_name-poc.pem

aws cloudformation create-stack \
--stack-name $customer_name-POC \
--template-body $path_to_cft \
--parameters ParameterKey=InstanceType,ParameterValue=m5.large ParameterKey=KeyPair,ParameterValue=$customer_name-poc ParameterKey=VpcId,ParameterValue=vpc-5c22ee38 ParameterKey=InstanceName,ParameterValue=$customer_name-poc ParameterKey=InstanceRoleName,ParameterValue=$instance_role_name \
--region us-west-2 \
--tags Key=deletion_exempt,Value=true Key=createdBy,Value=$user Key=expected_poc_end_date,Value=$expected_poc_end_date \
--profile $aws_profile_name

sleep 60

instance_ip=$(aws cloudformation describe-stacks \
--stack-name $customer_name-POC \
--region us-west-2 \
--query 'Stacks[0].Outputs[?OutputKey==`PublicIp`].OutputValue' \
--output text \
--profile $aws_profile_name)

echo "POC Created for " $customer_name
echo "The SSH key is located in /tmp/"
echo "Log into the instance at http://"$instance_ip":8001"

