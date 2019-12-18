#!/bin/bash
# DivvyCloud install script for the test-drive installation 
# Supports Ubuntu, RHEL, AWS Linux, and CentOS

CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}[CHECKING FOR DOCKER INSTALL]${NC}"

docker_version=`docker --version | grep "Docker version"`
if [ $? -eq 0 ];
then
    echo -e "${CYAN}[DOCKER ALREADY INSTALLED: ${NC}$docker_version${CYAN}]"
else
    echo -e "${CYAN}[DOCKER NOT FOUND, DOWNLOADING AND INSTALLING]${NC}"

    if [ -f "/etc/lsb-release" ]; then # Ubuntu
        curl -sSL https://get.docker.com/ | sudo sh
    elif [ -f "/etc/system-release" ]; then # Linux
        if grep -q "CentOS" /etc/system-release; then # CentOS
            sudo yum install -y yum-utils device-mapper-persistent-data lvm2
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo service docker start
        elif grep -q "Red Hat" /etc/system-release; then # RHEL
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y --setopt=obsoletes=0 docker-ce-17.03.2.ce-1.el7.centos.x86_64 docker-ce-selinux-17.03.2.ce-1.el7.centos.noarch
            sudo service docker start  
        elif grep -q "Amazon" /etc/system-release; then # AWS Linux
            sudo yum update -y
            sudo amazon-linux-extras install docker -y
            sudo service docker start              
        fi
    else # Misc / Macbook
        echo "Uknown operating system. Supported OSes are Ubuntu, RHEL, CentOS, and AWS Linux. Exiting" ; exit
    fi
    echo -e "${CYAN}[DOCKER INSTALL COMPLETE]${NC}"
fi

echo -e "${CYAN}[CHECKING FOR DOCKER-COMPOSE INSTALL]${NC}"

docker_compose_version=`docker-compose --version`

if [ $? -eq 0 ]; then
    echo -e "${CYAN}[DOCKER-COMPOSE ALREADY INSTALLED: ${NC}$docker_compose_version${CYAN}]"
else
    echo -e "${CYAN}[DOCKER-COMPOSE NOT FOUND, DOWNLOADING AND INSTALLING]${NC}"

    if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then ## Redhat / Centos / AWS
        sudo curl -L "https://github.com/docker/compose/releases/download/1.14.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/bin/docker-compose
        sudo chmod +x /usr/bin/docker-compose
    else # Ubuntu
        sudo curl -L "https://github.com/docker/compose/releases/download/1.14.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    echo -e "${CYAN}[DOCKER-COMPOSE INSTALL COMPLETE]${NC}"
fi

echo -e "${CYAN}[CREATING APP DIRECTORY /divvycloud]${NC}"
sudo mkdir /divvycloud
cd /divvycloud

echo -e "${CYAN}[DOWNLOADING DEFAULT CONFIG FILES]${NC}"
sudo curl -sO https://s3.amazonaws.com/get.divvycloud.com/compose/prod.env

sudo curl -o /divvycloud/httpd-ssl.conf http://get.divvycloud.com/apache/httpd-ssl.conf
sudo curl -o /divvycloud/httpd.conf http://get.divvycloud.com/apache/httpd.conf
sudo curl -o /divvycloud/server.key http://get.divvycloud.com/apache/server.key
sudo curl -o /divvycloud/server.crt http://get.divvycloud.com/apache/server.crt
sudo curl -o /divvycloud/docker-compose.yml http://get.divvycloud.com/compose/docker-compose.apache.db-local.yml

ip=`curl --silent http://icanhazip.com`

if [ -z "$ip" ] || [ ${#ip} -ge 15 ]; then 
    echo "Getting public IP via \`curl http://icanhazip.com\` failed. Leaving IP as \"localhost\""
else
    sudo sed -i "s/localhost/$instance_ip/g" httpd.conf 
fi

sudo chown -R $USER:$GROUP /divvycloud
echo -e "${CYAN}[ADDING USER TO DOCKER GROUP]${NC}"
sudo usermod -aG docker $USER
echo -e "${CYAN}[DOWNLOADING LATEST DIVVYCLOUD CONTAINERS]${NC}"

# If RedHat/CentOS/AWS
if [ -f /etc/system-release ]; then
    sudo /usr/bin/docker-compose -f /divvycloud/docker-compose.yml pull
    echo -e "${CYAN}[STARTING DIVVYCLOUD]${NC}"
    sudo /usr/bin/docker-compose -f /divvycloud/docker-compose.yml up -d    
else # Ubuntu
    sudo /usr/local/bin/docker-compose -f /divvycloud/docker-compose.yml pull
    echo -e "${CYAN}[STARTING DIVVYCLOUD]${NC}"
    sudo /usr/local/bin/docker-compose -f /divvycloud/docker-compose.yml up -d
fi

sudo /usr/bin/docker ps
echo -e "${CYAN}[IT MAY TAKE THE INTERFACE SERVER A COUPLE OF MINUTES TO BECOME AVAILABLE WHEN LAUNCHING FOR THE FIRST TIME]${NC}"
echo ""
echo ""
echo -e "${CYAN}[The '${USER}' user has been to the 'docker' group. However, you will need to start a new session for this change to take effect.]${NC}"

echo -e "${CYAN}[Adding DivvyCloud to crontab for auto-start on boot]${NC}"
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "@reboot /usr/local/bin/docker-compose -f /divvycloud/docker-compose.yml up -d" >> mycron
#install new cron file
crontab mycron
#Cleanup
rm mycron

# If RedHat/CentOS/AWS - start docker on boot 
if [ -f /etc/system-release ]; then
    sudo systemctl enable docker.service   
fi



