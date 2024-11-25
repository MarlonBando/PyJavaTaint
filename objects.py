from dataclasses import dataclass
from typing import List, Dict, Any
import yaml



@dataclass
class Parameter:
    """Represents a parameter configuration for an API endpoint."""
    type: str
    default_input: str
    name: str



@dataclass
class APIEndpoint:
    """Represents an API endpoint configuration."""
    name: str
    suffix: str
    parameters: List[Parameter]



class DB_table_settings:
  
  sql_datatypes: list[str] = ['TEXT', 'INT', 'text', 'int']

  def __init__(self):
    self.table_name = ''
    self.column_names = []
    self.column_datatypes = []
    

  def check_settings_length(self):
    if len(self.column_names) != len(self.column_datatype):
      raise Exception("column_names and data_types must be the same length")
    
  def check_datatype_validity(self):
    for datatype in self.column_datatype:
      if not datatype in self.sql_datatypes:
        raise Exception(f"datatypes must be TEXT or INT, not {datatype}")




class Settings:
    """Manages application settings loaded from YAML configuration."""


    def __init__(self, config_path: str = 'settings.yaml'):
        self.URL = ''
        self.USER = ''
        self.JSESSIONID = ''
        self.DIRECT_QUERY_ADDR = ''
        self.DIRECT_QUERY = ''
        self.api_endpoints: List[APIEndpoint] = []
        self.db_table_settings: DB_table_settings = DB_table_settings()
        
        raw_yaml_settings = self._load_yaml_file(config_path)
        self._load_all_settings(raw_yaml_settings)



    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Loads and returns the YAML configuration file."""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError:
            raise ValueError("Invalid YAML configuration file")



    def _load_all_settings(self, settings: Dict[str, Any]) -> None:
        """Orchestrates the loading of all configuration sections."""
        self._load_user_settings(settings.get('user_settings', {}))
        self._load_db_table_settings(settings.get('db_table_settings', {}))
        self._load_base_api_settings(settings.get('base_api_settings', {}))
        self._load_api_endpoints(settings.get('api_endpoints_settings', []))



    def _load_user_settings(self, user_settings: Dict[str, str]) -> None:
        """Loads user-specific settings."""
        if not user_settings.get('username'):
            raise ValueError("Missing 'username' in user_settings section of settings.yaml")
        if not user_settings.get('jsessionid'):
            raise ValueError("Missing 'jsessionid' in user_settings section of settings.yaml")
        self.USER = user_settings.get('username', '')
        self.JSESSIONID = user_settings.get('jsessionid', '')



    def _load_base_api_settings(self, base_settings: Dict[str, str]) -> None:
        """Loads base API configuration settings."""

        if not base_settings.get('url'):
            raise ValueError("Missing 'url' in base_api_settings section of settings.yaml")
        if not base_settings.get('direct_query_addr'):
            raise ValueError("Missing 'direct_query_addr' in base_api_settings section of settings.yaml")
        if not base_settings.get('direct_query'):
            raise ValueError("Missing 'direct_query' in base_api_settings section of settings.yaml")
        self.URL = base_settings.get('url', '')
        self.DIRECT_QUERY_ADDR = base_settings.get('direct_query_addr', '')
        self.DIRECT_QUERY = base_settings.get('direct_query', '')

    

    def _load_db_table_settings(self, db_table_settings: Dict[str, str]) -> None:

        if not db_table_settings.get('table_name'):
            raise ValueError("Missing 'table_name' in settings.yaml")
        if not db_table_settings.get('column_names'):
            raise ValueError("Missing 'column_names' in settings.yaml")
        if not db_table_settings.get('column_datatypes'):
            raise ValueError("Missing 'column_datatypes' in settings.yaml")
        self.db_table_settings.table_name = db_table_settings.get('table_name', '')
        self.db_table_settings.column_names = db_table_settings.get('column_names', [])
        self.db_table_settings.column_datatypes = db_table_settings.get('column_datatypes', [])



    def _load_api_endpoints(self, endpoints: List[Dict[str, Any]]) -> None:
        if not endpoints:
            raise ValueError("Missing API endpoints in api_settings section of settings.yaml")

        self.api_endpoints = []
        for i, endpoint in enumerate(endpoints):
            # Validate required fields
            if 'name' not in endpoint:
                raise ValueError(f"Missing 'name' in endpoint {i} of settings.yaml")
            if 'suffix' not in endpoint:
                raise ValueError(f"Missing 'suffix' in endpoint {i} of settings.yaml")

            # Create endpoint with parameters
            parameters = self._create_parameters(endpoint.get('parameters', []))
            api_endpoint = APIEndpoint(
                name=endpoint['name'],
                suffix=endpoint['suffix'],
                parameters=parameters
            )
            self.api_endpoints.append(api_endpoint)


    @staticmethod
    def _create_parameters(params_config: List[Dict[str, str]]) -> List[Parameter]:
        parameters = []
        for param in params_config:
            if 'type' not in param:
                raise ValueError("Parameter missing required 'type' field")
            if 'default_input' not in param:
                raise ValueError("Parameter missing required 'default_input' field")
            parameter = Parameter(
                name=param['name'],
                type=param['type'],
                default_input=param['default_input']
            )
            parameters.append(parameter)
        return parameters