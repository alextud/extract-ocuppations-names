import os
import json
import pandas as pd
import requests

def load_records(input_file: str) -> pd.DataFrame:
    """Load raw records from the semicolon separated input file."""
    with open(input_file, encoding='utf-8') as f:
        data = f.read()
    records = [r.strip().strip('"').replace('\n', ' ') for r in data.split(';') if r.strip()]
    return pd.DataFrame({'original': records})

def translate_records(df: pd.DataFrame) -> pd.DataFrame:
    """Translate Hungarian text to English."""
    def translate_text(text: str) -> str:
        url = 'https://translate.googleapis.com/translate_a/single'
        params = {'client': 'gtx', 'sl': 'hu', 'tl': 'en', 'dt': 't', 'q': text}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            try:
                return resp.json()[0][0][0]
            except Exception:
                return text
        return text

    df['translated'] = [translate_text(t) for t in df['original']]
    return df

def extract_occupations(df: pd.DataFrame) -> pd.DataFrame:
    """Use an LLM to extract occupations for deceased, husband and father."""
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    def call_llm(text: str) -> pd.Series:
        if not api_key:
            return pd.Series(['', '', ''])

        prompt = (
            "Extract the occupations of the deceased, their husband, and their father from the following obituary.\n"
            "Return a JSON object with keys 'deceased', 'husband', and 'father'. If an occupation is missing, use an empty string.\n"
            f"Obituary: {text}"
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
            'temperature': 0
        }
        try:
            resp = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=body, timeout=30)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                data = json.loads(content)
                return pd.Series([
                    data.get('deceased', ''),
                    data.get('husband', ''),
                    data.get('father', '')
                ])
        except Exception:
            pass
        return pd.Series(['', '', ''])

    df[['Deceased Occupation', 'Husband Occupation', 'Father Occupation']] = df['translated'].apply(call_llm)
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

if __name__ == '__main__':
    main()
