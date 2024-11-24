from constant import Settings, APIEndpoint, Parameter
import requests
import query_list_generator as qlg
from typing import Dict, Any
import json

class Fuzzer:

    def __init__(self, settings: Settings):
        self.basic_url: str = settings.URL + settings.DIRECT_QUERY_ADDR
        self.endpoints: list[str] = []
        self.endpoints: list = settings.api_endpoints

    def fuzz_all(self):
        for endpoint in self.endpoints:
            self._fuzz_endpoint(endpoint)

    def fuzz_endpoint(self, name):
        for endpoint in self.endpoints:
            if endpoint.name == name:
                self._fuzz_endpoint(endpoint)
                return
        print(f'Endpoint {name} not found')

    def _fuzz_endpoint(self, endpoint: APIEndpoint) -> None:
        url = self.basic_url + endpoint.suffix
        legit_result = self.get_legit_result(url, endpoint)

        for parameter in endpoint.parameters:
            injectable = False
            for tainted_query in qlg.generate_tainted_queries_for_exfiltration():
                tainted_result = self.get_tainted_result(url, endpoint, parameter, tainted_query)
                if tainted_result != legit_result:
                    print(f'Potential SQL Injection found in {endpoint.name} parameter {parameter.type}')
                    print(f'Original query: {parameter.default}')
                    print(f'Tainted query: {parameter.default + tainted_query}')
                    print(f'Legit result: {legit_result}')
                    print(f'Tainted result: {tainted_result}')
                    injectable = True
            if not injectable:
                print(f'No SQL Injection found in {endpoint.name} parameter {parameter.type}')

    def get_legit_result(self, url: str, endpoint: APIEndpoint) -> str:
        data = self.get_data_post_call(endpoint.parameters)
        return self.get_result(url, data)
    
    def get_tainted_result(self, url: str, endpoint: APIEndpoint, parameter: Parameter, tainted_query: str) -> str:
        param_data = self.get_data_post_call(endpoint.parameters)
        param_data[parameter.type] = parameter.default + tainted_query
        return self.get_result(url, param_data)

    def get_result(self, url: str, data: Dict[str, Any]) -> str:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        return self.validate_result(response)

    def validate_result(self, response):
        if response.status_code != 200:
            return {}
        
        response_json = json.loads(response.text)
        output = response.get("output", "")
        return output.replace('\n', '')
    
    def get_data_post_call(self, parameters: list[Parameter]) -> Dict[str, str]:
        return {param.type: param.default for param in parameters}
