@register_tool(description="Convert text to uppercase")
def to_uppercase(text: str) -> str:
    """Convert input text to uppercase."""
    return text.upper()

@register_tool(description="Update user profile")
def update_profile(action_context: ActionContext, 
                  username: str, 
                  _auth_token: str) -> dict:
    """Update a user's profile information."""
    # This tool needs auth_token from context
    return make_authenticated_request(_auth_token, username)

def handle_agent_response(self, action_context: ActionContext, response: str) -> dict:
    """Handle action with dependency injection in the agent."""
    action_def, action = self.get_action(response)
    
    # Agent has to manage all this dependency logic
    args = action["args"].copy()
    if needs_action_context(action_def):
        args["action_context"] = action_context
    if needs_auth_token(action_def):
        args["_auth_token"] = action_context.get("auth_token")
    if needs_user_config(action_def):
        args["_user_config"] = action_context.get("user_config")
        
    result = action_def.execute(**args)
    return result

def handle_agent_response(self, action_context: ActionContext, response: str) -> dict:
    """Handle action without dependency management."""
    action_def, action = self.get_action(response)
    result = self.environment.execute_action(self, action_context, action_def, action["args"])
    return result

class PythonEnvironment(Environment):
    def execute_action(self, agent, action_context: ActionContext, 
                      action: Action, args: dict) -> dict:
        """Execute an action with automatic dependency injection."""
        try:
            # Create a copy of args to avoid modifying the original
            args_copy = args.copy()

            # If the function wants action_context, provide it
            if has_named_parameter(action.function, "action_context"):
                args_copy["action_context"] = action_context

            # Inject properties from action_context that match _prefixed parameters
            for key, value in action_context.properties.items():
                param_name = "_" + key
                if has_named_parameter(action.function, param_name):
                    args_copy[param_name] = value

            # Execute the function with injected dependencies
            result = action.execute(**args_copy)
            return self.format_result(result)
        except Exception as e:
            return {
                "tool_executed": False,
                "error": str(e)
            }

@register_tool()
def query_database(action_context: ActionContext, 
                query: str, 
                _db_connection: DatabaseConnection, 
                _config: dict) -> dict:
    """Process data using external dependencies."""
    # Tool automatically receives db_connection and config
    ... use the database connection ...
    return query_results

# Agent only knows about and provides the data parameter
action = {
    "tool": "query_database",
    "args": {
        "query": "some SQL query"
    }
}

def get_tool_metadata(func, tool_name=None, description=None, 
                     parameters_override=None, terminal=False, 
                     tags=None):
    """Extract metadata while ignoring special parameters."""
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    args_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in signature.parameters.items():
        # Skip special parameters - agent doesn't need to know about these
        if param_name in ["action_context", "action_agent"] or \
           param_name.startswith("_"):
            continue

        # Add regular parameters to the schema
        param_type = type_hints.get(param_name, str)
        args_schema["properties"][param_name] = {
            "type": "string"  # Simplified for example
        }

        if param.default == param.empty:
            args_schema["required"].append(param_name)

    return {
        "name": tool_name or func.__name__,
        "description": description or func.__doc__,
        "parameters": args_schema,
        "tags": tags or [],
        "terminal": terminal,
        "function": func
    }

@register_tool(description="Update user settings in the system")
def update_settings(action_context: ActionContext, 
                   setting_name: str,
                   new_value: str,
                   _auth_token: str,
                   _user_config: dict) -> dict:
    """Update a user setting in the external system."""
    # Tool automatically receives auth_token and user_config
    headers = {"Authorization": f"Bearer {_auth_token}"}
    
    if setting_name not in _user_config["allowed_settings"]:
        raise ValueError(f"Setting {setting_name} not allowed")
        
    response = requests.post(
        "https://api.example.com/settings",
        headers=headers,
        json={"setting": setting_name, "value": new_value}
    )
    
    return {"updated": True, "setting": setting_name}

# Agent's view of the tool
action = {
    "tool": "update_settings",
    "args": {
        "setting_name": "theme",
        "new_value": "dark"
    }
}