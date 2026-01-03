#!/bin/bash
# Script to test console UI components
# This is a helper script for the console UI skill

echo "Testing Console UI Components"
echo "============================="

# Test basic color output
echo -e "Color Test:"
echo -e "\033[32m✓ Green (Success)\033[0m"
echo -e "\033[33m⚠ Yellow (Warning)\033[0m"
echo -e "\033[31m✗ Red (Error)\033[0m"
echo -e "\033[34mℹ Blue (Info)\033[0m"
echo

# Test formatting styles
echo -e "Formatting Test:"
echo -e "\033[1mBold Text\033[0m"
echo -e "\033[4mUnderline Text\033[0m"
echo -e "\033[3mItalic Text\033[0m"
echo -e "\033[1;4mBold + Underline\033[0m"
echo

# Test combined formatting
echo -e "Combined Formatting Test:"
echo -e "\033[1;32mBold Green\033[0m"
echo -e "\033[1;31mBold Red\033[0m"
echo -e "\033[4;34mUnderline Blue\033[0m"
echo

# Test environment detection
echo "Environment Detection:"
echo "NO_COLOR: $NO_COLOR"
echo "TERM: $TERM"
echo "Is TTY: $(if [ -t 1 ]; then echo "Yes"; else echo "No"; fi)"
echo

# Test emoji support
echo "Emoji Test:"
echo "✓ Success"
echo "⚠ Warning"
echo "✗ Error"
echo "ℹ Info"
echo "📝 Task"
echo "🔥 Important"
echo

# Simple spinner simulation
echo -n "Spinner Animation: "
for i in {1..3}; do
    for c in / - \\ \|; do
        echo -ne "\b$c"
        sleep 0.1
    done
done
echo -e "\bDone!"
echo

# Progress bar simulation
echo "Progress Bar:"
for i in {10..100..10}; do
    printf "\rProgress: ["
    for ((j=0; j<i/5; j++)); do
        echo -n "="
    done
    for ((j=0; j<20-i/5; j++)); do
        echo -n " "
    done
    printf "] %d%%" "$i"
    sleep 0.2
done
echo
echo

# Test table-like output
echo "Table Format Test:"
printf "%-10s %-15s %-10s\n" "ID" "TASK" "STATUS"
printf "%-10s %-15s %-10s\n" "--" "----" "------"
printf "%-10s %-15s %-10s\n" "1" "Buy groceries" "Pending"
printf "%-10s %-15s %-10s\n" "2" "Call mom" "Complete"
printf "%-10s %-15s %-10s\n" "3" "Write report" "Pending"
echo

# Test panel-like border
echo "Panel Format Test:"
echo "┌─────────────────────────────────┐"
echo "│        Task Summary             │"
echo "├─────────────────────────────────┤"
echo "│ • 3 tasks total               │"
echo "│ • 1 completed                 │"
echo "│ • 2 pending                   │"
echo "└─────────────────────────────────┘"
echo

# Test menu format
echo "Menu Format Test:"
echo "1) Add Task"
echo "2) List Tasks"
echo "3) Complete Task"
echo "4) Exit"
echo

echo "============================="
echo "UI Component testing complete."
echo "This script demonstrates various UI elements for CLI applications."