from objects import Settings
import query_list_generator as qlg
from fuzzer import Fuzzer

settings = Settings()

fuzzer = Fuzzer(settings)
fuzzer.fuzz_all_endpoints()
# fuzzer.fuzz_single_endpoint("Assignment 5a")