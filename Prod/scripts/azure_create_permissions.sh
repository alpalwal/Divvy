# Log into Azure again even though CloudShell logs you in automatically. There's a bug that doesn't let you to do everything you need without reauthenticating
az login

echo "Creating the app registration"
ID=`az ad app create --display-name DivvyCloud --query appId | sed s/\"//g`

echo "Creating app key(secret)"
# Create a Secret for the app
KEY=`az ad app credential reset \
--id $ID \
--append \
--credential-description "DivvyCloud Key" \
--end-date 2022-12-31 \
--query password | sed s/\"//g`

echo "Adding the Graph API \"Directory.Read.All\" permissions to the app"
az ad app permission add \
--id $ID \
--api 00000002-0000-0000-c000-000000000000 \
--api-permissions 5778995a-e1bf-45b8-affa-663a9f3f4d04=Role

# Grant permissions for the app to use the Graph permissions that were attached
az ad app permission admin-consent --id $ID

echo ===============================
echo Listing all Azure subscriptions 
echo ===============================

# List the Azure Subscriptions you have attached
az account list | egrep 'cloudName|"id"|name|tenantId'

# az account list | egrep 'cloudName|"id"|name|tenantId'
#     "cloudName": "AzureCloud",
#     "id": "79509b95-fed1-4683-b704-37002de8e21d",
#     "name": "Pay-As-You-Go",
#     "tenantId": "9c3f8122-c4ea-4692-9e50-1ffa0eac2023",
#       "name": "alex@abcwebdesigner.com",

# Find the Subscription this will be installed into you like from ^^ and save that ID and tenant ID

## Prompt the Sub you'll be using
echo ""
read -p "What is the Subscription ID you'll be using? (It's shown just as ID above) " SUB_ID
SCOPE=`echo /subscriptions/$SUB_ID`
echo ""
read -p "What is the Tenant ID you'll be using? " TENANT_ID

# Add the "Reader" role permissions to your App Registration
az role assignment create \
--assignee $ID \
--role "Reader" \
--scope $SCOPE \
--subscription $SUB_ID

echo ========================
echo Information to add into DivvyCloud
echo Tenant ID: $TENANT_ID
echo Subscription ID: $SUB_ID
echo Application ID: $ID 
echo API Key: $KEY
echo ""


############
read -r -p "Would you like to add this into DivvyCloud right now? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        echo "Starting onboarding"
        ;;
    *)
        exit
        ;;
esac


echo ""
read -p "Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): " base_url
read -p "DivvyCloud Username: " username
read -s -p "DivvyCloud Password: " password
echo ""
read -p "What will this cloud be called? Ex. Sandbox, Production, etc.: " nickname

# Get session token
login_url=`echo $base_url/v2/public/user/login`

session_token=`curl \
--request POST \
--header "content-type: application/json" \
--header "accept-encoding: gzip" \
--data "{\"username\": \"${username}\",\"password\": \"${password}\"}" \
$login_url \
| gunzip  | jq '.session_id' | sed s/\"//g`
        

add_cloud_url=`echo $base_url/v2/prototype/cloud/add`

curl \
--request POST \
--header "content-type: application/json" \
--header "accept-encoding: gzip" \
--header "x-auth-token: $session_token" \
-d '{"creation_params":{"cloud_type":"AZURE_ARM","name": "'$nickname'","authentication_type": "client_credentials","tenant_id": "'$TENANT_ID'","app_id": "'$ID'","subscription_id": "'$SUB_ID'","api_key": "'$KEY'"}}' \
$add_cloud_url | gunzip | jq

echo ""
echo "Azure onboarding finished"