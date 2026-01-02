#!/bin/bash
# Script to help apply plan improvements based on analysis report
# This is a helper script for the plan quality improver skill

ORIGINAL_PLAN="$1"
ANALYSIS_REPORT="$2"
CONSTITUTION_FILE="$3"

if [ -z "$ORIGINAL_PLAN" ]; then
    echo "Usage: $0 <original_plan> [analysis_report] [constitution_file]"
    exit 1
fi

echo "Improving plan: $ORIGINAL_PLAN"
echo "Based on analysis report: ${ANALYSIS_REPORT:-none}"
echo "With constitution file: ${CONSTITUTION_FILE:-none}"

# Extract clarity issues from analysis report if provided
if [ -n "$ANALYSIS_REPORT" ] && [ -f "$ANALYSIS_REPORT" ]; then
    echo -e "\n--- CLARITY ISSUES TO ADDRESS ---"
    grep -A 5 -B 5 -i "clarity\|ambiguity\|vague\|unclear" "$ANALYSIS_REPORT" || echo "No clarity issues found in analysis"

    # Extract acceptance criteria issues
    echo -e "\n--- ACCEPTANCE CRITERIA TO ADD/IMPROVE ---"
    grep -A 5 -B 5 -i "acceptance.*criteria\|done.*condition\|success.*indicator\|validation" "$ANALYSIS_REPORT" || echo "No acceptance criteria issues found in analysis"

    # Extract edge case issues
    echo -e "\n--- EDGE CASES TO ADD ---"
    grep -A 5 -B 5 -i "edge case\|failure\|dependency.*fail\|partial.*execution\|rework\|rollback" "$ANALYSIS_REPORT" || echo "No edge case issues found in analysis"

    # Extract consistency issues
    echo -e "\n--- CONSISTENCY ISSUES TO FIX ---"
    grep -A 5 -B 5 -i "consistency\|flow\|sequence\|dependency\|transition" "$ANALYSIS_REPORT" || echo "No consistency issues found in analysis"
else
    echo -e "\n--- ANALYSIS REPORT NOT PROVIDED ---"
    echo "Will apply conservative improvements based on plan content only"
    echo "Looking for common improvement opportunities in the plan..."
    grep -i -n -E "(handle|deal with|work on|implement|create|setup|configure|the system|it|that|this)" "$ORIGINAL_PLAN" || echo "No common vague terms found in plan"
fi

echo -e "\n--- IMPROVEMENT PROCESS ---"
echo "1. Apply changes only as identified in the analysis report (if provided)"
echo "2. Preserve original intent and scope"
echo "3. Generate change summary for all improvements made"
echo "4. Maintain plan-level focus (no task breakdown or code details)"