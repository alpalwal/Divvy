#Add to instance role

aws ec2 create-key-pair \
--region us-west-2 \
--key-name testcustomer-poc \
> testcustomer-poc.pem

chmod 400 testcustomer-poc.pem

aws cloudformation create-stack \
--stack-name myteststack \
--template-body file:////Users/alexcorstorphine/Dropbox/code/Divvy/cloudformation_templates/single_deployment.yml \
--parameters ParameterKey=InstanceType,ParameterValue=m5.large ParameterKey=KeyPair,ParameterValue=testcustomer-poc ParameterKey=VpcId,ParameterValue=vpc-5c22ee38 \
--region us-west-2 \
--tags Key=deletion_exempt,Value=true


