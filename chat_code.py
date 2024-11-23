import requests
import json

def api_call(url, data, filename):
    """
    Makes a POST request to the API with the specified query and saves the response to a file.
    """
    # Add your session cookies here
    cookies = {
        "JSESSIONID": "FoXUi_Zyzjl3YL2kl0EKUddv4YSZd4059BxCo2Gq",  # Replace this with the actual session ID
    }

    # Make the POST request with cookies
    response = requests.post(url, data=data, cookies=cookies)

    # Print the response
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    # Convert the response text to a JSON object
    response_json = json.loads(response.text)

    with open(filename, 'w') as f:
        f.write(response_json.get("output", ""))

def recreate_table(api_url, script_file):
    """
    Recreates the employees table by reading the SQL script from a file and sending it to the API.
    """
    with open(script_file, 'r') as file:
        sql_script = file.read()

    # Split the script into individual queries
    queries = [query.strip() for query in sql_script.split(';') if query.strip()]

    for query in queries:
        data = {"query": query}
        print(f"Executing query: {query}")
        api_call(api_url, data, 'recreate_table_response.json')

def check_all_employees(api_url, output_file):
    """
    Fetches all employees using the provided API and saves the response to a file.
    """
    data_check_all = {"query": "SELECT * FROM employees;"}
    api_call(api_url, data_check_all, output_file)

if __name__ == "__main__":
    # Define the API URLs
    api_url = "http://localhost:8080/WebGoat/SqlInjection/attack4?username=mathias"
    check_url = "http://localhost:8080/WebGoat/SqlInjection/attack2direct?username=mathias"

    # Path to the SQL script file
    script_file = "recreate_employees.sql"

    # Recreate the table
    recreate_table(api_url, script_file)

    # Check all employees
    # check_all_employees(check_url, 'check_all_employees.json')
