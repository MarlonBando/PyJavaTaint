from objects import Settings
import query_list_generator as qlg
from fuzzer import Fuzzer
import sys
import argparse

print("Starting PyJavaTaint fuzzer...")

# Set up argument parser
parser = argparse.ArgumentParser(description='PyJavaTaint Fuzzer')
parser.add_argument('-e', '--endpoint', 
           help='Endpoint name to fuzz. If omitted, all endpoints will be fuzzed. Available endpoints can be found in settings.yaml',
           required=False)

args = parser.parse_args()
settings = Settings()
fuzzer = Fuzzer(settings)

if args.endpoint:
    print(f"  > Fuzzing single endpoint: {args.endpoint}")
    fuzzer.fuzz_single_endpoint(args.endpoint)
else:
    print("  > Fuzzing all endpoints...")
    fuzzer.fuzz_all_endpoints()