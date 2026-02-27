import json
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Load raw papers
input_file = Path("data/raw/semantic_scholar_papers.json")
with open(input_file) as f:
    papers = json.load(f)

print(f"Loaded {len(papers)} papers")

# Build documents from title + abstract
docs_raw = []
for p in papers:
    title = p.get("title", "").strip()
    abstract = p.get("abstract", "").strip()
    year = p.get("year", "unknown")
    if abstract:
        text = f"Title: {title}\nYear: {year}\n\nAbstract: {abstract}"
        docs_raw.append(text)

print(f"Built {len(docs_raw)} documents")

# Chunk the documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.create_documents(docs_raw)
print(f"Created {len(chunks)} chunks")

# Save processed chunks for reference
processed_dir = Path("data/processed")
processed_dir.mkdir(parents=True, exist_ok=True)
with open(processed_dir / "chunks.json", "w") as f:
    json.dump([c.page_content for c in chunks], f, indent=2)

# Load into ChromaDB
print("Loading into ChromaDB...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="data/chroma"
)

print(f"✅ Vector store built and saved to data/chroma")
print(f"   Total vectors: {vectorstore._collection.count()}")