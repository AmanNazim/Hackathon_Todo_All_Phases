---
name: console-ux-skill
description: Defines advanced CLI user experience (UX) design and implementation strategies to produce premium-grade interactive command-line applications. Includes color schemes, text formatting, animations, emoji indicators, interactive elements, accessibility considerations, and environment detection.
---

# Console UX Skill

This skill defines advanced CLI user experience (UX) design and implementation strategies to produce **premium-grade interactive command-line applications**.

## 1. UX Specification

### Color Palette Strategy
- **Primary Colors**: Use ANSI escape codes for consistent color output
- **Status Indicators**:
  - Success: Green (32) or Bright Green (92)
  - Warning: Yellow (33) or Bright Yellow (93)
  - Error: Red (31) or Bright Red (91)
  - Info: Blue (34) or Bright Blue (94)
  - Neutral: White (37) or Gray (90)

### Typography & Formatting Conventions
- **Headers**: Bold + Underline for main sections
- **Commands**: Bold formatting for CLI commands
- **Arguments**: Italic or highlighted for arguments
- **Status messages**: Consistent formatting with appropriate colors
- **Code blocks**: Monospace formatting with background color

### Output Formatting Conventions
- Consistent indentation (2 spaces)
- Clear section separation
- Logical grouping of related information
- Balanced whitespace usage

### Animation Guidelines
- Subtle progress indicators only
- No distracting animations
- Respect NO_COLOR and non-TTY environments
- Use simple text-based animations (spinners, progress bars)

## 2. Components & APIs

### Core Component APIs

#### Color Text Utilities
```python
def color_text(text, color_code, bold=False):
    """Apply color and formatting to text"""
    pass

def success(text):
    """Format success message"""
    pass

def warning(text):
    """Format warning message"""
    pass

def error(text):
    """Format error message"""
    pass

def info(text):
    """Format info message"""
    pass
```

#### Layout Components
```python
def print_header(title, underline_char='='):
    """Print a formatted header"""
    pass

def alert_success(msg):
    """Display success alert with appropriate styling"""
    pass

def alert_warning(msg):
    """Display warning alert with appropriate styling"""
    pass

def alert_error(msg):
    """Display error alert with appropriate styling"""
    pass

def bordered_panel(content, title=None):
    """Display content in a bordered panel"""
    pass
```

#### Interactive Components
```python
def spinner(message="Processing..."):
    """Display animated spinner with message"""
    pass

def progress_bar(current, total, message="Progress:"):
    """Display progress bar with percentage"""
    pass

def interactive_prompt(question, default=None):
    """Display interactive prompt with validation"""
    pass

def confirm_action(message="Are you sure?"):
    """Get yes/no confirmation from user"""
    pass
```

#### Data Display Components
```python
def table(rows, headers=None, alignments=None):
    """Display data in tabular format"""
    pass

def render_task_list(tasks):
    """Display tasks in a formatted list with status indicators"""
    pass

def render_menu(options, title="Menu"):
    """Display interactive menu with options"""
    pass
```

## 3. Implementation Templates

### Environment Detection Utility
```python
import os
import sys
from typing import Dict, Any

class EnvironmentDetector:
    def __init__(self):
        self.no_color = os.getenv('NO_COLOR', '') != ''
        self.is_tty = sys.stdout.isatty()
        self.term = os.getenv('TERM', 'unknown')
        self.is_dumb = self.term == 'dumb'

    def use_colors(self) -> bool:
        return self.is_tty and not self.no_color and not self.is_dumb

    def use_animation(self) -> bool:
        return self.is_tty and not self.no_color and not self.is_dumb
```

### Color Utility Class
```python
class ColorFormatter:
    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
    }

    def __init__(self, enabled=True):
        self.enabled = enabled

    def format(self, text: str, *styles) -> str:
        if not self.enabled:
            return text
        style_str = ''.join(self.COLORS.get(s, '') for s in styles)
        return f"{style_str}{text}{self.COLORS['reset']}"
```

### UX Manager Class Template
```python
class UXManager:
    def __init__(self):
        self.env = EnvironmentDetector()
        self.colors = ColorFormatter(self.env.use_colors())

    def header(self, text: str):
        """Print formatted header"""
        if self.env.use_colors():
            print(self.colors.format(f"\n{text}", 'bold', 'underline'))
        else:
            print(f"\n{text}\n" + "="*len(text))

    def success(self, message: str):
        """Print success message"""
        if self.env.use_colors():
            print(self.colors.format(f"✓ {message}", 'bright_green'))
        else:
            print(f"[SUCCESS] {message}")

    def warning(self, message: str):
        """Print warning message"""
        if self.env.use_colors():
            print(self.colors.format(f"⚠ {message}", 'bright_yellow'))
        else:
            print(f"[WARNING] {message}")

    def error(self, message: str):
        """Print error message"""
        if self.env.use_colors():
            print(self.colors.format(f"✗ {message}", 'bright_red'))
        else:
            print(f"[ERROR] {message}")

    def info(self, message: str):
        """Print info message"""
        if self.env.use_colors():
            print(self.colors.format(f"ℹ {message}", 'bright_blue'))
        else:
            print(f"[INFO] {message}")
```

## 4. Edge Cases & Validation

### Environment Handling Matrix

| Environment | Colors | Animation | Formatting |
|-------------|--------|-----------|------------|
| TTY + Color | Enabled | Enabled | Full |
| TTY + NO_COLOR | Disabled | Disabled | Text-only |
| TTY + TERM=dumb | Disabled | Disabled | Minimal |
| Non-TTY (pipe) | Disabled | Disabled | Plain text |
| Script mode | Disabled | Disabled | Minimal |

### Validation Checklist
- [ ] Check if stdout is a TTY
- [ ] Respect NO_COLOR environment variable
- [ ] Handle TERM=dumb appropriately
- [ ] Fallback to plain text when colors disabled
- [ ] Validate Unicode/emoji support in terminal
- [ ] Test with various terminal emulators
- [ ] Ensure accessibility compliance

### Fallback Strategies
- **Colors disabled**: Use text-based indicators (✓, ✗, ⚠, ℹ)
- **Animations disabled**: Use static status updates
- **Emoji support missing**: Use text equivalents
- **Non-TTY output**: Use plain text with minimal formatting

## 5. Best Practices & References

### Color Usage Principles
- Use color for status indicators only (success, warning, error, info)
- Do not rely on color alone for meaning — include text or icons
- Offer optional color themes and respect `NO_COLOR`

### Consistency & Hierarchy
- Commands, arguments, flags, and output blocks follow consistent scheme
- Group sections with headers and spacing
- Maintain visual hierarchy with appropriate formatting

### Feedback & Interaction
- Provide structured feedback for user actions
- Use progress indicators, spinners, and subtle animations appropriately
- Detect non-TTY and fall back gracefully

### Symbol & Icon Usage
- Standard Unicode symbols for success/failure/status
- Use emojis optionally (with user toggle capability)

### Adaptive Onboarding UX
- Show context-aware hints and help prompts
- Provide immediate inline help on error or invalid input

### Structured Output Components
- Bordered panels, headings, task lists
- Tabular formats when appropriate
- Indentation and white-space for clarity

## 6. Learning References

### 1. OpenSource.com CLI UX Best Practices
Key practices for color, input/output consistency and ordering of arguments
- URL: https://opensource.com/article/18/4/cli-ux

### 2. Command Line Interface Guidelines
Best CLI design conventions and interactive behavior flags, including NO_COLOR and non-TTY handling
- URL: https://clig.dev/

### 3. Thoughtworks CLI UX Engineering Guide
Expressive flags, transparent actions, and help accessibility best-practices
- URL: https://thoughtworks.github.io/cli-guidelines/

### 4. Accessibility CLI Considerations
Respect environment variables like NO_COLOR and non-interactive modes to avoid harmful animations
- URL: https://www.w3.org/WAI/

### 5. CLI UX Recommendations from CLI-UX Designers
Principles of consistent messaging, symbol usage, and accessibility in CLI
- URL: https://uxdesign.cc/cli-ux-design-principles-4d8d4a5c4e4c

### Additional Resources
- ANSI Escape Codes: https://en.wikipedia.org/wiki/ANSI_escape_code
- NO_COLOR Specification: https://no-color.org/
- Terminal Capability Database: https://man7.org/linux/man-pages/man5/termcap.5.html

## Helper Tools

The skill includes:
- `scripts/ux_tester.sh` - Command-line helper for testing UX components
- `references/ux-patterns.md` - Detailed UX patterns and examples
- `assets/ux-components.json` - Component specification schema