# Username/password to authenticate against the API
username=""
password="" 

# DivvyCloud URL EX: http://localhost:8001 or http://45.59.252.4:8001)
base_url=""

# Get session token
login_url=`echo $base_url/v2/public/user/login`

session_token=`curl \
--request POST \
--header "content-type: application/json" \
--header "accept-encoding: gzip" \
--data "{\"username\": \"${username}\",\"password\": \"${password}\"}" \
$login_url \
| gunzip  | jq '.session_id' | sed s/\"//g`
        
# Get org info
org_url=`echo $base_url/v2/prototype/domain/organizations/detail/get`

curl \
--request GET \
--header "content-type: application/json" \
--header "accept-encoding: gzip" \
--header "x-auth-token: $session_token" \
$org_url | gunzip | jq

# Sample output:
# {
#   "organizations": [
#     {
#       "status": "ok",
#       "smtp_configured": true,
#       "clouds": 63,
#       "name": "DivvyCloud Demo",
#       "resource_id": "divvyorganization:1",
#       "organization_id": 1,
#       "bots": 17,
#       "users": 21
#     }
#   ]
# }