class DB_table_settings:
  
  sql_datatypes: list[str] = ['TEXT', 'INT', 'text', 'int']

  def __init__(self, table_name: str, column_names: list[str], data_types: list[str]):

    self.table_name = table_name
    self.column_names = column_names
    self.data_types = data_types
    self.check_settings_length()
    self.check_datatype_validity()
    


  def check_settings_length(self):
    if len(self.column_names) != len(self.data_types):
      raise Exception("column_names and data_types must be the same length")
    
  def check_datatype_validity(self):
    for datatype in self.data_types:
      if not datatype in self.sql_datatypes:
        raise Exception(f"datatypes must be TEXT or INT, not {datatype}")