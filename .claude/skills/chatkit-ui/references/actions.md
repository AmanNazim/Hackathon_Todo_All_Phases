# ChatKit Actions Reference

This document provides detailed information about actions in ChatKit, which allow triggering backend operations from user interactions in the chat interface.

## Overview

Actions are a way for the ChatKit frontend to trigger a streaming response without the user submitting a message. They can also be used to trigger side effects outside of ChatKit.

## Action Configuration

### ActionConfig Properties
- `type`: String identifier for the action type
- `payload`: Object containing data to be sent with the action
- `handler`: Specifies where to handle the action ("server" or "client")
- `loadingBehavior`: Controls loading state interactions

### Loading Behavior Options
- `auto`: Adapts based on context (default)
- `self`: Triggers loading on the widget node
- `container`: Triggers loading on the entire widget container
- `none`: No loading state

## Triggering Actions

### Widget-Based Actions
Actions can be triggered by attaching an ActionConfig to any widget node that supports it:

```python
Button(
    label="Submit",
    onClickAction=ActionConfig(
      type="form_submit",
      payload={"formData": "value"},
      handler="server",
      loadingBehavior="container"
    )
)
```

### Imperative Actions
Actions can be sent imperatively from the frontend:

```javascript
await chatKit.sendAction({
  type: "example",
  payload: { id: 123 },
});
```

## Handling Actions

### Server-Side Handling
By default, actions are sent to your server and handled by implementing the `action` method on `ChatKitServer`:

```python
class MyChatKitServer(ChatKitServer[RequestContext]):
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[Event]:
        if action.type == "form_submit":
            # Process the action
            await process_form_data(action.payload['formData'])

            # Add hidden context for the model
            await self.store.add_thread_item(
                thread.id,
                HiddenContextItem(
                    id="item_123",
                    content=f"<USER_ACTION>Form submitted with data: {action.payload['formData']}</USER_ACTION>",
                ),
                context,
            )

            # Generate response
            async for e in self.generate(context, thread):
                yield e
```

### Client-Side Handling
To handle actions on the client, specify `handler="client"` in the ActionConfig:

```python
Button(
    label="Example",
    onClickAction=ActionConfig(
      type="example",
      payload={"id": 123},
      handler="client"
    )
)
```

Then implement the client-side handler:

```javascript
async function handleWidgetAction(action) {
  if (action.type === "example") {
    const result = await doSomething(action.payload);

    // Fire off additional actions to the server if needed
    await chatKit.sendAction({
      type: "example_complete",
      payload: result
    });
  }
}

chatKit.setOptions({
  widgets: { onAction: handleWidgetAction }
});
```

## Strongly Typed Actions

Action and ActionConfig are not strongly typed by default, but you can create strongly typed actions:

```python
from pydantic import BaseModel
from typing import Literal, Annotated, Any
from openai_chatkit.types import Action
from typing_extensions import TypeAdapter
from pydantic import Field

class ExamplePayload(BaseModel):
    id: int

ExampleAction = Action[Literal["example"], ExamplePayload]
OtherAction = Action[Literal["other"], None]

AppAction = Annotated[
  ExampleAction
  | OtherAction,
  Field(discriminator="type"),
]

ActionAdapter: TypeAdapter[AppAction] = TypeAdapter(AppAction)

def parse_app_action(action: Action[str, Any]) -> AppAction:
    return ActionAdapter.model_validate(action)

# Usage in a widget
Button(
    label="Example",
    onClickAction=ExampleAction.create(ExamplePayload(id=123))
)

# Usage in action handler
class MyChatKitServer(ChatKitServer[RequestContext]):
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[Event]:
        # Add custom error handling if needed
        app_action = parse_app_action(action)
        if app_action.type == "example":
            await do_thing(app_action.payload.id)
```

## Form Actions

When widget nodes that take user input are mounted inside a `Form`, the values from those fields are included in the action payload:

```python
Form(
    onSubmitAction=ActionConfig(
        type="update_todo",
        payload={"id": todo.id}
    ),
    children=[
        Title(value="Edit Todo"),

        Text(value="Title", color="secondary", size="sm"),
        Text(
          value=todo.title,
          editable=EditableProps(name="title", required=True),
        ),

        Text(value="Description", color="secondary", size="sm"),
        Text(
          value=todo.description,
          editable=EditableProps(name="description"),
        ),

        Button(label="Save", type="submit")
    ]
)
```

In the action handler:
```python
class MyChatKitServer(ChatKitServer[RequestContext]):
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[Event]:
        if action.type == "update_todo":
            todo_id = action.payload['id']
            # Values from form fields are included in the payload
            title = action.payload['title']
            description = action.payload['description']

            # Update the todo item
            await update_todo(todo_id, title, description)
```

### Form Validation
- Forms use basic native form validation
- Enforces `required` and `pattern` attributes
- Blocks submission when the form has invalid fields
- For complex validation, consider using client-side modals

### Treating Card as a Form
You can pass `asForm=True` to a `Card` to make it behave as a form:

```python
Card(
    children=[...],
    asForm=True,
    confirm={
        "label": "Submit",
        "action": ActionConfig(type="card_submit", payload={"cardId": "xyz"})
    }
)
```

## Action Patterns

### Chaining Actions
You can chain actions by handling one action that triggers another:

```javascript
// Client-side handler
async function handleFirstAction(action) {
  if (action.type === "first_step") {
    // Do first step processing

    // Trigger second action
    await chatKit.sendAction({
      type: "second_step",
      payload: { ... }
    });
  }
}
```

### Conditional Actions
Handle actions conditionally based on the current state:

```python
async def action(
    self,
    thread: ThreadMetadata,
    action: Action[str, Any],
    sender: WidgetItem | None,
    context: RequestContext,
) -> AsyncIterator[Event]:
    if action.type == "conditional_action":
        if await check_condition():
            # Take one path
            yield await self.create_message(thread.id, "Condition met!")
        else:
            # Take another path
            yield await self.create_message(thread.id, "Condition not met!")
```

## Security Considerations

### Untrusted Data
- Actions and their payloads are sent by the client and should be treated as untrusted data
- Always validate and sanitize action payloads on the server
- Implement proper authentication and authorization checks
- Sanitize any data that will be stored or displayed

### Rate Limiting
- Implement rate limiting for actions to prevent abuse
- Monitor for unusual patterns of action usage

### Input Validation
- Validate all action payload data against expected schemas
- Reject actions with unexpected or malformed data
- Log suspicious action attempts

## Error Handling

### Action Errors
Handle errors gracefully in action handlers:

```python
async def action(
    self,
    thread: ThreadMetadata,
    action: Action[str, Any],
    sender: WidgetItem | None,
    context: RequestContext,
) -> AsyncIterator[Event]:
    try:
        if action.type == "process_data":
            result = await process_data(action.payload)
            yield await self.create_message(thread.id, f"Success: {result}")
    except ValidationError as e:
        yield await self.create_message(thread.id, f"Validation error: {str(e)}")
    except Exception as e:
        yield await self.create_error_message(thread.id, f"Processing error: {str(e)}")
```

## Best Practices

1. **Security**: Always validate action payloads as untrusted data
2. **Performance**: Keep action handlers efficient to maintain responsiveness
3. **Error Handling**: Implement proper error handling and user feedback
4. **Consistency**: Use consistent action naming conventions
5. **Payload Size**: Keep action payloads reasonably sized
6. **User Feedback**: Provide visual feedback during action processing
7. **Loading States**: Use appropriate loadingBehavior for different actions
8. **Logging**: Log action execution for debugging and monitoring
9. **Testing**: Test both client and server action flows
10. **Documentation**: Document action types and expected payloads