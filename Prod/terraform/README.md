// Lines 34, 101, 700, and 994 are of note.

# - The divvykeys_task is a one-time run to create the divvykeys database (this is temporary and we’re working on a better mechanism). 
# Once the rest of the services/tasks are working, you can delete the DELETE-ME-AFTER-FIRST-RUN service. 
# - For scaling the other services, you can use lines 68-88 or scale the services up after deployment. 
# - Uncomment lines 558-568, comment out lines 572-582 to disable HTTPS in favor of HTTP

# - Line 25: Set the account ID that Divvy will be deployed to
# - Line 31: Set the AZs you want Divvy to run in (at least 2)
# - Line 61: Set the IP range(s) that you want to be able to access Divvy from
# - Line 66: Set the region you'll be deploying into
# - Uncomment lines 562 to 575 to allow ingress on port 80
# - Comment out lines 577 to 588 to remove the 443 ingress rule that needs a cert

REQUIRES Terraform .12

Why 3 vs 2 AZs?

add flag for "first run" or not?

Services / topology being created:

added lb port variable. if 443, then it'll create the cert. if not 443, it'll create the lb inbound rule on 80