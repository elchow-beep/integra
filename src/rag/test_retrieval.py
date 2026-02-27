import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    persist_directory="data/chroma",
    embedding_function=embeddings
)

queries = [
    "how does psilocybin affect depression",
    "what is psychedelic integration",
    "MDMA therapy for PTSD",
    "how should a therapist prepare a participant before a psilocybin session"
]

for query in queries:
    print(f"\nQuery: {query}")
    results = vectorstore.similarity_search(query, k=2)
    for i, doc in enumerate(results):
        print(f"\n  Result {i+1}:\n  {doc.page_content[:300]}...")