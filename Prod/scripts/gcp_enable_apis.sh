# GCP API enabling
# Only works for projects you have access to
APIS_TO_ENABLE1='bigquery.googleapis.com file.googleapis.com dataflow.googleapis.com cloudresourcemanager.googleapis.com datastore.googleapis.com cloudkms.googleapis.com dataproc.googleapis.com sqladmin.googleapis.com pubsub.googleapis.com stackdriver.googleapis.com admin.googleapis.com'
APIS_TO_ENABLE2='cloudbilling.googleapis.com compute.googleapis.com iam.googleapis.com bigtable.googleapis.com bigtableadmin.googleapis.com cloudfunctions.googleapis.com spanner.googleapis.com sql-component.googleapis.com storage-component.googleapis.com storage-api.googleapis.com servicemanagement.googleapis.com dns.googleapis.com stackdriver.googleapis.com container.googleapis.com'

echo Listing all GCP projects that this user has access to
echo ===== List Of Projects =====
gcloud projects list | awk '{print $1}' | grep -v PROJECT_ID 
echo ""


gcloud projects list | awk '{print $1}' | grep -v PROJECT_ID  | while read -r PROJECT ; do
    echo ""
    echo "Enabling APIs for" $PROJECT
    gcloud --project $PROJECT services enable $APIS_TO_ENABLE1 ## run it in 2 commands because the max API limit is 20 (25 needed)
    gcloud --project $PROJECT services enable $APIS_TO_ENABLE2
done


# API Reference - delete the lines you don't want from APIS_TO_ENABLE1 and 2

# bigquery.googleapis.com # BigQuery API
# file.googleapis.com # Cloud Filestore API
# dataflow.googleapis.com # Cloud Dataflow API
# cloudresourcemanager.googleapis.com # Cloud Resource Manager API
# datastore.googleapis.com # Cloud Datastore API
# cloudkms.googleapis.com # Cloud Key Management Service (KMS) API
# dataproc.googleapis.com # Cloud Dataproc API
# sqladmin.googleapis.com # Cloud SQL Admin API
# pubsub.googleapis.com # Cloud Pub/Sub API
# stackdriver.googleapis.com # Stackdriver Logging API
# admin.googleapis.com # Admin SDK   
# cloudbilling.googleapis.com # Cloud Billing API
# compute.googleapis.com # Compute Engine API
# iam.googleapis.com # Identity and Access Management (IAM) API
# bigtable.googleapis.com # Cloud Bigtable API
# bigtableadmin.googleapis.com # Cloud Bigtable Admin API
# cloudfunctions.googleapis.com # Cloud Functions API
# spanner.googleapis.com # Cloud Spanner API
# sql-component.googleapis.com # Google Cloud SQL
# storage-component.googleapis.com # Google Cloud Storage
# storage-api.googleapis.com # Google Cloud Storage JSON API
# servicemanagement.googleapis.com # Service Management API
# dns.googleapis.com # Cloud DNS
# container.googleapis.com # Kubernetes Engine API
# stackdriver.googleapis.com # Stackdriver Monitoring



# gcloud projects list # https://cloud.google.com/sdk/gcloud/reference/projects/list

# gcloud services enable service1 service2 service3 # https://cloud.google.com/sdk/gcloud/reference/services/enable

# gcloud services list --enabled # https://cloud.google.com/sdk/gcloud/reference/services/list

# gcloud --project something-staging-2587 compute ssh my_vm
# #https://stackoverflow.com/questions/46770900/how-to-change-the-project-in-gcp-using-cli-commands

# gcloud --project alexsandboxproject services enable maps-backend.googleapis.com 
# Operation "operations/acf.5eece386-faa2-49aa-af1b-e2c32e15d03b" finished successfully.

# # https://medium.com/@pnatraj/how-to-run-gcloud-command-line-using-a-service-account-f39043d515b9


