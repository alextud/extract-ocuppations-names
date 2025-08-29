#!/usr/bin/env python3
"""
Script to translate Hungarian occupation/name data from to_extract.csv to English.
Creates a new CSV file with original data and English translations.
"""

import csv
import re
import time
from googletrans import Translator
import sys


def parse_csv_entries(filename):
    """
    Parse the custom CSV format where entries are terminated by semicolons
    and can span multiple lines.
    """
    entries = []
    current_entry = ""
    
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


def translate_text(text, translator, max_retries=3):
    """
    Translate text to English with retry mechanism for rate limiting.
    """
    for attempt in range(max_retries):
        try:
            # Split long text into smaller chunks if needed
            if len(text) > 500:
                # Split by commas or periods to get smaller segments
                segments = re.split(r'[,.]', text)
                translated_segments = []
                
                for segment in segments:
                    if segment.strip():
                        result = translator.translate(segment.strip(), src='hu', dest='en')
                        translated_segments.append(result.text)
                        time.sleep(0.1)  # Small delay between segments
                
                return ', '.join(translated_segments)
            else:
                result = translator.translate(text, src='hu', dest='en')
                return result.text
                
        except Exception as e:
            print(f"Translation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return f"[Translation failed: {text}]"
    
    return f"[Translation failed: {text}]"


def create_translated_csv(input_filename, output_filename):
    """
    Create a new CSV file with original Hungarian text and English translations.
    """
    print(f"Parsing entries from {input_filename}...")
    entries = parse_csv_entries(input_filename)
    print(f"Found {len(entries)} entries to translate.")
    
    # Initialize translator
    translator = Translator()
    
    # Create the output CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['original_hungarian', 'translated_to_english'])
        
        # Process each entry
        for i, entry in enumerate(entries, 1):
            print(f"Translating entry {i}/{len(entries)}: {entry[:50]}...")
            
            # Translate the entry
            translated = translate_text(entry, translator)
            
            # Write to CSV
            writer.writerow([entry, translated])
            
            # Add delay to avoid rate limiting
            time.sleep(0.5)
            
            # Progress update every 10 entries
            if i % 10 == 0:
                print(f"Completed {i}/{len(entries)} translations")
    
    print(f"Translation completed. Output saved to {output_filename}")


def main():
    input_file = 'to_extract.csv'
    output_file = 'to_extract_with_translations.csv'
    
    print("Starting translation process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    try:
        create_translated_csv(input_file, output_file)
        print("Translation process completed successfully!")
        
        # Verify the output
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Output file contains {len(lines)} lines (including header)")
            
    except Exception as e:
        print(f"Error during translation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()