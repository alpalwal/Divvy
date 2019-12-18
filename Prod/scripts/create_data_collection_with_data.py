# Script to create a data collection and populate it in divvycloud

import json
import requests
import getpass

######################
######################
# PARAMETERS 
######################
######################

# Username/password to authenticate against the API
<<<<<<< HEAD
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 
=======
username = "alexc"
password = "9srZMS%0PxlY" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 
>>>>>>> f7bf42ceb3ca912c789f6aee1f1481e3dcf2b5eb

# API URL
base_url = "https://sales-demo.divvycloud.com"

collection_data = { # value : description
    "ami-0b898040803850657":"Amazon Linux 2 AMI (HVM), SSD Volume Type",
    "ami-035b3c7efe6d061d5":"Amazon Linux AMI 2018.03.0 (HVM), SSD Volume Type",
    "ami-0c322300a1dd5dc79":"Red Hat Enterprise Linux 8 (HVM), SSD Volume Type",
    "ami-0b5372ab3202bd20b":"SUSE Linux Enterprise Server 15 SP1 (HVM), SSD Volume Type",
    "ami-07d0cf3af28718ef8":"Ubuntu Server 18.04 LTS (HVM), SSD Volume Type",
    "ami-0cfee17793b08a293":"Ubuntu Server 16.04 LTS (HVM), SSD Volume Type",
    "ami-04ca2d0801450d495":"Microsoft Windows Server 2019 Base",
    "ami-004852354728c0e51":"Deep Learning AMI (Ubuntu) Version 24.0",
    "ami-06c2c729346a4ffc0":"Deep Learning AMI (Amazon Linux) Version 24.0",
    "ami-0b5b391ed8ccaa538":"Deep Learning Base AMI (Ubuntu) Version 19.0",
    "ami-0bdd095c2fbd0e692":"Deep Learning Base AMI (Amazon Linux) Version 19.0",
    "ami-0220fe618f784ff03":"Microsoft Windows Server 2019 Base with Containers",
    "ami-07143576a508f7106":"Microsoft Windows Server 2019 with SQL Server 2017 Standard",
    "ami-007900f8c6bee1af9":"Microsoft Windows Server 2019 with SQL Server 2016 Standard",
    "ami-0e68d9d1aafa53347":"Microsoft Windows Server 2019 with SQL Server 2017 Enterprise",
    "ami-088c8c49c63ec3dbd":"Microsoft Windows Server 2019 with SQL Server 2016 Enterprise",
    "ami-00877efa2d3025556":"Microsoft Windows Server 1903 Base",
    "ami-013e2b5127d181b0c":"Microsoft Windows Server 2016 Base",
    "ami-00d4e9ff62bc40e03":"Ubuntu Server 14.04 LTS (HVM), SSD Volume Type",
    "ami-0b85dec54588aa1e7":"SUSE Linux Enterprise Server 12 SP4 (HVM), SSD Volume Type",
    "ami-027930fde2107b8f2":"Microsoft Windows Server 2016 Base with Containers",
    "ami-082f94cb58f926555":"Deep Learning AMI (Microsoft Windows Server 2016)",
    "ami-0056b6a062f55f6a1":"Microsoft Windows Server 2016 with SQL Server 2017 Standard",
    "ami-0df44240806ced84b":"Microsoft Windows Server 2016 with SQL Server 2017 Enterprise",
    "ami-019f4bf51ecc136b2":"Microsoft Windows Server 2016 with SQL Server 2016 Standard",
    "ami-047cb3ca56f97bf09":"Microsoft Windows Server 2016 with SQL Server 2016 Enterprise",
    "ami-0daee40e15682f8fa":"Microsoft Windows Server 2012 R2 Base",
    "ami-0d3f8fba08591e0cf":"Microsoft Windows Server 2012 R2 with SQL Server 2016 Standard",
    "ami-0cb2a062cc528a2ef":"Microsoft Windows Server 2012 R2 with SQL Server 2016 Enterprise",
    "ami-02666d31e797d5190":"Microsoft Windows Server 2012 Base",
    "ami-0be3b7126b85e11dc":"Microsoft Windows Server 2008 R2 Base",
    "ami-087a6127ba9676bb6":"Amazon Linux 2 LTS with SQL Server 2017 Standard",
    "ami-003dae68d018759d1":"Ubuntu Server 16.04 LTS (HVM) with SQL Server 2017 Standard",
    "ami-05673d809cbe59f27":".NET Core 2.1 with Amazon Linux 2 - Version 1.0",
    "ami-e24b7d9d":".NET Core 2.1 with Ubuntu Server 18.04 - Version 1.0",
    "ami-0637be04b7a7f7b5a":"Deep Learning Base AMI (Amazon Linux 2) Version 19.0",
    "ami-0d609b328e1c9ca6a":"Deep Learning AMI (Amazon Linux 2) Version 24.0"
}

# collection_data = {}
collection_name = "Approved AMIs"

######################
# End Parameters
######################

# Param validation
if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

# Full URL
login_url = base_url + '/v2/public/user/login'

# Shorthand helper function
def get_auth_token():
    response = requests.post(
        url=login_url,
        data=json.dumps({"username": username, "password": passwd}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        })
    return response.json()['session_id']

auth_token = get_auth_token()

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': auth_token
}

# Create a data collection w/ data populated
def create_collection():
    data = {
        "collection_data": collection_data,
        "collection_name": collection_name
    }
    response = requests.post(
        url=base_url + '/v2/datacollections/',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Create the pack
data_collection = create_collection()
print(data_collection)


