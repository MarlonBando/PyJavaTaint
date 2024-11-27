from objects import Settings, APIEndpoint, Parameter
import requests
import query_list_generator as qlg
from typing import Dict, Any
import json
import wg_interface
from report_writer import Vulnerability_report, Vulnerability, Endpoint_review
import time

class Fuzzer:



    def __init__(self, settings: Settings):
        self.basic_url: str = settings.URL
        self.jsessionid: str = settings.JSESSIONID
        self.endpoints: list = settings.api_endpoints
        self.direct_query_addr: str = settings.DIRECT_QUERY_ADDR
        self.direct_query: str = "SELECT * FROM employees;"
        self.fuzz_report: str = "FUZZER REPORT : \n"
        self.db_table_settings = settings.db_table_settings
        self.vulnerability_report: Vulnerability_report = Vulnerability_report()



    def fuzz_all_endpoints(self):

        global_start_time: float = time.time()
        for endpoint in self.endpoints:
            self._fuzz_endpoint(endpoint)
        global_end_time: float = time.time()
        global_execution_time:float = global_end_time - global_start_time
        self.vulnerability_report.global_execution_time = global_execution_time
        self.vulnerability_report.write_report_to_file()



    def fuzz_single_endpoint(self, endpoint_name):

        global_start_time: float = time.time()
        for endpoint in self.endpoints:
            if endpoint.name == endpoint_name:
                self._fuzz_endpoint(endpoint)
                global_end_time: float = time.time()
                global_execution_time:float = global_end_time - global_start_time
                self.vulnerability_report.global_execution_time = global_execution_time
                self.vulnerability_report.write_report_to_file()
                return
        raise Exception(f'Endpoint {endpoint_name} not found')



    def _fuzz_endpoint(self, endpoint: APIEndpoint) -> None:

            self.vulnerability_report.add_new_endpoint(endpoint.name)
            start_time: float = time.time()
            wg_interface.recreate_database(self.basic_url+self.direct_query_addr, self.jsessionid)
            self._fuzz_endpoint_with_exfiltration(endpoint)
            self._fuzz_endpoint_with_corruption(endpoint)
            end_time: float = time.time()
            execution_time: float = end_time - start_time
            self.vulnerability_report.set_exec_time_of_last_endpoint(execution_time)



    def _fuzz_endpoint_with_exfiltration(self, endpoint: APIEndpoint) -> None:

        url: str = self.basic_url + endpoint.suffix
        legit_json_result = self._get_legit_result(url, endpoint)
        for fuzzed_parameter in endpoint.parameters:
            for tainted_query in qlg.generate_tainted_queries_for_exfiltration(fuzzed_parameter.default_input):

                tainted_result = self._get_tainted_result(url, endpoint, fuzzed_parameter, tainted_query)
                if tainted_result != '[]' and tainted_result != legit_json_result:

                    self.vulnerability_report.add_vuln_to_last_endpoint( Vulnerability("exfiltration", endpoint.name, fuzzed_parameter.default_input, tainted_query, legit_json_result, tainted_result) )



    def _fuzz_endpoint_with_corruption(self, endpoint: APIEndpoint) -> None:

        url = self.basic_url + endpoint.suffix
        direct_url: str = self.basic_url + self.direct_query_addr
        sane_db_snapshot = self.get_db_snapshot()
        for fuzzed_parameter in endpoint.parameters:
            for tainted_query in qlg.generate_tainted_queries_for_corruption(fuzzed_parameter.default_input, self.db_table_settings):

                self._get_tainted_result(url, endpoint, fuzzed_parameter, tainted_query)
                new_db_snapshot = self.get_db_snapshot()
                if not sane_db_snapshot == new_db_snapshot:
                    self.vulnerability_report.add_vuln_to_last_endpoint( Vulnerability("corruption", endpoint.name, fuzzed_parameter.default_input, tainted_query, sane_db_snapshot, new_db_snapshot) )
                    wg_interface.recreate_database(direct_url, self.jsessionid)


    def _get_legit_result(self, url: str, endpoint: APIEndpoint) -> str:
        data = self._get_default_data_for_post_call(endpoint.parameters)
        return self._get_result(url, data, endpoint.name)
    


    def _get_tainted_result(self, url: str, endpoint: APIEndpoint, fuzzed_parameter: Parameter, tainted_query: str) -> str:
        parameters: list[Parameter] = endpoint.parameters
        param_data = self._get_default_data_for_post_call(parameters)
        param_data[fuzzed_parameter.name] = tainted_query
        return self._get_result(url, param_data, endpoint.name)



    def _get_result(self, url: str, data: Dict[str, Any], endpoint_name: str) -> str:
        response = wg_interface.query_webgoat(url, data, self.jsessionid, endpoint_name)
        return response

    

    def get_db_snapshot(self):
        direct_url: str = self.basic_url + self.direct_query_addr
        return wg_interface.wg_direct_database_check(direct_url, self.direct_query, self.jsessionid)
    


    def _get_default_data_for_post_call(self, parameters: list[Parameter]) -> Dict[str, str]:
        return {param.name: param.default_input for param in parameters}
    


    def _get_default_input(self, parameter: Parameter):
        return parameter.default_input
    
    

    def _get_cookies(self) -> Dict[str, str]:
        return {'JSESSIONID': self.jsessionid}
