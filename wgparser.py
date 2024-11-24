import re
import json

def clean_input(input_string):
    """
    Cleans the input string by removing escape characters and unnecessary whitespace.
    """
    return input_string.replace("\\r", "").replace("\\n", "").replace("\\", "").strip()

def parse_assignment_5b(text):
    # Extract headers and values for each column
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
    # Find all matches for each row
    first_pattern = patterns['USERID']
    rows_count = len(re.findall(first_pattern, text))
    
    for i in range(rows_count):
        row_data = {}
        for column, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches and i < len(matches):
                row_data[column] = matches[i]
        data.append(row_data)
    
    return json.dumps(data)

def parse_assignment_5a(text):
    # Clean and extract the 'output' field from JSON
    data = json.loads(text)
    table_text = clean_input(data['output'])

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

def parse_lesson_2(text):
    text = clean_input(text)

    header_pattern = r"<th>(.*?)</th>"
    row_pattern = r"<td>(.*?)</td>"

    headers = re.findall(header_pattern, text)
    rows = re.findall(row_pattern, text)
    results = [{headers[0]: value} for value in rows] if headers else []

    return json.dumps(results)

def webgoat_to_json(name,text):
    match name:
        case "example1":
            # Handle case for "example1"
            result = {"example1": text}
        case "Assignment 5b":
            return parse_assignment_5b(text)
        case "Assignment 5a":
            return parse_assignment_5a(text)
        case "Lesson 2":
            return parse_lesson_2(text)
        case _:
            # Handle default case
            result = {"default": text}
    return ""