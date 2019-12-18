var request = require("request");

// Username/password to authenticate against the API
username = "alexc"
password = "9srZMS%0PxlY" 

// DivvyCloud URL EX: http://localhost:8001 or http://45.59.252.4:8001)
base_url = "https://sales-demo.divvycloud.com"

var login_url = base_url + "/v2/public/user/login"

var options = {
  method: 'POST',
  url: login_url,
  headers: {
    'content-type': 'application/json',
    'accept-encoding': 'gzip'
  },
  body: {
    "username": username,
    "password": password
  },
  json: true,
  gzip: true 
};


request(options, function (error, response, body) {
    if (error) throw new Error(error);
    return body.session_id;
});



// function getRoutes(callback){
//     request(options, function(error, response, body) {
//         if (!error && response.statusCode == 200) {
//             result = JSON.stringify(JSON.parse(body));          
//             return callback(result, false);
//         } else {            
//             return callback(null, error);;
//         }
//     });
// }

// getRoutes()

/*
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

# Get Org info
def get_org():
    data = {}

    response = requests.get(
        url=base_url + '/v2/prototype/domain/organizations/detail/get',
        data=json.dumps(data),
        headers=headers
        )
    return response.json()    

# Create the pack
org_info = get_org()
print(org_info)
*/