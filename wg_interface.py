import re
import json
import requests

def query_webgoat(url, request_data, jsessionid, name_of_lesson):
     
    request_cookies = {"JSESSIONID": jsessionid}
    raw_webgoat_output = requests.post(url, data=request_data, cookies=request_cookies)
    return webgoat_to_json(name_of_lesson, raw_webgoat_output.text)



def wg_direct_database_check(direct_url: str, direct_query: str, jsessionid: str):

    request_data = {"query": direct_query}
    request_cookies = {"JSESSIONID": jsessionid}
    raw_webgoat_output = requests.post(direct_url, data=request_data, cookies=request_cookies)
    return webgoat_to_json("direct_query", raw_webgoat_output.text)




def webgoat_to_json(name_of_lesson, raw_webgoat_output_text):
    match name_of_lesson:
        case "direct_query":
            return parse_direct_query(raw_webgoat_output_text)
        case "example1":
            result = {"example1": raw_webgoat_output_text}
        case "Assignment 5b":
            return parse_assignment_5b(raw_webgoat_output_text)
        case "Assignment 5a":
            return parse_assignment_5a(raw_webgoat_output_text)
        case "Lesson 2":
            return parse_lesson_2(raw_webgoat_output_text)
        case _:
            raise Exception(f"Unhandled lesson : {name_of_lesson}")


def parse_direct_query(raw_webgoat_output_text):
    data = json.loads(raw_webgoat_output_text)
    if data['output'] != None:
        table_text = remove_white_spaces(data['output'])
    else: 
        return data 
    return table_text


def parse_assignment_5b(raw_webgoat_output_text):
    patterns = {
        'USERID': r'(\d+),\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]*,\s*\d+,\s*<br',
        'FIRST_NAME': r'\d+,\s*([^,]+),\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]*,\s*\d+,\s*<br',
        'LAST_NAME': r'\d+,\s*[^,]+,\s*([^,]+),\s*[^,]+,\s*[^,]+,\s*[^,]*,\s*\d+,\s*<br',
        'CC_NUMBER': r'\d+,\s*[^,]+,\s*[^,]+,\s*([^,]+),\s*[^,]+,\s*[^,]*,\s*\d+,\s*<br',
        'CC_TYPE': r'\d+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]+),\s*[^,]*,\s*\d+,\s*<br',
        'COOKIE': r'\d+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]*),\s*\d+,\s*<br',
        'LOGIN_COUNT': r'\d+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]*,\s*(\d+),\s*<br'
    }
    
    data = []
    first_pattern = patterns['USERID']
    rows_count = len(re.findall(first_pattern, raw_webgoat_output_text))
    
    for i in range(rows_count):
        row_data = {}
        for column, pattern in patterns.items():
            matches = re.findall(pattern, raw_webgoat_output_text)
            if matches and i < len(matches):
                row_data[column] = matches[i]
        data.append(row_data)
    
    return data



def parse_assignment_5a(raw_webgoat_output_text):
    data = json.loads(raw_webgoat_output_text)
    if data['output'] != None:
        table_text = remove_white_spaces(data['output'])
    else: 
        return data        

    patterns = {
        'USERID': r'<tr><td>(\d+)</td>',
        'FIRST_NAME': r'<tr><td>\d+</td><td>(\w+)</td>',
        'LAST_NAME': r'<tr><td>\d+</td><td>\w+</td><td>(\w+)</td>',
        'DEPARTMENT': r'<tr><td>\d+</td><td>\w+</td><td>\w+</td><td>(\w+)</td>',
        'SALARY': r'<tr><td>\d+</td><td>\w+</td><td>\w+</td><td>\w+</td><td>([\d\.]+)</td>',
        'AUTH_TAN': r'<tr><td>\d+</td><td>\w+</td><td>\w+</td><td>\w+</td><td>[\d\.]+</td><td>(\w+)</td>'
    }

    new_data = []
    columns_data = {column: re.findall(pattern, table_text) for column, pattern in patterns.items()}

    num_rows = len(columns_data['USERID'])
    for i in range(num_rows):
        row_data = {column: columns_data[column][i] for column in columns_data}
        new_data.append(row_data)
    return new_data



def parse_lesson_2(raw_webgoat_output_text):
    raw_webgoat_output_text = remove_white_spaces(raw_webgoat_output_text)

    header_pattern = r"<th>(.*?)</th>"
    row_pattern = r"<td>(.*?)</td>"

    headers = re.findall(header_pattern, raw_webgoat_output_text)
    rows = re.findall(row_pattern, raw_webgoat_output_text)
    results = [{headers[0]: value} for value in rows] if headers else []

    return results



def remove_white_spaces(input_string):
    return input_string.replace("\\r", "").replace("\\n", "").replace("\\", "").strip()



def recreate_database(direct_url: str, jsessionid:str):

    drop_table_query: str = "DROP TABLE employees"

    create_table_query: str = """
    CREATE TABLE employees (
        userid INT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        department VARCHAR(50),
        salary DECIMAL(10, 2),
        auth_tan VARCHAR(10)
    );
    """

    fill_table_query: str = """
    INSERT INTO employees (userid, first_name, last_name, department, salary, auth_tan)
    VALUES
        (32147, 'Paulina', 'Travers', 'Accounting', 46000.00, 'P45JSI'),
        (89762, 'Tobi', 'Barnett', 'Development', 77000.00, 'TA9LL1'),
        (96134, 'Bob', 'Franco', 'Marketing', 83700.00, 'LO9S2V'),
        (34477, 'Abraham', 'Holman', 'Development', 50000.00, 'UU2ALK'),
        (37648, 'John', 'Smith', 'Marketing', 64350.00, '3SL99A');
    """

    wg_direct_database_check(direct_url, drop_table_query, jsessionid)
    wg_direct_database_check(direct_url, create_table_query, jsessionid)
    wg_direct_database_check(direct_url, fill_table_query, jsessionid)

