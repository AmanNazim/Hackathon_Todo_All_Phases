# Console UI Patterns and Examples

This reference contains detailed UI patterns and examples for the Console UI Skill.

## Color Usage Patterns

### Semantic Color Meanings
```bash
# Success
echo -e "\033[32m✓ Task completed successfully\033[0m"
# Or with bright colors
echo -e "\033[92m✓ Success!\033[0m"

# Warning
echo -e "\033[33m⚠ Warning: Something needs attention\033[0m"
# Or with bright colors
echo -e "\033[93m⚠ Warning!\033[0m"

# Error
echo -e "\033[31m✗ Error: Something went wrong\033[0m"
# Or with bright colors
echo -e "\033[91m✗ Error!\033[0m"

# Info
echo -e "\033[34mℹ Information: Here's some info\033[0m"
# Or with bright colors
echo -e "\033[94mℹ Info\033[0m"
```

### Formatting Combinations
```bash
# Bold + Color
echo -e "\033[1;32mBold Green Text\033[0m"

# Underline + Color
echo -e "\033[4;34mUnderline Blue Text\033[0m"

# Multiple styles
echo -e "\033[1;4;35mBold, Underline Magenta\033[0m"
```

## Layout Patterns

### Header Formatting
```bash
print_header() {
    local title="$1"
    local char="${2:-=}"
    local len=${#title}

    echo
    echo -e "\033[1m$title\033[0m"
    printf '%*s\n' "$len" | tr ' ' "$char"
    echo
}
```

### Bordered Panel
```bash
bordered_panel() {
    local content="$1"
    local title="$2"
    local width=$(tput cols)

    # Calculate width based on content or terminal
    if [ ${#content} -gt $((width - 4)) ]; then
        width=$((width - 2))
    else
        width=$((${#content} + 4))
    fi

    # Top border
    printf '+'
    printf '%*s' $((width - 2)) | tr ' ' '-'
    printf '+\n'

    # Title row (if provided)
    if [ -n "$title" ]; then
        printf '| \033[1m%s\033[0m' "$title"
        printf '%*s' $((width - ${#title} - 4)) | tr ' ' ' '
        printf '|\n'

        # Separator after title
        printf '+'
        printf '%*s' $((width - 2)) | tr ' ' '-'
        printf '+\n'
    fi

    # Content row
    printf '| %s' "$content"
    printf '%*s' $((width - ${#content} - 4)) | tr ' ' ' '
    printf '|\n'

    # Bottom border
    printf '+'
    printf '%*s' $((width - 2)) | tr ' ' '-'
    printf '+\n'
}
```

## Interactive Components

### Spinner Animation
```bash
spinner() {
    local message="${1:-Processing...}"
    local pid=$!
    local delay=0.1
    local spinstr='|/-\\'
    local temp

    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        temp=${spinstr#?}
        printf " [%c]  %s..." "${spinstr%%?}" "$message"
        spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
        for ((i=0; i<${#message}+5; i++)); do
            printf "\b"
        done
    done
    printf "    \b\b"
}
```

### Progress Bar
```bash
progress_bar() {
    local current=$1
    local total=$2
    local message="${3:-Progress:}"

    local percent=$((current * 100 / total))
    local bar_length=30
    local filled_length=$((percent * bar_length / 100))

    printf "%s [" "$message"

    # Filled portion
    for ((i=0; i<filled_length; i++)); do
        printf "="
    done

    # Empty portion
    for ((i=0; i<bar_length-filled_length; i++)); do
        printf " "
    done

    printf "] %d%% (%d/%d)\n" "$percent" "$current" "$total"
}
```

## Environment Detection

### Color Support Detection
```bash
use_colors() {
    if [ -z "$NO_COLOR" ] && [ "$TERM" != "dumb" ] && [ -t 1 ]; then
        return 0  # True - use colors
    else
        return 1  # False - don't use colors
    fi
}
```

### Emoji Support Detection
```bash
has_emoji_support() {
    if command -v locale >/dev/null 2>&1; then
        local lang=$(locale | grep LANG | cut -d= -f2 | cut -d. -f1)
        if [[ "$lang" =~ ^[a-zA-Z_]+\.UTF-8$ ]] || [[ "$lang" == "en_US" ]]; then
            return 0  # Has UTF-8 support
        fi
    fi
    return 1  # No emoji support
}
```

## Component Examples

### Task List Rendering
```bash
render_task_list() {
    local tasks=("$@")
    local index=1

    echo "TASK LIST:"
    echo "--------"
    for task in "${tasks[@]}"; do
        if use_colors(); then
            printf "\033[32m%2d.\033[0m %s\n" "$index" "$task"
        else
            printf "%2d. %s\n" "$index" "$task"
        fi
        ((index++))
    done
    echo
}
```

### Interactive Menu
```bash
interactive_menu() {
    local options=("$@")
    local choice

    echo "Please select an option:"
    for i in "${!options[@]}"; do
        if use_colors(); then
            printf "\033[1m%2d.\033[0m %s\n" $((i+1)) "${options[i]}"
        else
            printf "%2d. %s\n" $((i+1)) "${options[i]}"
        fi
    done

    while true; do
        read -p "Enter choice (1-${#options[@]}): " choice

        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
            echo "${options[$((choice-1))]}"
            break
        else
            if use_colors(); then
                echo -e "\033[93m⚠ Invalid choice. Please try again.\033[0m"
            else
                echo "Invalid choice. Please try again."
            fi
        fi
    done
}
```

## Accessibility Considerations

### High Contrast Mode
For users with visual impairments, ensure sufficient contrast:
```bash
high_contrast_success() {
    if use_colors(); then
        echo -e "\033[1;4;92mSUCCESS\033[0m: $1"
    else
        echo "[SUCCESS] $1"
    fi
}
```

### Screen Reader Compatibility
Always include text alternatives for visual elements:
```bash
accessible_alert() {
    local type="$1"
    local message="$2"

    # Visual indicator with text equivalent
    case "$type" in
        "success")
            if use_colors(); then
                echo -e "\033[92m✓\033[0m SUCCESS: $message"
            else
                echo "[SUCCESS] $message"
            fi
            ;;
        "warning")
            if use_colors(); then
                echo -e "\033[93m⚠\033[0m WARNING: $message"
            else
                echo "[WARNING] $message"
            fi
            ;;
        "error")
            if use_colors(); then
                echo -e "\033[91m✗\033[0m ERROR: $message"
            else
                echo "[ERROR] $message"
            fi
            ;;
    esac
}
```

## Error Handling Patterns

### Consistent Error Format
```bash
error_handler() {
    local message="$1"
    local exit_code="${2:-1}"

    if use_colors(); then
        echo -e "\033[91m✗ ERROR:\033[0m $message" >&2
    else
        echo "ERROR: $message" >&2
    fi

    exit "$exit_code"
}
```

### Validation with Helpful Messages
```bash
validate_input() {
    local input="$1"
    local expected_type="$2"

    case "$expected_type" in
        "number")
            if ! [[ "$input" =~ ^[0-9]+$ ]]; then
                if use_colors(); then
                    echo -e "\033[93m⚠ WARNING:\033[0m Expected a number, got '$input'" >&2
                else
                    echo "WARNING: Expected a number, got '$input'" >&2
                fi
                return 1
            fi
            ;;
        "non_empty")
            if [ -z "$input" ]; then
                if use_colors(); then
                    echo -e "\033[91m✗ ERROR:\033[0m Input cannot be empty" >&2
                else
                    echo "ERROR: Input cannot be empty" >&2
                fi
                return 1
            fi
            ;;
    esac
    return 0
}
```

## Best Practices Summary

1. **Always respect environment variables** like NO_COLOR and TERM
2. **Test with different terminals** to ensure compatibility
3. **Provide text alternatives** for all visual elements
4. **Keep animations minimal** and respectful of performance
5. **Use consistent formatting** throughout your application
6. **Validate inputs gracefully** with helpful error messages
7. **Make output parseable** when used in scripts (non-TTY)
8. **Follow accessibility guidelines** for inclusive design

## Responsive Design for Terminals

### Dynamic Width Detection
```bash
get_terminal_width() {
    if command -v tput >/dev/null 2>&1; then
        tput cols
    else
        # Default to 80 if tput is not available
        echo 80
    fi
}

wrap_text() {
    local text="$1"
    local width=$(get_terminal_width)

    # Wrap text to terminal width
    echo "$text" | fold -w "$width"
}
```

### Adaptive Layouts
```bash
adaptive_table() {
    local width=$(get_terminal_width)

    if [ "$width" -ge 80 ]; then
        # Wide format
        printf "%-5s %-20s %-15s %-10s\n" "ID" "TASK" "STATUS" "PRIORITY"
    else
        # Compact format
        printf "%-3s %-15s\n" "ID" "TASK"
    fi
}
```

These patterns ensure that CLI UIs are both visually appealing and functionally robust across different environments and user needs.