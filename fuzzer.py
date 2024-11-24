from constant import Settings, APIEndpoint, Parameter
import requests
import query_list_generator as qlg
from typing import Dict, Any
import json
import wg_interface

class Fuzzer:



    def __init__(self, settings: Settings):
        self.basic_url: str = settings.URL
        self.jessionid: str = settings.JSESSIONID
        self.endpoints: list = settings.api_endpoints
        self.direct_query_addr: str = settings.DIRECT_QUERY_ADDR
        self.direct_query: str = "SELECT * FROM employees;"
        self.fuzz_report: str = "FUZZER REPORT : \n"



    def fuzz_all_endpoints(self):
        for endpoint in self.endpoints:
            self._fuzz_endpoint(endpoint)



    def fuzz_single_endpoint(self, endpoint_name):
        for endpoint in self.endpoints:
            if endpoint.name == endpoint_name:
                self._fuzz_endpoint(endpoint)
                return
        raise Exception(f'Endpoint {endpoint_name} not found')



    def _fuzz_endpoint(self, endpoint: APIEndpoint) -> None:

            self._fuzz_endpoint_with_exfiltration(endpoint)
            self._fuzz_endpoint_with_corruption(endpoint)



    def _fuzz_endpoint_with_exfiltration(self, endpoint: APIEndpoint) -> None:

        url: str = self.basic_url + endpoint.suffix
        legit_json_result = self._get_legit_result(url, endpoint)
        for fuzzed_parameter in endpoint.parameters:

            endpoint_is_injectable = False
            for tainted_query in qlg.generate_tainted_queries_for_exfiltration():

                tainted_result = self._get_tainted_result(url, endpoint.parameters, fuzzed_parameter, tainted_query)
                if tainted_result != legit_json_result:

                    self.write_injection_to_report(endpoint, fuzzed_parameter, tainted_query, legit_json_result, tainted_result)
                    endpoint_is_injectable = True
            if not endpoint_is_injectable:

                self.fuzz_report += f'No SQL Injection found in {endpoint.name} parameter {fuzzed_parameter.type}'
        self.save_report()



    def _fuzz_endpoint_with_corruption(self, endpoint: APIEndpoint) -> None:

        url = self.basic_url + endpoint.suffix
        sane_db_snapshot = self.get_db_snapshot()
        for fuzzed_parameter in endpoint.parameters:

            injectable = False
            for tainted_query in qlg.generate_tainted_queries_for_corruption():

                self._get_tainted_result(url, endpoint.parameters, fuzzed_parameter, tainted_query)
                new_db_snapshot = self.get_db_snapshot()
                if not sane_db_snapshot == new_db_snapshot:

                    self.write_injection_to_report(endpoint, fuzzed_parameter, tainted_query, sane_db_snapshot, new_db_snapshot)
                    injectable = True
            if not injectable:
            
                self.fuzz_report += f'No SQL Injection found in {endpoint.name} parameter {fuzzed_parameter.type}'
        self.save_report()



    def _get_legit_result(self, url: str, endpoint: APIEndpoint) -> str:
        data = self._get_default_data_for_post_call(endpoint.parameters)
        return self._get_result(url, data, endpoint.name)
    


    def _get_tainted_result(self, url: str, endpoint: APIEndpoint, fuzzed_parameter: Parameter, tainted_query: str) -> str:
        parameters: list[Parameter] = endpoint.parameters
        param_data = self._get_default_data_for_post_call(parameters)
        param_data[fuzzed_parameter.name] = tainted_query
        return self._get_result(url, param_data, endpoint.name)



    def _get_result(self, url: str, data: Dict[str, Any], endpoint_name: str) -> str:
        response = requests.post(url, data=data,cookies=self._get_cookies())
        response = wg_interface.query_webgoat(url, data, self.jessionid, endpoint_name)
        return self._validate_result(response)



    def _validate_result(self, response):
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            return {}
        
        response_json = json.loads(response.text)
        output = response_json.get("output", "")
        return output.replace('\n', '')
    

    def get_db_snapshot(self):
        return wg_interface.query_webgoat(url=self.basic_url, query=self.direct_query, name_of_lesson=self.direct_query_addr)
    


    def _get_default_data_for_post_call(self, parameters: list[Parameter]) -> Dict[str, str]:
        return {param.name: param.default_input for param in parameters}
    


    def _get_default_input(self, parameter: Parameter):
        return parameter.default_input
    
    

    def _get_cookies(self) -> Dict[str, str]:
        return {'JSESSIONID': self.jessionid}


    ## Functions linked to writing report

    def save_report(self):
        with open("fuzz_report.txt", "w") as report_file:
            report_file.write(self.fuzz_report)

    def write_injection_to_report(self, endpoint, parameter, tainted_query, legit_result, tainted_result):
        self.fuzz_report += f'Potential SQL Injection found in {endpoint.name} parameter {parameter.type}'
        self.fuzz_report += f'Original query: {parameter.default}'
        self.fuzz_report += f'Tainted query: {parameter.default + tainted_query}'
        self.fuzz_report += f'Legit result: {legit_result}'
        self.fuzz_report += f'Tainted result: {tainted_result}'
