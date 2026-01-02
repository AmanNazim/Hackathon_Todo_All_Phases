#!/bin/bash
# Script to test CLI parsing scenarios
# This is a helper script for the CLI parser skill

INPUT="$1"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 \"user input to parse\""
    echo "This script demonstrates the parsing pipeline stages"
    exit 1
fi

echo "Testing CLI Parser for input: '$INPUT'"
echo "====================================="

# Stage 1: Input Normalization
NORMALIZED=$(echo "$INPUT" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -s ' ')
echo "Stage 1 - Normalized: '$NORMALIZED'"

# Stage 2: Tokenization
echo "Stage 2 - Tokens:"
TOKENS=$(echo "$NORMALIZED" | tr ' ' '\n')
echo "$TOKENS"

# Stage 3: Intent Classification (simulated)
echo "Stage 3 - Intent Classification:"
case "$NORMALIZED" in
    add*|create*|new*)
        echo "  Detected: add/create intent"
        ;;
    delete*|remove*|del*)
        echo "  Detected: delete intent"
        ;;
    list*|show*|view*)
        echo "  Detected: list/view intent"
        ;;
    help*|?*)
        echo "  Detected: help intent"
        ;;
    *)
        echo "  Detected: unknown intent"
        ;;
esac

# Stage 4: Entity Extraction (simulated)
echo "Stage 4 - Entity Extraction:"
if [[ "$NORMALIZED" =~ ^add[[:space:]]+(.*) ]]; then
    ENTITY="${BASH_REMATCH[1]}"
    echo "  Extracted: '$ENTITY' as title/entity"
elif [[ "$NORMALIZED" =~ ^delete[[:space:]]+([0-9]+) ]]; then
    ID="${BASH_REMATCH[1]}"
    echo "  Extracted: '$ID' as identifier"
fi

# Stage 5: Validation (simulated)
echo "Stage 5 - Validation:"
if [ -z "$NORMALIZED" ]; then
    echo "  Status: Invalid - empty input"
elif [ "${#NORMALIZED}" -lt 2 ]; then
    echo "  Status: Ambiguous - input too short"
else
    echo "  Status: Valid - sufficient information"
fi

# Stage 6: Ambiguity Check
echo "Stage 6 - Ambiguity Check:"
if [[ "$NORMALIZED" =~ ^a[[:space:]]+.* ]] && [[ "$NORMALIZED" != "add"* ]]; then
    echo "  Warning: 'a' could be ambiguous (add/another/etc.)"
else
    echo "  Status: Unambiguous"
fi

# Stage 7: Final Result
echo "Stage 7 - Final Parse Result:"
echo "  {"
echo "    \"intent_name\": \"$(case "$NORMALIZED" in add*|create*|new*) echo "add";; delete*|remove*|del*) echo "delete";; list*|show*|view*) echo "list";; help*|?*) echo "help";; *) echo "unknown";; esac)\","
echo "    \"intent_confidence\": \"$(if [ "${#NORMALIZED}" -lt 3 ]; then echo "low"; else echo "high"; fi)\","
echo "    \"normalized_command\": \"$NORMALIZED\","
echo "    \"extracted_entities\": {},"
echo "    \"missing_information\": [],"
echo "    \"ambiguity_flags\": [],"
echo "    \"suggested_clarifications\": [],"
echo "    \"parse_status\": \"$(if [ -z "$NORMALIZED" ]; then echo "invalid"; elif [ "${#NORMALIZED}" -lt 2 ]; then echo "ambiguous"; else echo "success"; fi)\","
echo "    \"parse_reasoning\": \"Basic pattern matching applied\""
echo "  }"

echo "====================================="
echo "This script demonstrates the parsing pipeline for educational purposes."
echo "Actual implementation would include more sophisticated pattern matching."