#!/bin/bash
# Script to help apply spec improvements based on analysis report
# This is a helper script for the spec quality improver skill

ORIGINAL_SPEC="$1"
ANALYSIS_REPORT="$2"
CONSTITUTION_FILE="$3"

if [ -z "$ORIGINAL_SPEC" ] || [ -z "$ANALYSIS_REPORT" ]; then
    echo "Usage: $0 <original_spec> <analysis_report> [constitution_file]"
    exit 1
fi

echo "Improving spec: $ORIGINAL_SPEC"
echo "Based on analysis report: $ANALYSIS_REPORT"
echo "With constitution file: ${CONSTITUTION_FILE:-none}"

# Extract clarity issues from analysis report
echo -e "\n--- CLARITY ISSUES TO ADDRESS ---"
grep -A 5 -B 5 -i "clarity\|ambiguity\|vague" "$ANALYSIS_REPORT" || echo "No clarity issues found in analysis"

# Extract acceptance criteria issues
echo -e "\n--- ACCEPTANCE CRITERIA TO ADD/IMPROVE ---"
grep -A 5 -B 5 -i "acceptance.*criteria\|testable\|measurable" "$ANALYSIS_REPORT" || echo "No acceptance criteria issues found in analysis"

# Extract edge case issues
echo -e "\n--- EDGE CASES TO ADD ---"
grep -A 5 -B 5 -i "edge case\|invalid input\|boundary\|failure scenario" "$ANALYSIS_REPORT" || echo "No edge case issues found in analysis"

# Extract consistency issues
echo -e "\n--- CONSISTENCY ISSUES TO FIX ---"
grep -A 5 -B 5 -i "consistency\|terminology\|format\|contradiction" "$ANALYSIS_REPORT" || echo "No consistency issues found in analysis"

echo -e "\n--- IMPROVEMENT PROCESS ---"
echo "1. Apply changes only as identified in the analysis report"
echo "2. Preserve original intent and scope"
echo "3. Generate traceability report for all changes made"