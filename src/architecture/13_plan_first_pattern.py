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

@register_tool(tags=["planning"])
def create_plan(action_context: ActionContext,
                memory: Memory,
                action_registry: ActionRegistry) -> str:
   """Create a detailed execution plan based on the task and available tools."""

   # Get tool descriptions for the prompt
   tool_descriptions = "\n".join(
      f"- {action.name}: {action.description}"
      for action in action_registry.get_actions()
   )

   # Get relevant memory content
   memory_content = "\n".join(
      f"{m['type']}: {m['content']}"
      for m in _memory.items
      if m['type'] in ['user', 'system']
   )

   # Construct the prompt as a string
   prompt = f"""Given the task in memory and the available tools, create a detailed plan.
Think through this step by step:

1. First, identify the key components of the task
2. Consider what tools you have available
3. Break down the task into logical steps
4. For each step, specify:
   - What needs to be done
   - What tool(s) will be used
   - What information is needed
   - What the expected outcome is

Write your plan in clear, numbered steps. Each step should be specific and actionable.

Available tools:
{tool_descriptions}

Task context from memory:
{memory_content}

Create a plan that accomplishes this task effectively."""

   return prompt_llm(action_context=action_context, prompt=prompt)

# With planning
agent_response = """Plan for Sales Data Analysis:

1. Data Validation
   - Tool: validate_data()
   - Check data completeness and format
   - Ensure all required fields are present
   - Expected: Confirmation of valid dataset

2. Initial Analysis
   - Tool: analyze_data()
   - Calculate key metrics (revenue, growth)
   - Generate summary statistics
   - Expected: Basic statistical overview

3. Trend Identification
   - Tool: find_patterns()
   - Look for seasonal patterns
   - Identify sales trends
   - Expected: List of significant trends

4. Visualization
   - Tool: create_visualization()
   - Create relevant charts
   - Highlight key findings
   - Expected: Clear visual representations

5. Report Generation
   - Tool: generate_report()
   - Compile findings
   - Include visualizations
   - Expected: Comprehensive report

I'll begin with step 1: Data Validation..."""

agent = Agent(
    goals=[
        Goal(name="analysis",
             description="Analyze sales data and create a report")
    ],
    capabilities=[
        PlanFirstCapability(track_progress=True)
    ],
    # ... other agent configuration
)

result = agent.run("Analyze our Q4 sales data and create a report")