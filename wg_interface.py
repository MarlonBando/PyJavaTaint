import re
import json
import requests

def conduct_webgoat_query(url, query, jsessionid, name_of_lesson):
     
    request_data = { "query": query }
    request_cookies = {"JSESSIONID": jsessionid}
    raw_webgoat_output = requests.post(url, data=request_data, cookies=request_cookies)
    return webgoat_to_json(raw_webgoat_output)



def webgoat_to_json(name_of_lesson,raw_webgoat_output):
    match name_of_lesson:
        case "example1":
            result = {"example1": raw_webgoat_output}
        case "Assignment 5b":
            return parse_assignment_5b(raw_webgoat_output)
        case "Assignment 5a":
            return parse_assignment_5a(raw_webgoat_output)
        case "Lesson 2":
            return parse_lesson_2(raw_webgoat_output)
        case _:
            raise Exception(f"Unhandled lesson : {name_of_lesson}")



def parse_assignment_5b(raw_webgoat_output):
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
    rows_count = len(re.findall(first_pattern, raw_webgoat_output))
    
    for i in range(rows_count):
        row_data = {}
        for column, pattern in patterns.items():
            matches = re.findall(pattern, raw_webgoat_output)
            if matches and i < len(matches):
                row_data[column] = matches[i]
        data.append(row_data)
    
    return json.dumps(data)



def parse_assignment_5a(raw_webgoat_output):
    data = json.loads(raw_webgoat_output)
    table_text = remove_white_spaces(data['output'])

    patterns = {
        'USERID': r'<td>(\d+)</td>',
        'FIRST_NAME': r'<td>(\w+)</td>.*?<td>\w+</td>',
        'LAST_NAME': r'<td>\w+</td><td>(\w+)</td>',
        'DEPARTMENT': r'<td>\w+</td><td>\w+</td><td>(\w+)</td>',
        'SALARY': r'<td>\w+</td><td>\w+</td><td>\w+</td><td>(\d+)</td>',
        'AUTH_TAN': r'<td>\w+</td><td>\w+</td><td>\w+</td><td>\d+</td><td>(\w+)</td>',
        'PHONE': r'<td>\w+</td><td>\w+</td><td>\w+</td><td>\d+</td><td>\w+</td><td>(.*?)</td>'
    }

    data = []
    row_data = {}
    for column, pattern in patterns.items():
        matches = re.findall(pattern, table_text)
        if matches:
            row_data[column] = matches[0]
    data.append(row_data)

    return json.dumps(data)



def parse_lesson_2(raw_webgoat_output):
    raw_webgoat_output = remove_white_spaces(raw_webgoat_output)

    header_pattern = r"<th>(.*?)</th>"
    row_pattern = r"<td>(.*?)</td>"

    headers = re.findall(header_pattern, raw_webgoat_output)
    rows = re.findall(row_pattern, raw_webgoat_output)
    results = [{headers[0]: value} for value in rows] if headers else []

    return json.dumps(results)



def remove_white_spaces(input_string):
    return input_string.replace("\\r", "").replace("\\n", "").replace("\\", "").strip()