#!/usr/bin/env python3
"""
Translation script using a Hungarian-English dictionary for occupations and common terms.
Since online translation APIs are not available, this provides a basic translation
using a dictionary-based approach for the occupation data.
"""

import csv
import re


# Hungarian-English dictionary for common occupations and terms
HUNGARIAN_ENGLISH_DICT = {
    # Occupations
    'asztalos': 'carpenter',
    'mester': 'master',
    'kereskedő': 'merchant',
    'napszámos': 'day laborer',
    'csizmadia': 'shoemaker',
    'kőmives': 'stonemason',
    'szabó': 'tailor',
    'mészáros': 'butcher',
    'kovács': 'blacksmith',
    'földész': 'surveyor',
    'tanár': 'teacher',
    'tanító': 'elementary teacher',
    'kántor': 'cantor',
    'orvos': 'doctor',
    'ügyvéd': 'lawyer',
    'jegyző': 'notary',
    'kerekes': 'wheelwright',
    'szőcs': 'weaver',
    'pék': 'baker',
    'molnár': 'miller',
    'borbély': 'barber',
    'kocsis': 'coachman',
    'hivatalnok': 'official',
    'szolga': 'servant',
    'katona': 'soldier',
    'honvéd': 'home guard soldier',
    'vasutas': 'railway worker',
    'vasuti': 'railway',
    'erdész': 'forester',
    'biró': 'judge',
    'pap': 'priest',
    'lelkész': 'pastor',
    'szinész': 'actor',
    'zenész': 'musician',
    'karnagy': 'conductor',
    'mérnök': 'engineer',
    'bányász': 'miner',
    'gazda': 'farmer',
    'birtokos': 'landowner',
    'gépész': 'mechanic',
    'pincér': 'waiter',
    'szakács': 'cook',
    'cseléd': 'domestic servant',
    'dajka': 'nanny',
    'bejáró': 'commuter worker',
    'utász': 'sapper',
    'őr': 'guard',
    'rendőr': 'police officer',
    'tűzoltó': 'firefighter',
    'postás': 'postman',
    'levélhordó': 'mail carrier',
    'kertész': 'gardener',
    'szőlős': 'vintner',
    'borász': 'winemaker',
    'vadász': 'hunter',
    'halász': 'fisherman',
    'fuvaros': 'carrier',
    'bérkocsis': 'hired coachman',
    'ács': 'carpenter',
    'kőfaragó': 'stone carver',
    'műszerész': 'instrument maker',
    'órás': 'watchmaker',
    'ékszerész': 'jeweler',
    'aranyműves': 'goldsmith',
    'timár': 'leather dresser',
    'szűcs': 'furrier',
    'kelmefestő': 'cloth dyer',
    'nyomdász': 'printer',
    'könyvkötő': 'bookbinder',
    'patikus': 'pharmacist',
    'felcser': 'barber-surgeon',
    'bába': 'midwife',
    'díjnok': 'fee collector',
    'számtiszt': 'accountant',
    'pénztáros': 'cashier',
    'mérleggyártó': 'scale maker',
    'üveges': 'glazier',
    'fazakas': 'potter',
    'kádár': 'cooper',
    'bognár': 'wheelwright',
    'nyerges': 'saddler',
    'varga': 'leather worker',
    'tímár': 'tanner',
    'szappanfőző': 'soap maker',
    'gyertyamártó': 'candle maker',
    'mézeskalács': 'gingerbread maker',
    'cukrász': 'confectioner',
    'sörfőző': 'brewer',
    'pálinkafőző': 'brandy distiller',
    
    # Family relationships
    'neje': 'wife',
    'férje': 'husband',
    'fia': 'son',
    'leánya': 'daughter',
    'leánykája': 'little daughter',
    'gyermeke': 'child',
    'özvegye': 'widow',
    'özvegy': 'widower',
    'hajadon': 'unmarried woman',
    'nőtlen': 'unmarried man',
    'nős': 'married',
    'törvénytelen': 'illegitimate',
    'árva': 'orphan',
    'mostoha': 'step',
    'kereszt': 'god',
    'néhai': 'late/deceased',
    
    # Status and titles
    'mester': 'master',
    'segéd': 'apprentice/helper',
    'inas': 'apprentice',
    'legény': 'journeyman',
    'nyugalmazott': 'retired',
    'nyugalm': 'retired',
    'volt': 'former',
    'kir': 'royal',
    'királyi': 'royal',
    'magyar': 'Hungarian',
    'városi': 'city/municipal',
    'megyei': 'county',
    'állami': 'state',
    'főisk': 'college',
    'egyetemi': 'university',
    'gimnáziumi': 'gymnasium',
    'elemi': 'elementary',
    'iskola': 'school',
    'intézet': 'institute',
    'hivatal': 'office',
    'igazgató': 'director',
    'felügyelő': 'supervisor',
    'ellenőr': 'inspector',
    'titkár': 'secretary',
    'írnok': 'clerk',
    'százados': 'captain',
    'tiszt': 'officer',
    'főnök': 'chief',
    'vezető': 'leader',
    'gondnok': 'caretaker/steward',
    'egyházfi': 'church elder',
    'tanácsos': 'councilor',
    
    # Places and origins
    'születésű': 'born in',
    'sz': 'born',
    'lakó': 'resident',
    'illetőségű': 'belonging to',
    'várfalvi': 'from Várfalva',
    'kolozsvári': 'from Kolozsvár',
    'szentkirályi': 'from Szentkirály',
    'aranyos': 'from Aranyos',
    
    # Common words
    'és': 'and',
    'vagy': 'or',
    'kereszteletlen': 'unbaptized',
    'kereszt': 'baptized',
    'tanuló': 'student',
    'növendék': 'pupil',
    'osztály': 'class',
    'éves': 'years old',
    'osztálytanácsos': 'class councilor',
    'ministeri': 'ministerial',
    'pénzügyi': 'financial',
    'adó': 'tax',
    'vám': 'customs',
    'dohány': 'tobacco',
    'gyári': 'factory',
    'munkás': 'worker',
    'munkásnő': 'female worker',
    'őrző': 'guard',
    'seprő': 'sweeper',
    'söprő': 'sweeper',
    'mosó': 'washer',
    'főző': 'cook',
    'sütő': 'baker',
    'árus': 'vendor'
}


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


def translate_hungarian_text(text):
    """
    Translate Hungarian text using dictionary substitution.
    This provides a basic translation of occupation-related terms.
    """
    # Convert to lowercase for matching
    lower_text = text.lower()
    translated_parts = []
    
    # Split text into words
    words = re.findall(r'\b\w+\b', lower_text)
    
    for word in words:
        # Try to find translation in dictionary
        if word in HUNGARIAN_ENGLISH_DICT:
            translated_parts.append(HUNGARIAN_ENGLISH_DICT[word])
        else:
            # Keep original word if no translation found
            translated_parts.append(word)
    
    # Join translated parts
    basic_translation = ' '.join(translated_parts)
    
    # Add note about dictionary-based translation
    return f"{basic_translation} [Dictionary-based translation]"


def create_translated_csv(input_filename, output_filename):
    """
    Create a new CSV file with original Hungarian text and English translations.
    """
    print(f"Parsing entries from {input_filename}...")
    entries = parse_csv_entries(input_filename)
    print(f"Found {len(entries)} entries to translate.")
    
    # Create the output CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['original_hungarian', 'translated_to_english'])
        
        # Process each entry
        for i, entry in enumerate(entries, 1):
            if i % 50 == 0:
                print(f"Processing entry {i}/{len(entries)}")
            
            # Translate the entry using dictionary
            translated = translate_hungarian_text(entry)
            
            # Write to CSV
            writer.writerow([entry, translated])
    
    print(f"Translation completed. Output saved to {output_filename}")


def main():
    input_file = 'to_extract.csv'
    output_file = 'to_extract_with_translations.csv'
    
    print("Starting dictionary-based translation process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Dictionary contains {len(HUNGARIAN_ENGLISH_DICT)} Hungarian-English term pairs")
    
    try:
        create_translated_csv(input_file, output_file)
        print("Translation process completed successfully!")
        
        # Verify the output
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Output file contains {len(lines)} lines (including header)")
            
        # Show first few translations as sample
        print("\nSample translations:")
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if i < 5:  # Show first 5
                    print(f"{i+1}. Original: {row[0]}")
                    print(f"   Translation: {row[1]}")
                    print()
                else:
                    break
            
    except Exception as e:
        print(f"Error during translation: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())