/*
AWS Fargate Deployment - Roles/Perms/Secrets Manager
Author: Brendan Elliott
Date:   01/30/20
Ver:    1.0
*/

// Provider Info
provider "aws" {
    profile    = "default"
    region     =  var.region
}

// Existing SSL cert for ALB
locals {
    alb_ssl_arn = "arn:aws:acm:${var.region}:${var.account_id}:certificate/${var.alb_ssl_cert_name}"
}

// Role ARN for ECS exec
locals {
    ecs_exec_role = "${aws_iam_role.DivvyCloud-ECS-Task-Role.arn}"
}

// Role ARN for ECS task exec
locals {
    ecs_task_role = "${aws_iam_role.DivvyCloud-Standard-Role.arn}"
}

// Role ARN for RDS monitoring
locals {
    rds_monitor_role = "${aws_iam_role.DivvyCloud-RDS-Role.arn}"
}

// Timestamp for unique RDS snapshot
locals {
  timestamp = formatdate("YYYYMMDD-hhmm", timestamp())
}

// Random password generator for RDS. See `variable "database_credentials"` and `aws_db_instance.DivvyCloud-ECS-MySQL.password`
resource "random_string" "DivvyCloud-Random" {
  length = 20
  special = true
  number = true
  upper = true
}

// IAM
// Create DivvyCloud standard role
resource "aws_iam_role" "DivvyCloud-Standard-Role" {
  name = "DivvyCloud-Standard-Role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role" "DivvyCloud-RDS-Role" {
  name = "rds-monitoring-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "monitoring.rds.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role" "DivvyCloud-ECS-Task-Role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

// Create standard RO policy pt 1
resource "aws_iam_policy" "DivvyCloud-Standard-Role-Policy" {
  name        = "DivvyCloud-Standard-Policy"
  description = "DivvyCloud Standard RO Policy Pt 1"

  policy = file("${path.module}/divvycloud-standard1.json")

}

// Create standard RO policy pt 2
resource "aws_iam_policy" "DivvyCloud-Standard-Role-Policy2" {
  name        = "DivvyCloud-Standard-Policy2"
  description = "DivvyCloud Standard RO Policy Pt 2"

  policy = file("${path.module}/divvycloud-standard2.json")
}

// Policy to read secret
resource "aws_iam_policy" "DivvyCloud-getSecret-Policy" {
  name        = "DivvyCloud-getSecret-Policy"
  description = "DivvyCloud GetSecretValue Policy"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "${aws_secretsmanager_secret.divvycloud-credentials.arn}"
        }
    ]
}
EOF
}

// Create STS policy
resource "aws_iam_policy" "DivvyCloud-STS-policy" {
  name        = "DivvyCloud-STS-policy"
  description = "DivvyCloud STS policy"

  policy = file("${path.module}/divvycloud-sts.json")
}

// Attach DivvyCloud standard policies
resource "aws_iam_role_policy_attachment" "DivvyCloud-Standard-Role-Attach" {
  role       = aws_iam_role.DivvyCloud-Standard-Role.name
  policy_arn = aws_iam_policy.DivvyCloud-Standard-Role-Policy.arn
}

resource "aws_iam_role_policy_attachment" "DivvyCloud-Standard-Role-Attach2" {
  role       = aws_iam_role.DivvyCloud-Standard-Role.name
  policy_arn = aws_iam_policy.DivvyCloud-Standard-Role-Policy2.arn
}

resource "aws_iam_role_policy_attachment" "DivvyCloud-Standard-Role-Attach3" {
  role       = aws_iam_role.DivvyCloud-Standard-Role.name
  policy_arn = aws_iam_policy.DivvyCloud-getSecret-Policy.arn
}

// Attach DivvyCloud STS policy
resource "aws_iam_role_policy_attachment" "DivvyCloud-STS-Role-Attach" {
  role       = aws_iam_role.DivvyCloud-Standard-Role.name
  policy_arn = aws_iam_policy.DivvyCloud-STS-policy.arn
}

// Attach RDS enhanced monitoring policy
resource "aws_iam_role_policy_attachment" "DivvyCloud-RDS-Role-Attach" {
  role       = aws_iam_role.DivvyCloud-RDS-Role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

// Attach ECS task execution role policy
resource "aws_iam_role_policy_attachment" "DivvyCloud-ECS-Role-Attach" {
  role       = aws_iam_role.DivvyCloud-ECS-Task-Role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


// Allows for SSL certificate creation
/*
module "acm" {
  source = "terraform-aws-modules/acm/aws"
  version = "~> v2.0"
  create_certificate = true
  validate_certificate = false
}
locals {
    alb_ssl_arn = "arn:aws:acm:${var.region}:${var.account_id}:certificate/${module.acm.this_acm_certificate_arn}"
}
*/
// ---

// VPC
resource "aws_vpc" "DivvyCloud-ECS-VPC" {
    assign_generated_ipv6_cidr_block = false
    cidr_block                       = "172.31.0.0/16"
    enable_classiclink               = false
    enable_classiclink_dns_support   = false
    enable_dns_hostnames             = true
    enable_dns_support               = true
    instance_tenancy                 = "default"
    tags                             = {
        "Name" = "DivvyCloud-ECS-VPC"
    }
}

// IGW
resource "aws_internet_gateway" "DivvyCloud-InternetGateway" {
    tags     = {
        "Name" = "DivvyCloud-InternetGateway"
    }
    vpc_id   = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Private subnet 1
resource "aws_subnet" "DivvyCloud-ECS-Private-Subnet1" {
    assign_ipv6_address_on_creation = false
    availability_zone               = var.az[0]
    cidr_block                      = "172.31.0.0/20"
    map_public_ip_on_launch         = false
    tags                            = {
        "Name" = "DivvyCloud-ECS-Private-Subnet1"
    }
    vpc_id                          = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Private subnet 2
resource "aws_subnet" "DivvyCloud-ECS-Private-Subnet2" {
    assign_ipv6_address_on_creation = false
    availability_zone               = var.az[1]
    cidr_block                      = "172.31.16.0/20"
    map_public_ip_on_launch         = false
    tags                            = {
        "Name" = "DivvyCloud-ECS-Private-Subnet2"
    }
    vpc_id                          = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Private subnet 3
resource "aws_subnet" "DivvyCloud-ECS-Private-Subnet3" {
    assign_ipv6_address_on_creation = false
    availability_zone               = var.az[2]
    cidr_block                      = "172.31.32.0/20"
    map_public_ip_on_launch         = false
    tags                            = {
        "Name" = "DivvyCloud-ECS-Private-Subnet3"
    }
    vpc_id                          = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Public subnet 1
resource "aws_subnet" "DivvyCloud-ECS-Public-Subnet1" {
    assign_ipv6_address_on_creation = false
    availability_zone               = var.az[0]
    cidr_block                      = "172.31.48.0/20"
    map_public_ip_on_launch         = false
    tags                            = {
        "Name" = "DivvyCloud-ECS-Public-Subnet1"
    }
    vpc_id                          = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Public subnet 2
resource "aws_subnet" "DivvyCloud-ECS-Public-Subnet2" {
    assign_ipv6_address_on_creation = false
    availability_zone               = var.az[1]
    cidr_block                      = "172.31.64.0/20"
    map_public_ip_on_launch         = false
    tags                            = {
        "Name" = "DivvyCloud-ECS-Public-Subnet2"
    }
    vpc_id                          = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Public subnet 3
resource "aws_subnet" "DivvyCloud-ECS-Public-Subnet3" {
    assign_ipv6_address_on_creation = false
    availability_zone               = var.az[2]
    cidr_block                      = "172.31.80.0/20"
    map_public_ip_on_launch         = false
    tags                            = {
        "Name" = "DivvyCloud-ECS-Public-Subnet3"
    }
    vpc_id                          = aws_vpc.DivvyCloud-ECS-VPC.id
}

// NAT Gateway
resource "aws_eip" "DivvyCloud-NAT-GW-EIP" {
    public_ipv4_pool = "amazon"
    vpc              = true
}

// NAT Gateway 2
resource "aws_eip" "DivvyCloud-NAT-GW-EIP2" {
    public_ipv4_pool = "amazon"
    vpc              = true
}

// NAT Gateway 3
resource "aws_eip" "DivvyCloud-NAT-GW-EIP3" {
    public_ipv4_pool = "amazon"
    vpc              = true
}

resource "aws_nat_gateway" "DivvyCloud-NAT-GW" {
    allocation_id        = aws_eip.DivvyCloud-NAT-GW-EIP.id
    subnet_id            = aws_subnet.DivvyCloud-ECS-Public-Subnet1.id
    tags                 = {}
}

resource "aws_nat_gateway" "DivvyCloud-NAT-GW2" {
    allocation_id        = aws_eip.DivvyCloud-NAT-GW-EIP2.id
    subnet_id            = aws_subnet.DivvyCloud-ECS-Public-Subnet2.id
    tags                 = {}
}

resource "aws_nat_gateway" "DivvyCloud-NAT-GW3" {
    allocation_id        = aws_eip.DivvyCloud-NAT-GW-EIP3.id
    subnet_id            = aws_subnet.DivvyCloud-ECS-Public-Subnet3.id
    tags                 = {}
}

// Route table
resource "aws_route_table" "DivvyCloud-ECS-RouteTable-Public" {
    route            = [
        {
            cidr_block                = "0.0.0.0/0"
            egress_only_gateway_id    = ""
            gateway_id                = aws_internet_gateway.DivvyCloud-InternetGateway.id
            instance_id               = ""
            ipv6_cidr_block           = ""
            nat_gateway_id            = ""
            network_interface_id      = ""
            transit_gateway_id        = ""
            vpc_peering_connection_id = ""
        },
    ]
    tags             = {
        "Name" = "DivvyCloud-ECS-RouteTable-Public"
    }
    vpc_id           = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Route table
resource "aws_route_table" "DivvyCloud-ECS-RouteTable-Private" {
    route            = [
        {
            cidr_block                = "0.0.0.0/0"
            egress_only_gateway_id    = ""
            gateway_id                = ""
            instance_id               = ""
            ipv6_cidr_block           = ""
            nat_gateway_id            = aws_nat_gateway.DivvyCloud-NAT-GW.id
            network_interface_id      = ""
            transit_gateway_id        = ""
            vpc_peering_connection_id = ""
        },
    ]
    tags             = {
        "Name" = "DivvyCloud-ECS-RouteTable-Private"
    }
    vpc_id           = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Route table 2
resource "aws_route_table" "DivvyCloud-ECS-RouteTable-Private2" {
    route            = [
        {
            cidr_block                = "0.0.0.0/0"
            egress_only_gateway_id    = ""
            gateway_id                = ""
            instance_id               = ""
            ipv6_cidr_block           = ""
            nat_gateway_id            = aws_nat_gateway.DivvyCloud-NAT-GW2.id
            network_interface_id      = ""
            transit_gateway_id        = ""
            vpc_peering_connection_id = ""
        },
    ]
    tags             = {
        "Name" = "DivvyCloud-ECS-RouteTable-Private2"
    }
    vpc_id           = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Route table 3
resource "aws_route_table" "DivvyCloud-ECS-RouteTable-Private3" {
    route            = [
        {
            cidr_block                = "0.0.0.0/0"
            egress_only_gateway_id    = ""
            gateway_id                = ""
            instance_id               = ""
            ipv6_cidr_block           = ""
            nat_gateway_id            = aws_nat_gateway.DivvyCloud-NAT-GW3.id
            network_interface_id      = ""
            transit_gateway_id        = ""
            vpc_peering_connection_id = ""
        },
    ]
    tags             = {
        "Name" = "DivvyCloud-ECS-RouteTable-Private3"
    }
    vpc_id           = aws_vpc.DivvyCloud-ECS-VPC.id
}

resource "aws_route_table_association" "DivvyCloud-ECS-RouteTable-Assoc1" {
  subnet_id      = aws_subnet.DivvyCloud-ECS-Private-Subnet1.id
  route_table_id = aws_route_table.DivvyCloud-ECS-RouteTable-Private.id
}

resource "aws_route_table_association" "DivvyCloud-ECS-RouteTable-Assoc2" {
  subnet_id      = aws_subnet.DivvyCloud-ECS-Private-Subnet2.id
  route_table_id = aws_route_table.DivvyCloud-ECS-RouteTable-Private2.id
}

resource "aws_route_table_association" "DivvyCloud-ECS-RouteTable-Assoc3" {
  subnet_id      = aws_subnet.DivvyCloud-ECS-Private-Subnet3.id
  route_table_id = aws_route_table.DivvyCloud-ECS-RouteTable-Private3.id
}

resource "aws_route_table_association" "DivvyCloud-ECS-RouteTable-Assoc4" {
  subnet_id      = aws_subnet.DivvyCloud-ECS-Public-Subnet1.id
  route_table_id = aws_route_table.DivvyCloud-ECS-RouteTable-Public.id
}

resource "aws_route_table_association" "DivvyCloud-ECS-RouteTable-Assoc5" {
  subnet_id      = aws_subnet.DivvyCloud-ECS-Public-Subnet2.id
  route_table_id = aws_route_table.DivvyCloud-ECS-RouteTable-Public.id
}

resource "aws_route_table_association" "DivvyCloud-ECS-RouteTable-Assoc6" {
  subnet_id      = aws_subnet.DivvyCloud-ECS-Public-Subnet3.id
  route_table_id = aws_route_table.DivvyCloud-ECS-RouteTable-Public.id
}

// Redis security group
resource "aws_security_group" "DivvyCloud-ECS-SecurityGroup-Redis" {
    description = "RedisAccess"
    name        = "DivvyCloud-ECS-SecurityGroup-Redis"
    vpc_id      = aws_vpc.DivvyCloud-ECS-VPC.id
}

// Redis security group ingress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-Redis" {
    cidr_blocks       = [aws_vpc.DivvyCloud-ECS-VPC.cidr_block]
    from_port         = 6379
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "tcp"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-Redis.id
    self              = false
    to_port           = 6379
    type              = "ingress"

}
// Redis security group egress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-Redis2" {
    cidr_blocks       = var.egress_whitelist
    from_port         = 0
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "-1"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-Redis.id
    self              = false
    to_port           = 0
    type              = "egress"
}

// ALB security group
resource "aws_security_group" "DivvyCloud-ECS-SecurityGroup-ALB" {
    description = "DivvyCloud UI/ALB"
    name        = "DivvyCloud-ECS-SecurityGroup-ALB"
    vpc_id      = aws_vpc.DivvyCloud-ECS-VPC.id
}


// ALB security group ingress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-ALB" {
    cidr_blocks       = var.ingress_whitelist
    count = var.lb_port == 443 ? 0 : 1
    from_port         = 80
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "tcp"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-ALB.id
    self              = false
    to_port           = 80
    type              = "ingress"
}


// ALB security group ingress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-ALB2" {
    cidr_blocks       = var.ingress_whitelist
    count = var.lb_port == 443 ? 1 : 0
    from_port         = 443
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "tcp"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-ALB.id
    self              = false
    to_port           = 443
    type              = "ingress"
}

// ALB security group egress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-ALB3" {
    cidr_blocks       = var.egress_whitelist
    from_port         = 0
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "-1"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-ALB.id
    self              = false
    to_port           = 0
    type              = "egress"
}

// MySQL/RDS security group
resource "aws_security_group" "DivvyCloud-ECS-SecurityGroup-RDS" {
    description = "Database Rules"
    name        = "DivvyCloud-ECS-SecurityGroup-RDS"
    vpc_id      = aws_vpc.DivvyCloud-ECS-VPC.id
}

// MySQL/RDS security group  ingress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-RDS" {
    cidr_blocks       = [aws_vpc.DivvyCloud-ECS-VPC.cidr_block]
    from_port         = 3306
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "tcp"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-RDS.id
    self              = false
    to_port           = 3306
    type              = "ingress"
}

// MySQL/RDS security group egress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-RDS2" {
    cidr_blocks       = var.egress_whitelist
    from_port         = 0
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "-1"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-RDS.id
    self              = false
    to_port           = 0
    type              = "egress"
}

// EC2/UI-Scheduler security group
resource "aws_security_group" "DivvyCloud-ECS-SecurityGroup-UI" {
    description = "Worker/web rules"
    name        = "DivvyCloud-ECS-SecurityGroup-UI"
    tags        = {}
    vpc_id      = aws_vpc.DivvyCloud-ECS-VPC.id
}

// EC2/UI-Scheduler security group UI rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-UI" {
    cidr_blocks       = [aws_vpc.DivvyCloud-ECS-VPC.cidr_block]
    from_port         = 8001
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "tcp"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-UI.id
    self              = false
    to_port           = 8001
    type              = "ingress"
}

// EC2/UI-Scheduler security group egress rule
resource "aws_security_group_rule" "DivvyCloud-ECS-SecurityGroup-UI3" {
    cidr_blocks       = var.egress_whitelist
    from_port         = 0
    ipv6_cidr_blocks  = []
    prefix_list_ids   = []
    protocol          = "-1"
    security_group_id = aws_security_group.DivvyCloud-ECS-SecurityGroup-UI.id
    self              = false
    to_port           = 0
    type              = "egress"
}

// Data stack

// MySQL
resource "aws_db_subnet_group" "DivvyCloud-ECS-MySQL-Subnet-Group" {
  name       = "divvycloud-mysql-subnet-group"
  subnet_ids = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id, aws_subnet.DivvyCloud-ECS-Private-Subnet2.id]
  tags = {
    Name = "DivvyCloud-ECS-MySQL-Subnet-Group"
  }
}

resource "aws_db_instance" "DivvyCloud-ECS-MySQL" {
    allocated_storage                     = 100
    auto_minor_version_upgrade            = true
    backup_retention_period               = 14
    backup_window                         = "09:52-10:22"
    copy_tags_to_snapshot                 = true
    db_subnet_group_name                  = aws_db_subnet_group.DivvyCloud-ECS-MySQL-Subnet-Group.id
    deletion_protection                   = true
    enabled_cloudwatch_logs_exports       = ["audit","error","slowquery"]
    engine                                = "mysql"
    engine_version                        = "5.7.26"
    final_snapshot_identifier             = "divvycloud-ecs-mysql-final-${local.timestamp}"
    iam_database_authentication_enabled   = false
    identifier                            = "divvycloud-ecs-mysql"
    instance_class                        = "db.m5.large"
    license_model                         = "general-public-license"
    maintenance_window                    = "wed:04:37-wed:05:07"
    max_allocated_storage                 = 500
    monitoring_interval                   = 30
    monitoring_role_arn                   = local.rds_monitor_role
    multi_az                              = true
    name                                  = "divvy"
    option_group_name                     = "default:mysql-5-7"
    parameter_group_name                  = aws_db_parameter_group.DivvyCloud-RDS-SlowQuery-PG.name
    // See `variable "database_credentials"`
    //password                              = var.database_credentials[1]
    password                              = random_string.DivvyCloud-Random.result
    performance_insights_enabled          = true
    performance_insights_retention_period = 7
    port                                  = 3306
    publicly_accessible                   = true
    security_group_names                  = []
    skip_final_snapshot                   = false
    // Only use if creating database from snapshot
    //snapshot_identifier                 = "YOUR-SNAPSHOT-ID-HERE" 
    storage_encrypted                     = true
    storage_type                          = "gp2"
    tags                                  = {
        "Name" = "DivvyCloud-ECS-MySQL"
    }
    username                              = var.database_credentials[0]
    vpc_security_group_ids                = [aws_security_group.DivvyCloud-ECS-SecurityGroup-RDS.id]

}

// Create parameter group to export slow queries to CloudWatch
resource "aws_db_parameter_group" "DivvyCloud-RDS-SlowQuery-PG" {
  name   = "divvycloud-slow-query-pg"
  family = "mysql5.7"

  parameter {
    name  = "log_output"
    value = "FILE"
  }

  parameter {
    name  = "slow_query_log"
    value = "1"
  }
}

locals {
dbsecret_json = {
    default = {
        engine = aws_db_instance.DivvyCloud-ECS-MySQL.engine
        host = aws_db_instance.DivvyCloud-ECS-MySQL.address
        username = var.database_credentials[0]
        //password = var.database_credentials[1]
        password = "${random_string.DivvyCloud-Random.result}"
        dbInstanceIdentifier = aws_db_instance.DivvyCloud-ECS-MySQL.identifier
        dbname = aws_db_instance.DivvyCloud-ECS-MySQL.name
        port = aws_db_instance.DivvyCloud-ECS-MySQL.port
    }
    type = "map"
}
}
resource "aws_secretsmanager_secret" "divvycloud-credentials" {
    name             = var.divvycloud-credentials
    tags             = {}
}


resource "aws_secretsmanager_secret_version" "divvycloud-credentials" {
  secret_id     = aws_secretsmanager_secret.divvycloud-credentials.id
  secret_string = jsonencode(local.dbsecret_json.default)
}


// Container variables
locals {
    environment = [
{
    name  = "VIRTUAL_ENV"
    value = "/"
},
{
    name  = "DIVVY_REDIS_HOST"
    value = "${aws_elasticache_replication_group.DivvyCloud-ECS-Redis-RG.primary_endpoint_address}"
},
{
    name  = "DIVVY_DB_NAME"
    value = "divvy"
},
{
    name  = "DIVVY_REDIS_PORT"
    value = "6379"
},
{
    name  = "DIVVY_SECRET_DB_NAME"
    value = "divvykeys"
},
{
    name  = "DIVVY_SECRETS_PROVIDER_CONFIG"
    value = "AWSAssumeRole,region=${var.region},secret_name=${var.divvycloud-credentials}"
}
    ]
}

// Redis
resource "aws_elasticache_subnet_group" "DivvyCloud-ECS-Redis-Subnet-Group" {
  name       = "divvycloud-redis-subnet-group"
  subnet_ids = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id, aws_subnet.DivvyCloud-ECS-Private-Subnet2.id,aws_subnet.DivvyCloud-ECS-Private-Subnet3.id]
}

resource "aws_elasticache_replication_group" "DivvyCloud-ECS-Redis-RG" {
    at_rest_encryption_enabled    = false
    auto_minor_version_upgrade    = true
    automatic_failover_enabled    = true
    engine                        = "redis"
    engine_version                = "5.0.6"
    maintenance_window            = "sat:05:30-sat:06:30"
    node_type                     = "cache.t2.small"
    number_cache_clusters         = 3
    parameter_group_name          = "default.redis5.0"
    port                          = 6379
    replication_group_description = "DivvyCloud-ECS-Redis"
    replication_group_id          = "DivvyCloud-ECS-Redis"
    security_group_ids            = [aws_security_group.DivvyCloud-ECS-SecurityGroup-Redis.id]
    security_group_names          = []
    snapshot_retention_limit      = 0
    snapshot_window               = "23:30-00:30"
    subnet_group_name             = aws_elasticache_subnet_group.DivvyCloud-ECS-Redis-Subnet-Group.id
    transit_encryption_enabled    = false

    timeouts {}
}

// ALB
resource "aws_lb" "DivvyCloud-ECS-ALB" {
    enable_deletion_protection = false
    enable_http2               = true
    idle_timeout               = 60
    internal                   = false
    ip_address_type            = "ipv4"
    load_balancer_type         = "application"
    name                       = "DivvyCloud-ECS-ALB"
    security_groups            = ["${aws_security_group.DivvyCloud-ECS-SecurityGroup-ALB.id}"]
    tags                       = {}

    subnet_mapping {
        subnet_id = aws_subnet.DivvyCloud-ECS-Public-Subnet1.id
    }
    subnet_mapping {
        subnet_id = aws_subnet.DivvyCloud-ECS-Public-Subnet2.id
    }
    subnet_mapping {
        subnet_id = aws_subnet.DivvyCloud-ECS-Public-Subnet3.id
    }

    timeouts {}
}

resource "aws_lb_listener" "DivvCloud-ECS-ALB-Listener-HTTP" {
    load_balancer_arn = aws_lb.DivvyCloud-ECS-ALB.arn
    count            = var.lb_port == 443 ? 0 : 1
    port              = 80
    protocol          = "HTTP"
    
    default_action {
        order            = 1
        target_group_arn = aws_lb_target_group.DivvyCloud-ECS-ALB-TG.arn
        type             = "forward"
    }

    timeouts {}
}

resource "aws_lb_listener" "DivvCloud-ECS-ALB-Listener-HTTPS" {
    certificate_arn   = local.alb_ssl_arn
    count             = var.lb_port == 443 ? 1 : 0
    load_balancer_arn = aws_lb.DivvyCloud-ECS-ALB.arn
    port              = 443
    protocol          = "HTTPS"
    ssl_policy        = "ELBSecurityPolicy-2016-08"

    default_action {
        order            = 1
        target_group_arn = aws_lb_target_group.DivvyCloud-ECS-ALB-TG.arn
        type             = "forward"
    }

    timeouts {}
}

resource "aws_lb_target_group" "DivvyCloud-ECS-ALB-TG" {
    deregistration_delay = 300
    name                 = "DivvyCloud-ECS-ALB-TG"
    port                 = 8001
    protocol             = "HTTP"
    slow_start           = 0
    tags                 = {}
    target_type          = "ip"
    vpc_id               = aws_vpc.DivvyCloud-ECS-VPC.id

    health_check {
        enabled             = true
        healthy_threshold   = 5
        interval            = 30
        matcher             = "200"
        path                = "/Status"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
    }

    stickiness {
        cookie_duration = 86400
        enabled         = false
        type            = "lb_cookie"
    }
}

// ECS/Fargate stack
resource "aws_ecs_cluster" "DivvyCloud-ECS-Cluster" {
    name = "DivvyCloud-ECS"
    capacity_providers = ["FARGATE","FARGATE_SPOT"]
    default_capacity_provider_strategy {
        capacity_provider = "FARGATE_SPOT"
        weight = 1 
    }
    tags = {}

    setting {
        name  = "containerInsights"
        value = "enabled"
    }
}



resource "aws_cloudwatch_log_group" "DivvyCloud-ECS-Cluster-LogGroup" {
  name = aws_ecs_cluster.DivvyCloud-ECS-Cluster.name
}

resource "aws_ecs_service" "interfaceserver" {
    cluster                            = "arn:aws:ecs:${var.region}:${var.account_id}:cluster/${aws_ecs_cluster.DivvyCloud-ECS-Cluster.name}"
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 50
    desired_count                      = var.interface_server_task_count
    enable_ecs_managed_tags            = false
    health_check_grace_period_seconds  = 300
    load_balancer {
    target_group_arn                   = aws_lb_target_group.DivvyCloud-ECS-ALB-TG.arn
    container_name                     = "interfaceserver"
    container_port                     = 8001
    }
    name                               = "interfaceserver"
    platform_version                   = "LATEST"
    scheduling_strategy                = "REPLICA"
    tags                               = {}
    task_definition                    = aws_ecs_task_definition.interfaceserver.id

    deployment_controller {
        type = "ECS"
    }

    network_configuration {
        assign_public_ip = false
        security_groups  = ["${aws_security_group.DivvyCloud-ECS-SecurityGroup-UI.id}"]
        subnets          = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id,aws_subnet.DivvyCloud-ECS-Private-Subnet2.id,aws_subnet.DivvyCloud-ECS-Private-Subnet3.id]
    }

    capacity_provider_strategy {
        base              = 0
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
    }
}

resource "aws_ecs_service" "scheduler" {
    cluster                            = "arn:aws:ecs:${var.region}:${var.account_id}:cluster/${aws_ecs_cluster.DivvyCloud-ECS-Cluster.name}"
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 50
    desired_count                      = var.scheduler_task_count
    enable_ecs_managed_tags            = false
    health_check_grace_period_seconds  = 0
    name                               = "scheduler"
    platform_version                   = "LATEST"
    scheduling_strategy                = "REPLICA"
    tags                               = {}
    task_definition                    = aws_ecs_task_definition.scheduler.id

    deployment_controller {
        type = "ECS"
    }

    network_configuration {
        assign_public_ip = false
        security_groups  = []
        subnets          = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id,aws_subnet.DivvyCloud-ECS-Private-Subnet2.id,aws_subnet.DivvyCloud-ECS-Private-Subnet3.id]
    }

    capacity_provider_strategy {
        base              = 0
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
    }
}


resource "aws_ecs_service" "divvykeys" {
    cluster                            = "arn:aws:ecs:${var.region}:${var.account_id}:cluster/${aws_ecs_cluster.DivvyCloud-ECS-Cluster.name}"
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 100
    desired_count                      = var.divvykeys_task_count
    enable_ecs_managed_tags            = false
    health_check_grace_period_seconds  = 0
    name                               = "DELETE-ME-AFTER-FIRST-RUN"
    platform_version                   = "LATEST"
    scheduling_strategy                = "REPLICA"
    tags                               = {}
    task_definition                    = aws_ecs_task_definition.divvykeys.id

    deployment_controller {
        type = "ECS"
    }

    network_configuration {
        assign_public_ip = false
        security_groups  = []
        subnets          = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id]
    }

    capacity_provider_strategy {
        base              = 0
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
    }
}


resource "aws_ecs_service" "worker" {
    cluster                            = "arn:aws:ecs:${var.region}:${var.account_id}:cluster/${aws_ecs_cluster.DivvyCloud-ECS-Cluster.name}"
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 100
    desired_count                      = var.worker_task_count
    enable_ecs_managed_tags            = false
    health_check_grace_period_seconds  = 0
    name                               = "worker"
    platform_version                   = "LATEST"
    scheduling_strategy                = "REPLICA"
    tags                               = {}
    task_definition                    = aws_ecs_task_definition.worker.id

    deployment_controller {
        type = "ECS"
    }

    network_configuration {
        assign_public_ip = false
        security_groups  = []
        subnets          = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id,aws_subnet.DivvyCloud-ECS-Private-Subnet2.id,aws_subnet.DivvyCloud-ECS-Private-Subnet3.id]
    }

    capacity_provider_strategy {
        base              = 0
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
    }
}

resource "aws_ecs_service" "workerPersistent" {
    capacity_provider_strategy {
        capacity_provider = "FARGATE"
        weight = 1 
    }
    cluster                            = "arn:aws:ecs:${var.region}:${var.account_id}:cluster/${aws_ecs_cluster.DivvyCloud-ECS-Cluster.name}"
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 100
    desired_count                      = var.worker_persistent_task_count
    enable_ecs_managed_tags            = false
    health_check_grace_period_seconds  = 0
    name                               = "workerPersistent"
    platform_version                   = "LATEST"
    scheduling_strategy                = "REPLICA"
    tags                               = {}
    task_definition                    = aws_ecs_task_definition.workerPersistent.id

    deployment_controller {
        type = "ECS"
    }

    network_configuration {
        assign_public_ip = false
        security_groups  = []
        subnets          = [aws_subnet.DivvyCloud-ECS-Private-Subnet1.id,aws_subnet.DivvyCloud-ECS-Private-Subnet2.id,aws_subnet.DivvyCloud-ECS-Private-Subnet3.id]
    }

    capacity_provider_strategy {
        capacity_provider = "FARGATE"
        weight = 1 
    }
}

resource "aws_ecs_task_definition" "interfaceserver" {
    container_definitions    = jsonencode(
        [
            {
                command                = [
                    "divvycloud",
                    "webserver",
                ]
                cpu                    = 0
                dnsSearchDomains       = []
                dnsServers             = []
                dockerLabels           = {}
                dockerSecurityOptions  = []
                entryPoint             = []
                environment            = local.environment
                essential              = true
                extraHosts             = []
                image                  = "${var.divvycloud_version}"
                links                  = []
                linuxParameters        = {
                    capabilities = {}
                    devices      = []
                }
                logConfiguration       = {
                    logDriver = "awslogs"
                    options   = {
                        awslogs-group         = aws_ecs_cluster.DivvyCloud-ECS-Cluster.name
                        awslogs-region        = var.region
                       awslogs-stream-prefix = "interfaceserver"
                    }
                }
                mountPoints            = []
                name                   = "interfaceserver"
                portMappings           = [
                    {
                        containerPort = 8001
                        hostPort      = 8001
                        protocol      = "tcp"
                    },
                ]
                privileged             = false
                pseudoTerminal         = false
                readonlyRootFilesystem = false
                ulimits                = []
                volumesFrom            = []
            },
        ]
    )
    cpu                      = "1024"
    execution_role_arn       = local.ecs_exec_role
    family                   = "interfaceserver"
    memory                   = "2048"
    network_mode             = "awsvpc"
    requires_compatibilities = [
        "FARGATE",
    ]
    tags                     = {}
    task_role_arn            = local.ecs_task_role
}

resource "aws_ecs_task_definition" "scheduler" {
    container_definitions    = jsonencode(
        [
            {
                command                = [
                    "divvycloud",
                    "scheduler",
                    "--db-upgrade",
                ]
                cpu                    = 0
                dnsSearchDomains       = []
                dnsServers             = []
                dockerLabels           = {}
                dockerSecurityOptions  = []
                entryPoint             = []
                environment            = local.environment
                essential              = true
                extraHosts             = []
                image                  = "${var.divvycloud_version}"
                links                  = []
                linuxParameters        = {
                    capabilities = {}
                    devices      = []
                }
                logConfiguration       = {
                    logDriver = "awslogs"
                    options   = {
                        awslogs-group         = aws_ecs_cluster.DivvyCloud-ECS-Cluster.name
                        awslogs-region        = var.region
                        awslogs-stream-prefix = "scheduler"
                    }
                }
                mountPoints            = []
                name                   = "scheduler"
                portMappings           = []
                privileged             = false
                pseudoTerminal         = false
                readonlyRootFilesystem = false
                ulimits                = []
                volumesFrom            = []
            },
        ]
    )
    cpu                      = "1024"
    execution_role_arn       = local.ecs_exec_role
    family                   = "scheduler"
    memory                   = "2048"
    network_mode             = "awsvpc"
    requires_compatibilities = [
        "FARGATE",
    ]
    tags                     = {}
    task_role_arn            = local.ecs_task_role
}


resource "aws_ecs_task_definition" "divvykeys" {
    container_definitions    = jsonencode(
        [
            {
                command                = [
                    "mysql",
                    "-h",
                    "${aws_db_instance.DivvyCloud-ECS-MySQL.address}",
                    "-u",
                    "${var.database_credentials[0]}",
                    //"-p${var.database_credentials[1]}",
                    "-p${random_string.DivvyCloud-Random.result}",
                    "-e",
                    "CREATE DATABASE divvykeys"
                ]
                cpu                    = 0
                dnsSearchDomains       = []
                dnsServers             = []
                dockerLabels           = {}
                dockerSecurityOptions  = []
                entryPoint             = []
                environment            = local.environment
                essential              = true
                extraHosts             = []
                image                  = "${var.divvycloud_version}"
                links                  = []
                linuxParameters        = {
                    capabilities = {}
                    devices      = []
                }
                logConfiguration       = {
                    logDriver = "awslogs"
                    options   = {
                        awslogs-group         = aws_ecs_cluster.DivvyCloud-ECS-Cluster.name
                        awslogs-region        = var.region
                        awslogs-stream-prefix = "divvykeys"
                    }
                }
                mountPoints            = []
                name                   = "divvykeys"
                portMappings           = []
                privileged             = false
                pseudoTerminal         = false
                readonlyRootFilesystem = false
                ulimits                = []
                volumesFrom            = []
            },
        ]
    )
    cpu                      = "512"
    execution_role_arn       = local.ecs_exec_role
    family                   = "divvykeys"
    memory                   = "1024"
    network_mode             = "awsvpc"
    requires_compatibilities = [
        "FARGATE",
    ]
    tags                     = {}
    task_role_arn            = local.ecs_task_role
}


resource "aws_ecs_task_definition" "worker" {
    container_definitions    = jsonencode(
        [
            {
                command                = [
                    "divvycloud",
                    "worker",
                    "--queue",
                    "p2"
                ]
                cpu                    = 0
                dnsSearchDomains       = []
                dnsServers             = []
                dockerLabels           = {}
                dockerSecurityOptions  = []
                entryPoint             = []
                environment            = local.environment
                essential              = true
                extraHosts             = []
                image                  = "${var.divvycloud_version}"
                links                  = []
                linuxParameters        = {
                    capabilities = {}
                    devices      = []
                }
                logConfiguration       = {
                    logDriver = "awslogs"
                    options   = {
                        awslogs-group         = aws_ecs_cluster.DivvyCloud-ECS-Cluster.name
                        awslogs-region        = var.region
                        awslogs-stream-prefix = "worker"
                    }
                }
                mountPoints            = []
                name                   = "worker"
                portMappings           = []
                privileged             = false
                pseudoTerminal         = false
                readonlyRootFilesystem = false
                ulimits                = []
                volumesFrom            = []
            },
        ]
    )
    cpu                      = var.worker_task_cpu
    execution_role_arn       = local.ecs_exec_role
    family                   = "worker"
    memory                   = var.worker_task_mem
    network_mode             = "awsvpc"
    requires_compatibilities = [
        "FARGATE",
    ]
    tags                     = {}
    task_role_arn            = local.ecs_task_role
}

resource "aws_ecs_task_definition" "workerPersistent" {
    container_definitions    = jsonencode(
        [
            {
                command                = [
                    "divvycloud",
                    "worker",
                    "--queue",
                    "p0",
                    "--queue",
                    "p1"

                ]
                cpu                    = 0
                dnsSearchDomains       = []
                dnsServers             = []
                dockerLabels           = {}
                dockerSecurityOptions  = []
                entryPoint             = []
                environment            = local.environment
                essential              = true
                extraHosts             = []
                image                  = "${var.divvycloud_version}"
                links                  = []
                linuxParameters        = {
                    capabilities = {}
                    devices      = []
                }
                logConfiguration       = {
                    logDriver = "awslogs"
                    options   = {
                        awslogs-group         = aws_ecs_cluster.DivvyCloud-ECS-Cluster.name
                        awslogs-region        = var.region
                        awslogs-stream-prefix = "workerPersistent"
                    }
                }
                mountPoints            = []
                name                   = "workerPersistent"
                portMappings           = []
                privileged             = false
                pseudoTerminal         = false
                readonlyRootFilesystem = false
                ulimits                = []
                volumesFrom            = []
            },
        ]
    )
    cpu                      = var.worker_task_cpu
    execution_role_arn       = local.ecs_exec_role
    family                   = "workerPersistent"
    memory                   = var.worker_task_mem
    network_mode             = "awsvpc"
    requires_compatibilities = [
        "FARGATE",
    ]
    tags                     = {}
    task_role_arn            = local.ecs_task_role
}

