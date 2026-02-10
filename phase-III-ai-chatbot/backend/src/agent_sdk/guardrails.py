"""
Guardrails

Input and output validation guardrails for safety and quality.
"""

from agents import input_guardrail, output_guardrail, GuardrailFunctionOutput
from typing import Any


@input_guardrail
async def input_validation_guardrail(ctx: Any, agent: Any, input: Any) -> GuardrailFunctionOutput:
    """
    Validate user input before processing.

    Checks:
    - Message length (1-1000 characters)
    - Non-empty message

    Args:
        ctx: Context object
        agent: Agent instance
        input: User input to validate

    Returns:
        GuardrailFunctionOutput with validation result
    """
    # Convert input to string
    message = input if isinstance(input, str) else str(input)

    # Check if message is empty
    if not message or len(message.strip()) == 0:
        return GuardrailFunctionOutput(
            output_info={"error": "Message cannot be empty"},
            tripwire_triggered=True
        )

    # Check message length
    if len(message) < 1:
        return GuardrailFunctionOutput(
            output_info={"error": "Message is too short"},
            tripwire_triggered=True
        )

    if len(message) > 1000:
        return GuardrailFunctionOutput(
            output_info={"error": "Message must be at most 1000 characters"},
            tripwire_triggered=True
        )

    # Input is valid
    return GuardrailFunctionOutput(
        output_info={"valid": True, "length": len(message)},
        tripwire_triggered=False
    )


@output_guardrail
async def output_quality_guardrail(ctx: Any, agent: Any, input: Any, output: Any) -> GuardrailFunctionOutput:
    """
    Validate agent output quality.

    Checks:
    - Output is not empty
    - Output has minimum length
    - Output is a string

    Args:
        ctx: Context object
        agent: Agent instance
        input: Original user input
        output: Agent output to validate

    Returns:
        GuardrailFunctionOutput with validation result
    """
    # Convert output to string
    response = output if isinstance(output, str) else str(output)

    # Check if output is empty
    if not response or len(response.strip()) == 0:
        return GuardrailFunctionOutput(
            output_info={"error": "Response is empty"},
            tripwire_triggered=True
        )

    # Check minimum length (at least 5 characters for meaningful response)
    if len(response.strip()) < 5:
        return GuardrailFunctionOutput(
            output_info={"error": "Response is too short"},
            tripwire_triggered=True
        )

    # Output is valid
    return GuardrailFunctionOutput(
        output_info={"quality": "good", "length": len(response)},
        tripwire_triggered=False
    )


@input_guardrail
async def content_safety_guardrail(ctx: Any, agent: Any, input: Any) -> GuardrailFunctionOutput:
    """
    Check input for inappropriate content (placeholder implementation).

    This is a basic implementation. In production, you would integrate
    with a content moderation service.

    Args:
        ctx: Context object
        agent: Agent instance
        input: User input to check

    Returns:
        GuardrailFunctionOutput with safety check result
    """
    message = input if isinstance(input, str) else str(input)

    # Basic keyword check (expand in production)
    inappropriate_keywords = ["spam", "abuse"]  # Placeholder

    message_lower = message.lower()
    for keyword in inappropriate_keywords:
        if keyword in message_lower:
            return GuardrailFunctionOutput(
                output_info={"error": "Content may be inappropriate"},
                tripwire_triggered=True
            )

    return GuardrailFunctionOutput(
        output_info={"safe": True},
        tripwire_triggered=False
    )
