#!/bin/bash
# Script to help analyze plan quality using grep and other tools
# This is a helper script for the plan quality analyzer skill

PLAN_FILE="$1"
SPEC_FILE="$2"
CONSTITUTION_FILE="$3"

if [ -z "$PLAN_FILE" ]; then
    echo "Usage: $0 <plan_file> [spec_file] [constitution_file]"
    exit 1
fi

echo "Analyzing plan file: $PLAN_FILE"
echo "With spec file: ${SPEC_FILE:-none}"
echo "With constitution file: ${CONSTITUTION_FILE:-none}"

# Check for common clarity issues in plans
echo -e "\n--- CLARITY ISSUES ---"
grep -n -i -E "(handle errors|optimize|improve|refactor|tune|adjust|make.*better|fix.*later|deal with|take care of|work on)" "$PLAN_FILE" || echo "No common vague terms found"

# Check for acceptance criteria mentions
echo -e "\n--- ACCEPTANCE CRITERIA ANALYSIS ---"
grep -n -i -E "(acceptance|criteria|done|complete|verified|validated|confirmed|tested|reviewed|approved)" "$PLAN_FILE" || echo "No acceptance criteria patterns found"

# Check for edge cases mentions
echo -e "\n--- EDGE CASES ANALYSIS ---"
grep -n -i -E "(failure|error|exception|invalid|rollback|recovery|cancel|interrupt|boundary|limit|edge case|fallback|alternative)" "$PLAN_FILE" || echo "No edge case patterns found"

# Check for plan structure patterns
echo -e "\n--- PLAN STRUCTURE ANALYSIS ---"
grep -c -E "^#[[:space:]]|^##[[:space:]]|^###[[:space:]]" "$PLAN_FILE" || echo "0 header patterns found"

# Count plan steps if they follow common patterns
echo -e "\n--- PLAN STEP PATTERNS ---"
grep -c -E "^1\. |^2\. |^3\. |^[0-9]\. |^- |^\* " "$PLAN_FILE" || echo "0 step patterns found"

echo -e "\n--- ANALYSIS COMPLETE ---"
echo "Note: This script provides initial pattern detection only."
echo "Full analysis requires human review of the plan content."