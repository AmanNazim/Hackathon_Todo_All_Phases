# ChatKit Widgets Reference

This document provides detailed information about the various widgets available in ChatKit for creating rich, interactive chat experiences.

## Widget Categories

### Containers
- **Card**: A bounded container for widgets with support for status indicators, primary actions, and confirm/cancel buttons
- **ListView**: Displays a vertical list of items as ListViewItems

### Layout Components
- **Box**: Flexible container supporting direction, spacing, and styling
- **Row**: Arranges children horizontally
- **Col**: Arranges children vertically
- **Form**: Layout container that can submit actions
- **Spacer**: Flexible empty space used in layouts

### Content Components
- **Text**: Displays plain text with support for streaming updates
- **Title**: Prominent heading text
- **Markdown**: Renders markdown-formatted text
- **Image**: Displays images with styling options
- **Icon**: Displays icons by name

### Interactive Components
- **Button**: Action buttons with various styles and sizes
- **Select**: Dropdown single-select input
- **DatePicker**: Date input with dropdown calendar
- **Badge**: Small labels for status or metadata

### Utility Components
- **Divider**: Horizontal or vertical separators
- **Caption**: Smaller supporting text
- **Transition**: Wraps content that may animate

## Widget Properties

### Card Container Properties
- `children`: List of child widget nodes
- `size`: Size options ("sm", "md", "lg", "full") - default: "md"
- `padding`: Padding configuration
- `background`: Background color
- `status`: Status indicator text and icon
- `collapsed`: Whether the card is collapsed
- `asForm`: Whether to treat as a form
- `confirm`: Confirm button configuration
- `cancel`: Cancel button configuration
- `theme`: Theme ("light", "dark")
- `key`: Unique identifier

### Box Component Properties
- `children`: Child widget nodes
- `direction`: Flex direction ("row", "column")
- `align`: Alignment ("start", "center", "end", "baseline", "stretch")
- `justify`: Justification options
- `wrap`: Wrap behavior ("nowrap", "wrap", "wrap-reverse")
- `flex`: Flex properties
- `dimensions`: Width, height, min/max values
- `gap`: Spacing between children
- `padding`/`margin`: Spacing properties
- `border`: Border configuration
- `radius`: Corner radius
- `background`: Background styling
- `aspectRatio`: Aspect ratio
- `key`: Unique identifier

### Button Component Properties
- `submit`: Whether it's a submit button
- `style`: Style ("primary", "secondary")
- `label`: Button text
- `onClickAction`: Action to execute on click
- `icons`: Start/end icons
- `color`: Color options
- `variant`: Visual variant
- `size`: Size options
- `styling`: Pill, block, uniform options
- `key`: Unique identifier

## Widget Actions

Widgets can trigger actions that are handled on the server or client side:

```python
Button(
    label="Example",
    onClickAction=ActionConfig(
      type="example",
      payload={"id": 123},
      handler="server"  # or "client"
    )
)
```

## Form Handling

Widgets with input capabilities can be placed inside a Form to collect values:

```python
Form(
    onSubmitAction=ActionConfig(
        type="update_todo",
        payload={"id": todo.id}
    ),
    children=[
        Title(value="Edit Todo"),
        Text(
            value=todo.title,
            editable=EditableProps(name="title", required=True),
        ),
        Button(label="Save", type="submit")
    ]
)
```

## Loading States

Use `loadingBehavior` to control how actions affect UI:

- `auto`: Adapts based on context (default)
- `self`: Triggers loading on the widget node
- `container`: Triggers loading on the entire widget container
- `none`: No loading state

## Widget Composition

Widgets can be composed hierarchically to create complex UIs:

```
Card
  └─ Box (layout)
      ├─ Title
      ├─ Text
      └─ Row
          ├─ Button
          └─ Badge
```

## Best Practices

1. Use appropriate container widgets to group related content
2. Maintain consistent styling across your widget hierarchy
3. Use loading behaviors to provide feedback during operations
4. Validate form inputs before submission
5. Provide clear labels and instructions for interactive widgets
6. Consider responsive design when laying out widgets