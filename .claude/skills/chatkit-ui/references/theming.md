# ChatKit Theming Reference

This document provides detailed information about theming and customization options in ChatKit for creating cohesive user experiences.

## Theme Configuration

ChatKit themes can be configured through options objects that are passed to the component initialization:

### React Integration
```javascript
const { control } = useChatKit({
  theme: {
    // Theme configuration here
  },
  // Other options
});
```

### Advanced Integration
```javascript
chatkit.setOptions({
  theme: {
    // Theme configuration here
  },
  // Other options
});
```

## Color Scheme

### colorScheme
- Values: `"light" | "dark"`
- Sets the overall light/dark mode for the chat interface

### Accent Colors
- `accent.primary`: Sets the primary accent color (e.g., "#2D8CFF")
- `accent.level`: Numeric value indicating the intensity level

### Background Colors
- `background.page`: Overall page background
- `background.surface`: Surface backgrounds for cards and panels
- `background.message.user`: Background for user messages
- `background.message.assistant`: Background for assistant messages

## Typography

### fontFamily
- Sets the font family for the entire chat interface
- Example: `"fontFamily": "'Inter', sans-serif"`

### fontSize
- Base font size for the interface
- Can be set in px, rem, em, or other CSS units

### fontWeight
- Controls the weight of text throughout the interface
- Common values: `"normal" | "medium" | "semibold" | "bold"`

## Density

Controls the compactness of UI elements:
- `"compact"`: Tightly packed elements
- `"regular"`: Standard spacing
- `"comfortable"`: More spacious layout

## Radius

Controls corner rounding:
- `"sharp"`: Square corners
- `"rounded"`: Moderately rounded corners
- `"round"`: Fully rounded corners
- Specific values: `"2xs" | "xs" | "sm" | "md" | "lg" | "xl" | "2xl" | "3xl" | "4xl" | "full"`

## Component-Specific Styling

### Header Customization
```javascript
{
  header: {
    background: "#ffffff",
    textColor: "#000000",
    borderColor: "#e5e5e5"
  }
}
```

### Composer (Input Area) Styling
```javascript
{
  composer: {
    background: "#f9f9f9",
    placeholderColor: "#999999",
    borderColor: "#e5e5e5",
    borderRadius: "8px"
  }
}
```

### Message Bubble Styling
```javascript
{
  message: {
    user: {
      background: "#e3f2fd",
      textColor: "#000000",
      borderRadius: "12px"
    },
    assistant: {
      background: "#f5f5f5",
      textColor: "#000000",
      borderRadius: "12px"
    }
  }
}
```

## Responsive Design

### Mobile Adaptations
```javascript
{
  mobile: {
    theme: {
      density: "compact",
      fontSize: "14px"
    }
  }
}
```

### Desktop Adaptations
```javascript
{
  desktop: {
    theme: {
      density: "regular",
      fontSize: "16px"
    }
  }
}
```

## Starter Prompts Styling

Customize the appearance of starter prompts on the welcome screen:

```javascript
{
  startScreen: {
    prompts: {
      background: "#f0f0f0",
      hoverBackground: "#e0e0e0",
      textColor: "#333333",
      borderRadius: "6px",
      padding: "12px 16px"
    }
  }
}
```

## Entity Tags Styling

Style @mentions and entity tags:

```javascript
{
  entities: {
    tag: {
      background: "#e6f7ff",
      textColor: "#1890ff",
      borderRadius: "4px",
      padding: "2px 6px"
    }
  }
}
```

## Widget Styling

Apply themes to widgets:

```javascript
{
  widgets: {
    card: {
      background: "#ffffff",
      borderColor: "#d9d9d9",
      borderRadius: "8px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
    },
    button: {
      primary: {
        background: "#1890ff",
        textColor: "#ffffff",
        hoverBackground: "#40a9ff"
      }
    }
  }
}
```

## Locale Override

Override the default locale for internationalization:

```javascript
{
  locale: 'de-DE'  // German locale
}
```

## Custom CSS Variables

You can also define custom CSS variables for more granular control:

```css
:root {
  --chatkit-primary-color: #2D8CFF;
  --chatkit-secondary-color: #f0f0f0;
  --chatkit-border-radius: 8px;
  --chatkit-font-family: 'Inter', sans-serif;
}
```

## Theme Switching

Implement dynamic theme switching:

```javascript
const [theme, setTheme] = useState('light');

const themeOptions = {
  theme: {
    colorScheme: theme,
    color: {
      accent: {
        primary: theme === 'dark' ? '#2D8CFF' : '#1890ff'
      }
    }
  }
};

// Switch theme
const toggleTheme = () => {
  setTheme(theme === 'light' ? 'dark' : 'light');
};
```

## Accessibility Considerations

### Contrast Ratios
- Ensure text/background contrast ratios meet WCAG AA standards (4.5:1 for normal text)
- Consider increased contrast for users with visual impairments

### Color Blindness
- Don't rely solely on color to convey information
- Use patterns, textures, or labels in addition to color

### Font Scaling
- Use relative units (rem, em) instead of fixed units (px) where possible
- Respect user's system font scaling preferences

## Performance Tips

### Theme Loading
- Define themes statically when possible to avoid runtime calculations
- Use CSS custom properties for frequently changed values
- Minimize the number of theme variants to improve performance

## Best Practices

1. Maintain consistency with your app's overall design system
2. Test themes across different devices and screen sizes
3. Ensure adequate contrast for readability
4. Consider cultural differences when selecting colors
5. Provide both light and dark mode options
6. Maintain accessibility standards across all themes
7. Document your theme customization options for team members
8. Use semantic color names rather than literal color values