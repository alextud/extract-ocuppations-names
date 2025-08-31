import os
import json
import pandas as pd
import requests
import time
from dotenv import load_dotenv
from typing import Dict, List, Tuple

load_dotenv()

def load_records(input_file: str) -> pd.DataFrame:
    """Load raw records from the semicolon separated input file."""
    with open(input_file, encoding='utf-8') as f:
        data = f.read()
    records = [r.strip().strip('"').replace('\n', ' ') for r in data.split(';') if r.strip()]
    return pd.DataFrame({'original': records})

def create_translation_batch_file(df: pd.DataFrame, filename: str) -> None:
    """Create JSONL file for batch translation requests."""
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-5-mini')
    
    print(f"Creating translation batch file with {len(df)} requests...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for index, row in df.iterrows():
            request = {
                "custom_id": f"translate_{index}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a professional translator. Translate the given Hungarian text to English accurately and naturally."},
                        {"role": "user", "content": f"Translate the following Hungarian text to English:\n{row['original']}"}
                    ],
                    "temperature": 1
                }
            }
            f.write(json.dumps(request, ensure_ascii=False) + '\n')
    
    print(f"Created translation batch file: {filename}")

def create_extraction_batch_file(df: pd.DataFrame, filename: str) -> None:
    """Create JSONL file for batch occupation extraction requests."""
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-5-mini')
    
    print(f"Creating extraction batch file with {len(df)} requests...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for index, row in df.iterrows():
            prompt = (
                "Extract the occupations of the deceased, their husband, and their father from the following obituary.\n"
                "Return a JSON object with keys 'deceased', 'husband', and 'father'. If an occupation is missing, use an empty string.\n"
                "IMPORTANT: Extract the occupations in the original Hungarian language, not in English translation.\n"
                "Use the English translation to understand the context, but return the occupation terms in Hungarian.\n"
                f"Original Hungarian text: {row['original']}\n"
                f"English translation: {row['translated']}"
            )
            
            request = {
                "custom_id": f"extract_{index}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You extract occupations from obituaries."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 1
                }
            }
            f.write(json.dumps(request, ensure_ascii=False) + '\n')
    
    print(f"Created extraction batch file: {filename}")

def upload_batch_file(filename: str) -> str:
    """Upload a JSONL file to OpenAI and return the file ID."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    print(f"Uploading batch file: {filename}")
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    with open(filename, 'rb') as f:
        files = {
            'file': (filename, f, 'application/json'),
            'purpose': (None, 'batch')
        }
        
        response = requests.post(
            'https://api.openai.com/v1/files',
            headers=headers,
            files=files,
            timeout=60
        )
    
    if response.status_code == 200:
        file_id = response.json()['id']
        print(f"File uploaded successfully. File ID: {file_id}")
        return file_id
    else:
        raise Exception(f"Failed to upload file: {response.status_code} {response.text}")

def create_batch_job(file_id: str, description: str) -> str:
    """Create a batch job and return the batch ID."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    print(f"Creating batch job: {description}")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    body = {
        'input_file_id': file_id,
        'endpoint': '/v1/chat/completions',
        'completion_window': '24h',
        'metadata': {
            'description': description
        }
    }
    
    response = requests.post(
        'https://api.openai.com/v1/batches',
        headers=headers,
        json=body,
        timeout=60
    )
    
    if response.status_code == 200:
        batch_id = response.json()['id']
        print(f"Batch job created successfully. Batch ID: {batch_id}")
        return batch_id
    else:
        raise Exception(f"Failed to create batch job: {response.status_code} {response.text}")

def monitor_batch_job(batch_id: str, description: str) -> Dict:
    """Monitor a batch job until completion and return the final status."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    print(f"Monitoring batch job {batch_id}: {description}")
    print("This may take up to 24 hours. Checking every 5 minutes...")
    
    while True:
        response = requests.get(
            f'https://api.openai.com/v1/batches/{batch_id}',
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            batch_data = response.json()
            status = batch_data['status']
            
            print(f"Batch status: {status}")
            
            if status == 'completed':
                print(f"Batch job completed successfully!")
                print(batch_data)
                return batch_data
            elif status in ['failed', 'cancelled', 'expired']:
                print(f"Batch job failed with status: {status}")
                if 'errors' in batch_data:
                    print(f"Errors: {batch_data['errors']}")
                return batch_data
            elif status in ['validating', 'in_progress', 'finalizing']:
                # Job is still processing
                time.sleep(300)  # Wait 5 minutes before checking again
            else:
                print(f"Unknown status: {status}")
                time.sleep(300)
        else:
            print(f"Error checking batch status: {response.status_code} {response.text}")
            time.sleep(300)

def download_batch_results(batch_data: Dict, output_filename: str) -> str:
    """Download batch results and save to file."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if batch_data['status'] != 'completed':
        raise Exception(f"Batch not completed. Status: {batch_data['status']}")
    
    output_file_id = batch_data['output_file_id']
    print(f"Downloading results from file ID: {output_file_id}")
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    response = requests.get(
        f'https://api.openai.com/v1/files/{output_file_id}/content',
        headers=headers,
        timeout=60
    )
    
    if response.status_code == 200:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Results saved to: {output_filename}")
        return output_filename
    else:
        raise Exception(f"Failed to download results: {response.status_code} {response.text}")

def process_translation_results(results_file: str, df: pd.DataFrame) -> pd.DataFrame:
    """Process translation batch results and add to DataFrame."""
    print(f"Processing translation results from: {results_file}")
    
    # Initialize with original text as fallback
    df['translated'] = df['original'].copy()
    
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line.strip())
            
            if result.get('response') and result['response'].get('status_code') == 200:
                custom_id = result['custom_id']
                if custom_id.startswith('translate_'):
                    index = int(custom_id.replace('translate_', ''))
                    content = result['response']['body']['choices'][0]['message']['content']
                    df.at[index, 'translated'] = content.strip()
            else:
                # Handle errors
                custom_id = result['custom_id']
                if custom_id.startswith('translate_'):
                    index = int(custom_id.replace('translate_', ''))
                    print(f"Translation failed for record {index}: {result.get('error', 'Unknown error')}")
    
    print("Translation results processed successfully!")
    return df

def process_extraction_results(results_file: str, df: pd.DataFrame) -> pd.DataFrame:
    """Process extraction batch results and add to DataFrame."""
    print(f"Processing extraction results from: {results_file}")
    
    # Initialize with empty strings
    df['Deceased Occupation'] = ''
    df['Husband Occupation'] = ''
    df['Father Occupation'] = ''
    
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line.strip())
            
            if result.get('response') and result['response'].get('status_code') == 200:
                custom_id = result['custom_id']
                if custom_id.startswith('extract_'):
                    index = int(custom_id.replace('extract_', ''))
                    content = result['response']['body']['choices'][0]['message']['content']
                    
                    try:
                        data = json.loads(content)
                        df.at[index, 'Deceased Occupation'] = data.get('deceased', '')
                        df.at[index, 'Husband Occupation'] = data.get('husband', '')
                        df.at[index, 'Father Occupation'] = data.get('father', '')
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON for record {index}: {content}")
            else:
                # Handle errors
                custom_id = result['custom_id']
                if custom_id.startswith('extract_'):
                    index = int(custom_id.replace('extract_', ''))
                    print(f"Extraction failed for record {index}: {result.get('error', 'Unknown error')}")
    
    print("Extraction results processed successfully!")
    return df

def main():
    # translation_batch_data = monitor_batch_job("batch_68b29f9bd7848190b29c8955d1e4bdcf", "Translation")
    # translation_results_file = 'translation_results.jsonl'
    # download_batch_results(translation_batch_data, translation_results_file)
    # df_translated = process_translation_results(translation_results_file, df)
    # df_translated.to_csv(args.translated, index=False)
    # print(f"Translated data saved to: {args.translated}")
    # return

    import argparse
    parser = argparse.ArgumentParser(description="Process Hungarian CSV and extract occupations using OpenAI Batch API")
    parser.add_argument('--input', default='to_extract.csv', help='Input CSV file')
    parser.add_argument('--translated', default='translated_to_english_batch.csv', help='Output translated CSV')
    parser.add_argument('--extracted', default='extracted_occupations_batch.csv', help='Output CSV with extracted occupations')
    parser.add_argument('--skip-translation', action='store_true', help='Skip translation and load existing translated file')
    args = parser.parse_args()

    try:
        if not args.skip_translation:
            # Stage 1: Translation
            print("=== Stage 1: Translation ===")
            df = load_records(args.input)
            
            # Create translation batch file
            translation_batch_file = 'translation_batch.jsonl'
            create_translation_batch_file(df, translation_batch_file)
            
            # Upload and process translation batch
            translation_file_id = upload_batch_file(translation_batch_file)
            translation_batch_id = create_batch_job(translation_file_id, "Hungarian to English Translation")
            translation_batch_data = monitor_batch_job(translation_batch_id, "Translation")
            
            # Download and process translation results
            translation_results_file = 'translation_results.jsonl'
            download_batch_results(translation_batch_data, translation_results_file)
            df_translated = process_translation_results(translation_results_file, df)
            df_translated.to_csv(args.translated, index=False)
            print(f"Translated data saved to: {args.translated}")
        else:
            print("=== Loading existing translated data ===")
            df_translated = pd.read_csv(args.translated)
        
        # Stage 2: Occupation Extraction
        print("\n=== Stage 2: Occupation Extraction ===")
        
        # Create extraction batch file
        extraction_batch_file = 'extraction_batch.jsonl'
        create_extraction_batch_file(df_translated, extraction_batch_file)
        
        # Upload and process extraction batch
        extraction_file_id = upload_batch_file(extraction_batch_file)
        extraction_batch_id = create_batch_job(extraction_file_id, "Occupation Extraction")
        extraction_batch_data = monitor_batch_job(extraction_batch_id, "Extraction")
        
        # Download and process extraction results
        extraction_results_file = 'extraction_results.jsonl'
        download_batch_results(extraction_batch_data, extraction_results_file)
        df_extracted = process_extraction_results(extraction_results_file, df_translated)
        df_extracted.to_csv(args.extracted, index=False)
        print(f"Final results saved to: {args.extracted}")
        
        print("\n=== Batch Processing Complete! ===")
        print(f"Processed {len(df_extracted)} records")
        print(f"Cost savings: ~50% compared to standard API calls")
        
    except Exception as e:
        print(f"Error during batch processing: {e}")
        raise

if __name__ == '__main__':
    main()
