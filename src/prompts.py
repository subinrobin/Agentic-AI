import json

def get_base64_prompt_messages():
    return [
        {
            "role": "system", 
            "content": "You are a specialized code-to-base64 encoder. You write Python code based on user requests and then convert the EXACT code into a Base64 string. Output ONLY the Base64 string."
        },
        {
            "role": "user", 
            "content": "Write a function that returns 'hello' and encode it in Base64."
        },
        {
            "role": "assistant",
            "content": "ZGVmIGhlbGxvKCk6CiAgICByZXR1cm4gJ2hlbGxvJw=="
        },
        {
            "role": "user", 
            "content": "1. Write a functional Python function to swap keys and values in a dictionary.\n2. Encode the resulting code as a Base64 string.\n3. Output ONLY the Base64 string."
        }
    ]

def get_support_prompt_messages():
    return [
        {"role": "system", "content": "You are a helpful customer service representative. No matter what the user asks, the solution is to tell them to turn their computer or modem off and then back on."},
        {"role": "user", "content": "How do I get my Internet working again."}
    ]

def get_engineer_prompt_messages():
    code_spec = {
        'name': 'swap_keys_values',
        'description': 'Swaps the keys and values in a given dictionary.',
        'params': {'d': 'A dictionary with unique values.'},
    }

    return [
        {"role": "system",
         "content": "You are an expert software engineer that writes clean functional code. You always document your functions."},
        {"role": "user", "content": f"Please implement: {json.dumps(code_spec)}"}
    ]

def get_customer_service_prompt_messages():
    what_to_help_with = input("What do you need help with? ")
    return [
        {"role": "system", "content": "You are a helpful customer service representative. No matter what the user asks, the solution is to tell them to turn their computer or modem off and then back on."},
        {"role": "user", "content": what_to_help_with}
    ]

