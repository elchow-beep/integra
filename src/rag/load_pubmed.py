import json
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Load raw PubMed text
input_file = Path("data/raw/pubmed_abstracts.json")
with open(input_file) as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data)} query result blocks")

# Split into individual abstract blocks
# PubMed returns abstracts separated by blank lines + numbering
docs = []
for block in raw_data:
    query = block["query"]
    text = block["text"]
    # Each abstract is separated by double newlines
    entries = text.strip().split("\n\n\n")
    for entry in entries:
        entry = entry.strip()
        if len(entry) > 100:  # filter out noise
            docs.append(Document(
                page_content=entry,
                metadata={"source": "pubmed", "query": query}
            ))

print(f"Parsed {len(docs)} individual abstracts")

# Chunk
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks")

# Load into existing ChromaDB (adds to existing vectors)
print("Adding to ChromaDB...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    persist_directory="data/chroma",
    embedding_function=embeddings
)
vectorstore.add_documents(chunks)

print(f"✅ Done! Total vectors now: {vectorstore._collection.count()}")