#!/bin/bash
# Script to help analyze task quality using grep and other tools
# This is a helper script for the tasks quality analyzer skill

TASKS_FILE="$1"
SPEC_FILE="$2"
PLAN_FILE="$3"
CONSTITUTION_FILE="$4"

if [ -z "$TASKS_FILE" ]; then
    echo "Usage: $0 <tasks_file> [spec_file] [plan_file] [constitution_file]"
    exit 1
fi

echo "Analyzing tasks file: $TASKS_FILE"
echo "With spec file: ${SPEC_FILE:-none}"
echo "With plan file: ${PLAN_FILE:-none}"
echo "With constitution file: ${CONSTITUTION_FILE:-none}"

# Check for common clarity issues in tasks
echo -e "\n--- CLARITY ISSUES ---"
grep -n -i -E "(handle|support|manage|implement|create|setup|configure|deal with|take care of|work on|tune|adjust|optimize|improve|refactor|fix.*later)" "$TASKS_FILE" || echo "No common vague verbs found"

# Check for task structure patterns
echo -e "\n--- TASK STRUCTURE ANALYSIS ---"
grep -c -E "^1\. |^2\. |^3\. |^[0-9]\. |^- |^\* " "$TASKS_FILE" || echo "0 task patterns found"

# Check for potential dependency indicators
echo -e "\n--- DEPENDENCY INDICATORS ---"
grep -n -i -E "(after|before|requires|depends|prerequisite|must.*first|then|followed by|precedes)" "$TASKS_FILE" || echo "No dependency patterns found"

# Check for validation/verification mentions
echo -e "\n--- VALIDATION CHECKS ---"
grep -n -i -E "(validate|verify|test|check|confirm|review|approve|ensure|assert|validate.*that)" "$TASKS_FILE" || echo "No validation patterns found"

# Check for edge case mentions
echo -e "\n--- EDGE CASE PATTERNS ---"
grep -n -i -E "(error|exception|invalid|empty|boundary|limit|edge case|fallback|alternative|cancellation|interrupt|conflict|duplicate|concurrent)" "$TASKS_FILE" || echo "No edge case patterns found"

echo -e "\n--- ANALYSIS COMPLETE ---"
echo "Note: This script provides initial pattern detection only."
echo "Full analysis requires human review of the task content and alignment with spec/plan."