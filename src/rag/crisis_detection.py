"""
src/rag/crisis_detection.py

Pre-LLM crisis detection for Integra.

This check runs on every user message BEFORE the RAG pipeline.
If crisis signals are detected, the RAG pipeline is bypassed entirely
and a crisis response is returned directly.

Two-layer detection (biased toward false positives -- missing a crisis
signal is worse than over-flagging):

    Layer 1: Keyword scan against a crisis signal list.
             Fast, runs first, zero API cost.
             If any keyword matches: flag as crisis immediately.

    Layer 2: GPT semantic check.
             Runs only if keyword layer is clean.
             Short, cheap GPT call: "does this message contain crisis signals?"
             Catches indirect expressions of distress that keywords miss.

Returns:
    {
        "is_crisis": bool,
        "method": "keyword" | "semantic" | "none",
        "response": str | None   # pre-written crisis response if flagged
    }
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------------------------
# Crisis response -- shown to user if crisis is detected.
# The RAG pipeline does not run when this fires.
# ---------------------------------------------------------------------------

CRISIS_RESPONSE = """What you're sharing matters, and I'm glad you're here.

Please reach out to the 988 Suicide and Crisis Lifeline by calling or texting 988 -- they're available 24/7 and trained to help. If you're in immediate danger, call 911.
""".strip()


# ---------------------------------------------------------------------------
# Layer 1: Keyword list
# Biased toward inclusion. Ambiguous terms are included rather than excluded.
# ---------------------------------------------------------------------------

CRISIS_KEYWORDS = [
    # Suicidal ideation
    "suicide", "suicidal", "kill myself", "end my life", "take my life",
    "don't want to be alive", "don't want to live", "want to die",
    "wish I were dead", "wish I was dead", "better off dead",
    "not worth living", "life isn't worth", "no reason to live",
    "thinking about ending", "thinking about death",

    # Self-harm
    "self-harm", "self harm", "hurt myself", "cutting myself", "cut myself",
    "burning myself", "harming myself", "injure myself",

    # Hopelessness markers (indirect but high-signal)
    "can't go on", "cannot go on", "can't do this anymore",
    "cannot do this anymore", "giving up", "no way out",
    "there's no point", "there is no point", "nothing matters anymore",

    # Acute psychosis / loss of reality contact (integration-specific risk)
    "i am god", "i am the messiah", "chosen one", "everyone is after me",
    "they are watching me", "voices telling me to",
]


def _keyword_check(text: str) -> bool:
    """Return True if any crisis keyword is found in the text."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CRISIS_KEYWORDS)


# ---------------------------------------------------------------------------
# Layer 2: GPT semantic check
# ---------------------------------------------------------------------------

SEMANTIC_CHECK_PROMPT = """You are a safety classifier for a mental health journaling app.

Your job is to determine whether the following user message contains crisis signals, including:
- Suicidal ideation or intent (explicit or indirect)
- Self-harm intent
- Acute hopelessness suggesting imminent risk
- Loss of contact with reality in a way that suggests acute psychosis

Respond with ONLY one word: YES or NO.
Do not explain. Do not add any other text.

User message:
{message}"""


def _semantic_check(text: str) -> bool:
    """
    Use GPT to semantically check for crisis signals.
    Returns True if GPT responds YES.
    Defaults to False on any API error (fail open, not fail closed --
    the keyword layer is the primary safety net).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": SEMANTIC_CHECK_PROMPT.format(message=text),
                }
            ],
            max_tokens=5,
            temperature=0.0,
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer == "YES"
    except Exception as e:
        print(f"[crisis_detection] Semantic check failed: {e}. Defaulting to no crisis.")
        return False


# ---------------------------------------------------------------------------
# Main check function
# ---------------------------------------------------------------------------

def check_for_crisis(text: str) -> dict:
    """
    Run the full two-layer crisis check on a user message.

    Args:
        text: the user's journal entry or chat message

    Returns:
        dict with keys:
            is_crisis (bool)
            method    ("keyword" | "semantic" | "none")
            response  (str crisis response if flagged, else None)
    """
    # Layer 1
    if _keyword_check(text):
        return {
            "is_crisis": True,
            "method": "keyword",
            "response": CRISIS_RESPONSE,
        }

    # Layer 2
    if _semantic_check(text):
        return {
            "is_crisis": True,
            "method": "semantic",
            "response": CRISIS_RESPONSE,
        }

    return {
        "is_crisis": False,
        "method": "none",
        "response": None,
    }


# ---------------------------------------------------------------------------
# Quick test
# Usage: python src/rag/crisis_detection.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_cases = [
        # Should flag
        ("explicit", "I've been thinking about ending my life. I don't see a way out."),
        ("indirect", "I've just been feeling like there's really no point to any of this anymore. I don't know how much longer I can keep going."),
        ("psychosis", "Since the session I've realized I am the messiah and I have a mission."),

        # Should not flag
        ("normal_hard", "This week has been really hard. I'm struggling with grief about my dad and feeling confused about who I am."),
        ("normal_awe", "The experience was enormous. I felt like I dissolved into everything. Still processing."),
        ("normal_calm", "Six weeks out. I feel like myself again, just more spacious. Grateful for the process."),
    ]

    print("Running crisis detection tests...\n")
    for label, text in test_cases:
        result = check_for_crisis(text)
        flag = "FLAGGED" if result["is_crisis"] else "clean"
        print(f"[{flag}] ({label}) via {result['method']}")
        print(f"  TEXT: {text[:80]}...")
        print()
