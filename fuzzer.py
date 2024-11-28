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
        print("[DEBUG] Initializing Fuzzer...")
        self.basic_url: str = settings.URL
        self.jsessionid: str = settings.JSESSIONID
        self.endpoints: list = settings.api_endpoints
        self.direct_query_addr: str = settings.DIRECT_QUERY_ADDR
        self.direct_query: str = "SELECT * FROM employees;"
        self.fuzz_report: str = "FUZZER REPORT : \n"
        self.db_table_settings = settings.db_table_settings
        self.vulnerability_report: Vulnerability_report = Vulnerability_report()
        print(f"[DEBUG] Fuzzer initialized with URL: {self.basic_url}")



    def fuzz_all_endpoints(self):
        print("\n[DEBUG] Starting to fuzz all endpoints...")
        print(f"[DEBUG] Total endpoints to process: {len(self.endpoints)}")
        global_start_time: float = time.time()
        for i, endpoint in enumerate(self.endpoints, 1):
            print(f"\n[DEBUG] Processing endpoint {i}/{len(self.endpoints)}: {endpoint.name}")
            self._fuzz_endpoint(endpoint)
        global_end_time: float = time.time()
        global_execution_time:float = global_end_time - global_start_time
        self.vulnerability_report.global_execution_time = global_execution_time
        print(f"[DEBUG] Writing final report to file...")
        self.vulnerability_report.write_report_to_file()
        print(f"[DEBUG] Finished fuzzing all endpoints. Total time: {global_execution_time:.2f}s")



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
        print(f"\n[DEBUG] Fuzzing endpoint: {endpoint.name}")
        print(f"[DEBUG] Endpoint URL suffix: {endpoint.suffix}")
        print(f"[DEBUG] Number of parameters: {len(endpoint.parameters)}")
        self.vulnerability_report.add_new_endpoint(endpoint.name)
        start_time: float = time.time()
        print("[DEBUG] Recreating database for fresh test environment...")
        #wg_interface.recreate_database(self.basic_url+self.direct_query_addr, self.jsessionid,endpoint.table)
        print("[DEBUG] Starting exfiltration tests...")
        self._fuzz_endpoint_with_exfiltration(endpoint)
        print("[DEBUG] Starting corruption tests...")
        self._fuzz_endpoint_with_corruption(endpoint)
        end_time: float = time.time()
        execution_time: float = end_time - start_time
        self.vulnerability_report.set_exec_time_of_last_endpoint(execution_time)
        print(f"[DEBUG] Endpoint {endpoint.name} complete. Execution time: {execution_time:.2f}s")



    def _fuzz_endpoint_with_exfiltration(self, endpoint: APIEndpoint) -> None:
        print(f"[DEBUG] Testing exfiltration on endpoint: {endpoint.name}")
        url: str = self.basic_url + endpoint.suffix
        print(f"[DEBUG] Full URL: {url}")
        legit_json_result = self._get_legit_result(url, endpoint)
        print(f"[DEBUG] Legitimate result baseline length: {len(legit_json_result)}")
        
        print("[DEBUG] Setting up table configuration...")
        table_settings_dict = {table.table_name: table for table in self.db_table_settings}
        print(f"[DEBUG] Available tables: {', '.join(table_settings_dict.keys())}")
        
        for fuzzed_parameter in endpoint.parameters:
            print(f"\n[DEBUG] Fuzzing parameter: {fuzzed_parameter.name}")
            print(f"[DEBUG] Default input value: {fuzzed_parameter.default_input}")
            queries = qlg.generate_tainted_queries_for_exfiltration(fuzzed_parameter.default_input, table_settings_dict, endpoint.table)
            print(f"[DEBUG] Generated {len(queries)} test queries")
            
            for i, tainted_query in enumerate(queries, 1):
                print(f"[DEBUG] Testing query {i}/{len(queries)}: {tainted_query}")
                tainted_result = self._get_tainted_result(url, endpoint, fuzzed_parameter, tainted_query)
                print(f"[DEBUG] Result length: {len(tainted_result)}")
                if tainted_result != '[]' and tainted_result != legit_json_result:
                    print(f"[DEBUG] Vulnerability detected! Result differs from baseline")
                    self.vulnerability_report.add_vuln_to_last_endpoint( Vulnerability("exfiltration", endpoint.name, fuzzed_parameter.default_input, tainted_query, legit_json_result, tainted_result) )



    def _fuzz_endpoint_with_corruption(self, endpoint: APIEndpoint) -> None:
        print(f"[DEBUG] Testing corruption on endpoint: {endpoint.name}")
        url = self.basic_url + endpoint.suffix
        direct_url: str = self.basic_url + self.direct_query_addr
        sane_db_snapshot = self.get_db_snapshot()
        table_settings_dict = {table.table_name: table for table in self.db_table_settings}
        
        for fuzzed_parameter in endpoint.parameters:
            print(f"[DEBUG] Fuzzing parameter: {fuzzed_parameter.name}")
            for tainted_query in qlg.generate_tainted_queries_for_corruption(fuzzed_parameter.default_input, table_settings_dict, endpoint.table):
                print(f"[DEBUG] Testing query: {tainted_query}")
                self._get_tainted_result(url, endpoint, fuzzed_parameter, tainted_query)
                new_db_snapshot = self.get_db_snapshot()
                if not sane_db_snapshot == new_db_snapshot:
                    print(f"[DEBUG] Found corruption vulnerability!")
                    self.vulnerability_report.add_vuln_to_last_endpoint( Vulnerability("corruption", endpoint.name, fuzzed_parameter.default_input, tainted_query, sane_db_snapshot, new_db_snapshot) )
                    wg_interface.recreate_database(direct_url, self.jsessionid,endpoint.table)


    def _get_legit_result(self, url: str, endpoint: APIEndpoint) -> str:
        print(f"[DEBUG] Getting legitimate result for endpoint: {endpoint.name}")
        data = self._get_default_data_for_post_call(endpoint.parameters)
        return self._get_result(url, data, endpoint.name)
    


    def _get_tainted_result(self, url: str, endpoint: APIEndpoint, fuzzed_parameter: Parameter, tainted_query: str) -> str:
        print(f"[DEBUG] Testing endpoint {endpoint.name} with tainted parameter {fuzzed_parameter.name}")
        parameters: list[Parameter] = endpoint.parameters
        param_data = self._get_default_data_for_post_call(parameters)
        param_data[fuzzed_parameter.name] = tainted_query
        return self._get_result(url, param_data, endpoint.name)



    def _get_result(self, url: str, data: Dict[str, Any], endpoint_name: str) -> str:
        print(f"[DEBUG] Sending request to {url}")
        print(f"[DEBUG] Request data: {json.dumps(data, indent=2)}")
        response = wg_interface.query_webgoat(url, data, self.jsessionid, endpoint_name)
        print(f"[DEBUG] Response length: {len(response)}")
        return response

    

    def get_db_snapshot(self):
        print("[DEBUG] Taking database snapshot...")
        direct_url: str = self.basic_url + self.direct_query_addr
        result = wg_interface.wg_direct_database_check(direct_url, self.direct_query, self.jsessionid)
        print(f"[DEBUG] Snapshot result: {result[:100]}...")
        return result
    


    def _get_default_data_for_post_call(self, parameters: list[Parameter]) -> Dict[str, str]:
        return {param.name: param.default_input for param in parameters}
    


    def _get_default_input(self, parameter: Parameter):
        return parameter.default_input
    
    

    def _get_cookies(self) -> Dict[str, str]:
        return {'JSESSIONID': self.jsessionid}
