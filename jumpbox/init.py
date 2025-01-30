#!/usr/bin/env python3

import os
import time
import requests

# Read ES_HOST from environment or use a default
ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
WORDS_FILE = "/app/words.txt"

def wait_for_elasticsearch():
    """ Wait until Elasticsearch is accessible on ES_HOST. """
    while True:
        try:
            r = requests.get(ES_HOST, timeout=3)
            if r.status_code == 200:
                print(f"Elasticsearch is up at {ES_HOST}.")
                break
        except requests.exceptions.RequestException:
            pass
        print(f"Waiting for Elasticsearch to be ready at {ES_HOST}...")
        time.sleep(3)

def create_autocomplete_index():
    """ Create the 'autocomplete' index with a 'completion' field mapping. """
    print("Creating the 'autocomplete' index with completion mapping...")

    # Define the mapping for the 'suggest' field
    mapping = {
        "mappings": {
            "properties": {
                "suggest": {
                    "type": "completion"
                }
            }
        }
    }

    url = f"{ES_HOST}/autocomplete"
    # Use PUT to create or update index
    response = requests.put(url, json=mapping)
    if response.status_code in (200, 201):
        print("Index created or updated successfully.")
    else:
        # It's okay if index already exists; 400/404 can happen
        print(f"Index creation response ({response.status_code}): {response.text}")

def index_words():
    """ Read words from words.txt and index them into Elasticsearch. """
    print(f"Indexing words from {WORDS_FILE}...")
    if not os.path.isfile(WORDS_FILE):
        print("No words.txt file found; skipping.")
        return

    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    for word in words:
        doc = {"suggest": word}
        url = f"{ES_HOST}/autocomplete/_doc?refresh=wait_for"
        response = requests.post(url, json=doc)
        if response.status_code in (200, 201):
            print(f"Indexed word: {word}")
        else:
            print(f"Failed to index word: {word} - {response.status_code} {response.text}")

def main():
    wait_for_elasticsearch()
    create_autocomplete_index()
    index_words()
    print("Index initialization complete.")

if __name__ == "__main__":
    main()
