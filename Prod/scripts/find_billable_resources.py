## Script for finding all billable resources in an AWS account. Currently tees off of the default AWS profile

## EXCLUDES Middle east, China, and GovCloud regions
## Excluded Neptune since DocumentDB and Neptune seem to return the same cluster values and don't want to double count

import boto3 

regions = ["us-east-2","us-east-1","us-west-1","us-west-2","ap-south-1","ap-northeast-2","ap-southeast-1","ap-southeast-2","ap-northeast-1","ca-central-1","eu-central-1","eu-west-1","eu-west-2","eu-west-3","eu-north-1","sa-east-1"]

instance_list = []
rds_list = []
redshift_cluster_list = []
elasticache_cluster_list = []
dynamodb_table_list = []
elasticsearch_domain_list = []
workspaces_list = []
documentdb_list = []
# neptune_list = []

for region in regions:
    ## EC2
    print("### Starting EC2 List for region: " + region + " ###")
    ec2client = boto3.client('ec2', region_name=region)
    response = ec2client.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_list.append(instance["InstanceId"] + " , " + region)
            print(instance["InstanceId"] + " , " + region)

    ## RDS
    print("### Starting RDS List for region: " + region + " ###")
    rds = boto3.client('rds', region_name=region)
    response = rds.describe_db_instances()
    for db_instance in response['DBInstances']:
        print (db_instance['Endpoint']['Address'])
        rds_list.append(db_instance['Endpoint']['Address'])

    ## Redshift
    print("### Starting Redshift List for region: " + region + " ###")
    redshiftclient = boto3.client('redshift', region_name=region)
    response = redshiftclient.describe_clusters()
    for cluster in response["Clusters"]:
        redshift_cluster_list.append(cluster['ClusterIdentifier'] + " , " + region)
        print(cluster['ClusterIdentifier'] + " , " + region)

    ## Elasticache
    print("### Starting Elasticache List for region: " + region + " ###")
    elasticacheclient = boto3.client('elasticache', region_name=region)
    response = elasticacheclient.describe_cache_clusters()
    for cluster in response["CacheClusters"]:
        elasticache_cluster_list.append(cluster['CacheClusterId'] + " , " + region)
        print(cluster['CacheClusterId'] + " , " + region)

    ## DynamoDB
    print("### Starting DynamoDB List for region: " + region + " ###")
    dynamodbclient = boto3.client('dynamodb', region_name=region)
    response = dynamodbclient.list_tables()
    for table in response["TableNames"]:
        dynamodb_table_list.append(table + " , " + region)
        print(table + " , " + region)

    ## ElasticSearch
    print("### Starting ElasticSearch List for region: " + region + " ###")
    elasticsearchclient = boto3.client('es', region_name=region)
    response = elasticsearchclient.list_domain_names()
    for domain in response["DomainNames"]:
        elasticsearch_domain_list.append(domain['DomainName'] + " , " + region)
        print(domain['DomainName'] + " , " + region)


    ## Workspaces
    workspaces_regions = ["us-east-1","us-west-2","ap-northeast-2","ap-southeast-1","ap-southeast-2","ap-northeast-1","ca-central-1","eu-central-1","eu-west-1","eu-west-2","sa-east-1"]
    if region in workspaces_regions:
        print("### Starting Workspaces List for region: " + region + " ###")
        workspacesclient = boto3.client('workspaces', region_name=region)
        response = workspacesclient.describe_workspaces()
        for workspace in response["Workspaces"]:
            workspaces_list.append(workspace['WorkspaceId'] + " , " + region)
            print(workspace['WorkspaceId'] + " , " + region)
    else:
        print("Workspaces not supported in " + region + ". Skipping")


    ## DocumentDB
    documentdb_regions = ["us-east-1","us-west-2","ap-south-1","ap-northeast-2","ap-southeast-2","ap-northeast-1","ca-central-1","eu-central-1","eu-west-1","eu-west-2"]
    if region in documentdb_regions:
        print("### Starting DocumentDB List for region: " + region + " ###")
        documentdbclient = boto3.client('docdb', region_name=region)
        response = documentdbclient.describe_db_clusters()
        for documentdb in response["DBClusters"]:
            documentdb_list.append(documentdb['DBClusterIdentifier'] + " , " + region)
            print(documentdb['DBClusterIdentifier'] + " , " + region)
    else:
        print("DocumentDB not supported in " + region + ". Skipping")

    # ## Neptune
    # neptune_regions = ["us-east-1","us-east-2","us-west-2","ap-south-1","ap-northeast-2","ap-southeast-1","ap-southeast-2","ap-northeast-1","ca-central-1","eu-central-1","eu-west-1","eu-west-2","eu-west-3","eu-north-1","sa-east-1"]
    # if region in neptune_regions:
    #     print("### Starting Neptune List for region: " + region + " ###")
    #     neptuneclient = boto3.client('neptune', region_name=region)
    #     response = neptuneclient.describe_db_clusters()
    #     for neptune in response["DBClusters"]:
    #         neptune_list.append(neptune['DBClusterIdentifier'] + " , " + region)
    #         print(neptune['DBClusterIdentifier'] + " , " + region)
    # else:
    #     print("Neptune not supported in " + region + ". Skipping")


instance_count = len(instance_list)
rds_count = len(rds_list)
redshift_cluster_count = len(redshift_cluster_list)
elasticache_cluster_count = len(elasticache_cluster_list)
dynamodb_cluster_count = len(dynamodb_table_list)
elasticsearch_domain_count = len(elasticsearch_domain_list)
workspaces_count = len(workspaces_list)
documentdb_count = len(documentdb_list)
# neptune_count = len(neptune_list)

print("\n########### OVERALL COUNTS #############")

print("EC2 Instances in this account: " + str(instance_count))
print("RDS Instances in this account: " + str(rds_count))
print("Redshift Clusters in this account: " + str(redshift_cluster_count))
print("Elasticache Clusters in this account: " + str(elasticache_cluster_count))
print("DynamoDB Clusters in this account: " + str(dynamodb_cluster_count))
print("Elasticsearch Clusters in this account: " + str(elasticsearch_domain_count))
print("Workspaces in this account: " + str(workspaces_count))
print("DocumentDBs in this account: " + str(documentdb_count))
# print("Neptune DBs in this account: " + str(neptune_count))

#total_counts_list = [instance_count,rds_count,redshift_cluster_count,elasticache_cluster_count,dynamodb_cluster_count,elasticsearch_domain_count,workspaces_count,documentdb_count,neptune_count]
total_counts_list = [instance_count,rds_count,redshift_cluster_count,elasticache_cluster_count,dynamodb_cluster_count,elasticsearch_domain_count,workspaces_count,documentdb_count]
total_count = sum(total_counts_list)
print("\n### TOTAL BILLABLE RESOURCE COUNT: " + str(total_count))