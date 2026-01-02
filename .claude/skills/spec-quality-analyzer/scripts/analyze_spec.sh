#!/bin/bash
# Script to help analyze spec quality using grep and other tools
# This is a helper script for the spec quality analyzer skill

SPEC_FILE="$1"
CONSTITUTION_FILE="$2"

if [ -z "$SPEC_FILE" ]; then
    echo "Usage: $0 <spec_file> [constitution_file]"
    exit 1
fi

echo "Analyzing spec file: $SPEC_FILE"
echo "With constitution file: ${CONSTITUTION_FILE:-none}"

# Check for common clarity issues
echo -e "\n--- CLARITY ISSUES ---"
grep -n -i -E "(should|fast|user-friendly|efficient|good|bad|better|best|fast|slow|immediate|soon|later|etc\.?|and so on|and more)" "$SPEC_FILE" || echo "No common vague terms found"

# Check for missing acceptance criteria
echo -e "\n--- ACCEPTANCE CRITERIA ANALYSIS ---"
grep -n -i -E "(acceptance|criteria|given|when|then|if.*then|condition|requirement|must|shall)" "$SPEC_FILE" || echo "No acceptance criteria patterns found"

# Check for edge cases mentions
echo -e "\n--- EDGE CASES ANALYSIS ---"
grep -n -i -E "(error|exception|invalid|empty|boundary|limit|maximum|minimum|overflow|underflow|timeout|failure|cancel|interrupt|conflict|duplicate|concurrent)" "$SPEC_FILE" || echo "No edge case patterns found"

# Check for consistency issues
echo -e "\n--- CONSISTENCY CHECKS ---"
# Count different requirement formats
echo "Requirement format patterns:"
grep -c -i -E "(requirement|req\.?|feature|user story|as a|given|when|then)" "$SPEC_FILE" 2>/dev/null || echo "0 requirement patterns"