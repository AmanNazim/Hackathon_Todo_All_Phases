# OpenAI Agents SDK API Reference

## Table of Contents
1. [Agents](#agents)
2. [Runner](#runner)
3. [Tools](#tools)
4. [Sessions](#sessions)
5. [Guardrails](#guardrails)
6. [Handoffs](#handoffs)
7. [Models](#models)
8. [Results](#results)
9. [Streaming](#streaming)
10. [Tracing](#tracing)
11. [Extensions](#extensions)
12. [Types](#types)

## Agents

### Agent Class
```python
class Agent(
    name: str,
    instructions: Optional[str] = None,
    model: Union[str, Model] = "gpt-4.1",
    tools: Optional[List[Callable]] = None,
    handoffs: Optional[List[Union[Agent, Handoff]]] = None,
    input_guardrails: Optional[List[Callable]] = None,
    output_guardrails: Optional[List[Callable]] = None,
    output_type: Optional[Type[BaseModel]] = None,
    model_settings: Optional[ModelSettings] = None,
    max_iterations: Optional[int] = 10,
    handoff_description: Optional[str] = None,
    failure_error_function: Optional[Callable] = None
)
```

Core agent class representing an AI assistant with specific instructions and capabilities.

**Parameters:**
- `name` (str): Display name for the agent
- `instructions` (str, optional): Instructions that define the agent's behavior
- `model` (Union[str, Model]): Model identifier or model instance to use (default: "gpt-4.1")
- `tools` (List[Callable], optional): List of function tools available to the agent
- `handoffs` (List[Union[Agent, Handoff]], optional): List of agents or handoffs that this agent can transfer to
- `input_guardrails` (List[Callable], optional): List of input validation functions
- `output_guardrails` (List[Callable], optional): List of output validation functions
- `output_type` (Type[BaseModel], optional): Expected output type for structured output
- `model_settings` (ModelSettings, optional): Model configuration settings
- `max_iterations` (int, optional): Maximum number of iterations before stopping (default: 10)
- `handoff_description` (str, optional): Description used for routing handoffs
- `failure_error_function` (Callable, optional): Function to handle tool call failures

**Methods:**
- `as_tool(tool_name: str, tool_description: str) -> Tool` - Convert agent to a function tool
- `clone(**overrides) -> Agent` - Duplicate agent with optional property changes

## Runner

### Runner.run
```python
@staticmethod
async def run(
    agent: Agent,
    input: Union[str, List[Dict]],
    session: Optional[Session] = None,
    context_variables: Optional[Dict] = None,
    output_type: Optional[Type[BaseModel]] = None,
    run_config: Optional[RunConfig] = None
) -> RunResult
```

Execute an agent asynchronously with the given input.

**Parameters:**
- `agent` (Agent): The agent to run
- `input` (Union[str, List[Dict]]): Input message or list of messages
- `session` (Session, optional): Session to maintain conversation history
- `context_variables` (Dict, optional): Variables to pass to the agent
- `output_type` (Type[BaseModel], optional): Expected output type
- `run_config` (RunConfig, optional): Configuration for the run

**Returns:**
- `RunResult`: Result of the agent execution

### Runner.run_sync
```python
@staticmethod
def run_sync(
    agent: Agent,
    input: Union[str, List[Dict]],
    session: Optional[Session] = None,
    context_variables: Optional[Dict] = None,
    output_type: Optional[Type[BaseModel]] = None,
    run_config: Optional[RunConfig] = None
) -> RunResult
```

Synchronous version of run().

### Runner.run_streamed
```python
@staticmethod
async def run_streamed(
    agent: Agent,
    input: Union[str, List[Dict]],
    session: Optional[Session] = None,
    context_variables: Optional[Dict] = None,
    output_type: Optional[Type[BaseModel]] = None,
    run_config: Optional[RunConfig] = None
) -> AsyncGenerator[StreamEvent, None]
```

Stream the agent execution results.

## Tools

### function_tool Decorator
```python
def function_tool(
    func: Optional[Callable] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    strict: bool = True
) -> Callable
```

Decorator to convert Python functions into agent tools.

**Parameters:**
- `func` (Callable, optional): Function to decorate
- `name` (str, optional): Custom name for the tool
- `description` (str, optional): Description of the tool
- `strict` (bool): Whether to use strict schema validation

### Tool Class
```python
class Tool(ABC):
    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
```

Base class for all tools.

### Hosted Tools
- `WebSearchTool()` - Enables web searching capabilities
- `FileSearchTool(max_num_results: int, vector_store_ids: List[str])` - Retrieves info from OpenAI Vector Stores
- `ComputerTool()` - Automates computer use tasks
- `CodeInterpreterTool()` - Executes code in sandboxed environments
- `ImageGenerationTool()` - Creates images from prompts
- `LocalShellTool()` - Runs local shell commands

## Sessions

### Session Interface
```python
class Session(ABC):
    @abstractmethod
    async def get_items(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all items in the session."""

    @abstractmethod
    async def add_items(self, items: List[Dict]) -> None:
        """Add items to the session."""

    @abstractmethod
    async def pop_item(self) -> Optional[Dict]:
        """Remove and return the most recent item."""

    @abstractmethod
    async def clear_session(self) -> None:
        """Clear all items from the session."""
```

Base abstract class for all session implementations.

### SQLiteSession
```python
class SQLiteSession(Session):
    def __init__(self, session_id: str, db_path: str = ":memory:"):
        """Initialize SQLite session."""
```

Default, lightweight session implementation using SQLite.

### OpenAIConversationsSession
```python
class OpenAIConversationsSession(Session):
    def __init__(self, conversation_id: Optional[str] = None):
        """Initialize OpenAI Conversations API session."""
```

Uses OpenAI's Conversations API for session management.

### SQLAlchemySession
```python
class SQLAlchemySession(Session):
    @classmethod
    def from_url(cls, session_id: str, url: str, create_tables: bool = True):
        """Create session from SQLAlchemy URL."""
```

Production-ready sessions using any SQLAlchemy-supported database.

### AdvancedSQLiteSession
```python
class AdvancedSQLiteSession(SQLiteSession):
    def __init__(
        self,
        session_id: str,
        db_path: str = "conversations.db",
        create_tables: bool = True,
        ttl: Optional[int] = None
    ):
        """Initialize advanced SQLite session with analytics."""
```

Enhanced SQLite sessions with conversation branching and usage analytics.

### EncryptedSession
```python
class EncryptedSession(Session):
    def __init__(
        self,
        session_id: str,
        underlying_session: Session,
        encryption_key: str,
        ttl: Optional[int] = None
    ):
        """Initialize encrypted session wrapper."""
```

Transparent encryption wrapper for any session implementation.

## Guardrails

### input_guardrail Decorator
```python
def input_guardrail(func: Callable) -> Callable:
    """Decorator for input validation guardrails."""
```

### output_guardrail Decorator
```python
def output_guardrail(func: Callable) -> Callable:
    """Decorator for output validation guardrails."""
```

### GuardrailFunctionOutput
```python
class GuardrailFunctionOutput:
    def __init__(
        self,
        output_info: Dict,
        tripwire_triggered: bool
    ):
        """Output from a guardrail function."""
```

Output from a guardrail function.

**Attributes:**
- `output_info` (Dict): Information about the guardrail evaluation
- `tripwire_triggered` (bool): Whether the guardrail tripwire was triggered

## Handoffs

### handoff Function
```python
def handoff(
    agent: Agent,
    on_handoff: Optional[Callable] = None,
    input_type: Optional[Type[BaseModel]] = None,
    input_filter: Optional[Callable] = None,
    tool_name_override: Optional[str] = None,
    tool_description_override: Optional[str] = None
) -> Handoff
```

Creates a handoff configuration for transferring control to another agent.

**Parameters:**
- `agent` (Agent): Target agent for the handoff
- `on_handoff` (Callable, optional): Callback function when handoff occurs
- `input_type` (Type[BaseModel], optional): Expected input type for handoff
- `input_filter` (Callable, optional): Filter function for handoff input
- `tool_name_override` (str, optional): Override for tool name
- `tool_description_override` (str, optional): Override for tool description

### Handoff Class
```python
class Handoff:
    def __init__(
        self,
        agent: Agent,
        on_handoff: Optional[Callable] = None,
        input_type: Optional[Type[BaseModel]] = None,
        input_filter: Optional[Callable] = None,
        tool_name_override: Optional[str] = None,
        tool_description_override: Optional[str] = None
    ):
        """Configuration for transferring control to another agent."""
```

## Models

### Model Interface
```python
class Model(ABC):
    @abstractmethod
    async def call(self, messages: List[Dict], **kwargs) -> Dict:
        """Call the model with messages."""
```

Base interface for all models.

### ModelSettings
```python
class ModelSettings:
    def __init__(
        self,
        temperature: Optional[float] = None,
        include_usage: bool = False,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        tool_choice: Optional[Union[str, Literal["auto", "required", "none"]]] = None,
        extra_args: Optional[Dict] = None
    ):
        """Configuration for model behavior."""
```

**Parameters:**
- `temperature` (float, optional): Temperature setting for the model
- `include_usage` (bool): Whether to include usage statistics
- `timeout` (float, optional): Request timeout in seconds
- `max_retries` (int): Maximum number of retries (default: 3)
- `tool_choice` (str): Tool selection behavior
- `extra_args` (Dict, optional): Additional model-specific arguments

### OpenAIChatCompletionsModel
```python
class OpenAIChatCompletionsModel(Model):
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize OpenAI chat completions model."""
```

Implementation for OpenAI chat completion models.

### LitellmModel
```python
class LitellmModel(Model):
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize LiteLLM model for multi-provider support."""
```

Implementation for LiteLLM to support 100+ different LLM providers.

## Results

### RunResult
```python
class RunResult:
    final_output: Any
    was_handoff: bool
    context_wrapper: RunContextWrapper
    usage: Optional[Usage]

    def final_output_as(self, output_type: Type[BaseModel]) -> BaseModel:
        """Convert final output to specified type."""
```

Result returned from agent execution.

### Usage
```python
class Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime
```

Usage statistics for a run or model call.

## Streaming

### StreamEvent
```python
class StreamEvent(ABC):
    """Base class for all streaming events."""
```

Base class for all streaming events.

### RawResponsesStreamEvent
```python
class RawResponsesStreamEvent(StreamEvent):
    raw_response: Dict
```

Event containing raw LLM response data.

### RunItemStreamEvent
```python
class RunItemStreamEvent(StreamEvent):
    item: RunItem
```

Event containing a completed run item.

### AgentUpdatedStreamEvent
```python
class AgentUpdatedStreamEvent(RunItemStreamEvent):
    new_agent: Agent
    previous_agent: Agent
```

Event indicating an agent handoff has occurred.

## Tracing

### set_tracing_disabled
```python
def set_tracing_disabled(disabled: bool = True) -> None:
    """Disable tracing globally."""
```

### trace
```python
def trace(name: str, **kwargs) -> ContextManager:
    """Create a trace context."""
```

### span
```python
def span(name: str, **kwargs) -> ContextManager:
    """Create a span within a trace."""
```

## Extensions

### Handoff Filters
- `collapse_messages(items: List[Dict]) -> List[Dict]` - Filter function to collapse conversation messages

## Types

### BaseModel
From Pydantic, used for structured outputs and handoff input types.

### GuardrailFunctionOutput
See above in Guardrails section.