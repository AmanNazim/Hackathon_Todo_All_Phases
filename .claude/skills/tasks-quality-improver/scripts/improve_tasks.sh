#!/bin/bash
# Script to help apply task improvements based on analysis report
# This is a helper script for the tasks quality improver skill

ORIGINAL_TASKS="$1"
ANALYSIS_REPORT="$2"
SPEC_FILE="$3"
CONSTITUTION_FILE="$4"

if [ -z "$ORIGINAL_TASKS" ] || [ -z "$ANALYSIS_REPORT" ]; then
    echo "Usage: $0 <original_tasks> <analysis_report> [spec_file] [constitution_file]"
    echo "ERROR: Both original tasks file and analysis report are required"
    exit 1
fi

echo "Improving tasks: $ORIGINAL_TASKS"
echo "Based on analysis report: $ANALYSIS_REPORT"
echo "With spec file: ${SPEC_FILE:-none}"
echo "With constitution file: ${CONSTITUTION_FILE:-none}"

# Check if analysis report exists and has content
if [ ! -f "$ANALYSIS_REPORT" ]; then
    echo "ERROR: Analysis report file does not exist: $ANALYSIS_REPORT"
    exit 1
fi

ANALYSIS_SIZE=$(wc -c < "$ANALYSIS_REPORT")
if [ "$ANALYSIS_SIZE" -lt 100 ]; then
    echo "WARNING: Analysis report appears to be very small - may not contain sufficient detail"
fi

# Extract clarity issues from analysis report
echo -e "\n--- CLARITY ISSUES TO ADDRESS ---"
grep -A 5 -B 5 -i "unclear\|ambiguous\|vague\|not.*clear" "$ANALYSIS_REPORT" || echo "No clarity issues found in analysis"

# Extract missing tasks
echo -e "\n--- MISSING TASKS TO ADD ---"
grep -A 5 -B 5 -i "missing\|incomplete\|not.*covered" "$ANALYSIS_REPORT" || echo "No missing tasks identified in analysis"

# Extract granularity issues
echo -e "\n--- GRANULARITY ISSUES TO FIX ---"
grep -A 5 -B 5 -i "overly.*broad\|too.*large\|granularity\|atomic" "$ANALYSIS_REPORT" || echo "No granularity issues found in analysis"

# Extract edge case issues
echo -e "\n--- EDGE CASE TASKS TO ADD ---"
grep -A 5 -B 5 -i "edge case\|invalid.*input\|boundary\|error.*handling\|failure\|empty.*state" "$ANALYSIS_REPORT" || echo "No edge case issues found in analysis"

# Extract dependency issues
echo -e "\n--- DEPENDENCY ISSUES TO FIX ---"
grep -A 5 -B 5 -i "dependency\|ordering\|prerequisite\|cyclic\|requires" "$ANALYSIS_REPORT" || echo "No dependency issues found in analysis"

echo -e "\n--- IMPROVEMENT PROCESS ---"
echo "1. Apply changes only as identified in the analysis report"
echo "2. Verify each change maps to spec or analysis report"
echo "3. Preserve original intent and scope"
echo "4. Generate improved tasks with proper structure"