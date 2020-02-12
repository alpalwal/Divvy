

# Requires:
#### Terraform 0.12
#### Permissions on the IAM user to be able to create policies and roles


# Services / resources being created


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


# Troubleshooting:
- Go to the DivvyCloud-ECS cluster
- Look to see if the tasks are running
- If not, go to the logs for the DELETE-ME task and look for the "Stopped" logs
- If there's nothing there, go to the Tasks tab, click on a task (stopped), and expand the details ">" at the bottom. The logs there should help. 

# Teardown
- RDS has deletion protection on
- The NAT GW can't be deleted if RDS is still around as it'll have IPs associated


# Cleanup:
 - The divvykeys_task is a one-time run to create the divvykeys database (this is temporary and we’re working on a better mechanism). 
 Once the rest of the services/tasks are working, you can delete the DELETE-ME-AFTER-FIRST-RUN service. 
 - For scaling the other services, you can use lines 68-88 or scale the services up after deployment. 
 - Uncomment lines 558-568, comment out lines 572-582 to disable HTTPS in favor of HTTP

 - Line 25: Set the account ID that Divvy will be deployed to
 - Line 31: Set the AZs you want Divvy to run in (at least 2)
 - Line 61: Set the IP range(s) that you want to be able to access Divvy from
 - Line 66: Set the region you'll be deploying into
 - Uncomment lines 562 to 575 to allow ingress on port 80
 - Comment out lines 577 to 588 to remove the 443 ingress rule that needs a cert
