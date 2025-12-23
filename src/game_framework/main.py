import json
import time
import traceback
from litellm import completion
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any
import os
from framework import (
    Agent,
    AgentFunctionCallingActionLanguage,
    Action,
    ActionRegistry,
    Environment,
    Goal,
    generate_response
)

def main():
        # Define the agent's goals
    goals = [
        Goal(priority=1, name="Gather Information", description="Read only the setup.py file in the project"),
        Goal(priority=1, name="Terminate", description="Call the terminate call when you have read the setup.py file "
                                                       "and provide the content of the setup.py in the terminate message")
    ]

    # Define the agent's language
    agent_language = AgentFunctionCallingActionLanguage()

    def read_project_file(name: str) -> str:
        with open(name, "r") as f:
            return f.read()

    def list_project_files() -> List[str]:
        return sorted([file for file in os.listdir(".") if file.endswith(".py")])


    # Define the action registry and register some actions
    action_registry = ActionRegistry()
    action_registry.register(Action(
        name="list_project_files",
        function=list_project_files,
        description="Lists all files in the project.",
        parameters={},
        terminal=False
    ))
    action_registry.register(Action(
        name="read_project_file",
        function=read_project_file,
        description="Reads a file from the project.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        },
        terminal=False
    ))
    action_registry.register(Action(
        name="terminate",
        function=lambda message: f"{message}\nTerminating...",
        description="Terminates the session and prints the message to the user.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": []
        },
        terminal=True
    ))

    # Define the environment
    environment = Environment()

    # Create an agent instance
    agent = Agent(goals, agent_language, action_registry, generate_response, environment)

    # Run the agent with user input
    user_input = "Write a README for this project."
    final_memory = agent.run(user_input)

    # Print the final memory
    print(final_memory.get_memories())

if __name__ == "__main__":
    main()