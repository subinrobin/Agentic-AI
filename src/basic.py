from llm_utils import generate_response


from prompts import (
    get_base64_prompt_messages,
    get_support_prompt_messages,
    get_engineer_prompt_messages,
    get_customer_service_prompt_messages
)

prompts = [
    ("Base64", get_base64_prompt_messages),
    ("Support", get_support_prompt_messages),
    ("Engineer", get_engineer_prompt_messages),
    ("Customer Service", get_customer_service_prompt_messages)
]

for label, get_messages in prompts:
    input(f"Press Enter to execute {label} prompt...")
    messages = get_messages()
    response = generate_response(messages)
    print(f"{label} Response:\n{response}\n")
    