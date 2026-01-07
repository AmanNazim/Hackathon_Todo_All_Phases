#!/bin/bash
# Script to validate theme configurations
# This is a helper script for the dynamic CLI theme engine skill

THEME_FILE="$1"

if [ -z "$THEME_FILE" ]; then
    echo "Usage: $0 <theme_config_file>"
    echo "Validates theme configuration files for CLI applications"
    exit 1
fi

echo "Validating theme configuration: $THEME_FILE"
echo "=========================================="

if [ ! -f "$THEME_FILE" ]; then
    echo "ERROR: Theme file does not exist: $THEME_FILE"
    exit 1
fi

# Check if it's a JSON file
if [[ "$THEME_FILE" == *.json ]]; then
    echo "Checking JSON format..."
    if ! python3 -m json.tool "$THEME_FILE" > /dev/null 2>&1; then
        echo "ERROR: Invalid JSON format in $THEME_FILE"
        exit 1
    fi
    echo "✓ JSON format is valid"

    # Check for required theme properties
    echo "Checking theme properties..."
    if grep -q '"colors"' "$THEME_FILE"; then
        echo "✓ Colors property found"
    else
        echo "⚠️  Warning: 'colors' property not found"
    fi

    if grep -q '"styles"' "$THEME_FILE"; then
        echo "✓ Styles property found"
    else
        echo "⚠️  Warning: 'styles' property not found"
    fi

    if grep -q '"name"' "$THEME_FILE"; then
        echo "✓ Name property found"
    else
        echo "⚠️  Warning: 'name' property not found"
    fi
elif [[ "$THEME_FILE" == *.yaml ]] || [[ "$THEME_FILE" == *.yml ]]; then
    echo "Checking YAML format..."
    if ! python3 -c "import yaml; yaml.safe_load(open('$THEME_FILE'))" 2>/dev/null; then
        echo "ERROR: Invalid YAML format in $THEME_FILE"
        exit 1
    fi
    echo "✓ YAML format is valid"
else
    echo "Warning: Unknown file format. Expected .json, .yaml, or .yml"
fi

# Check for color format validity (basic check)
echo "Checking color format validity..."
if grep -E '#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})' "$THEME_FILE" > /dev/null; then
    echo "✓ Valid hex color formats found"
else
    echo "ℹ️  No hex color formats found (may use named colors)"
fi

# Check for terminal capability detection patterns
echo "Checking for terminal capability patterns..."
if grep -i -E "(color|term|terminal|ansi|256|rgb)" "$THEME_FILE" > /dev/null; then
    echo "✓ Terminal capability patterns found"
else
    echo "ℹ️  No terminal capability patterns found"
fi

echo "=========================================="
echo "Theme validation completed for: $THEME_FILE"
echo "This script provides basic validation of theme configuration files."
echo "For full validation, implement in your application using Rich, Textual, or Prompt_toolkit."