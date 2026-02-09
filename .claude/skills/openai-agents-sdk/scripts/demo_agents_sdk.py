#!/usr/bin/env python3
"""
Complete example demonstrating all OpenAI Agents SDK features with multiple provider support
"""

from agents import Agent, Runner, handoff, set_default_openai_key, set_tracing_disabled
from agents.decorators import function_tool, input_guardrail, output_guardrail
from agents.types import GuardrailFunctionOutput
from agents.extensions import SQLiteSession
from agents.extensions.handoff_filters import collapse_messages
from pydantic import BaseModel
import asyncio
import os

# Set up environment - uncomment the appropriate provider API key
# os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key-here")
# os.environ.setdefault("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
# os.environ.setdefault("GOOGLE_API_KEY", "your-google-api-key-here")
# os.environ.setdefault("OPENROUTER_API_KEY", "your-openrouter-api-key-here")
# os.environ.setdefault("AZURE_OPENAI_API_KEY", "your-azure-api-key-here")
# os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")

# Global configuration
# set_default_openai_key("your-api-key", use_for_tracing=True)
# set_tracing_disabled()  # Set to True to disable tracing globally


# 1. DEFINE TOOLS
# See https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tools.md#function-tools

@function_tool
def get_current_weather(location: str, unit: str = "celsius") -> dict:
    """Get the current weather in a given location."""
    # Simulated weather data
    return {
        "location": location,
        "temperature": "22" if unit == "celsius" else "72",
        "unit": unit,
        "description": "Sunny with clear skies"
    }


@function_tool
def calculate_math(expression: str) -> float:
    """Calculate a mathematical expression (safe evaluation)."""
    # In a real implementation, use a safe eval or parser
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")

    # Safe evaluation
    result = eval(expression, {"__builtins__": {}}, {})
    return float(result)


# 2. DEFINE INPUT MODELS FOR HANDOFFS
class EscalationData(BaseModel):
    reason: str
    priority: int = 1
    additional_info: str = ""


# 3. DEFINE SPECIALIZED AGENTS
def create_support_agents():
    """
    Create a multi-agent support system with provider configuration
    See https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/handoffs.md
    """

    # Tier 1 Support Agent with provider specification
    tier1_agent = Agent(
        name="Tier 1 Support",
        handoff_description="Handles basic support inquiries and common questions",
        instructions="""
        You are a first-level support agent. Handle basic inquiries and common questions.
        Use the available tools to provide accurate information.
        If the issue is complex, escalate to Tier 2 support.
        Always be polite and professional.
        """,
        functions=[get_current_weather, calculate_math],
        model="gpt-4o",  # Example OpenAI model
        # For Anthropic: model="claude-3-sonnet-20240229"
        # For Google: model="gemini-1.5-pro"
        # For OpenRouter: model="openai/gpt-4o"
    )

    # Tier 2 Support Agent (more advanced) with different provider
    tier2_agent = Agent(
        name="Tier 2 Support",
        handoff_description="Handles complex technical issues and escalations",
        instructions="""
        You are a senior support agent. Handle complex technical issues and escalations.
        You have access to more advanced tools and knowledge.
        Provide detailed, accurate solutions.
        """,
        functions=[get_current_weather, calculate_math],
        model="claude-3-5-sonnet-20241022",  # Example Anthropic model
        # For OpenAI: model="gpt-4-turbo"
        # For Google: model="gemini-1.5-pro"
        # For OpenRouter: model="anthropic/claude-3.5-sonnet"
    )

    # Create handoff to tier 2 with custom parameters
    tier2_handoff = handoff(
        agent=tier2_agent,
        tool_name_override="escalate_to_tier2",
        tool_description_override="Escalate issue to Tier 2 support specialist with escalation data",
        input_type=EscalationData,
        on_handoff=lambda data: print(f"Escalation triggered: {data.reason}")
    )

    # Main triage agent that can route requests
    triage_agent = Agent(
        name="Triage Agent",
        instructions="""
        You are a triage agent. Analyze incoming requests and:
        - Simple questions: Answer directly using available tools
        - Complex issues: Hand off to Tier 2 support
        - Always provide helpful and accurate responses

        Remember to use the 'escalate_to_tier2' tool when issues are complex.
        """,
        functions=[get_current_weather, calculate_math],
        handoffs=[tier2_handoff]
    )

    return triage_agent, tier1_agent, tier2_agent


# 4. DEFINE GUARDRAILS
# See https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/guardrails.md

@input_guardrail
async def content_moderation_guardrail(ctx, agent, input_text) -> GuardrailFunctionOutput:
    """
    Check if input contains inappropriate content
    """
    # Simple content check (in real implementation, use proper content moderation)
    inappropriate_keywords = ["hate", "spam", "attack"]
    has_inappropriate = any(keyword.lower() in input_text.lower() for keyword in inappropriate_keywords)

    return GuardrailFunctionOutput(
        output_info={"contains_inappropriate": has_inappropriate},
        tripwire_triggered=has_inappropriate
    )


@output_guardrail
async def fact_check_guardrail(ctx, agent, input_text, output_text) -> GuardrailFunctionOutput:
    """
    Check if output contains hallucinated or incorrect information
    """
    # Simple fact-checking (in real implementation, use proper fact-checking tools)
    # For this example, we'll just ensure output isn't empty
    is_empty = not output_text.strip()
    has_confidence_issues = "I don't know" in output_text or "not sure" in output_text

    return GuardrailFunctionOutput(
        output_info={
            "is_empty": is_empty,
            "has_confidence_issues": has_confidence_issues
        },
        tripwire_triggered=is_empty
    )


# 5. COMPLETE SYSTEM CLASS
class DemoAgentSystem:
    """
    Complete demo system showcasing all OpenAI Agents SDK features
    """
    def __init__(self):
        # Create agents
        self.triage_agent, self.tier1_agent, self.tier2_agent = create_support_agents()

        # Create session
        self.session = SQLiteSession("demo_conversation")

        print("Demo Agent System initialized with:")
        print("- Triage Agent (routes requests)")
        print("- Tier 1 Support Agent (basic support)")
        print("- Tier 2 Support Agent (advanced support)")
        print("- SQLite Session for conversation history")
        print("- Content Moderation Input Guardrail")
        print("- Fact-Checking Output Guardrail")
        print()

    async def process_request(self, user_input: str, user_id: str = None):
        """
        Process a user request through the complete system
        """
        print(f"Processing request: '{user_input}'")

        try:
            # Run the agent with session
            result = await Runner.run(
                self.triage_agent,
                user_input,
                context_variables={"user_id": user_id} if user_id else {},
                session=self.session
            )

            print(f"Response: {result.final_output}")
            print(f"Was handoff: {result.was_handoff}")
            print()

            return result

        except Exception as e:
            print(f"Error processing request: {str(e)}")
            print()
            return None


# 6. MAIN DEMONSTRATION
async def main():
    """
    Demonstrate all features of the OpenAI Agents SDK
    """
    print("=== OpenAI Agents SDK Complete Demo ===\n")

    # Initialize the system
    system = DemoAgentSystem()

    # Example 1: Simple request that can be handled by Tier 1
    print("Example 1: Simple request")
    await system.process_request("What's the weather like in New York?")

    # Example 2: Mathematical calculation
    print("Example 2: Mathematical calculation")
    await system.process_request("Calculate 25 * 4 + 10")

    # Example 3: Complex request that should trigger a handoff
    print("Example 3: Complex request (should trigger handoff)")
    await system.process_request("I'm having issues with my complex networking setup and need advanced troubleshooting")

    # Example 4: Another simple request to show session continuity
    print("Example 4: Follow-up question (shows session continuity)")
    await system.process_request("What about the weather tomorrow?")

    print("=== Demo Complete ===")
    print("\nKey features demonstrated:")
    print("✓ Agent creation and configuration")
    print("✓ Function tools with type hints")
    print("✓ Multi-agent coordination with handoffs")
    print("✓ Session management with SQLite")
    print("✓ Input and output guardrails")
    print("✓ Asynchronous execution")
    print("✓ Context variables")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())