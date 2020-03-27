// Provider Info
provider "aws" {
    profile    = "default"
    region     =  var.region
}

variable "region" {
    type = string
    default = "us-east-1"
}

// What account is DivvyCloud running in?
variable "trusted_account_id" {
    type    = string
    default = "014578312761"
}

// IAM
// Create DivvyCloud PowerUser role
resource "aws_iam_role" "DivvyCloud-PowerUser-Role" {
  name = "DivvyCloud-PowerUser-Role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::${var.trusted_account_id}:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {}
    }
  ]
}
EOF
}

// Create PowerUser RO policy pt 1
resource "aws_iam_policy" "DivvyCloud-PowerUser-Role-Policy" {
  name        = "DivvyCloud-PowerUser-Policy"
  description = "DivvyCloud PowerUser RO Policy Pt 1"

  policy = file("${path.module}/divvycloud-poweruser.json")

}

// Attach DivvyCloud PowerUser policies
resource "aws_iam_role_policy_attachment" "DivvyCloud-PowerUser-Role-Attach" {
  role       = aws_iam_role.DivvyCloud-PowerUser-Role.name
  policy_arn = aws_iam_policy.DivvyCloud-PowerUser-Role-Policy.arn
}

