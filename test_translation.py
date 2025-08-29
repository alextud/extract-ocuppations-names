#!/usr/bin/env python3
"""
Test script to verify translation functionality with a small sample.
"""

import csv
import re
import time
from googletrans import Translator


def parse_csv_entries(filename):
    """Parse the custom CSV format."""
    entries = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    raw_entries = content.split(';')
    
    for entry in raw_entries:
        cleaned = entry.strip()
        cleaned = re.sub(r'^"', '', cleaned)
        cleaned = re.sub(r'"$', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        if cleaned:
            entries.append(cleaned)
    
    return entries


def translate_text(text, translator):
    """Translate text to English with error handling."""
    try:
        result = translator.translate(text, src='hu', dest='en')
        return result.text
    except Exception as e:
        print(f"Translation failed for '{text}': {e}")
        return f"[Translation failed: {text}]"


def main():
    print("Testing translation with first 3 entries...")
    
    entries = parse_csv_entries('to_extract.csv')
    translator = Translator()
    
    # Test with first 3 entries
    test_entries = entries[:3]
    
    for i, entry in enumerate(test_entries, 1):
        print(f"\nEntry {i}: {entry}")
        translated = translate_text(entry, translator)
        print(f"Translation: {translated}")
        time.sleep(1)  # Delay to avoid rate limiting


if __name__ == "__main__":
    main()