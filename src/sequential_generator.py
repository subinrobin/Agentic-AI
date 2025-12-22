import re
import json
from llm_utils import generate_response

OUTPUT_FILE = "src/output_function.py"

def extract_python_code(text: str) -> str:
    """Extract Python code blocks from LLM response."""
    pattern = r"```python\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[-1].strip()  # Return the last (most updated) code block
    return text.strip()

def main():
    print("\n🚀 Sequential Function Generator Starting...")
    
    # Initialize conversation
    messages = [
        {"role": "system", "content": "You are an expert Python developer. You write clean, functional code and follow PEP 8 standards."}
    ]

    # --- Step 1: Basic Function Generation ---
    user_input = input("\n[Step 1] What function would you like to create? ")
    prompt_1 = f"Please write a basic Python function for the following requirement: {user_input}. Provide the code in a markdown python block."
    
    messages.append({"role": "user", "content": prompt_1})
    print("\n--- Generating Basic Function ---")
    response_1 = generate_response(messages)
    print(response_1)
    messages.append({"role": "assistant", "content": response_1})
    
    basic_code = extract_python_code(response_1)
    print("\nBasic Code Generated:\n")
    print(basic_code)

    # --- Step 2: Documentation ---
    prompt_2 = (
        "Now, add comprehensive documentation to this function. Include:\n"
        "- Function description\n"
        "- Parameter descriptions\n"
        "- Return value description\n"
        "- Example usage\n"
        "- Edge cases\n"
        "Return the updated function in a markdown python block."
    )
    
    messages.append({"role": "user", "content": prompt_2})
    print("\n--- Adding Documentation ---")
    response_2 = generate_response(messages)
    messages.append({"role": "assistant", "content": response_2})
    
    documented_code = extract_python_code(response_2)
    print("\nDocumented Code Generated:\n")
    print(documented_code)

    # --- Step 3: Unittest Generation ---
    prompt_3 = (
        "Finally, add a suite of test cases for this function using the Python unittest framework. "
        "Include tests for basic functionality, edge cases, and error handling. "
        "Provide a single script that includes both the function and the test suite, "
        "and ensures the tests run if the script is executed directly (`if __name__ == '__main__': unittest.main()`)."
    )
    
    messages.append({"role": "user", "content": prompt_3})
    print("\n--- Generating Test Cases ---")
    response_3 = generate_response(messages)
    messages.append({"role": "assistant", "content": response_3})
    
    final_script = extract_python_code(response_3)
    
    # --- Persistence ---
    with open(OUTPUT_FILE, "w") as f:
        f.write(final_script)
    
    print(f"\n✅ Final version saved to {OUTPUT_FILE}")
    print("\nSuggested next step: Run 'python3 src/output_function.py' to verify the tests.")

if __name__ == "__main__":
    main()
