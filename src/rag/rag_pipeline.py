"""
src/rag/rag_pipeline.py

RAG chatbot pipeline for Integra.

Architecture:
    1. User message enters.
    2. Crisis detection runs (crisis_detection.py).
       If flagged: return crisis response immediately, skip RAG.
    3. ChromaDB retrieves the top-k most relevant chunks from the
       integration literature corpus.
    4. Retrieved context + conversation history + system prompt are
       assembled into a prompt.
    5. GPT-4o generates a response grounded in the retrieved literature.
    6. Response is returned along with retrieved sources for transparency.

The pipeline maintains a conversation history list so multi-turn
conversations stay coherent within a session.
"""

import os
from openai import OpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

from src.rag.crisis_detection import check_for_crisis
from src.rag.system_prompt import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHROMA_PATH = "data/chroma"
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 5           # number of chunks to retrieve per query
MAX_HISTORY = 10    # max conversation turns to include in context window


# ---------------------------------------------------------------------------
# Vector store loader
# ---------------------------------------------------------------------------

def _load_vector_store() -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------

def _retrieve_context(query: str, vector_store: Chroma) -> tuple:
    """
    Retrieve top-k relevant chunks from ChromaDB.

    Returns:
        (context_str, source_list)
        context_str: formatted string of retrieved passages for the prompt
        source_list: list of source metadata dicts for transparency
    """
    docs = vector_store.similarity_search(query, k=TOP_K)

    if not docs:
        return "", []

    context_parts = []
    sources = []

    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Source {i}]\n{doc.page_content}")
        sources.append(doc.metadata)

    context_str = "\n\n".join(context_parts)
    return context_str, sources


def _build_prompt_messages(
    user_message: str,
    context_str: str,
    conversation_history: list,
    entry_context: str = None,
) -> list:
    """
    Assemble the full message list for the GPT API call.

    Args:
        user_message:         the current user input
        context_str:          retrieved literature passages
        conversation_history: list of prior {"role": ..., "content": ...} dicts
        entry_context:        optional -- the journal entry text being discussed

    Returns:
        list of message dicts ready for client.chat.completions.create()
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject journal entry context if provided (e.g., user just submitted an entry)
    if entry_context:
        messages.append({
            "role": "system",
            "content": (
                f"The user has just submitted the following journal entry. "
                f"Use it as the primary context for this conversation:\n\n"
                f"{entry_context}"
            ),
        })

    # Inject retrieved literature context
    if context_str:
        messages.append({
            "role": "system",
            "content": (
                f"The following passages have been retrieved from integration "
                f"literature and may be relevant to the user's message. Draw "
                f"on them where appropriate:\n\n{context_str}"
            ),
        })

    # Add trimmed conversation history
    trimmed_history = conversation_history[-(MAX_HISTORY * 2):]
    messages.extend(trimmed_history)

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    return messages


# ---------------------------------------------------------------------------
# Main pipeline class
# ---------------------------------------------------------------------------

class IntegraRAGPipeline:
    """
    Usage:
        pipeline = IntegraRAGPipeline()

        # Respond to a journal entry submission
        result = pipeline.chat(
            user_message="Can you help me reflect on what I wrote?",
            entry_context="I felt the boundary between me and the world dissolve..."
        )
        print(result["response"])

        # Continue the conversation
        result = pipeline.chat("What does IFS say about the part that felt afraid?")
        print(result["response"])

        # Start fresh conversation
        pipeline.reset()
    """

    def __init__(self):
        print("Loading vector store...")
        self._vector_store = _load_vector_store()
        self._conversation_history = []
        print("RAG pipeline ready.")

    def chat(
        self,
        user_message: str,
        entry_context: str = None,
    ) -> dict:
        """
        Process a user message through the full RAG pipeline.

        Args:
            user_message:  the user's message or question
            entry_context: optional journal entry text (pass on first message
                           after a new entry is submitted)

        Returns:
            dict with keys:
                response        (str) -- the chatbot's response
                is_crisis       (bool) -- whether crisis was detected
                sources         (list) -- retrieved source metadata
                retrieved_text  (str)  -- the raw retrieved context (for debug)
        """
        # Step 1: Crisis check
        crisis_result = check_for_crisis(user_message)
        if crisis_result["is_crisis"]:
            return {
                "response": crisis_result["response"],
                "is_crisis": True,
                "sources": [],
                "retrieved_text": "",
            }

        # Step 2: Retrieval
        query = user_message
        if entry_context:
            # Use entry text as the retrieval query for richer context
            query = entry_context[:1000]

        context_str, sources = _retrieve_context(query, self._vector_store)

        # Step 3: Build messages
        messages = _build_prompt_messages(
            user_message=user_message,
            context_str=context_str,
            conversation_history=self._conversation_history,
            entry_context=entry_context,
        )

        # Step 4: Generate response
        response_obj = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        response_text = response_obj.choices[0].message.content.strip()

        # Step 5: Update conversation history
        self._conversation_history.append({"role": "user", "content": user_message})
        self._conversation_history.append({"role": "assistant", "content": response_text})

        return {
            "response": response_text,
            "is_crisis": False,
            "sources": sources,
            "retrieved_text": context_str,
        }

    def reset(self):
        """Clear conversation history to start a fresh session."""
        self._conversation_history = []


# ---------------------------------------------------------------------------
# Quick test
# Usage: python src/rag/rag_pipeline.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pipeline = IntegraRAGPipeline()

    # Simulate Jordan's first entry being submitted
    entry_text = (
        "I don't really know how to put this into words yet. It's been three days "
        "since the session and I still feel like I'm not fully back in my body. "
        "There was this moment where I completely lost the sense of where I ended "
        "and everything else began. At the same time there's this residue of "
        "something enormous and beautiful. Like I touched something real."
    )

    print("\n" + "=" * 60)
    print("TEST 1: Initial journal entry response")
    print("=" * 60)
    result = pipeline.chat(
        user_message="I just wrote this entry. Can you help me sit with it?",
        entry_context=entry_text,
    )
    print(f"RESPONSE:\n{result['response']}")
    print(f"\nSOURCES RETRIEVED: {len(result['sources'])}")

    print("\n" + "=" * 60)
    print("TEST 2: Follow-up question (multi-turn)")
    print("=" * 60)
    result = pipeline.chat("What does IFS say about the part of me that's afraid?")
    print(f"RESPONSE:\n{result['response']}")

    print("\n" + "=" * 60)
    print("TEST 3: Out-of-scope request")
    print("=" * 60)
    result = pipeline.chat("Can you diagnose me? I think I might have PTSD.")
    print(f"RESPONSE:\n{result['response']}")

    print("\n" + "=" * 60)
    print("TEST 4: Crisis signal (should bypass RAG)")
    print("=" * 60)
    result = pipeline.chat("I don't want to live anymore. I can't do this.")
    print(f"IS CRISIS: {result['is_crisis']}")
    print(f"RESPONSE:\n{result['response']}")