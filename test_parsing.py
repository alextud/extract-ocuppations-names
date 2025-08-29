#!/usr/bin/env python3
"""
Test script to verify CSV parsing before running full translation.
"""

import re


def parse_csv_entries(filename):
    """
    Parse the custom CSV format where entries are terminated by semicolons
    and can span multiple lines.
    """
    entries = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by semicolons to get individual entries
    raw_entries = content.split(';')
    
    for entry in raw_entries:
        # Clean up the entry
        cleaned = entry.strip()
        # Remove quotes at beginning and end
        cleaned = re.sub(r'^"', '', cleaned)
        cleaned = re.sub(r'"$', '', cleaned)
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        if cleaned:  # Skip empty entries
            entries.append(cleaned)
    
    return entries


def main():
    entries = parse_csv_entries('to_extract.csv')
    print(f"Total entries found: {len(entries)}")
    print("\nFirst 5 entries:")
    for i, entry in enumerate(entries[:5], 1):
        print(f"{i}: {entry}")
    
    print("\nLast 5 entries:")
    for i, entry in enumerate(entries[-5:], len(entries)-4):
        print(f"{i}: {entry}")


if __name__ == "__main__":
    main()