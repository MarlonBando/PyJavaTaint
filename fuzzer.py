from constant import Settings, APIEndpoint, Parameter
import requests
import query_list_generator as qlg
from typing import Dict, Any
import json

class Fuzzer:



    def __init__(self, settings: Settings):
        self.basic_url: str = settings.URL
        self.jessionid: str = settings.JSESSIONID
        self.endpoints: list = settings.api_endpoints
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

        input_type: str = endpoint.parameters[0].type # TODO : take into account case of several queries
        if input_type == 'query': 
            self._fuzz_with_exfiltration_queries(endpoint)
            self._fuzz_with_corruption_queries(endpoint)
        elif input_type == 'string':
            self._fuzz_with_exfiltration_strings(endpoint)
            self._fuzz_with_corruption_strings(endpoint)
        else:
            raise Exception(f"The type of an endpoint's parameter can be 'string' or 'query', not{input_type}")



    def _fuzz_with_exfiltration_queries(self, endpoint: APIEndpoint) -> None:

        url: str = self.basic_url + endpoint.suffix
        legit_json_result = self._get_legit_result(url, endpoint)
        for parameter in endpoint.parameters:
            
            injectable = False
            for tainted_query in qlg.generate_tainted_queries_for_exfiltration():
                tainted_result = self._get_tainted_result(url, endpoint, parameter, tainted_query)
                if tainted_result != legit_json_result:
                    self.write_injection_to_report(endpoint, parameter, tainted_query, legit_json_result, tainted_result)
                    injectable = True
            if not injectable:
                self.fuzz_report += f'No SQL Injection found in {endpoint.name} parameter {parameter.type}'
        self.save_report()



    def _fuzz_with_corruption_queries(self, endpoint: APIEndpoint) -> None:

        url = self.basic_url + endpoint.suffix
        sane_db_snapshot = self.get_db_snapshot
        for parameter in endpoint.parameters:
            injectable = False
            for tainted_query in qlg.generate_tainted_queries_for_corruption():
                # TODO : query the DB to try and corrupt it
                new_db_snapshot = self.get_db_snapshot()
                if not self.db_snapshots_are_equal(sane_db_snapshot, new_db_snapshot):
                    # TODO : write injection to report
                    # TODO : restore the database to its sane state thanks to the snapshot
                    injectable = True
            if not injectable:
                self.fuzz_report += f'No SQL Injection found in {endpoint.name} parameter {parameter.type}'
        self.save_report()

    

    def _fuzz_with_exfiltration_strings(self, endpoint: APIEndpoint) -> None:

        url = self.basic_url + endpoint.suffix
        legit_result = self._get_legit_result(url, endpoint)
        for parameter in endpoint.parameters:
            injectable = False
            for tainted_query in qlg.generate_tainted_strings_for_exfiltration():
                tainted_result = self._get_tainted_result(url, endpoint, parameter, tainted_query)
                if tainted_result != legit_result:
                    self.write_injection_to_report(endpoint, parameter, tainted_query, legit_result, tainted_result)
                    injectable = True
            if not injectable:
                self.fuzz_report += f'No SQL Injection found in {endpoint.name} parameter {parameter.type}'
        self.save_report()



    def _fuzz_with_corruption_strings(self, endpoint: APIEndpoint) -> None:
        """ Same as function above but adapted to strings """



    def _get_legit_result(self, url: str, endpoint: APIEndpoint) -> str:
        data = self._get_data_post_call(endpoint.parameters)
        return self._get_result(url, data=data)
    


    def _get_tainted_result(self, url: str, endpoint: APIEndpoint, parameter: Parameter, tainted_query: str) -> str:
        param_data = self._get_data_post_call(endpoint.parameters)
        param_data[parameter.type] = parameter.default + tainted_query
        return self._get_result(url, param_data)



    def _get_result(self, url: str, data: Dict[str, Any]) -> str:
        response = requests.post(url, data=data,cookies=self._get_cookies())
        return self._validate_result(response)



    def _validate_result(self, response):
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            return {}
        
        response_json = json.loads(response.text)
        output = response_json.get("output", "")
        return output.replace('\n', '')
    

    def get_db_snapshot(self):
        """ Write function that stores state of db""" # TODO
    


    def db_snapshots_are_equal(db_snapshot_A, db_snapshot_B) -> bool:
        """ Compares the state of the 2 snapshots""" # TODO



    def _get_data_post_call(self, parameters: list[Parameter]) -> Dict[str, str]:
        return {param.name: param.default for param in parameters}
    


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
