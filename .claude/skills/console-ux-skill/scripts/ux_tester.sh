#!/bin/bash
# Script to test console UX components
# This is a helper script for the console UX skill

echo "Testing Console UX Components"
echo "============================="

# Test color output
echo -e "Color Test:"
echo -e "\033[32mGreen (Success)\033[0m"
echo -e "\033[33mYellow (Warning)\033[0m"
echo -e "\033[31mRed (Error)\033[0m"
echo -e "\033[34mBlue (Info)\033[0m"
echo

# Test formatting
echo -e "Formatting Test:"
echo -e "\033[1mBold Text\033[0m"
echo -e "\033[4mUnderline Text\033[0m"
echo -e "\033[3mItalic Text\033[0m"
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
echo

# Simple spinner simulation
echo -n "Spinner Test: "
for i in {1..5}; do
    for c in / - \\ \|; do
        echo -ne "\b$c"
        sleep 0.1
    done
done
echo -e "\bDone!"
echo

echo "============================="
echo "UX Component testing complete."
echo "This script demonstrates various UX elements for CLI applications."