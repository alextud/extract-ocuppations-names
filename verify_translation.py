#!/usr/bin/env python3
"""
Verification script to check data integrity of the translated CSV file.
"""

import csv


def verify_csv_integrity(filename):
    """
    Verify that the CSV file has proper structure and data alignment.
    """
    print(f"Verifying integrity of {filename}...")
    
    errors = []
    row_count = 0
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Check header
            header = next(reader)
            expected_header = ['original_hungarian', 'translated_to_english']
            
            if header != expected_header:
                errors.append(f"Header mismatch. Expected: {expected_header}, Got: {header}")
            else:
                print("✓ Header is correct")
            
            # Check data rows
            for i, row in enumerate(reader, 1):
                row_count = i
                
                # Check row has exactly 2 columns
                if len(row) != 2:
                    errors.append(f"Row {i}: Expected 2 columns, got {len(row)}")
                    continue
                
                # Check both columns have content
                if not row[0].strip():
                    errors.append(f"Row {i}: Original Hungarian text is empty")
                
                if not row[1].strip():
                    errors.append(f"Row {i}: Translation is empty")
                
                # Check translation contains the marker
                if '[Dictionary-based translation]' not in row[1]:
                    errors.append(f"Row {i}: Missing translation marker")
            
            print(f"✓ Processed {row_count} data rows")
            
    except Exception as e:
        errors.append(f"Error reading file: {e}")
    
    # Report results
    if errors:
        print(f"\n❌ Found {len(errors)} issues:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more issues")
        return False
    else:
        print(f"\n✅ File integrity verified successfully!")
        print(f"  - Total rows: {row_count + 1} (including header)")
        print(f"  - Data rows: {row_count}")
        return True


def compare_with_original(original_file, translated_file):
    """
    Compare the number of entries between original and translated files.
    """
    print(f"\nComparing {original_file} with {translated_file}...")
    
    # Count entries in original file (parsed entries)
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    original_entries = [entry.strip() for entry in content.split(';') if entry.strip()]
    
    # Count rows in translated file (excluding header)
    with open(translated_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        translated_rows = list(reader)
    
    print(f"Original entries: {len(original_entries)}")
    print(f"Translated rows: {len(translated_rows)}")
    
    if len(original_entries) == len(translated_rows):
        print("✅ Entry counts match!")
        return True
    else:
        print("❌ Entry counts don't match!")
        return False


def main():
    print("CSV Translation Verification Tool")
    print("=" * 40)
    
    # Verify the translated file
    integrity_ok = verify_csv_integrity('to_extract_with_translations.csv')
    
    # Compare with original
    count_ok = compare_with_original('to_extract.csv', 'to_extract_with_translations.csv')
    
    if integrity_ok and count_ok:
        print("\n🎉 All verification checks passed!")
        return 0
    else:
        print("\n⚠️  Some verification checks failed!")
        return 1


if __name__ == "__main__":
    exit(main())