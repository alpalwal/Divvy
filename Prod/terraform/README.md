# Requires:
- Terraform 0.12
- Permissions on the IAM user to be able to create policies and roles

# Required variable to set or update

#### account_id
Target account id. Where will DivvyCloud be deployed?  
account_id = "013456789123"  

#### region
What region will the install be rolled out in?  
region = "us-west-2"  
  
#### az
3 AZs for redundancy (ALL 3 ARE REQUIRED)  
az = ["us-west-2a","us-west-2b","us-west-2c"]  

#### egress_whitelist
Where should outbound access be allowed from (does not apply to IGW)  
egress_whitelist = ["0.0.0.0/0"]  

#### ingress_whitelist
Where should access to the UI be exposed to?  
ingress_whitelist = ["1.2.3.4/32", "73.169.50.3/32"]  

#### lb_port
Accepted values: 80 and 443  
If 443 is set, a certificate needs to be supplied as well  
lb_port = 80

#### alb_ssl_cert_name
If setting 443 the name of the ACM cert that will be attached needs to be supplied. Note: Just the name, not the full ARN  
alb_ssl_cert_name = "YOUR-ACM-SSL-CERT-ID-HERE"  


# Troubleshooting
- Go to the DivvyCloud-ECS cluster  
- Look to see if the tasks are running  
- If not, go to the logs for the DELETE-ME task and look for the "Stopped" logs  
- If there's nothing there, go to the Tasks tab, click on a task (stopped), and expand the details ">" at the bottom. The logs there should help.  

# Teardown
- RDS has deletion protection on and will need to have that manually turned off before destroying. 
- The NAT GW can't be deleted if RDS is still around as it'll have IPs associated  


# Notes
 - The divvykeys_task is a one-time run to create the divvykeys database (this is temporary and we’re working on a better mechanism). Once the rest of the services/tasks are working, you can delete the DELETE-ME-AFTER-FIRST-RUN service.  
 - For scaling the other services, you can adjust the task variables up after deployment.  
 

 # Resources that will be created
#### 3 IAM Roles:
DivvyCloud-Standard-Role  
DivvyCloud-RDS-Role   
DivvyCloud-ECS-Task-Role  

#### 3 IAM Policies:
DivvyCloud-Standard-Role-Policy    
DivvyCloud-Standard-Role-Policy2   
DivvyCloud-getSecret-Policy  

#### 1 VPC:
DivvyCloud-ECS-VPC  

#### 4 Security Groups:
DivvyCloud-ECS-SecurityGroup-Redis     
DivvyCloud-ECS-SecurityGroup-ALB  
DivvyCloud-ECS-SecurityGroup-RDS  
DivvyCloud-ECS-SecurityGroup-UI  

#### 1 IGW:
DivvyCloud-InternetGateway   

#### 6 Subnets:
DivvyCloud-ECS-Private-Subnet1    
DivvyCloud-ECS-Private-Subnet2  
DivvyCloud-ECS-Private-Subnet3  
DivvyCloud-ECS-Public-Subnet1  
DivvyCloud-ECS-Public-Subnet2  
DivvyCloud-ECS-Public-Subnet3  

#### 3 NAT Gateways:
DivvyCloud-NAT-GW  
DivvyCloud-NAT-GW2  
DivvyCloud-NAT-GW3  

#### 3 EIPs for the NAT GWs:
DivvyCloud-NAT-GW-EIP  
DivvyCloud-NAT-GW-EIP2  
DivvyCloud-NAT-GW-EIP3  

#### 4 Route Tables:
DivvyCloud-ECS-RouteTable-Public   
DivvyCloud-ECS-RouteTable-Private  
DivvyCloud-ECS-RouteTable-Private2  
DivvyCloud-ECS-RouteTable-Private3  

#### 1 RDS Instance:
DivvyCloud-ECS-MySQL   

#### 1 Secrets Manager Secret:
divvycloud-credentials   

#### 1 ALB:
DivvyCloud-ECS-ALB   

#### 1 Elasticache Instance (Redis):
DivvyCloud-ECS-Redis  

#### 1 ECS Cluster:
DivvyCloud-ECS-Cluster   

#### 5 ECS Services and Task Definitions:
interfaceserver   
scheduler  
divvykeys  
worker  
workerPersistent  

#### 1 CloudWatch Logs Group:
DivvyCloud-ECS-Cluster-LogGroup   