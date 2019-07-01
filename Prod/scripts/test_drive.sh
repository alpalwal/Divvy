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
          # If RedHat/CentOS, start the docker service
          if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
              sudo yum install -y ftp://bo.mirror.garr.it/1/slc/centos/7.1.1503/extras/x86_64/Packages/container-selinux-2.9-4.el7.noarch.rpm
              sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
              sudo yum install -y docker-ce docker-ce-cli containerd.io
              sudo service docker start
          else # Ubuntu
              curl -sSL https://get.docker.com/ | sudo sh
          fi
          echo -e "${CYAN}[DOCKER INSTALL COMPLETE]${NC}"
fi

echo -e "${CYAN}[CHECKING FOR DOCKER-COMPOSE INSTALL]${NC}"

docker_compose_version=`docker-compose --version`

if [ $? -eq 0 ];
then
    echo -e "${CYAN}[DOCKER-COMPOSE ALREADY INSTALLED: ${NC}$docker_compose_version${CYAN}]"
else
    echo -e "${CYAN}[DOCKER-COMPOSE NOT FOUND, DOWNLOADING AND INSTALLING]${NC}"

    if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then ## Redhat
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

if [ "$DIVVY_ENV" == "prod" ];
then
    curl -sO https://s3.amazonaws.com/get.divvycloud.com/compose/docker-compose.yml
else
    curl -s https://s3.amazonaws.com/get.divvycloud.com/compose/docker-compose.db-local.yml -o docker-compose.yml

    # Check for enough disk space to run the test-drive install. It's a hassle to fix the install if we run out of space and want to make sure that they're warned about it. 
    # Currently just checking for Ubuntu and Amazon Linux
    if [ ! -f /etc/redhat-release ] ; then
        disk_space=`df /  --output=avail | grep -v Avail | sed s/G//g`
        if [ "$disk_space" -lt "17000000" ]; then
            while true; do
                read -p "The DivvyCloud test drive installation should have at least 20gb of disk space to run without issue. This instance has less than that. Would you like to continue?" yn
                case $yn in
                    [Yy]* ) make install; break;;
                    [Nn]* ) exit;;
                    * ) echo "Please answer yes or no.";;
                esac
            done
        fi
    fi

fi

sudo chown -R $USER:$GROUP /divvycloud
echo -e "${CYAN}[ADDING USER TO DOCKER GROUP]${NC}"
sudo usermod -aG docker $USER
echo -e "${CYAN}[DOWNLOADING LATEST DIVVYCLOUD CONTAINERS]${NC}"

# If RedHat/CentOS
if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
    sudo /usr/bin/docker-compose pull
    echo -e "${CYAN}[STARTING DIVVYCLOUD]${NC}"
    sudo /usr/bin/docker-compose up -d
else # Ubuntu
    sudo /usr/local/bin/docker-compose pull
    echo -e "${CYAN}[STARTING DIVVYCLOUD]${NC}"
    sudo /usr/local/bin/docker-compose up -d
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

# If RedHat/CentOS - start docker on boot 
if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
    sudo chkconfig docker on
fi