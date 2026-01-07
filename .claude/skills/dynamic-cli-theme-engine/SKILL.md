---
name: dynamic-cli-theme-engine
description: Enables Python CLI applications to have premium-level interactive themes, including advanced color schemes, emoji indicators, subtle animations, text formatting, and theme-based layouts. Teaches how to implement sophisticated CLI UX patterns with references to Rich, Textual, and Prompt_toolkit libraries.
---

# Dynamic CLI Theme Engine Skill — Spec & Design

## 1. Skill Overview

### Purpose
The Dynamic CLI Theme Engine Skill enables Python CLI applications to achieve premium-level interactive themes, including advanced color schemes, emoji indicators, subtle animations, text formatting, and theme-based layouts. This skill teaches Claude how to implement sophisticated CLI UX patterns that match the quality of top-tier applications like Git, htop, and pip.

### Scope
- Advanced color scheme management (foreground, background, accents)
- Emoji-based indicators for status and context
- Subtle animated transitions and loading states
- Text formatting (bold, italic, underline, color highlights)
- Theme-based layouts and responsive design
- Dynamic theme selection and runtime customization
- Asset generation and management
- Edge-case handling for various terminal environments
- Accessibility compliance and contrast optimization

### Benefits
- Creates premium, professional CLI experiences
- Improves user engagement and usability
- Ensures consistent branding across CLI applications
- Provides adaptive interfaces for different environments
- Offers accessibility-compliant designs

## 2. Theme Strategies

### Color Palettes
- **Solarized**: Carefully selected palette with 16 colors optimized for readability
- **Gruvbox**: Warm, earthy tones with excellent contrast ratios
- **Dracula**: Dark theme with vibrant accent colors
- **Monokai**: High contrast theme with distinct color separation
- **Custom corporate themes**: Brand-specific color schemes

### Formatting Strategies
- **Semantic color usage**:
  - Success: Green tones (✓ completed, ✓ saved)
  - Warning: Yellow/orange tones (⚠️ caution, ⚠️ needs attention)
  - Error: Red tones (❌ failed, ❌ error)
  - Info: Blue tones (ℹ️ information, ℹ️ details)
- **Hierarchy through formatting**: Bold for headers, regular for content, dimmed for metadata
- **Consistent spacing**: Proper padding and margins for visual balance
- **Responsive layouts**: Adapts to terminal width with appropriate wrapping

### Emoji Usage Policies
- **Minimal and contextual**: Use only when they add clear value
- **Status indicators**: ✅ success, ❌ error, ⚠️ warning, ℹ️ info, 🔄 processing
- **Action indicators**: ➕ add, 📝 edit, 🗑️ delete, 📋 copy
- **Avoid overuse**: Maximum 1-2 emojis per line to prevent visual clutter
- **Fallback support**: Ensure text alternatives for terminals without emoji support

### Animation Patterns
- **Loading spinners**: Simple rotating patterns (|/-\), dots (..), or more complex (◐◓◑◒)
- **Progress bars**: Visual indication of long-running operations
- **Subtle highlights**: Brief color flashes for important notifications
- **Smooth transitions**: Between menu states or command results
- **Typing effects**: Simulated typing for narrative or tutorial flows

### Layout Guidelines
- **Panel-based layouts**: Organized sections with clear boundaries
- **Table formats**: For displaying structured data
- **Hierarchical indentation**: For nested information
- **Status bars**: Persistent information at bottom of screen
- **Responsive grids**: Adapts to available terminal width

## 3. Implementation Guidelines

### CLI API Design
```python
# Theme engine API example
class ThemeEngine:
    def __init__(self, theme_name="default"):
        self.theme = self.load_theme(theme_name)

    def apply_style(self, text, style_type):
        return self.theme.apply(text, style_type)

    def create_spinner(self, message):
        return self.theme.spinner(message)

    def render_table(self, data, headers):
        return self.theme.table(data, headers)
```

### Terminal Capability Handling
- **Color depth detection**: 16-color, 256-color, or truecolor support
- **Terminal size detection**: Width and height for responsive layouts
- **Feature availability**: Check for emoji support, animation capabilities
- **Fallback strategies**: Graceful degradation for basic terminals

### Theme Objects & Assets
- **Theme structure**: JSON/YAML configuration files for color schemes
- **Asset management**: Icons, logos, and custom graphics with local caching
- **Runtime switching**: Ability to change themes during execution
- **User preferences**: Override defaults with user settings

### Runtime Dynamic Theme Application
- **Event-driven updates**: Theme changes based on CLI context
- **Context-aware styling**: Different themes for different command types
- **Live preview**: Show theme changes before applying permanently
- **Session persistence**: Remember user's theme choice for future sessions

### Integration with Commands
- **Consistent API**: Uniform styling across all CLI commands
- **Context-sensitive formatting**: Different styles for different command states
- **Error handling**: Graceful styling for error messages and warnings
- **Progress indication**: Visual feedback for long-running operations

## 4. Learning References

### Top CLI Libraries
- **Rich**: https://rich.readthedocs.io/en/stable/ - Advanced formatting and widgets
- **Textual**: https://textual.textualize.io/ - TUI framework for rich terminal apps
- **Prompt_toolkit**: https://python-prompt-toolkit.readthedocs.io/en/master/ - Advanced input handling
- **Click**: https://click.palletsprojects.com/ - Command-line interface creation
- **Typer**: https://typer.tiangolo.com/ - Modern CLI creation with type hints

### Examples of Advanced CLI Apps
- **Git**: Clean, informative output with status indicators
- **htop**: Real-time data visualization with color coding
- **pip**: Clear progress indication and status messages
- **Docker**: Consistent formatting across all commands
- **Kubectl**: Hierarchical information display with status indicators

### Reference Color Palettes
- **Solarized**: http://ethanschoonover.com/solarized
- **Base16**: https://github.com/chriskempson/base16
- **Dracula**: https://draculatheme.com/
- **Gruvbox**: https://github.com/morhetz/gruvbox
- **Material Design Colors**: https://material.io/design/color/

### Advanced UX Guidelines
- **ANSI Escape Codes**: For terminal formatting and colors
- **Unicode Standard**: For emoji and special characters
- **WCAG Guidelines**: For accessibility compliance
- **Terminal Standards**: XTerm, VT100, and other terminal specifications

## 5. Edge Cases

| Edge Case | Detection Strategy | Handling Approach | Fallback |
|-----------|-------------------|-------------------|----------|
| No color support | Check TERM environment variable | Disable color formatting | Plain text output |
| Limited emoji support | Test emoji rendering | Replace with text symbols | Text-only indicators |
| Small terminal size | Get terminal dimensions | Wrap content, truncate if needed | Scrollable or condensed view |
| Windows console | Check OS and terminal type | Use Windows-compatible codes | Standard ANSI codes |
| 16-color terminal | Check COLORTERM variable | Use 16-color palette | Basic color support |
| Terminal resize | Monitor resize events | Redraw interface with new dimensions | Maintain current layout |
| Accessibility mode | Check screen reader environment | High contrast, text-only | Accessible output format |
| Slow connection | Detect network latency | Reduce animations, simplify output | Basic, fast output |
| Low performance | Monitor system resources | Disable heavy animations | Lightweight rendering |
| Non-standard terminal | Check terminal capabilities | Use basic formatting | Conservative styling |

## 6. Recommended Enhancements

### Optional Improvements
- **Theme marketplace**: User-contributed themes with rating system
- **Dynamic color adaptation**: Adjust colors based on time of day or user preference
- **Interactive theme editor**: GUI for creating custom themes
- **Theme sharing**: Export/import themes between users
- **AI-powered theme suggestions**: Recommend themes based on usage patterns

### UX Refinements
- **Micro-interactions**: Small animations for button presses and selections
- **Contextual help**: Tooltips and hints based on current context
- **Progress visualization**: More sophisticated progress indicators
- **Keyboard shortcuts**: Visual indication of available shortcuts
- **Custom cursors**: Themed cursor styles for different modes

### Accessibility Considerations
- **High contrast mode**: Enhanced contrast for visually impaired users
- **Screen reader compatibility**: Proper ARIA labels and semantic structure
- **Keyboard navigation**: Full functionality without mouse interaction
- **Color-blind friendly**: Ensure information isn't conveyed by color alone
- **Text size adjustment**: Support for different text scaling preferences

## 7. Output Examples

### Sample CLI Renderings
```
┌─────────────────────────────────────────────────────────┐
│                    TODO APPLICATION                     │
├─────────────────────────────────────────────────────────┤
│ ✅ [ ] Buy groceries (due: tomorrow)                    │
│ ⚠️ [ ] Call doctor (due: today)                        │
│ ❌ [x] Finish report (completed)                        │
└─────────────────────────────────────────────────────────┘
```

### Example Color Themes
- **Dark Theme**: Background: #282c34, Text: #abb2bf, Accent: #61afef
- **Light Theme**: Background: #fafafa, Text: #263238, Accent: #2196f3
- **Solarized Dark**: Background: #002b36, Text: #839496, Accent: #2aa198

### Example Emoji Usage
- Task Status: ✅ Completed, 🔄 In Progress, ❌ Failed, ⏸️ Paused
- System Status: 🟢 Online, 🔴 Offline, 🟡 Warning, 🔵 Maintenance
- Actions: ➕ Add, 📝 Edit, 🗑️ Delete, 📋 Copy, 📤 Export

### Animated Transition Demo Descriptions
- **Loading**: "Processing your request [◐◓◑◒]"
- **Success**: Brief green flash with checkmark animation
- **Error**: Red pulse with error indicator
- **Menu Transition**: Smooth fade between different views
- **Progress**: Animated progress bar with percentage indicator

## Helper Tools

The skill includes:
- `scripts/theme_validator.sh` - Command-line helper for validating theme configurations
- `references/cli-ux-patterns.md` - Detailed CLI UX patterns and examples
- `assets/sample-themes.json` - Sample theme configurations for reference