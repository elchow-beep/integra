import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

PDF_DIR = Path("data/raw")
pdf_files = list(PDF_DIR.glob("*.pdf"))
print(f"Found {len(pdf_files)} PDFs:")
for f in pdf_files:
    print(f"  {f.name}")

# Load all PDFs
all_docs = []
for pdf_path in pdf_files:
    print(f"\nLoading: {pdf_path.name}")
    try:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        print(f"  {len(docs)} pages loaded")
        all_docs.extend(docs)
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nTotal pages across all PDFs: {len(all_docs)}")

# Chunk
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(all_docs)
print(f"Created {len(chunks)} chunks")

# Add to existing ChromaDB
print("Adding to ChromaDB...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    persist_directory="data/chroma",
    embedding_function=embeddings
)
vectorstore.add_documents(chunks)

print(f"\n Done! Total vectors now: {vectorstore._collection.count()}")