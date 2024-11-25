from dataclasses import dataclass, asdict, field
from typing import List
import json

@dataclass
class Vulnerability:

  exfiltration_or_corruption: str
  name_of_lesson: str
  legit_query: str
  tainted_query: str
  expected: dict
  obtained: dict

@dataclass
class Endpoint_review:

  vulnerability_list: List[Vulnerability] = field(default_factory=list)
  execution_time: float = 0.


class Vulnerability_report:

  endpoint_list: List[Endpoint_review]
  global_execution_time: float


  def __init__(self):
    self.endpoint_list = []



  def add_new_endpoint(self):
    self.endpoint_list.append(Endpoint_review())



  def add_vuln_to_last_endpoint(self, new_vulnerability: Vulnerability) -> None:
    self.endpoint_list[-1].vulnerability_list.append(new_vulnerability)



  def write_report_to_file(self, report_name="dynamic_analysis_report") -> None:
    report_name += ".json"
    dict_for_json = self.build_dict_for_json()
    with open(report_name, "w") as json_file:
      json.dump(dict_for_json, json_file, indent=4, sort_keys=True)



  def set_exec_time_of_last_endpoint(self, new_execution_time: float) -> None:
    self.endpoint_list[-1].execution_time = new_execution_time



  def build_dict_for_json(self) -> dict:
    return { "execution_time": self.global_execution_time,
          "vulnerabilities_found": [asdict(vuln) for vuln in self.endpoint_list] }