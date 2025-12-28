def run(self, user_input: str, memory=None, action_context_props=None):

    ... existing code ...
    
    # Initialize capabilities
    for capability in self.capabilities:
        capability.init(self, action_context)
        
    while True:
        # Start of loop capabilities
        can_start_loop = reduce(lambda a, c: c.start_agent_loop(self, action_context),
                              self.capabilities, False)

        ... existing code ...
        
        # Construct prompt with capability modifications
        prompt = reduce(lambda p, c: c.process_prompt(self, action_context, p),
                      self.capabilities, base_prompt)

        ... existing code ...
        
        # Process response with capabilities
        response = reduce(lambda r, c: c.process_response(self, action_context, r),
                        self.capabilities, response)

        ... existing code ...
        
        # Process action with capabilities
        action = reduce(lambda a, c: c.process_action(self, action_context, a),
                      self.capabilities, action)
        
        ... existing code ...
        
        # Process result with capabilities
        result = reduce(lambda r, c: c.process_result(self, action_context, response,
                                                     action_def, action, r),
                       self.capabilities, result)

        ... existing code ...
        
        # End of loop capabilities
        for capability in self.capabilities:
            capability.end_agent_loop(self, action_context)

class Capability:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def init(self, agent, action_context: ActionContext) -> dict:
        """Called once when the agent starts running."""
        pass

    def start_agent_loop(self, agent, action_context: ActionContext) -> bool:
        """Called at the start of each iteration through the agent loop."""
        return True

    def process_prompt(self, agent, action_context: ActionContext, 
                      prompt: Prompt) -> Prompt:
        """Called right before the prompt is sent to the LLM."""
        return prompt

    def process_response(self, agent, action_context: ActionContext, 
                        response: str) -> str:
        """Called after getting a response from the LLM."""
        return response

    def process_action(self, agent, action_context: ActionContext, 
                      action: dict) -> dict:
        """Called after parsing the response into an action."""
        return action

    def process_result(self, agent, action_context: ActionContext,
                      response: str, action_def: Action,
                      action: dict, result: any) -> any:
        """Called after executing the action."""
        return result

    def process_new_memories(self, agent, action_context: ActionContext,
                           memory: Memory, response, result,
                           memories: List[dict]) -> List[dict]:
        """Called when new memories are being added."""
        return memories

    def end_agent_loop(self, agent, action_context: ActionContext):
        """Called at the end of each iteration through the agent loop."""
        pass

    def should_terminate(self, agent, action_context: ActionContext,
                        response: str) -> bool:
        """Called to check if the agent should stop running."""
        return False

    def terminate(self, agent, action_context: ActionContext) -> dict:
        """Called when the agent is shutting down."""
        pass

# Example from the agent loop
prompt = reduce(lambda p, c: c.process_prompt(self, action_context, p),
               self.capabilities, base_prompt)

class Agent:
    def __init__(self,
                 goals: List[Goal],
                 agent_language: AgentLanguage,
                 action_registry: ActionRegistry,
                 generate_response: Callable[[Prompt], str],
                 environment: Environment,
                 capabilities: List[Capability] = [],
                 max_iterations: int = 10,
                 max_duration_seconds: int = 180):
        """
        Initialize an agent with its core GAME components and capabilities.
        
        Goals, Actions, Memory, and Environment (GAME) form the core of the agent,
        while capabilities provide ways to extend and modify the agent's behavior.
        
        Args:
            goals: What the agent aims to achieve
            agent_language: How the agent formats and parses LLM interactions
            action_registry: Available tools the agent can use
            generate_response: Function to call the LLM
            environment: Manages tool execution and results
            capabilities: List of capabilities that extend agent behavior
            max_iterations: Maximum number of action loops
            max_duration_seconds: Maximum runtime in seconds
        """
        self.goals = goals
        self.generate_response = generate_response
        self.agent_language = agent_language
        self.actions = action_registry
        self.environment = environment
        self.capabilities = capabilities or []
        self.max_iterations = max_iterations
        self.max_duration_seconds = max_duration_seconds

agent = Agent(
    goals=[
        Goal(name="scheduling",
             description="Schedule meetings considering current time and availability")
    ],
    agent_language=JSONAgentLanguage(),
    action_registry=registry,
    generate_response=llm.generate,
    environment=PythonEnvironment(),
    capabilities=[
        TimeAwareCapability(),
        LoggingCapability(log_level="INFO"),
        MetricsCapability(metrics_server="prometheus:9090")
    ]
)

## implementing time awareness
from datetime import datetime
from zoneinfo import ZoneInfo

class TimeAwareCapability(Capability):
    def __init__(self):
        super().__init__(
            name="Time Awareness",
            description="Allows the agent to be aware of time"
        )
        
    def init(self, agent, action_context: ActionContext) -> dict:
        """Set up time awareness at the start of agent execution."""
        # Get timezone from context or use default
        time_zone_name = action_context.get("time_zone", "America/Chicago")
        timezone = ZoneInfo(time_zone_name)
        
        # Get current time in specified timezone
        current_time = datetime.now(timezone)
        
        # Format time in both machine and human-readable formats
        iso_time = current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        human_time = current_time.strftime("%H:%M %A, %B %d, %Y")
        
        # Store time information in memory
        memory = action_context.get_memory()
        memory.add_memory({
            "type": "system",
            "content": f"""Right now, it is {human_time} (ISO: {iso_time}).
            You are in the {time_zone_name} timezone.
            Please consider the day/time, if relevant, when responding."""
        })
        
    def process_prompt(self, agent, action_context: ActionContext, 
                      prompt: Prompt) -> Prompt:
        """Update time information in each prompt."""
        time_zone_name = action_context.get("time_zone", "America/Chicago")
        current_time = datetime.now(ZoneInfo(time_zone_name))
        
        # Add current time to system message
        system_msg = (f"Current time: "
                     f"{current_time.strftime('%H:%M %A, %B %d, %Y')} "
                     f"({time_zone_name})\n\n")
        
        # Add to existing system message or create new one
        messages = prompt.messages
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = system_msg + messages[0]["content"]
        else:
            messages.insert(0, {
                "role": "system",
                "content": system_msg
            })
            
        return Prompt(messages=messages)

agent = Agent(
    goals=[Goal(name="task", description="Complete the assigned task")],
    agent_language=JSONAgentLanguage(),
    action_registry=registry,
    generate_response=llm.generate,
    environment=PythonEnvironment(),
    capabilities=[
        TimeAwareCapability()
    ]
)

# Example conversation
agent.run("Schedule a team meeting for today")

# Agent response might include:
"Since it's already 5:30 PM on Friday, I recommend scheduling the meeting 
for Monday morning instead. Would you like me to look for available times 
on Monday?"

class EnhancedTimeAwareCapability(TimeAwareCapability):
    def process_action(self, agent, action_context: ActionContext, 
                      action: dict) -> dict:
        """Add timing information to action results."""
        # Add execution time to action metadata
        action["execution_time"] = datetime.now(
            ZoneInfo(action_context.get("time_zone", "America/Chicago"))
        ).isoformat()
        return action
        
    def process_result(self, agent, action_context: ActionContext,
                      response: str, action_def: Action,
                      action: dict, result: any) -> any:
        """Add duration information to results."""
        if isinstance(result, dict):
            result["action_duration"] = (
                datetime.now(ZoneInfo(action_context.get("time_zone"))) -
                datetime.fromisoformat(action["execution_time"])
            ).total_seconds()
        return result