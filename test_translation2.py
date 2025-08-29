#!/usr/bin/env python3
"""
Test script using alternative translation library.
"""

import re
import time
from translate import Translator


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
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Translation failed for '{text}': {e}")
        return f"[Translation failed: {text}]"


def main():
    print("Testing alternative translation library...")
    
    entries = parse_csv_entries('to_extract.csv')
    translator = Translator(from_lang="hungarian", to_lang="english")
    
    # Test with first 2 entries
    test_entries = entries[:2]
    
    for i, entry in enumerate(test_entries, 1):
        print(f"\nEntry {i}: {entry}")
        translated = translate_text(entry, translator)
        print(f"Translation: {translated}")
        time.sleep(2)  # Delay to avoid rate limiting


if __name__ == "__main__":
    main()