#Required for each account
variable "external_id" {    
  type = "string"
  default = "divvycloud"
}

#Create the role and setup the trust policy
resource "aws_iam_role" "divvycloud" {
  name               = "DivvyCloud-cross-account"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::625820357955:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "${var.external_id}"
        }
      }
    }
  ]
}
EOF
}

#Create the first readonly policy
resource "aws_iam_policy" "readonly-policy1" {
  name        = "divvycloud-readonly-policy1"
  description = ""
  policy      = "${file("read_only_policy1.json")}"
}

#Create the second readonly policy (it's too long to be in just 1 policy)
resource "aws_iam_policy" "readonly-policy2" {
  name        = "divvycloud-readonly-policy2"
  description = ""
  policy      = "${file("read_only_policy2.json")}"
}

#Attach 4 policies to the cross-account role
resource "aws_iam_policy_attachment" "attach-diivvycloud-read-policy1" {
  name       = "Attach-readonly1"
  roles      = ["${aws_iam_role.divvycloud.name}"]
  policy_arn = "${aws_iam_policy.readonly-policy1.arn}"
}

resource "aws_iam_policy_attachment" "attach-diivvycloud-read-policy2" {
  name       = "Attach-readonly2"
  roles      = ["${aws_iam_role.divvycloud.name}"]
  policy_arn = "${aws_iam_policy.readonly-policy2.arn}"
}


#Output the role ARN
output "Role_ARN" {
  value = "${aws_iam_role.divvycloud.arn}"
}
