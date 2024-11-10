from src.JVM_emulator import JVM_emulator
from src.utils.full_path import *

# file_path: str = './jpamb_examples/json_files/Simple.json'
# method_name: str = 'divideByZero'

file_path: str = get_full_path('webgoat_code_examples/json_files/SqlInjectionLesson3.json')
method_name: str = ''

jvm_emulator: JVM_emulator = JVM_emulator(file_path, method_name)
jvm_emulator.run()