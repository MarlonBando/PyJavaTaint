from constant import Settings
import query_list_generator as qlg
from fuzzer import Fuzzer

settings = Settings()

fuzzer = Fuzzer(settings)
fuzzer.fuzz_endpoint("Lesson 2")