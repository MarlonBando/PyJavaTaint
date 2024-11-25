from dataclasses import dataclass, asdict
import json

@dataclass
class Vulnerability:

  exfiltration_or_corruption: str
  name_of_lesson: str
  legit_query: str
  tainted_query: str
  expected: dict
  obtained: dict

class Vulnerability_report:

  vulnerabilities: list[Vulnerability]

  def __init__(self):
    self.vulnerabilities = []

  def add_vulnerability(self, new_vulnerability: Vulnerability):
    self.vulnerabilities.append(new_vulnerability)

  def write_report_to_file(self, report_name="dynamic_analysis_report"):
    report_name += ".json"
    vulnerabilities_as_dicts = [asdict(vuln) for vuln in self.vulnerabilities]
    with open(report_name, "w") as json_file:
      json.dump(vulnerabilities_as_dicts, json_file, indent=4, sort_keys=True)