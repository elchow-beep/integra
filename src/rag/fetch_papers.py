import requests
import json
import time
from pathlib import Path

QUERIES = [
    "psilocybin therapy",
    "MDMA psychotherapy",
    "ketamine depression treatment",
    "psychedelic integration",
    "psychedelic assisted therapy",
    "psilocybin depression clinical trial",
    "psychedelic ego dissolution",
    "ayahuasca therapeutic effects",
    "psychedelic mystical experience",
    "MDMA PTSD treatment"
]

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def fetch_papers(query, limit=25):
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,authors,openAccessPdf"
    }

    for attempt in range(5):
        try:
            response = requests.get(BASE_URL, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json().get("data", [])
                # filter out papers with no abstract
                return [p for p in data if p.get("abstract")]
            elif response.status_code in (429, 500, 502, 503):
                wait = 20 * (attempt + 1)
                print(f"  Error {response.status_code}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  Unexpected status {response.status_code}, skipping.")
                return []
        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempt + 1}, retrying...")
            time.sleep(15)

    print(f"  Gave up on: {query}")
    return []

all_papers = []

for i, query in enumerate(QUERIES):
    print(f"[{i+1}/{len(QUERIES)}] Fetching: {query}")
    papers = fetch_papers(query)
    print(f"  Got {len(papers)} papers with abstracts")
    all_papers.extend(papers)
    time.sleep(15)  # respectful delay between queries

# Deduplicate by paperId
seen = set()
unique_papers = []
for p in all_papers:
    if p["paperId"] not in seen:
        seen.add(p["paperId"])
        unique_papers.append(p)

print(f"\nTotal unique papers fetched: {len(unique_papers)}")

output_file = OUTPUT_DIR / "semantic_scholar_papers.json"
with open(output_file, "w") as f:
    json.dump(unique_papers, f, indent=2)

print(f"Saved to {output_file}")