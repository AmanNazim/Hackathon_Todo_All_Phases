#!/bin/bash
# Premium UI Validator Script
# Validates premium UI components and ensures sophisticated design compliance

UI_COMPONENT_FILE="$1"

if [ -z "$UI_COMPONENT_FILE" ]; then
    echo "Usage: $0 <ui_component_file>"
    echo "Validates premium UI component files for CLI applications"
    exit 1
fi

echo "Validating premium UI component: $UI_COMPONENT_FILE"
echo "=================================================="

if [ ! -f "$UI_COMPONENT_FILE" ]; then
    echo "ERROR: UI component file does not exist: $UI_COMPONENT_FILE"
    exit 1
fi

# Check if it's a Python file
if [[ "$UI_COMPONENT_FILE" == *.py ]]; then
    echo "Checking Python syntax..."
    if ! python3 -m py_compile "$UI_COMPONENT_FILE" 2>/dev/null; then
        echo "ERROR: Invalid Python syntax in $UI_COMPONENT_FILE"
        exit 1
    fi
    echo "✓ Python syntax is valid"

    # Check for premium UI patterns
    echo "Checking for premium UI patterns..."

    if grep -q "rich\." "$UI_COMPONENT_FILE"; then
        echo "✓ Rich library integration found"
    else
        echo "⚠️  Warning: Rich library integration not found"
    fi

    if grep -q "PremiumUIManager\|PremiumThemeProvider\|PremiumLayoutEngine" "$UI_COMPONENT_FILE"; then
        echo "✓ Premium UI component classes found"
    else
        echo "ℹ️  No premium UI classes detected"
    fi

    if grep -q "gradient\|TrueColor\|24-bit\|theme" "$UI_COMPONENT_FILE"; then
        echo "✓ Advanced color/gradient patterns found"
    else
        echo "ℹ️  No advanced color patterns detected"
    fi

    if grep -q "async\|await\|asyncio" "$UI_COMPONENT_FILE"; then
        echo "✓ Asynchronous UI patterns found"
    else
        echo "ℹ️  No asynchronous patterns detected"
    fi

elif [[ "$UI_COMPONENT_FILE" == *.json ]]; then
    echo "Checking JSON format..."
    if ! python3 -m json.tool "$UI_COMPONENT_FILE" > /dev/null 2>&1; then
        echo "ERROR: Invalid JSON format in $UI_COMPONENT_FILE"
        exit 1
    fi
    echo "✓ JSON format is valid"

    # Check for premium theme properties
    if grep -q '"gradient"' "$UI_COMPONENT_FILE"; then
        echo "✓ Gradient theme properties found"
    fi
    if grep -q '"corporate"\|"modern"\|"enterprise"' "$UI_COMPONENT_FILE"; then
        echo "✓ Premium theme types found"
    fi

elif [[ "$UI_COMPONENT_FILE" == *.yaml ]] || [[ "$UI_COMPONENT_FILE" == *.yml ]]; then
    echo "Checking YAML format..."
    if ! python3 -c "import yaml; yaml.safe_load(open('$UI_COMPONENT_FILE'))" 2>/dev/null; then
        echo "ERROR: Invalid YAML format in $UI_COMPONENT_FILE"
        exit 1
    fi
    echo "✓ YAML format is valid"
else
    echo "Warning: Unknown file format. Expected .py, .json, .yaml, or .yml"
fi

# Check for accessibility features
echo "Checking for accessibility features..."
if grep -i -E "(accessibility|screen.*reader|contrast|a11y|wcag)" "$UI_COMPONENT_FILE" > /dev/null; then
    echo "✓ Accessibility features detected"
else
    echo "ℹ️  No accessibility features detected"
fi

# Check for responsive design patterns
echo "Checking for responsive design patterns..."
if grep -i -E "(responsive|adaptive|terminal.*size|shutil.*get_terminal_size)" "$UI_COMPONENT_FILE" > /dev/null; then
    echo "✓ Responsive design patterns detected"
else
    echo "ℹ️  No responsive design patterns detected"
fi

echo "=================================================="
echo "Premium UI validation completed for: $UI_COMPONENT_FILE"
echo "This script validates sophisticated UI components for CLI applications."
echo "For full validation, ensure components follow premium design principles."