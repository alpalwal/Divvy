// Target account id. Where will DivvyCloud be deployed?
variable "account_id" {
    type    = string
    default = "014578312761"
}

variable "region" {
    type = string
    default = "us-west-2"
}

// 3 AZs for redundancy (ALL 3 ARE REQUIRED)
variable "az" {
    type    = list(string)
    default = ["us-west-2a","us-west-2b","us-west-2c"]
}

// Set the name of the secrets manager secret
variable "divvycloud-credentials" {
    type = string
    default = "divvycloud-credentials"
}

// If you do not want a random RDS/MySQL password automatically generated, specify here
variable "database_credentials" {
    type    = list(string)
    default = ["divvy","DivvyCloud1!"]
}

variable "divvycloud_version" {
    type = string
    // Example "divvycloud/divvycloud:latest" or "divvycloud/divvycloud:v19.3.2"
    default = "divvycloud/divvycloud:v20.1.1"
}

// Allow outbound access (does not apply to IGW)
variable "egress_whitelist" {
    type    = list(string)
    default = ["0.0.0.0/0"]
}

// Allow access to the ALB (UI) via these IP address(es)
variable "ingress_whitelist" {
    type    = list(string)
    default = ["1.2.3.4/32", "73.169.50.3/32"]
}

// Accepted values: 80 and 443
// If 443 is set, a certificate needs to be supplied as well
variable "lb_port" {
  type    = number
  default = 80
}

// If setting 443 the name of the ACM cert that will be attached needs to be supplied. If on 80 - leave this alone
// Note: Just the name, not the full ARN  
variable "alb_ssl_cert_name" {
  type    = string
  default = "YOUR-ACM-SSL-CERT-ID-HERE"
}



// ===========================
// Scale Options
// ===========================
variable "divvykeys_task_count" {
    type = number
    default = 1
}

variable "interface_server_task_count" {
    type = number
    default = 1
}

variable "scheduler_task_count" {
    type = number
    default = 1
}

// P2 Spot instances
variable "worker_task_count" {
    type = number
    default = 1
}

// P0/1 persistent instances
variable "worker_persistent_task_count" {
    type = number
    default = 1
}

variable "worker_task_cpu" {
    type = number
    default = 1024
}

variable "worker_task_mem" {
    type = number
    default = 2048
}