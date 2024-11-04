from JVM_emulator import JVM_emulator

file_path: str = './jpamb_examples/json_files/Simple.json'
method_name: str = 'divideByZero'

jvm_emulator: JVM_emulator = JVM_emulator(file_path, method_name)
jvm_emulator.run()