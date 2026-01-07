---
name: console-ux-skill
description: Defines advanced CLI user experience (UX) design and implementation strategies to produce premium-grade interactive command-line applications. Includes sophisticated color schemes, advanced animations, complex layouts, professional typography, enterprise accessibility, and environment-adaptive rendering using Rich, Textual, and Prompt_toolkit libraries.
---

# Console UX Skill - Premium CLI User Experience Design

This skill defines **advanced CLI user experience (UX) design and implementation strategies** to produce **premium-grade interactive command-line applications** with sophisticated visual design comparable to modern web UIs with CSS/Tailwind sophistication.

## 1. Premium UX Specification

### Advanced Color Strategy
- **Corporate Color Systems**: Sophisticated brand-aligned palettes with gradient support
- **TrueColor 24-bit Support**: Full 16.7 million color spectrum for premium visual quality
- **Gradient Color Transitions**: Smooth color blending for modern visual effects
- **Semantic Color Mapping**: Context-aware color assignment with accessibility compliance
- **Dynamic Theme Switching**: Runtime theme adaptation with smooth transitions
- **Color Psychology Integration**: Strategic color usage for user behavior guidance

### Professional Typography & Formatting
- **Advanced Text Composition**: Mixed formatting with bold, italic, underline, strikethrough, superscript, subscript
- **Responsive Font Sizing**: Adaptive text sizing based on terminal dimensions
- **Visual Hierarchy Systems**: Multi-level heading structures with consistent styling
- **Rich Text Styling**: Complex text formatting with mixed attributes and colors
- **Typography Pairing**: Strategic font-style combinations for enhanced readability
- **Line Spacing & Kerning**: Professional spacing controls for premium appearance

### Sophisticated Layout Architecture
- **Grid-Based Layouts**: CSS Grid-inspired terminal layouts with row/column management
- **Flexbox-Like Behavior**: Adaptive component positioning and sizing
- **Component-Based Architecture**: Reusable styled UI components with consistent design
- **Responsive Design Patterns**: Terminal-size adaptive layouts with breakpoints
- **Z-Index Management**: Layered component rendering with depth perception
- **Container Queries**: Context-aware component sizing and styling

### Complex Animation Systems
- **Physics-Based Motion**: Realistic easing functions with bounce, elastic effects
- **Multi-Stage Loading Sequences**: Animated loading flows with progress states
- **Micro-Interactions**: Subtle animations for user feedback and engagement
- **Particle Effects**: Advanced visual effects for premium user experience
- **Transition Animations**: Smooth state changes with custom easing curves
- **Performance-Optimized Rendering**: Efficient animation without terminal lag

### Enterprise Accessibility Features
- **WCAG 2.1 AA Compliance**: Full accessibility standard adherence
- **Screen Reader Compatibility**: Proper semantic markup for assistive technologies
- **High Contrast Mode**: Enhanced visibility options for visual impairments
- **Keyboard Navigation**: Complete functionality without mouse interaction
- **Color-Blind Friendly**: Information conveyed through multiple channels
- **Text Scaling Support**: Responsive design for different text sizes

## 2. Premium Component APIs

### Advanced Color Text Utilities
```python
from rich.text import Text
from rich.style import Style

class PremiumColorFormatter:
    """Sophisticated color and text formatting with gradient support"""

    @staticmethod
    def gradient_text(text: str, start_color: str, end_color: str) -> Text:
        """Create gradient-colored text for premium visual effects"""
        pass

    @staticmethod
    def themed_text(text: str, theme_style: str) -> Text:
        """Apply theme-based styling with semantic meaning"""
        pass

    @staticmethod
    def animated_text(text: str, effect: str) -> Text:
        """Create animated text with typing or other effects"""
        pass

def premium_success(text: str, icon: str = "✓") -> Text:
    """Premium success message with gradient styling"""
    pass

def premium_warning(text: str, icon: str = "⚠") -> Text:
    """Premium warning message with attention-grabbing effects"""
    pass

def premium_error(text: str, icon: str = "✗") -> Text:
    """Premium error message with enhanced visibility"""
    pass

def premium_info(text: str, icon: str = "ℹ") -> Text:
    """Premium info message with professional styling"""
    pass
```

### Sophisticated Layout Components
```python
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

class PremiumLayoutEngine:
    """Advanced layout management with CSS Grid-like capabilities"""

    @staticmethod
    def responsive_panel(content, title=None, border_style="premium") -> Panel:
        """Create responsive panels with advanced styling"""
        pass

    @staticmethod
    def gradient_table(data, headers, colors=["#3b82f6", "#8b5cf6"]) -> Table:
        """Create tables with gradient headers and sophisticated styling"""
        pass

    @staticmethod
    def flex_container(items, direction="row", justify="start") -> Layout:
        """CSS Flexbox-inspired container layout"""
        pass

def premium_header(title: str, style: str = "bold #3b82f6") -> Panel:
    """Premium header with gradient effects and professional styling"""
    pass

def premium_alert_success(msg: str) -> Panel:
    """Premium success alert with animated effects"""
    pass

def premium_alert_warning(msg: str) -> Panel:
    """Premium warning alert with attention-grabbing design"""
    pass

def premium_alert_error(msg: str) -> Panel:
    """Premium error alert with enhanced visibility"""
    pass

def premium_bordered_panel(content, title=None) -> Panel:
    """Premium bordered panel with gradient borders"""
    pass
```

### Advanced Interactive Components
```python
import asyncio
from rich.spinner import Spinner
from rich.progress import Progress, BarColumn, TextColumn

class PremiumInteractiveEngine:
    """Sophisticated interactive components with modern UX patterns"""

    @staticmethod
    async def premium_spinner(message: str = "Processing...",
                            spinner_type: str = "dots",
                            color: str = "#3b82f6") -> Spinner:
        """Advanced animated spinner with customizable effects"""
        pass

    @staticmethod
    def premium_progress_bar(total: int,
                           description: str = "Progress",
                           completed_style: str = "#10b981",
                           pending_style: str = "#e5e7eb") -> Progress:
        """Premium progress bar with gradient effects and smooth animation"""
        pass

    @staticmethod
    def premium_interactive_prompt(question: str,
                                 options: list = None,
                                 default: str = None) -> str:
        """Advanced interactive prompt with validation and suggestions"""
        pass

    @staticmethod
    def premium_confirm_action(message: str = "Are you sure?",
                             confirm_style: str = "bold #ef4444",
                             cancel_style: str = "dim") -> bool:
        """Premium confirmation with enhanced visual feedback"""
        pass
```

### Professional Data Display Components
```python
from rich.tree import Tree
from rich.columns import Columns

class PremiumDataDisplay:
    """Sophisticated data visualization components"""

    @staticmethod
    def premium_table(rows: list,
                     headers: list = None,
                     style: str = "premium",
                     colors: dict = None) -> Table:
        """Advanced table with gradient headers and professional styling"""
        pass

    @staticmethod
    def premium_task_list(tasks: list,
                         status_colors: dict = None,
                         show_progress: bool = True) -> Tree:
        """Premium task list with visual progress indicators"""
        pass

    @staticmethod
    def premium_menu(options: list,
                    title: str = "Menu",
                    style: str = "premium") -> Panel:
        """Sophisticated menu with hover effects and animations"""
        pass

    @staticmethod
    def premium_dashboard(panels: list,
                        layout: str = "grid") -> Layout:
        """Premium dashboard with multiple panels and responsive design"""
        pass
```

## 3. Premium Implementation Templates

### Advanced Theme Provider
```python
from rich.theme import Theme
from rich.style import Style

class PremiumThemeProvider:
    """Sophisticated theme management with dynamic switching"""

    def __init__(self):
        self.themes = {
            "corporate": Theme({
                "success": Style(color="#10b981", bold=True),
                "warning": Style(color="#f59e0b", bold=True),
                "error": Style(color="#ef4444", bold=True),
                "info": Style(color="#3b82f6", bold=True),
                "header": Style(color="#6366f1", bold=True, underline=True),
                "accent": Style(color="#8b5cf6", italic=True),
            }),
            "modern": Theme({
                "success": Style(color="#22c55e", bold=True),
                "warning": Style(color="#f97316", bold=True),
                "error": Style(color="#dc2626", bold=True),
                "info": Style(color="#0ea5e9", bold=True),
                "header": Style(color="#06b6d4", bold=True, italic=True),
                "accent": Style(color="#ec4899", bold=True),
            }),
            "enterprise": Theme({
                "success": Style(color="#059669", bold=True),
                "warning": Style(color="#d97706", bold=True),
                "error": Style(color="#dc2626", bold=True),
                "info": Style(color="#0284c7", bold=True),
                "header": Style(color="#4f46e5", bold=True, underline=True),
                "accent": Style(color="#7c3aed", italic=True),
            })
        }
        self.current_theme = "corporate"

    def get_style(self, style_name: str) -> Style:
        """Get style from current theme"""
        return self.themes[self.current_theme].get(style_name)

    def switch_theme(self, theme_name: str):
        """Switch to different theme with smooth transition"""
        if theme_name in self.themes:
            self.current_theme = theme_name
```

### Premium UX Manager Class
```python
from rich.console import Console
from rich.live import Live
from rich.status import Status

class PremiumUXManager:
    """Advanced UX management with sophisticated rendering capabilities"""

    def __init__(self):
        self.console = Console()
        self.theme_provider = PremiumThemeProvider()
        self.is_interactive = self.console.is_interactive

    def render_header(self, text: str, style: str = "header"):
        """Render premium header with gradient effects"""
        styled_text = Text(text, style=self.theme_provider.get_style(style))
        self.console.print(Panel(styled_text, border_style="premium"))

    def render_success(self, message: str):
        """Render premium success message with animation"""
        success_style = self.theme_provider.get_style("success")
        success_text = Text(f"✅ {message}", style=success_style)
        self.console.print(success_text)

    def render_warning(self, message: str):
        """Render premium warning message with attention-grabbing effect"""
        warning_style = self.theme_provider.get_style("warning")
        warning_text = Text(f"⚠️ {message}", style=warning_style)
        self.console.print(warning_text)

    def render_error(self, message: str):
        """Render premium error message with enhanced visibility"""
        error_style = self.theme_provider.get_style("error")
        error_text = Text(f"❌ {message}", style=error_style)
        self.console.print(error_text)

    def render_info(self, message: str):
        """Render premium info message with professional styling"""
        info_style = self.theme_provider.get_style("info")
        info_text = Text(f"ℹ️ {message}", style=info_style)
        self.console.print(info_text)

    def render_loading(self, message: str = "Loading..."):
        """Render premium loading indicator with smooth animation"""
        return Status(message, spinner="dots", spinner_style="premium")

    def render_table(self, data: list, headers: list = None):
        """Render premium table with sophisticated styling"""
        table = Table()
        if headers:
            for header in headers:
                table.add_column(header, style="header")
        else:
            for i in range(len(data[0]) if data else 0):
                table.add_column(f"Column {i+1}", style="header")

        for row in data:
            table.add_row(*[str(item) for item in row])

        self.console.print(table)

    def render_dashboard(self, widgets: list):
        """Render premium dashboard with multiple components"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        self.console.print(layout)
```

### Advanced Interactive Flow Controller
```python
import asyncio
from rich.prompt import Prompt, Confirm

class PremiumFlowController:
    """Sophisticated flow control with advanced UX patterns"""

    def __init__(self, ux_manager: PremiumUXManager):
        self.ux_manager = ux_manager
        self.console = ux_manager.console

    async def run_with_loading(self, coroutine, loading_message: str = "Processing..."):
        """Run async operation with premium loading indicator"""
        with self.ux_manager.render_loading(loading_message) as status:
            result = await coroutine
        return result

    def get_user_input(self, prompt_text: str,
                      validator=None,
                      default=None,
                      password: bool = False):
        """Get user input with premium validation and feedback"""
        return Prompt.ask(
            prompt_text,
            default=default,
            password=password,
            console=self.console
        )

    def confirm_action(self, message: str = "Are you sure?"):
        """Get confirmation with premium styling"""
        return Confirm.ask(
            message,
            console=self.console
        )

    def select_option(self, message: str, options: list):
        """Display premium selection interface"""
        choices = [f"{i+1}. {option}" for i, option in enumerate(options)]
        self.ux_manager.render_info(message)
        for choice in choices:
            self.console.print(f"  {choice}")

        selection = Prompt.ask(
            "Select option (number)",
            choices=[str(i+1) for i in range(len(options))],
            console=self.console
        )

        return options[int(selection) - 1]
```

## 4. Advanced Environment Detection & Adaptive Rendering

### Terminal Capability Intelligence
```python
import os
import sys
import shutil
from typing import Dict, Any, Optional

class TerminalIntelligence:
    """Advanced terminal capability detection and adaptive rendering"""

    def __init__(self):
        self.terminal_size = shutil.get_terminal_size()
        self.color_depth = self._detect_color_depth()
        self.supported_features = self._detect_features()
        self.accessibility_mode = self._detect_accessibility()

    def _detect_color_depth(self) -> int:
        """Detect terminal color depth capability (16, 256, or 24-bit)"""
        # Check environment variables and terminal capabilities
        if os.getenv('COLORTERM') == 'truecolor' or os.getenv('TERM_PROGRAM') == 'iTerm.app':
            return 24  # TrueColor support
        elif os.getenv('TERM') and any(t in os.getenv('TERM') for t in ['256', 'xterm-256']):
            return 8  # 256 color support
        else:
            return 4  # Basic 16 color support

    def _detect_features(self) -> Dict[str, bool]:
        """Detect advanced terminal features"""
        return {
            'emoji_support': self._check_emoji_support(),
            'animation_support': self._check_animation_support(),
            'mouse_support': self._check_mouse_support(),
            'unicode_support': self._check_unicode_support(),
            'truecolor_support': self.color_depth == 24
        }

    def _detect_accessibility(self) -> Dict[str, bool]:
        """Detect accessibility requirements"""
        return {
            'high_contrast': os.getenv('HIGH_CONTRAST', '').lower() == '1',
            'screen_reader': bool(os.getenv('SCREEN_READER')),
            'reduced_motion': os.getenv('REDUCED_MOTION', '').lower() == '1'
        }

    def get_rendering_strategy(self) -> str:
        """Get optimal rendering strategy based on terminal capabilities"""
        if self.accessibility_mode['high_contrast']:
            return 'high_contrast'
        elif self.supported_features['truecolor_support']:
            return 'premium'
        elif self.color_depth >= 8:
            return 'enhanced'
        else:
            return 'basic'
```

### Adaptive Rendering Engine
```python
class AdaptiveRenderingEngine:
    """Intelligent rendering that adapts to terminal capabilities"""

    def __init__(self):
        self.terminal_intel = TerminalIntelligence()
        self.rendering_strategy = self.terminal_intel.get_rendering_strategy()

    def render_with_fallback(self, premium_component, fallback_component):
        """Render premium component with fallback for limited terminals"""
        if self.rendering_strategy == 'premium':
            return premium_component
        else:
            return fallback_component

    def adjust_for_accessibility(self, component):
        """Adjust component for accessibility requirements"""
        if self.terminal_intel.accessibility_mode['high_contrast']:
            # Apply high contrast styling
            component.style = component.style.update(color="white", bgcolor="black")
        if self.terminal_intel.accessibility_mode['reduced_motion']:
            # Remove animations
            component.animation = None
        return component
```

## 5. Premium UX Patterns & Validation

### Sophisticated UX Patterns
- **Progressive Disclosure**: Show information in layers to avoid overwhelming users
- **Contextual Help**: Provide relevant help based on current user context
- **Predictive Suggestions**: Offer intelligent suggestions based on user behavior
- **Micro-Feedback**: Provide immediate feedback for all user interactions
- **Consistent Navigation**: Maintain consistent navigation patterns throughout
- **Error Recovery**: Help users recover from errors with clear guidance

### Premium Validation Matrix

| Feature | Premium | Enhanced | Basic | Fallback |
|---------|---------|----------|-------|----------|
| Color Depth | 24-bit TrueColor | 256-color | 16-color | Monochrome |
| Animation | Physics-based | Smooth | Basic | Static |
| Layout | Grid/Flexbox-like | Structured | Simple | Linear |
| Typography | Rich formatting | Bold/Italic | Plain | Plain |
| Emoji Support | Full set | Selected | None | Text alternatives |
| Accessibility | WCAG AA+ | WCAG A | Basic | Text-only |

### Advanced Validation Checklist
- [ ] Terminal capability detection and adaptive rendering
- [ ] Accessibility compliance with screen readers
- [ ] High contrast mode support
- [ ] Reduced motion preferences respected
- [ ] Color-blind friendly design
- [ ] Keyboard navigation completeness
- [ ] Text scaling accommodation
- [ ] Performance optimization for animations
- [ ] Cross-platform terminal compatibility
- [ ] Graceful degradation for basic terminals

## 6. Premium UX Libraries & Integration

### Rich Library Advanced Patterns
- **Panels with Gradient Borders**: Create sophisticated containers
- **Tables with Header Gradients**: Professional data presentation
- **Trees with Custom Icons**: Hierarchical information display
- **Live Updates without Flicker**: Smooth real-time content updates
- **Syntax Highlighting**: Professional code display
- **Progress with Custom Columns**: Detailed progress information

### Textual Framework Integration
- **TUI Components**: Full terminal user interfaces
- **Event-Driven Updates**: Real-time user interaction
- **CSS-like Styling**: Familiar styling paradigms for terminals
- **Grid Layout System**: Sophisticated component arrangement
- **Focus Management**: Professional keyboard navigation
- **Modal Dialogs**: Temporary overlays for focused interaction

### Prompt_toolkit Advanced Features
- **Multi-line Editing**: Professional text input capabilities
- **Context-Aware Completion**: Intelligent command completion
- **Real-time Syntax Highlighting**: Immediate code feedback
- **Custom Key Bindings**: Personalized interaction patterns
- **Asynchronous Input**: Background processing with user input
- **Advanced Dialogs**: Sophisticated user interaction

### Premium UX Design Principles
- **Visual Hierarchy**: Clear information prioritization
- **Consistent Branding**: Cohesive visual identity
- **Responsive Design**: Adapts to different terminal sizes
- **Performance First**: Fast rendering without lag
- **Accessibility Built-in**: Inclusive design from the start
- **Professional Aesthetics**: Premium visual quality

## 7. Learning References & Premium Resources

### 1. Advanced CLI UX Design Patterns
Comprehensive guide to sophisticated CLI user experience with modern design principles
- URL: https://carlosbecker.com/posts/terminal-apps/

### 2. Rich Library Documentation
Advanced formatting and widgets for premium terminal applications
- URL: https://rich.readthedocs.io/en/latest/

### 3. Textual TUI Framework
Building full terminal user interfaces with CSS-like styling
- URL: https://textual.textualize.io/

### 4. Terminal UI Design Principles
Professional design patterns for terminal applications
- URL: https://blog.klipse.tech/terminal/2021/02/04/terminal-ui.html

### 5. Modern CLI UX Guidelines
Contemporary approaches to command-line user experience
- URL: https://alistapart.com/article/terminal-ui-design/

### Premium Design Resources
- **Color Theory for CLI**: https://color.adobe.com/
- **Terminal Color Palettes**: https://github.com/mbadolato/iTerm2-Color-Schemes
- **Accessibility Standards**: https://www.w3.org/TR/WCAG21/
- **Design Systems Principles**: https://www.designsystems.com/

## Helper Tools

The skill includes:
- `scripts/premium-ux-validator.sh` - Advanced validation for premium UX components
- `references/premium-ux-patterns.md` - Sophisticated UX patterns and examples
- `assets/premium-themes.json` - Premium theme configurations for reference