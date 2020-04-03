# Script for onboarding multiple Azure Subscriptions
# You need to have permissions to grant permissions to an app registration for this to work
# Steps:
# - Log into the Azure Portal
# - Open up Cloud Shell using Bash
# - Copy the script down and run it with bash $filename

# What it does:
# - Lists all Azure Subscriptions you can see 
# - Creates an app registration 
# - Grants Graph API Read permissions to the registration
# - Creates a key for the App
# - Adds the reader role to the App
# - Adds it into DivvyCloud


## Set up Divvy Creds
echo ""
read -p "Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): " BASE_URL
read -p "DivvyCloud Username: " username
read -s -p "DivvyCloud Password: " password
echo ""

# Get session token (just need it once)
login_url=`echo $BASE_URL/v2/public/user/login`

SESSION_TOKEN=`curl -s -k \
--request POST \
--header "content-type: application/json" \
--header "accept-encoding: gzip" \
--data "{\"username\": \"${username}\",\"password\": \"${password}\"}" \
$login_url \
| gunzip  | jq '.session_id' | sed s/\"//g`
        
ADD_CLOUD_URL=`echo $BASE_URL/v2/prototype/cloud/add`

# Zero out existing CLI sessions
az account clear 

# Log into Azure again even though CloudShell logs you in automatically. There's a bug that doesn't let you to do everything you need without reauthenticating
echo Logging into Azure
az login

echo Building list of Azure Subscriptions to onboard

# List the Azure Subscriptions you have
az account list --query '[].{Id:id}' --output tsv | while read -r SUB_ID ; do
    SCOPE=`echo /subscriptions/$SUB_ID`

    # Get the name and tenant ID from the sub
    SUB_NAME=`az account show -s $SUB_ID --query '[name]' --output tsv`
    TENANT_ID=`az account show -s $SUB_ID --query '[tenantId]' --output tsv`
    
    echo "Starting onboarding of Subscription $SUB_NAME (ID: $SUB_ID)"

    # Rename pay-as-you-go subscriptions so they don't have name collisions during Divvy onboarding

    if [ "$SUB_NAME" = "Pay-As-You-Go" ]; then
        RANDOM_STRING=`openssl rand -hex 5`
        SUB_NAME=$SUB_NAME-$RANDOM_STRING
    fi

    # Switch subscriptions
    az account set --subscription $SUB_ID

    echo "Creating the app registration"
    APP_ID=`az ad app create --display-name DivvyCloud-test --query appId | sed s/\"//g`

    echo "Creating app key(secret)"
    # Create a Secret for the app
    KEY=`az ad app credential reset \
    --id $APP_ID \
    --append \
    --credential-description "DivvyCloud Key" \
    --end-date 2022-12-31 \
    --query password | sed s/\"//g`

    echo "Adding the Graph API \"Directory.Read.All\" permissions to the app"
    az ad app permission add \
    --id $APP_ID \
    --api 00000002-0000-0000-c000-000000000000 \
    --api-permissions 5778995a-e1bf-45b8-affa-663a9f3f4d04=Role

    # Grant permissions for the app to use the Graph permissions that were attached
    az ad app permission admin-consent --id $APP_ID

    # ERROR WHEN IT FAILS:
    # Forbidden({"ClassName":"Microsoft.Portal.Framework.Exceptions.ClientException","Message":"Graph call failed with httpCode=Forbidden, errorCode=Authorization_RequestDenied, errorMessage=This operation can only be performed by an administrator. Sign out and sign in as an administrator or contact one of your organization's administrators., reason=Forbidden, correlationId = 38fc3999-5f71-4c15-a82c-358a0b4d84f9, response = {\"odata.error\":{\"code\":\"Authorization_RequestDenied\",\"message\":{\"lang\":\"en\",\"value\":\"This operation can only be performed by an administrator. Sign out and sign in as an administrator or contact one of your organization's administrators.\"},\"requestId\":\"a907abdd-ad51-480b-b3dd-691ed51c379e\",\"date\":\"2020-04-03T18:17:36\"}}","Data":{},"HResult":-2146233088,"XMsServerRequestId":null,"Source":null,"HttpStatusCode":403,"ClientData":{"errorCode":"Authorization_RequestDenied","localizedErrorDetails":{"errorDetail":"This operation can only be performed by an administrator. Sign out and sign in as an administrator or contact one of your organization's administrators."},"operationResults":null,"timeStampUtc":"2020-04-03T18:17:36.0707002Z","clientRequestId":"38fc3999-5f71-4c15-a82c-358a0b4d84f9","internalTransactionId":"3afc6711-b6bc-4af6-93f6-396044b23959","tenantId":"6e46cb91-12a1-46a3-abb5-99d3eb2d6ccb","userObjectId":"09638488-c514-4bee-b262-2f84a8642934","exceptionType":"AADGraphException"}})

    echo Sleeping 60 - waiting for app registration permissions to propagate
    sleep 60 ## If you try to run the next command too quickly, it'll fail

    # Add the "Reader" role permissions to your App Registration
    az role assignment create \
    --assignee $APP_ID \
    --role "Reader" \
    --scope $SCOPE \
    --subscription $SUB_ID


    echo ========================
    echo Information to add into DivvyCloud
    echo Subscription Name: $SUB_NAME
    echo Tenant ID: $TENANT_ID
    echo Subscription ID: $SUB_ID
    echo Application ID: $APP_ID 
    echo API Key: $KEY
    echo ""

    echo Sleeping for 30 - waiting for Azure permissions to propagate
    sleep 30 ## More Azure lags and unnecessary errors

    echo Starting DivvyCloud onboarding

    curl -k \
    --request POST \
    --header "content-type: application/json" \
    --header "accept-encoding: gzip" \
    --header "x-auth-token: $SESSION_TOKEN" \
    -d '{"creation_params":{"cloud_type":"AZURE_ARM","name": "'"$SUB_NAME"'","authentication_type": "client_credentials","tenant_id": "'$TENANT_ID'","app_id": "'$APP_ID'","subscription_id": "'$SUB_ID'","api_key": "'$KEY'"}}' \
    $ADD_CLOUD_URL 

done