# OpenAI Agents SDK Skill

This skill provides comprehensive knowledge and implementation examples for the OpenAI Agents SDK, covering all core components: Agents, Tools, Handoffs, Guardrails, Sessions, and Tracing.

## Overview

The OpenAI Agents SDK is a lightweight framework for building multi-agent workflows that supports OpenAI APIs and 100+ other LLMs. This skill contains complete documentation, examples, and best practices for implementing all SDK features with support for multiple LLM providers.

## Components Covered

- **Agents**: LLMs configured with instructions, tools, guardrails, and handoffs
- **Tools**: Function tools, hosted tools, and agents as tools
- **Handoffs**: Agent-to-agent delegation for specialized tasks
- **Guardrails**: Input/output validation and safety checks
- **Sessions**: Conversation history management
- **Tracing**: Built-in debugging and monitoring
- **Provider Configuration**: Support for OpenAI, Anthropic, Google, OpenRouter, Azure, and other LLM providers

## Key Features

- Complete API reference documentation
- Production-ready examples with all components integrated
- Best practices and error handling patterns
- Environment configuration guidance
- Multi-agent system implementation

## Usage

Use this skill when you need to:
- Implement multi-agent systems with proper coordination
- Integrate tools and functions with agents
- Set up handoffs between specialized agents
- Implement safety guardrails for input/output validation
- Manage conversation sessions across interactions
- Add tracing and monitoring to agent systems

## Files Included

- `SKILL.md`: Complete documentation and implementation guide
- `references/api-reference.md`: Detailed API reference
- `scripts/demo_agents_sdk.py`: Complete working example
- `assets/`: Additional resources (empty in this version)

## Prerequisites

- Python 3.9+
- OpenAI Agents SDK: `pip install openai-agents`
- Optional extras: `pip install 'openai-agents[redis]'` for Redis sessions