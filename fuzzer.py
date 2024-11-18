import random
import string
import caller 
import dictionnary_generator

  
def inject_data(query):
    """Inject a query via the API using the method from caller.py."""
    try:
        # Define the URL and data (you may need to adjust these based on fuzzed inputs)
        url = 'http://localhost:8080/WebGoat/SqlInjection/attack4?username=mathias'  # Example URL for SQL injection
        data = {"query": query}
        
        # Call the api_call method from caller.py to send the fuzzed query
        caller.api_call(url, data, 'inject_result.json')
        
    except Exception as e:
        print(f"Error injecting data: {e}")

def verify_state(expected_filename):
    """Verify the state by checking the output file after injection."""
    try:
        # Check the output file for expected results
        with open(expected_filename, 'r') as f:
            output = f.read()
            if "expected_value" in output:
                print("State verified successfully!")
            else:
                print("State verification failed.")
    except Exception as e:
        print(f"Error verifying state: {e}")

def fuzz(fuzz_dict):
    """Fuzz the API calls using the provided dictionary."""
    for operation, values in fuzz_dict.items():
        for value in values:
            if operation == "inject_data":
                inject_data(value)
            elif operation == "verify_state":
                verify_state(value)

# Call the fuzzer with the dictionary
injection_queries = dictionnary_generator.get_injection_queries()
fuzz(injection_queries)
  