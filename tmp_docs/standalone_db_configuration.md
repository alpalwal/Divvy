# Create the infrastructure

1. Spin up an instance that meets these requirements: https://docs.divvycloud.com/docs/server-and-network-recommendations

2. Spin up an external database (RDS, CloudSQL, etc.) using the requirements defined in the link above  
    *MAKE SURE THE DB IS RUNNING THE LATEST VERSION OF MYSQL 5.7*  
    Note down the hostname or IP, the username, and password for the DB

3. Verify that you have connectivity from the instance to the database (networking rules can be tricky)  
``` telnet <db hostname or ip> 3306 ```

Good:
```root@ip-172-31-1-18:/home/ubuntu# telnet standalonerds.coqr2r2zaakr.us-east-1.rds.amazonaws.com 3306
Trying 172.31.54.207...
Connected to standalonerds.coqr2r2zaakr.us-east-1.rds.amazonaws.com.
Escape character is '^]'.
J
5.6.40?@aG"q6W2?6U,y@q8dlu%Vmysql_native_password^C
Connection closed by foreign host.
```

Bad:
```root@ip-172-31-1-18:/home/ubuntu# telnet standalonerds.coqr2r2zaakr.us-east-1.rds.amazonaws.com 3306
Trying 172.31.54.207...
<lags here and nothing happens>
^C
```

# Configure the instance

1. SSH into the instance

2. Install Divvycloud  
```curl -s https://s3.amazonaws.com/get.divvycloud.com/index.html | sudo bash```

3. Stop the DivvyCloud software
```
cd /divvycloud
sudo docker-compose down
```

4. Update the docker-compose file so that it doesn't spin up a MySQL docker container. We don't need it since there's a standalone one instead. 

```
sudo awk '$1 == "mysql:"{t=1}
   t==1 && $1 == "image:"{t++; next}
   t==2 && /redis:[[:blank:]]*$/{t=0}
   t != 2' docker-compose.yml > /tmp/docker-compose.yml.tmp
sudo sed -i '/mysql/d' /tmp/docker-compose.yml.tmp
sudo mv /tmp/docker-compose.yml.tmp docker-compose.yml
```

5. Set your database credentials as environment variables (temporarily)
```
HOST="standalonerds.coqr2r2zaakr.us-east-1.rds.amazonaws.com"
USERNAME="tempuser"
PASSWORD="temppassword"
```

6. Install the MySQL client and connect to your database from the instance

```
sudo apt-get install -y mysql-client
mysql -h $HOST -u $USERNAME -p
# It'll prompt you to enter your password
```

7. Add the DivvyCloud tables and settings to your database
```
CREATE DATABASE divvy;
CREATE DATABASE divvykeys;
GRANT ALL PRIVILEGES on divvy.* to '%' IDENTIFIED BY 'divvy';
GRANT ALL PRIVILEGES on divvykeys.* to '%' IDENTIFIED BY 'divvy';
GRANT RELOAD ON *.* TO '%' IDENTIFIED BY 'divvy';
FLUSH PRIVILEGES;
exit
```

8. Update your prod.env file to point to your new database
```
sudo sed -i s/DIVVY_DB_HOST=mysql/DIVVY_DB_HOST=$HOST/g ./prod.env
sudo sed -i s/DIVVY_SECRET_DB_HOST=mysql/DIVVY_SECRET_DB_HOST=$HOST/g ./prod.env
sudo sed -i s/DIVVY_DB_USERNAME=divvy/DIVVY_DB_USERNAME=$USERNAME/g ./prod.env
sudo sed -i s/DIVVY_SECRET_DB_USERNAME=divvy/DIVVY_SECRET_DB_USERNAME=$USERNAME/g ./prod.env
sudo sed -i s/DIVVY_DB_PASSWORD=divvy/DIVVY_DB_PASSWORD=$PASSWORD/g ./prod.env
sudo sed -i s/DIVVY_SECRET_DB_PASSWORD=divvy/DIVVY_SECRET_DB_PASSWORD=$PASSWORD/g ./prod.env
```

9. Clean up your environment variables
```
unset HOST
unset USERNAME
unset PASSWORD
```

10. Start DivvyCloud
```
sudo docker-compose up -d
```

11. Check the logs to make sure DivvyCloud can connect to the database:
Good: 
```
scheduler_1        | --
scheduler_1        | -- Host: localhost    Database: divvy
scheduler_1        | -- ------------------------------------------------------
scheduler_1        | -- Server version	5.7.22-log
scheduler_1        | 
scheduler_1        | /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
scheduler_1        | /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
scheduler_1        | /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
scheduler_1        | /*!40101 SET NAMES utf8 */;
scheduler_1        | /*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
scheduler_1        | /*!40103 SET TIME_ZONE='+00:00' */;
scheduler_1        | /*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
scheduler_1        | /*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
scheduler_1        | /*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
scheduler_1        | /*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
scheduler_1        | --
scheduler_1        | -- Table structure for table `AWSPlacementGroups`
scheduler_1        | --
scheduler_1        | 
scheduler_1        | DROP TABLE IF EXISTS `AWSPlacementGroups`;
scheduler_1        | /*!40101 SET @saved_cs_client     = @@character_set_client */;
scheduler_1        | /*!40101 SET character_set_client = utf8 */;
scheduler_1        | CREATE TABLE `AWSPlacementGroups` (
scheduler_1        |   `resource_id` varchar(255) NOT NULL,
scheduler_1        |   `organization_service_id` int(4) NOT NULL,
scheduler_1        |   `region_name` varchar(16) NOT NULL,
scheduler_1        |   `group_id` varchar(40) NOT NULL,
scheduler_1        |   `name` varchar(255) DEFAULT NULL,
scheduler_1        |   `strategy` varchar(32) NOT NULL,
scheduler_1        |   `state` varchar(32) DEFAULT NULL,
scheduler_1        |   PRIMARY KEY (`resource_id`)
scheduler_1        | ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
scheduler_1        | /*!40101 SET character_set_client = @saved_cs_client */;
scheduler_1        | --
scheduler_1        | -- Dumping data for table `AWSPlacementGroups`
scheduler_1        | --
scheduler_1        | 
scheduler_1        | LOCK TABLES `AWSPlacementGroups` WRITE;
scheduler_1        | /*!40000 ALTER TABLE `AWSPlacementGroups` DISABLE KEYS */;
scheduler_1        | /*!40000 ALTER TABLE `AWSPlacementGroups` ENABLE KEYS */;
scheduler_1        | UNLOCK TABLES;
scheduler_1        | --
scheduler_1        | -- Table structure for table `ApiAccountingConfigs`
scheduler_1        | --

```

Bad:
```
worker_6           | ERROR:DivvyCloudCli:Unable to connect to database
worker_6           | Traceback (most recent call last):
worker_6           |   File "/usr/local/lib/python2.7/dist-packages/divvycloud/load.py", line 85, in validate_database_schemas
worker_6           |     DivvyCloudGatewayORM().ValidateSchemaVersion()
worker_6           |   File "/usr/local/lib/python2.7/dist-packages/DivvyDb/DivvyDb.py", line 441, in ValidateSchemaVersion
worker_6           |     raise DatabaseConnectivityValidationException(database_name='divvy')
worker_6           | DatabaseConnectivityValidationException: Database validation error.
worker_6           | WARNING:root:Incorrect database schema, waiting for db to be upgraded.
```