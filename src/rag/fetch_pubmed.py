import requests
import json
import time
from pathlib import Path

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = "elaine.c.designs@gmail.com"  # PubMed asks for this as courtesy, any email works

QUERIES = [
    "psilocybin therapy depression",
    "MDMA assisted psychotherapy PTSD",
    "ketamine treatment depression",
    "psychedelic integration therapy",
    "psychedelic assisted therapy outcomes",
    "psilocybin mystical experience",
    "ayahuasca therapeutic",
    "psychedelic ego dissolution",
]

def search_pubmed(query, retmax=25):
    """Step 1: search for paper IDs"""
    url = f"{BASE_URL}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
        "email": EMAIL
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    ids = response.json()["esearchresult"]["idlist"]
    return ids

def fetch_abstracts(ids):
    """Step 2: fetch abstracts for a list of IDs"""
    url = f"{BASE_URL}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "rettype": "abstract",
        "retmode": "text",
        "email": EMAIL
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.text

all_text_blocks = []

for i, query in enumerate(QUERIES):
    print(f"[{i+1}/{len(QUERIES)}] Searching: {query}")
    try:
        ids = search_pubmed(query)
        print(f"  Found {len(ids)} IDs")
        if ids:
            text = fetch_abstracts(ids)
            all_text_blocks.append({
                "query": query,
                "text": text
            })
            print(f"  Fetched abstracts ✓")
        time.sleep(1.5)  # NCBI rate limit: ~3 req/sec without API key
    except Exception as e:
        print(f"  Error: {e}")
        time.sleep(5)

# Save raw text
output_file = OUTPUT_DIR / "pubmed_abstracts.json"
with open(output_file, "w") as f:
    json.dump(all_text_blocks, f, indent=2)

print(f"\n Saved {len(all_text_blocks)} query results to {output_file}")