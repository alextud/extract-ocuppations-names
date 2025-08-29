# Hungarian Occupation Names Translation

This repository contains tools to translate Hungarian historical occupation and name data from the `to_extract.csv` file to English.

## Files

- `to_extract.csv` - Original CSV file containing Hungarian historical records with names, occupations, and family relationships
- `to_extract_with_translations.csv` - Enhanced CSV file with original Hungarian text and English translations
- `translate_csv_dictionary.py` - Main translation script using Hungarian-English dictionary
- `verify_translation.py` - Verification script to check data integrity

## Translation Process

The translation was performed using a comprehensive Hungarian-English dictionary containing 167+ occupation and relationship terms commonly found in historical records. The dictionary includes:

- **Occupations**: asztalos (carpenter), kereskedő (merchant), napszámos (day laborer), csizmadia (shoemaker), etc.
- **Family relationships**: neje (wife), fia (son), leánya (daughter), özvegye (widow), etc.
- **Status terms**: mester (master), nős (married), nőtlen (unmarried), törvénytelen (illegitimate), etc.
- **Titles and ranks**: tanár (teacher), hivatalnok (official), katona (soldier), etc.

## Usage

### Run Translation
```bash
python3 translate_csv_dictionary.py
```

### Verify Results
```bash
python3 verify_translation.py
```

## Output Format

The output CSV file `to_extract_with_translations.csv` contains two columns:
- `original_hungarian` - Original Hungarian text from the source file
- `translated_to_english` - English translation using dictionary-based approach

Each translation is marked with `[Dictionary-based translation]` to indicate the translation method used.

## Sample Translations

| Original Hungarian | English Translation |
|-------------------|-------------------|
| Dunki Ferencz, asztalos mester, nős | dunki ferencz carpenter master married |
| Szász Ilona, Puskás Béla, kereskedő neje | szász ilona puskás béla merchant wife |
| Dóczi Samu, napszámos, nős | dóczi samu day laborer married |

## Data Integrity

- Original file: 392 entries
- Translated file: 392 entries + header
- All entries successfully processed and verified
- No data loss or corruption detected

## Notes

This translation uses a dictionary-based approach rather than online translation APIs due to network restrictions. The dictionary was specifically curated for Hungarian historical and occupation-related terminology commonly found in 19th-century records.