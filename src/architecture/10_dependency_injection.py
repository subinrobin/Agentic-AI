@register_tool(
    description="Analyze code quality and suggest improvements",
    tags=["code_quality"]
)
def analyze_code_quality(code: str) -> str:
    """Review code quality and suggest improvements."""
    # But how do we access the conversation history?
    # We can't just import the agent instance - that would create tight coupling
    
    return prompt_expert(
        description_of_expert="""
        Senior software architect reviewing code quality
        """,
        prompt=f"Review this code:\n{code}"
    )

class ActionContext:
    def __init__(self, properties: Dict=None):
        self.context_id = str(uuid.uuid4())
        self.properties = properties or {}

    def get(self, key: str, default=None):
        return self.properties.get(key, default)

    def get_memory(self):
        return self.properties.get("memory", None)

@register_tool(
    description="Analyze code quality and suggest improvements",
    tags=["code_quality"]
)
def analyze_code_quality(action_context: ActionContext, code: str) -> str:
    """Review code quality and suggest improvements."""
    # Get memory to understand the code's context
    memory = action_context.get_memory()
    
    # Extract relevant history
    development_context = []
    for mem in memory.get_memories():
        if mem["type"] == "user":
            development_context.append(f"User: {mem['content']}")
        # Hypotethical scenario where our agent includes the phrase "Here's the implementation" when it generates code
        elif mem["type"] == "assistant" and "Here's the implementation" in mem["content"]:
            development_context.append(f"Implementation Decision: {mem['content']}")
    
    # Create review prompt with full context
    review_prompt = f"""Review this code in the context of its development history:

Development History:
{'\n'.join(development_context)}

Current Implementation:
{code}

Analyze:
1. Does the implementation meet all stated requirements?
2. Are all constraints and considerations from the discussion addressed?
3. Have any requirements or constraints been overlooked?
4. What improvements could make the code better while staying within the discussed parameters?
"""
    
    generate_response = action_context.get("llm")
    return generate_response(review_prompt)


## Handling Session or Request-Specific Dependencies
@register_tool(
    description="Update code review status in project management system",
    tags=["project_management"]
)
def update_review_status(action_context: ActionContext, 
                        review_id: str, 
                        status: str) -> dict:
    """Update the status of a code review in the project system."""
    # Get the authentication token for this specific request
    auth_token = action_context.get("auth_token")
    if not auth_token:
        raise ValueError("Authentication token not found in context")
    
    # Make authenticated request
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"https://...someapi.../reviews/{review_id}/status",
        headers=headers,
        json={"status": status}
    )
    
    if response.status_code != 200:
        raise ValueError(f"Failed to update review status: {response.text}")
        
    return {"status": "updated", "review_id": review_id}

def run(self, user_input: str, memory=None, action_context_props=None):
    """Execute the agent loop."""
    memory = memory or Memory()
    
    # Create context with all necessary resources
    action_context = ActionContext({
        'memory': memory,
        'llm': self.generate_response,
        # Request-specific auth
        **action_context_props
    })
    
    while True:
        prompt = self.construct_prompt(action_context, self.goals, memory)
        response = self.prompt_llm_for_action(action_context, prompt)
        result = self.handle_agent_response(action_context, response)
        
        if self.should_terminate(action_context, response):
            break

...
# Run the agent and create custom context for the action to 
# pass to tools that need it
some_agent.run("Update the project status...", 
               memory=..., 
               # Pass request-specific auth token
               action_context_props={"auth_token": "my_auth_token"})