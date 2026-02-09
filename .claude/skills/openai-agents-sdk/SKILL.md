---
name: openai-agents-sdk
description: Complete OpenAI Agents SDK implementation covering all components: Agents, Tools, Handoffs, Guardrails, Sessions, Models, and Tracing. Implements all documented patterns and best practices from official documentation. Use when building multi-agent systems with proper tool integration, safety checks, and session management.
---

# OpenAI Agents SDK Complete Skill

This skill implements the complete OpenAI Agents SDK framework with all documented components and best practices.

## Documentation References

Based on OpenAI Agents SDK documentation:
- Core Documentation: https://openai.github.io/openai-agents-python/
- Quickstart: https://openai.github.io/openai-agents-python/quickstart
- Examples: https://openai.github.io/openai-agents-python/examples
- Agents: https://openai.github.io/openai-agents-python/agents
- Running Agents: https://openai.github.io/openai-agents-python/running_agents
- Sessions: https://openai.github.io/openai-agents-python/sessions
- Tools: https://openai.github.io/openai-agents-python/tools
- Guardrails: https://openai.github.io/openai-agents-python/guardrails
- Models: https://openai.github.io/openai-agents-python/models
- Models with LiteLLM: https://openai.github.io/openai-agents-python/models/litellm

## Overview

The OpenAI Agents SDK is a production-ready framework for building multi-agent workflows that supports OpenAI APIs and 100+ other LLMs. It provides core primitives:
- **Agents**: LLMs with instructions and tools
- **Handoffs**: Delegation between agents
- **Guardrails**: Input/output validation
- **Sessions**: Conversation history management

## Installation

```bash
pip install openai-agents
```

For optional features:
- Voice support: `pip install 'openai-agents[voice]'`
- Redis sessions: `pip install 'openai-agents[redis]'`
- LiteLLM integration: `pip install 'openai-agents[litellm]'`

## Quickstart

### Hello World Example

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
```

### Complete Multi-Agent Example

```python
from agents import Agent, Runner, handoff
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

# Create specialized agents
history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

# Create triage agent with handoffs
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)

async def main():
    result = await Runner.run(triage_agent, "who was the first president of the united states?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Components

### 1. Agents

Agents are the fundamental building blocks containing an LLM with instructions and tools.

```python
from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    """returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form",
    model="gpt-5-nano",
    tools=[get_weather],
)
```

#### Core Agent Parameters:
- `name`: Required identifier string
- `instructions`: System prompt or developer message
- `model`: LLM selection with optional `model_settings`
- `tools`: Available functions for the agent
- `handoffs`: List of agents to transfer to
- `input_guardrails`: Input validation functions
- `output_guardrails`: Output validation functions
- `output_type`: Expected structured output type
- `max_iterations`: Maximum number of iterations before stopping

#### Context Management:
Agents support generic context types through dependency injection:

```python
from dataclasses import dataclass

@dataclass
class UserContext:
    name: str
    uid: str
    is_pro_user: bool

agent = Agent[UserContext](
    # ... other parameters
)
```

#### Output Types:
Specify structured outputs using Pydantic models:

```python
from pydantic import BaseModel

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
```

#### Multi-Agent Design Patterns:

**Manager Pattern (Agents as Tools)**:
Central orchestrator invokes specialized sub-agents while maintaining control:

```python
booking_agent = Agent(...)
refund_agent = Agent(...)

customer_facing_agent = Agent(
    name="Customer-facing agent",
    instructions=(
        "Handle all direct user communication. "
        "Call the relevant tools when specialized expertise is needed."
    ),
    tools=[
        booking_agent.as_tool(
            tool_name="booking_expert",
            tool_description="Handles booking questions and requests.",
        ),
        refund_agent.as_tool(
            tool_name="refund_expert",
            tool_description="Handles refund questions and requests.",
        )
    ],
)
```

**Handoffs Pattern**:
Decentralized delegation where agents transfer conversation control:

```python
booking_agent = Agent(...)
refund_agent = Agent(...)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Help the user with their questions. "
        "If they ask about booking, hand off to the booking agent. "
        "If they ask about refunds, hand off to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent],
)
```

### 2. Running Agents

The `Runner` class provides three methods to execute agents:

- `Runner.run()` - asynchronous method returning `RunResult`
- `Runner.run_sync()` - synchronous wrapper around the async version
- `Runner.run_streamed()` - returns `RunResultStreaming` with event streaming

```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")
    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
```

#### The Agent Loop Process:
- Calls the LLM with current agent and input
- Processes output: final output ends loop, handoff updates agent/input, tool calls execute and re-run
- Raises `MaxTurnsExceeded` if `max_turns` limit reached

#### Streaming Capabilities:
Streaming allows receiving real-time events during LLM execution:

```python
from agents import Runner

async def stream_agent_response(agent, message):
    async for event in Runner.run_streamed(agent, message):
        if hasattr(event, 'text'):
            print(f"Streaming: {event.text}")
```

### 3. Tools and Functions

The Agent SDK provides three classes of tools:

#### Hosted Tools:
Built-in tools work with `OpenAIResponsesModel`:
- `WebSearchTool`: Enables web searching capabilities
- `FileSearchTool`: Retrieves info from OpenAI Vector Stores
- `ComputerTool`: Automates computer use tasks
- `CodeInterpreterTool`: Executes code in sandboxed environments
- `HostedMCPTool`: Exposes remote MCP server tools
- `ImageGenerationTool`: Creates images from prompts
- `LocalShellTool`: Runs local shell commands

```python
from agents import Agent, FileSearchTool, Runner, WebSearchTool

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["VECTOR_STORE_ID"],
        ),
    ],
)
```

#### Function Tools:
Python functions become tools automatically with the `@function_tool` decorator:

```python
from agents.decorators import function_tool

@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return "sunny"

@function_tool
async def fetch_user_data(user_id: str) -> dict:
    """Fetch user data by ID."""
    return {"id": user_id, "name": "John Doe"}
```

Function tools features:
- Automatic schema generation from function signatures
- Docstring parsing for descriptions
- Support for sync/async functions
- Context injection via RunContextWrapper
- Custom name overrides

#### Agents as Tools:
Orchestrate specialized agents through `agent.as_tool()`:

```python
spanish_agent = Agent(name="Spanish Translator", instructions="Translate to Spanish")
spanish_tool = spanish_agent.as_tool(
    tool_name="translate_to_spanish",
    tool_description="Translate text to Spanish"
)
```

### 4. Sessions

Sessions provide built-in memory to maintain conversation history across multiple agent runs.

#### Quick Start:
```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

session = SQLiteSession("conversation_123")

result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"
```

#### Session Types:

**SQLite Sessions** (default):
The default, lightweight implementation using SQLite:

```python
from agents import SQLiteSession

# In-memory database (lost when process ends)
session = SQLiteSession("user_123")

# Persistent file-based database
session = SQLiteSession("user_123", "conversations.db")
```

**OpenAI Conversations API Sessions**:
Use OpenAI's Conversations API through `OpenAIConversationsSession`:

```python
from agents import Agent, Runner, OpenAIConversationsSession

session = OpenAIConversationsSession()
# Optionally resume a previous conversation by passing a conversation ID
# session = OpenAIConversationsSession(conversation_id="conv_123")
```

**SQLAlchemy Sessions**:
Production-ready sessions using any SQLAlchemy-supported database:

```python
from agents.extensions.memory import SQLAlchemySession

session = SQLAlchemySession.from_url(
    "user_123",
    url="postgresql+asyncpg://user:pass@localhost/db",
    create_tables=True
)
```

**Advanced SQLite Sessions**:
Enhanced SQLite sessions with conversation branching, usage analytics, and structured queries:

```python
from agents.extensions.memory import AdvancedSQLiteSession

session = AdvancedSQLiteSession(
    session_id="user_123",
    db_path="conversations.db",
    create_tables=True
)

# Automatic usage tracking
result = await Runner.run(agent, "Hello", session=session)
await session.store_run_usage(result)  # Track token usage
```

**Encrypted Sessions**:
Transparent encryption wrapper for any session implementation:

```python
from agents.extensions.memory import EncryptedSession, SQLAlchemySession

underlying_session = SQLAlchemySession.from_url(
    "user_123",
    url="sqlite+aiosqlite:///conversations.db",
    create_tables=True
)

session = EncryptedSession(
    session_id="user_123",
    underlying_session=underlying_session,
    encryption_key="your-secret-key",
    ttl=600  # 10 minutes
)
```

#### Session Management:
Use meaningful session IDs that help organize conversations:
- User-based: `"user_12345"`
- Thread-based: `"thread_abc123"`
- Context-based: `"support_ticket_456"`

Memory persistence options:
- Use in-memory SQLite for temporary conversations
- Use file-based SQLite for persistent conversations
- Use SQLAlchemy-powered sessions for production systems
- Use OpenAI-hosted storage when preferring OpenAI's storage
- Use encrypted sessions to wrap any session with encryption

### 5. Guardrails

Guardrails enable validation of user input and agent output to prevent malicious usage and optimize costs.

#### Input Guardrails:
Run on initial user input with two execution modes:
- **Parallel execution** (default): Guardrail runs concurrently with agent for best latency
- **Blocking execution**: Guardrail completes before agent starts, preventing token consumption

```python
from agents.decorators import input_guardrail
from agents.types import GuardrailFunctionOutput

@input_guardrail
async def math_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    # Implementation logic here
    return GuardrailFunctionOutput(
        output_info=result,
        tripwire_triggered=condition,
    )
```

#### Output Guardrails:
Run on final agent output following the same pattern as input guardrails:

```python
from agents.decorators import output_guardrail

@output_guardrail
async def content_safety_guardrail(ctx, agent, input, output) -> GuardrailFunctionOutput:
    # Check if output contains unsafe content
    has_unsafe_content = check_unsafe_content(output)
    return GuardrailFunctionOutput(
        output_info={"is_safe": not has_unsafe_content},
        tripwire_triggered=has_unsafe_content,
    )
```

### 6. Models

#### OpenAI Models Support:
The SDK includes built-in support for OpenAI models through two primary interfaces:
- **OpenAIResponsesModel** (recommended): Uses OpenAI's Responses API
- **OpenAIChatCompletionsModel**: Uses Chat Completions API

The default model is `gpt-4.1` for compatibility and low latency, though `gpt-5.2` is recommended for higher quality.

```python
export OPENAI_DEFAULT_MODEL=gpt-5
```

#### Non-OpenAI Model Integration:
Most alternative models work via LiteLLM integration:

```bash
pip install "openai-agents[litellm]"
```

Use models with the `litellm/` prefix format:
```python
Agent(model="litellm/anthropic/claude-3-5-sonnet-20240620")
```

#### Model Configuration:
Configure models using `ModelSettings`:

```python
Agent(
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0.1),
)
```

For Responses API parameters not available top-level, use `extra_args`:

```python
model_settings=ModelSettings(
    temperature=0.1,
    extra_args={"service_tier": "flex", "user": "user_12345"},
)
```

#### LiteLLM Integration:
Use `LitellmModel` to work with any AI model through a single interface:

```python
from agents.extensions.models.litellm_model import LitellmModel

agent = Agent(
    name="Assistant",
    model=LitellmModel(model="openai/gpt-4.1", api_key="your-key"),
)
```

Tracking usage data with LiteLLM:

```python
from agents import ModelSettings

agent = Agent(
    model=LitellmModel(model="your/model", api_key="..."),
    model_settings=ModelSettings(include_usage=True),  # Enable usage tracking
)
```

## Handoffs

Handoffs enable agent-to-agent delegation for specialized tasks.

```python
from agents import Agent, handoff
from agents.extensions.handoff_filters import collapse_messages
from pydantic import BaseModel

# Create specialized agents
billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing-related inquiries"
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="Handle refund requests and processes"
)

# Create triage agent with handoffs
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are a triage agent. Analyze incoming requests and hand off to the appropriate specialist:
    - Billing inquiries: transfer to Billing Agent
    - Refund requests: transfer to Refund Agent
    """,
    handoffs=[billing_agent, handoff(refund_agent)]
)

# Custom handoff with parameters
class HandoffData(BaseModel):
    reason: str
    priority: int

def on_refund_handoff(data: HandoffData):
    """Callback when handoff occurs"""
    print(f"Handing off with reason: {data.reason}")

refund_handoff = handoff(
    agent=refund_agent,
    on_handoff=on_refund_handoff,
    input_type=HandoffData,
    input_filter=collapse_messages,
    tool_name_override="escalate_to_refund_specialist",
    tool_description_override="Transfer to refund specialist with escalation data"
)
```

## Tracing

The Agents SDK includes built-in tracing that collects comprehensive records of events during agent runs, including LLM generations, tool calls, handoffs, guardrails, and custom events. The Traces dashboard at platform.openai.com/traces enables debugging, visualization, and monitoring of workflows during development and production.

### Default Tracing Behavior:
Tracing is enabled by default and captures:
- The entire Runner.run() operation wrapped in a trace()
- Each agent run wrapped in agent_span()
- LLM generations wrapped in generation_span()
- Function tool calls wrapped in function_span()
- Guardrails wrapped in guardrail_span()
- Handoffs wrapped in handoff_span()
- Audio inputs wrapped in transcription_span()
- Audio outputs wrapped in speech_span()

To disable tracing:
```python
from agents import set_tracing_disabled
set_tracing_disabled()  # Disable tracing globally
```

## Streaming

The OpenAI Agents SDK provides streaming capabilities through `Runner.run_streamed()` which returns a `RunResultStreaming` object with async stream events.

### Raw Response Events:
`RawResponsesStreamEvent` provides raw LLM events in OpenAI Responses API format, useful for token-by-token streaming to users.

### Run Item Events:
`RunItemStreamEvent` provides higher-level events when items are fully generated, enabling progress updates at message/tool level rather than per token. Includes `AgentUpdatedStreamEvent` for handoff notifications.

### Example Streaming Usage:
```python
from agents import Runner

# Stream responses as they're generated
async def stream_agent_response(agent, message, session=None):
    async for event in Runner.run_streamed(agent, message, session=session):
        if hasattr(event, 'text'):
            print(f"Streaming: {event.text}")
        # Handle different event types as needed
```

## Complete Multi-Agent System Example

```python
from agents import Agent, Runner, handoff
from agents.decorators import function_tool, input_guardrail, output_guardrail
from agents.types import GuardrailFunctionOutput
from agents.extensions import SQLiteSession
from agents.model_settings import ModelSettings
from pydantic import BaseModel
import asyncio

# Define input model for handoffs
class EscalationData(BaseModel):
    reason: str
    priority: int = 1

# Define function tools
@function_tool
def search_knowledge_base(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """Search the knowledge base for relevant information."""
    return [{"id": "1", "content": "Sample result", "score": 0.9}]

@function_tool
def get_user_info(user_id: str) -> dict[str, any]:
    """Get information about a user."""
    return {"id": user_id, "name": "John Doe", "status": "active"}

# Define specialized agents
def create_support_agents():
    """
    Create specialized support agents with handoffs
    """
    # Tier 1 support agent
    tier1_agent = Agent(
        name="Tier 1 Support",
        instructions="""
        You are a first-level support agent. Handle basic inquiries and common questions.
        If the issue is complex or requires escalation, hand off to Tier 2 support.
        """,
        tools=[search_knowledge_base, get_user_info]
    )

    # Tier 2 support agent
    tier2_agent = Agent(
        name="Tier 2 Support",
        instructions="""
        You are a second-level support agent. Handle complex technical issues and escalations.
        """,
        tools=[search_knowledge_base, get_user_info]
    )

    # Create handoff to tier 2
    tier2_handoff = handoff(
        agent=tier2_agent,
        tool_name_override="escalate_to_tier2",
        tool_description_override="Escalate issue to Tier 2 support specialist",
        input_type=EscalationData
    )

    # Triage agent that can route to appropriate support level
    triage_agent = Agent(
        name="Triage Agent",
        instructions="""
        You are a triage agent. Analyze incoming support requests:
        - Simple questions: Answer directly using knowledge base
        - Complex issues: Hand off to Tier 2 support
        """,
        tools=[search_knowledge_base, get_user_info],
        handoffs=[tier2_handoff]
    )

    return triage_agent, tier1_agent, tier2_agent

# Define guardrails
@input_guardrail
async def support_request_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    """
    Check if support request is appropriate
    """
    is_appropriate = "support" in input.lower() or "help" in input.lower()
    return GuardrailFunctionOutput(
        output_info={"is_appropriate": is_appropriate},
        tripwire_triggered=not is_appropriate
    )

@output_guardrail
async def response_quality_guardrail(ctx, agent, input, output) -> GuardrailFunctionOutput:
    """
    Check response quality and compliance
    """
    quality_score = 0.9  # Simplified example
    is_compliant = quality_score >= 0.8  # Threshold for quality
    return GuardrailFunctionOutput(
        output_info={"quality_score": quality_score},
        tripwire_triggered=not is_compliant
    )

# Complete system with all components
class SupportSystem:
    """
    Complete support system with agents, tools, handoffs, and guardrails
    """
    def __init__(self):
        self.triage_agent, self.tier1_agent, self.tier2_agent = create_support_agents()
        self.session = SQLiteSession("support_conversation")

    async def handle_request(self, user_request: str, user_id: str = None):
        """
        Handle a support request with full system
        """
        result = await Runner.run(
            self.triage_agent,
            user_request,
            context_variables={"user_id": user_id} if user_id else {},
            session=self.session
        )
        return result.final_output

# Example usage
async def main():
    support_system = SupportSystem()
    response = await support_system.handle_request("How do I reset my password?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

1. **Include handoff instructions in agent prompts** to ensure LLMs understand transfer capabilities properly.
2. **Use appropriate session management** to maintain conversation context across interactions.
3. **Implement comprehensive guardrails** to ensure safety and quality of inputs and outputs.
4. **Structure tools properly** with clear function signatures and meaningful descriptions.
5. **Handle errors gracefully** with custom error functions via `failure_error_function` parameter.
6. **Use LiteLLM for multi-provider support** when working with 100+ different LLM providers.
7. **Enable usage tracking** with `ModelSettings(include_usage=True)` for monitoring and analytics.
8. **Use structured output types** with Pydantic models for reliable data extraction.

## Error Handling

Function tools support custom error functions via `failure_error_function` parameter to provide user-friendly error responses to the LLM when tool calls fail.

## Development

Requires Python 3.9+ and uv for development:
```bash
make sync      # Install dependencies
make check     # Run tests, linter, typechecker
make tests     # Run tests only
```