import requests
import os
import json
import random

GITHUB_TOKEN = 'apiToken'
SEARCH_QUERY = 'extension:json+size:>0'
RESULTS_DIR = 'github_json_files'
MAX_FILES = 5000
PER_PAGE = 100

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

def is_english_text(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True

def download_file(url, filename):
    # Check if the file already exists before downloading
    if not os.path.exists(filename):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            content = response.content.decode('utf-8')
            # Load JSON content and check if primarily English
            if is_english_text(content):
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"1 file has been scraped and saved to {filename}")
            else:
                print("File skipped, not in English:", filename)
        except requests.RequestException as e:
            print(f"Error downloading {url}: {str(e)}")
    else:
        print(f"File already exists: {filename}")

def search_github_files(query, max_files):
    count = 0
    page = 1
    try:
        while count < max_files:
            search_url = f'https://api.github.com/search/code?q={query}&per_page={PER_PAGE}&page={page}'
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            if not items:
                break  # No more items found
            random.shuffle(items)  # Shuffle items to introduce randomness
            for item in items:
                if count >= max_files:
                    break
                raw_url = item['html_url'].replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                filename = os.path.join(RESULTS_DIR, f"{count}_{os.path.basename(raw_url)}")
                download_file(raw_url, filename)
                count += 1
            page += 1
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

search_github_files(SEARCH_QUERY, MAX_FILES)
