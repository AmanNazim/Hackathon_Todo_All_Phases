#!/bin/bash
# Script to test task normalization scenarios
# This is a helper script for the task normalization skill

INPUT="$1"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 \"task input to normalize\""
    echo "This script demonstrates the normalization process"
    exit 1
fi

echo "Normalizing Task: '$INPUT'"
echo "========================="

# Remove polite prefixes and priority indicators
NORMALIZED=$(echo "$INPUT" | sed -E 's/^(please |remind me to |help me to |can you |would you )//i' | sed -E 's/^urgent: //i' | sed -E 's/^high priority: //i' | sed -E 's/^low priority: //i')

# Extract potential temporal hints (these go to description)
TEMPORAL_HINTS=$(echo "$NORMALIZED" | grep -oE "(before|after|on|by|until|during|for) [^,;]*" || echo "")

# Extract title (main action) - remove temporal hints and parentheses content
TITLE=$(echo "$NORMALIZED" | sed -E 's/\([^)]*\)//g' | sed -E 's/(before|after|on|by|until|during|for) [^,;]*//g' | sed -E 's/[[:space:]]+/ /g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# Determine priority based on explicit indicators
PRIORITY="normal"
if [[ "$INPUT" =~ (urgent|asap|immediately|emergency|critical|important) ]]; then
    PRIORITY="high"
elif [[ "$INPUT" =~ (whenever|optional|maybe|if possible|low priority) ]]; then
    PRIORITY="low"
fi

# Extract tags (from parentheses or explicit categories)
TAGS="[]"
if [[ "$INPUT" =~ \(([a-zA-Z0-9, -]+)\) ]]; then
    TAGS_MATCH="${BASH_REMATCH[1]}"
    # Convert to JSON array format
    TAGS="["
    IFS=',' read -ra TAG_ARRAY <<< "$TAGS_MATCH"
    for i in "${!TAG_ARRAY[@]}"; do
        if [ $i -gt 0 ]; then
            TAGS="$TAGS, "
        fi
        TAG_CLEAN=$(echo "${TAG_ARRAY[i]}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr '[:upper:]' '[:lower:]')
        TAGS="$TAGS\"$TAG_CLEAN\""
    done
    TAGS="$TAGS]"
fi

# Set description based on temporal hints or other context
DESCRIPTION="null"
if [ -n "$TEMPORAL_HINTS" ]; then
    DESCRIPTION="\"$TEMPORAL_HINTS\""
elif [ -z "$TEMPORAL_HINTS" ] && [[ "$NORMALIZED" != "$TITLE" ]]; then
    ADDITIONAL=$(echo "$NORMALIZED" | sed "s/$TITLE//g" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -n "$ADDITIONAL" ]; then
        DESCRIPTION="\"$ADDITIONAL\""
    fi
fi

# Output the normalized task object
echo "{"
echo "  \"title\": \"$TITLE\","
echo "  \"description\": $DESCRIPTION,"
echo "  \"priority\": \"$PRIORITY\","
echo "  \"tags\": $TAGS,"
echo "  \"due_date\": null,"
echo "  \"recurrence\": null"
echo "}"

echo "========================="
echo "This script demonstrates the normalization process for educational purposes."
echo "Actual implementation would include more sophisticated text processing."