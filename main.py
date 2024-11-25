from objects import Settings
import query_list_generator as qlg
from fuzzer import Fuzzer
import sys

settings = Settings()
fuzzer = Fuzzer(settings)

if len(sys.argv) <= 2:
  fuzzer.fuzz_all_endpoints()
elif len(sys.argv) == 3:
  lesson_name: str = sys.argv[2]
  fuzzer.fuzz_single_endpoint(lesson_name)
else:
  raise ValueError("The fuzzer only accets one argument")

