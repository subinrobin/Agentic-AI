@register_tool()
def call_agent(action_context: ActionContext, 
               agent_name: str, 
               task: str) -> dict:
    """
    Invoke another agent to perform a specific task.
    
    Args:
        action_context: Contains registry of available agents
        agent_name: Name of the agent to call
        task: The task to ask the agent to perform
        
    Returns:
        The result from the invoked agent's final memory
    """
    # Get the agent registry from our context
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        raise ValueError("No agent registry found in context")
    
    # Get the agent's run function from the registry
    agent_run = agent_registry.get_agent(agent_name)
    if not agent_run:
        raise ValueError(f"Agent '{agent_name}' not found in registry")
    
    # Create a new memory instance for the invoked agent
    invoked_memory = Memory()
    
    try:
        # Run the agent with the provided task
        result_memory = agent_run(
            user_input=task,
            memory=invoked_memory,
            # Pass through any needed context properties
            action_context_props={
                'auth_token': action_context.get('auth_token'),
                'user_config': action_context.get('user_config'),
                # Don't pass agent_registry to prevent infinite recursion
            }
        )
        
        # Get the last memory item as the result
        if result_memory.items:
            last_memory = result_memory.items[-1]
            return {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "No result content")
            }
        else:
            return {
                "success": False,
                "error": "Agent failed to run."
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@register_tool()
def check_availability(
    action_context: ActionContext,
    attendees: List[str],
    start_date: str,
    end_date: str,
    duration_minutes: int,
    _calendar_api_key: str
) -> List[Dict]:
    """Find available time slots for all attendees."""
    return calendar_service.find_available_slots(...)

@register_tool()
def create_calendar_invite(
    action_context: ActionContext,
    title: str,
    description: str,
    start_time: str,
    duration_minutes: int,
    attendees: List[str],
    _calendar_api_key: str
) -> Dict:
    """Create and send a calendar invitation."""
    return calendar_service.create_event(...)

scheduler_agent = Agent(
    goals=[
        Goal(
            name="schedule_meetings",
            description="""Schedule meetings efficiently by:
            1. Finding times that work for all attendees
            2. Creating and sending calendar invites
            3. Handling any scheduling conflicts"""
        )
    ],
...
)

@register_tool()
def get_project_status(
    action_context: ActionContext,
    project_id: str,
    _project_api_token: str
) -> Dict:
    """Retrieve current project status information."""
    return project_service.get_status(...)

@register_tool()
def update_project_log(
    action_context: ActionContext,
    entry_type: str,
    description: str,
    _project_api_token: str
) -> Dict:
    """Record an update in the project log."""
    return project_service.log_update(...)

@register_tool()
def call_agent(
    action_context: ActionContext,
    agent_name: str,
    task: str
) -> Dict:
    """Delegate to a specialist agent."""
    # Implementation as shown in previous tutorial

project_manager = Agent(
    goals=[
        Goal(
            name="project_oversight",
            description="""Manage project progress by:
            1. Getting the current project status
            2. Identifying when meetings are needed if there are issues in the project status log
            3. Delegating meeting scheduling to the "scheduler_agent" to arrange the meeting
            4. Recording project updates and decisions"""
        )
    ],
    ...
)

class AgentRegistry:
    def __init__(self):
        self.agents = {}
        
    def register_agent(self, name: str, run_function: callable):
        """Register an agent's run function."""
        self.agents[name] = run_function
        
    def get_agent(self, name: str) -> callable:
        """Get an agent's run function by name."""
        return self.agents.get(name)

# When setting up the system
registry = AgentRegistry()
registry.register_agent("scheduler_agent", scheduler_agent.run)

# Include registry in action context
action_context = ActionContext({
    'agent_registry': registry,
    # Other shared resources...
})