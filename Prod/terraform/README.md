# DivvyCloud-OnBoarding-Terraform
Terraform Templates that Prepare the Role on AWS account to connenct to DivvyCloud 

# Steps:

## In Terraform:
1. Choose file according to the protection mode you prefer (Read Only or Full Protect)
2. Remove or rename the .tf file you won't be using since Terraform will try to run all *.tf files in the directory.
3. Run 'terraform plan'
4. If this looks good, run 'terraform apply'
5. After the process finished, a new role is created which will contain the "Role ARN".



