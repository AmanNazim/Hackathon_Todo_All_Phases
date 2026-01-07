#!/bin/bash
# Premium UX Validator Script
# Validates premium UX components and ensures sophisticated design compliance

UX_COMPONENT_FILE="$1"

if [ -z "$UX_COMPONENT_FILE" ]; then
    echo "Usage: $0 <ux_component_file>"
    echo "Validates premium UX component files for CLI applications"
    exit 1
fi

echo "Validating premium UX component: $UX_COMPONENT_FILE"
echo "=================================================="

if [ ! -f "$UX_COMPONENT_FILE" ]; then
    echo "ERROR: UX component file does not exist: $UX_COMPONENT_FILE"
    exit 1
fi

# Check if it's a Python file
if [[ "$UX_COMPONENT_FILE" == *.py ]]; then
    echo "Checking Python syntax..."
    if ! python3 -m py_compile "$UX_COMPONENT_FILE" 2>/dev/null; then
        echo "ERROR: Invalid Python syntax in $UX_COMPONENT_FILE"
        exit 1
    fi
    echo "✓ Python syntax is valid"

    # Check for premium UX patterns
    echo "Checking for premium UX patterns..."

    if grep -q "rich\." "$UX_COMPONENT_FILE"; then
        echo "✓ Rich library integration found"
    else
        echo "⚠️  Warning: Rich library integration not found"
    fi

    if grep -q "PremiumUXManager\|PremiumThemeProvider\|PremiumLayoutEngine" "$UX_COMPONENT_FILE"; then
        echo "✓ Premium UX component classes found"
    else
        echo "ℹ️  No premium UX classes detected"
    fi

    if grep -q "gradient\|TrueColor\|24-bit\|theme" "$UX_COMPONENT_FILE"; then
        echo "✓ Advanced color/gradient patterns found"
    else
        echo "ℹ️  No advanced color patterns detected"
    fi

    if grep -q "async\|await\|asyncio" "$UX_COMPONENT_FILE"; then
        echo "✓ Asynchronous UX patterns found"
    else
        echo "ℹ️  No asynchronous patterns detected"
    fi

elif [[ "$UX_COMPONENT_FILE" == *.json ]]; then
    echo "Checking JSON format..."
    if ! python3 -m json.tool "$UX_COMPONENT_FILE" > /dev/null 2>&1; then
        echo "ERROR: Invalid JSON format in $UX_COMPONENT_FILE"
        exit 1
    fi
    echo "✓ JSON format is valid"

    # Check for premium theme properties
    if grep -q '"gradient"' "$UX_COMPONENT_FILE"; then
        echo "✓ Gradient theme properties found"
    fi
    if grep -q '"corporate"\|"modern"\|"enterprise"' "$UX_COMPONENT_FILE"; then
        echo "✓ Premium theme types found"
    fi

elif [[ "$UX_COMPONENT_FILE" == *.yaml ]] || [[ "$UX_COMPONENT_FILE" == *.yml ]]; then
    echo "Checking YAML format..."
    if ! python3 -c "import yaml; yaml.safe_load(open('$UX_COMPONENT_FILE'))" 2>/dev/null; then
        echo "ERROR: Invalid YAML format in $UX_COMPONENT_FILE"
        exit 1
    fi
    echo "✓ YAML format is valid"
else
    echo "Warning: Unknown file format. Expected .py, .json, .yaml, or .yml"
fi

# Check for accessibility features
echo "Checking for accessibility features..."
if grep -i -E "(accessibility|screen.*reader|contrast|a11y|wcag)" "$UX_COMPONENT_FILE" > /dev/null; then
    echo "✓ Accessibility features detected"
else
    echo "ℹ️  No accessibility features detected"
fi

# Check for responsive design patterns
echo "Checking for responsive design patterns..."
if grep -i -E "(responsive|adaptive|terminal.*size|shutil.*get_terminal_size)" "$UX_COMPONENT_FILE" > /dev/null; then
    echo "✓ Responsive design patterns detected"
else
    echo "ℹ️  No responsive design patterns detected"
fi

echo "=================================================="
echo "Premium UX validation completed for: $UX_COMPONENT_FILE"
echo "This script validates sophisticated UX components for CLI applications."
echo "For full validation, ensure components follow premium design principles."