import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

load_dotenv()

def load_records(input_file: str) -> pd.DataFrame:
    """Load raw records from the semicolon separated input file."""
    with open(input_file, encoding='utf-8') as f:
        data = f.read()
    records = [r.strip().strip('"').replace('\n', ' ') for r in data.split(';') if r.strip()]
    return pd.DataFrame({'original': records})

# def translate_records(df: pd.DataFrame) -> pd.DataFrame:
#     """Translate Hungarian text to English."""
#     def translate_text(text: str) -> str:
#         url = 'https://translate.googleapis.com/translate_a/single'
#         params = {'client': 'gtx', 'sl': 'hu', 'tl': 'en', 'dt': 't', 'q': text}
#         resp = requests.get(url, params=params)
#         if resp.status_code == 200:
#             try:
#                 return resp.json()[0][0][0]
#             except Exception:
#                 return text
#         return text

#     df['translated'] = [translate_text(t) for t in df['original']]
#     return df

def translate_records(df: pd.DataFrame, max_workers: int = 10) -> pd.DataFrame:
    """Translate Hungarian text to English using OpenAI with concurrent requests."""
    api_key = os.getenv('OPENAI_API_KEY')
    model = "gpt-5-nano" #os.getenv('OPENAI_MODEL', 'gpt-5-mini')

    def translate_text(args) -> tuple:
        index, text = args
        if not api_key:
            return index, text
        
        print(f"Translating record {index}: {text[:50]}...")
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        body = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': 'You are a professional translator. Translate the given Hungarian text to English accurately and naturally.'},
                {'role': 'user', 'content': f'Translate the following Hungarian text to English:\n{text}'}
            ],
            'temperature': 1
        }
        try:
            # Add small delay to avoid hitting rate limits too hard
            time.sleep(0.1)
            resp = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=body, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                translated = data['choices'][0]['message']['content'].strip()
                print(f"Completed record {index}: {translated[:80]}...")
                return index, translated
            else:
                print(f"API error for record {index}: {resp.status_code}")
        except Exception as e:
            print(f"Error translating record {index}: {e}")
        return index, text

    # Prepare data for concurrent processing
    translation_tasks = [(i, text) for i, text in enumerate(df['original'])]
    results = {}
    
    print(f"Starting concurrent translation of {len(translation_tasks)} records with {max_workers} workers...")
    
    # Use ThreadPoolExecutor for concurrent API calls
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {executor.submit(translate_text, task): task[0] for task in translation_tasks}
        
        # Collect results as they complete
        for future in as_completed(future_to_index):
            index, translated_text = future.result()
            results[index] = translated_text
    
    # Reconstruct the results in original order
    df['translated'] = [results[i] for i in range(len(df))]
    print("Translation completed!")
    return df

def extract_occupations(df: pd.DataFrame, max_workers: int = 10) -> pd.DataFrame:
    """Use an LLM to extract occupations for deceased, husband and father with concurrent requests."""
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-5-mini')

    def call_llm(args) -> tuple:
        index, original_text, translated_text = args
        if not api_key:
            return index, pd.Series(['', '', ''])

        prompt = (
            "Extract the occupations of the deceased, their husband, and their father from the following obituary.\n"
            "Return a JSON object with keys 'deceased', 'husband', and 'father'. If an occupation is missing, use an empty string.\n"
            "IMPORTANT: Extract the occupations in the original Hungarian language, not in English translation.\n"
            "Use the English translation to understand the context, but return the occupation terms in Hungarian.\n"
            f"Original Hungarian text: {original_text}\n"
            f"English translation: {translated_text}"
        )
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        body = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': 'You extract occupations from obituaries.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 1
        }
        try:
            print(f"Extracting occupations from record {index}: {original_text[:50]}...")
            # Add small delay to avoid hitting rate limits too hard
            time.sleep(0.1)
            resp = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=body, timeout=60)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                data = json.loads(content)
                print(f"Completed extraction for record {index}: {data}")
                return index, pd.Series([
                    data.get('deceased', ''),
                    data.get('husband', ''),
                    data.get('father', '')
                ])
            else:
                print(f"API error for record {index}: {resp.status_code}")
        except Exception as e:
            print(f"Error extracting occupations for record {index}: {e}")
        return index, pd.Series(['', '', ''])

    # Prepare data for concurrent processing - pass both original and translated text
    extraction_tasks = [(i, original_text, translated_text) for i, (original_text, translated_text) in enumerate(zip(df['original'], df['translated']))]
    results = {}
    
    print(f"Starting concurrent occupation extraction of {len(extraction_tasks)} records with {max_workers} workers...")
    
    # Use ThreadPoolExecutor for concurrent API calls
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {executor.submit(call_llm, task): task[0] for task in extraction_tasks}
        
        # Collect results as they complete
        for future in as_completed(future_to_index):
            index, occupation_series = future.result()
            results[index] = occupation_series
    
    # Reconstruct the results in original order
    occupation_data = [results[i] for i in range(len(df))]
    df[['Deceased Occupation', 'Husband Occupation', 'Father Occupation']] = pd.DataFrame(occupation_data, index=df.index)
    print("Occupation extraction completed!")
    return df

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process Hungarian CSV and extract occupations")
    parser.add_argument('--input', default='to_extract.csv', help='Input CSV file')
    parser.add_argument('--translated', default='translated_to_english.csv', help='Output translated CSV')
    parser.add_argument('--extracted', default='extracted_occupations.csv', help='Output CSV with extracted occupations')
    args = parser.parse_args()

    df = load_records(args.input)
    df_translated = translate_records(df.copy())
    df_translated.to_csv(args.translated, index=False)

    df_extracted = extract_occupations(df_translated.copy())
    df_extracted.to_csv(args.extracted, index=False)

    # Load the already translated CSV file
    # df = pd.read_csv("translated_to_english.csv")
    # df_extracted = extract_occupations(df.copy())
    # df_extracted.to_csv("extracted_occupations.csv", index=False)

if __name__ == '__main__':
    main()
