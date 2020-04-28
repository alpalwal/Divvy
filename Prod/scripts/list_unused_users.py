#List All Divvy users who haven't logged in in 90 days and output to CSV
import json
import requests
import getpass
import csv
from datetime import date,time,datetime,timedelta

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

username = "" # Username/password to authenticate against the API
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URL
base_url = ""

#  Param validation
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
        verify=False,
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

def get_domain_admins():
    data = {'limit': 500, 'offset': 0, 'order_by': "name", 'filters': []}
    response = requests.post(
        url=base_url + '/v2/prototype/domains/admins/list',
        verify=False,
        data=json.dumps(data),
        headers=headers
    )
    try:
        return response.json()
    except:
        print(response)
        exit()

def get_users():
    data = {'limit': 500, 'offset': 0, 'order_by': "name", 'filters': []}
    response = requests.post(
        url=base_url + '/v2/public/users/list',
        verify=False,
        data=json.dumps(data),
        headers=headers
    )
    try:
        return response.json()
    except:
        print(response)
        exit()

admin_list = get_domain_admins() ## Get list of admins and put them into an array
normal_user_list = get_users() ## Same thing for normal users

# Both responses above are the same. Squish them into a master array
all_user_list = []
all_user_list.extend(admin_list['users'])
all_user_list.extend(normal_user_list['users'])

old_users = []
today = date.today()  # get todays date

for user in all_user_list:
    try:
        last_login_date = user['last_login_time'].split(" ")[0] # Just pull date and ignore the time ## "last_login_time": "2020-02-07 21:52:18",
        year, month, day = map(int, last_login_date.split("-"))
        last_login_date_formatted = date(year, month, day)
        days_since_last_login = (today - last_login_date_formatted).days
        
        if days_since_last_login > 90:
            user['days_since_last_login'] = days_since_last_login
            old_users.append(user)
    except KeyError:
        user['days_since_last_login'] = "Never logged in"
        user['last_login_time'] = "Never logged in"
        old_users.append(user)

with open('expired_users.csv', mode='w', newline="") as csv_file:
    fieldnames = ['name','user_id','organization_admin','domain_admin','domain_viewer','email_address','username','two_factor_enabled','two_factor_required','suspended','last_login_time','days_since_last_login']
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)
    for user in old_users:
        writer.writerow([user['name'],str(user['user_id']),user['organization_admin'],user['domain_admin'],user['domain_viewer'],user['email_address'],user['username'],user['two_factor_enabled'],user['two_factor_required'],user['suspended'],user['last_login_time'],str(user['days_since_last_login'])])