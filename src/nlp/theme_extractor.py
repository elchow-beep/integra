"""
src/nlp/theme_extractor.py

Theme extraction pipeline for Integra.

Two-layer approach:
    Layer 1: Keyword/phrase matching against a curated integration lexicon.
             Fast, interpretable, high precision for known integration language.
    Layer 2: Zero-shot classification using facebook/bart-large-mnli via
             HuggingFace Inference API -- no local model download required.
             Catches themes that keyword matching misses. Runs only on the
             themes not already caught by Layer 1.

Final output merges both layers, deduplicates, and returns a ranked list
of themes detected in the entry.

Theme categories (16 total):
    ego dissolution, boundary dissolution, awe and transcendence,
    grief and loss, fear and anxiety, confusion and disorientation,
    nature connection, body and somatic, identity shift, family relationships,
    meaning-making, spiritual experience, gratitude and acceptance,
    integration difficulty, inner parts work, ongoing practice
"""

import os
import time
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Integration lexicon -- keyword/phrase -> theme mapping
# Phrases are matched case-insensitively as substrings.
# ---------------------------------------------------------------------------

LEXICON = {
    "ego dissolution": [
        "ego death", "ego dissolution", "lost myself", "sense of self dissolved",
        "no longer felt like me", "self disappeared", "lost the sense of who",
    ],
    "boundary dissolution": [
        "boundary dissolved", "boundary between", "no separation", "merged with",
        "where I ended", "dissolved into", "couldn't tell where",
    ],
    "awe and transcendence": [
        "awe", "enormous", "infinite", "vastness", "transcen", "beyond words",
        "ineffable", "something larger", "cosmic", "universe", "opening",
        "sky kept opening", "touched something real",
    ],
    "grief and loss": [
        "grief", "loss", "mourning", "griev", "tears", "cried", "crying",
        "sadness", "ache", "hollow", "empty", "miss", "missing",
    ],
    "fear and anxiety": [
        "fear", "afraid", "terrified", "terror", "panic", "anxiety", "anxious",
        "scared", "dread", "frightened", "nervous",
    ],
    "confusion and disorientation": [
        "confused", "confusion", "disoriented", "don't know what to do",
        "unclear", "lost", "don't understand", "can't make sense",
        "don't know how", "foggy", "strange",
    ],
    "nature connection": [
        "trees", "nature", "river", "forest", "earth", "sky", "ocean",
        "outside", "walk", "birds", "alive", "everything is alive",
        "garden", "mountains", "wind",
    ],
    "body and somatic": [
        "body", "somatic", "breath", "breathwork", "sensation", "chest",
        "stomach", "tension", "physical", "grounded", "grounding",
        "in my body", "felt it in", "hands", "heart",
    ],
    "identity shift": [
        "who I am", "identity", "becoming", "who I'm becoming", "different person",
        "sense of self", "changed", "I'm not the same", "autopilot",
        "more myself", "my old self", "old part of myself",
    ],
    "family relationships": [
        "father", "dad", "mother", "mom", "brother", "sister", "family",
        "parent", "parents", "sibling", "childhood", "relationship with",
    ],
    "meaning-making": [
        "meaning", "understand", "make sense", "why", "purpose", "lesson",
        "what it means", "trying to understand", "what I learned",
        "integrate", "integration", "carry forward",
    ],
    "spiritual experience": [
        "spiritual", "sacred", "divine", "god", "universe", "presence",
        "something greater", "prayer", "mystical", "spirit", "soul",
        "light", "energy", "connected to everything",
    ],
    "gratitude and acceptance": [
        "grateful", "gratitude", "thankful", "accept", "acceptance",
        "at peace", "peace", "enough", "okay", "appreciate", "blessing",
    ],
    "integration difficulty": [
        "hard", "difficult", "struggle", "struggling", "not working",
        "can't integrate", "stuck", "overwhelmed by the process",
        "don't know how to", "jet lag", "can't stop it",
    ],
    "inner parts work": [
        "part of me", "parts", "inner", "IFS", "a part that", "old part",
        "defensive part", "the part that", "voice inside", "inner critic",
    ],
    "ongoing practice": [
        "meditation", "meditating", "journaling", "breathwork", "practice",
        "daily", "routine", "continuing", "keep doing", "committed to",
        "therapist", "therapy session",
    ],
}

ALL_THEMES = list(LEXICON.keys())

ZERO_SHOT_THRESHOLD = 0.20
MIN_KEYWORD_HITS = 1

MODEL_ID = "facebook/bart-large-mnli"
MAX_RETRIES = 3
RETRY_DELAY = 8  # bart-large-mnli can be slow to warm up; give it more time


# ---------------------------------------------------------------------------
# Layer 1: Keyword matching
# ---------------------------------------------------------------------------

def _keyword_match(text: str) -> list:
    """
    Return list of themes found via keyword/phrase matching.
    Case-insensitive substring search.
    """
    text_lower = text.lower()
    detected = []

    for theme, phrases in LEXICON.items():
        hits = sum(1 for phrase in phrases if phrase in text_lower)
        if hits >= MIN_KEYWORD_HITS:
            detected.append(theme)

    return detected


# ---------------------------------------------------------------------------
# Layer 2: Zero-shot classification via Inference API
# ---------------------------------------------------------------------------

def _zero_shot_classify(text: str, client: InferenceClient, candidate_themes: list) -> list:
    """
    Run zero-shot classification on themes not caught by keyword matching.
    Returns list of themes above the score threshold.

    The Inference API for zero-shot-classification returns a dict with
    "labels" and "scores" keys, matching the local pipeline output shape.
    """
    if not candidate_themes:
        return []

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            result = client.zero_shot_classification(
                text=text,
                candidate_labels=candidate_themes,
                multi_label=True,
                model=MODEL_ID,
            )
            break
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                print(f"ThemeExtractor: attempt {attempt + 1} failed ({e}), retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    else:
        print(f"ThemeExtractor: zero-shot failed after {MAX_RETRIES} attempts ({last_error}). Skipping zero-shot layer.")
        return []

    # InferenceClient returns a list of ClassificationOutput objects,
    # each with .label and .score attributes
    detected = [
        item.label
        for item in result
        if item.score >= ZERO_SHOT_THRESHOLD
    ]

    return detected


# ---------------------------------------------------------------------------
# Main extractor class
# ---------------------------------------------------------------------------

class ThemeExtractor:
    """
    Usage:
        extractor = ThemeExtractor()
        themes = extractor.extract("I felt the boundary between me and the world dissolve...")
        print(themes)
        # ["boundary dissolution", "awe and transcendence", "ego dissolution"]

    The zero-shot classifier is only called on themes not already found by
    keyword matching, keeping inference fast for entries with rich integration
    language.

    Uses the HuggingFace Inference API -- no local model download.
    Requires HF_TOKEN in .env (or Spaces secrets).
    """

    def __init__(self):
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not hf_token:
            raise ValueError(
                "HuggingFace token not found. Set HF_TOKEN in your .env file "
                "or in HuggingFace Spaces secrets."
            )
        self._client = InferenceClient(token=hf_token)
        print("ThemeExtractor ready (Inference API).")

    def extract(self, text: str, verbose: bool = False) -> list:
        """
        Run full two-layer theme extraction on a text string.

        Returns:
            Sorted list of detected theme strings.
        """
        if not text or not text.strip():
            return []

        # Layer 1
        keyword_themes = _keyword_match(text)

        # Layer 2 -- only run zero-shot on themes keyword matching missed
        remaining_themes = [t for t in ALL_THEMES if t not in keyword_themes]
        zero_shot_themes = _zero_shot_classify(text, self._client, remaining_themes)

        # Merge and deduplicate, preserving keyword results first
        all_themes = list(dict.fromkeys(keyword_themes + zero_shot_themes))

        if verbose:
            print(f"  Keyword match:  {keyword_themes}")
            print(f"  Zero-shot:      {zero_shot_themes}")
            print(f"  Combined:       {all_themes}")

        return all_themes


# ---------------------------------------------------------------------------
# Quick test -- run directly to verify
# Usage: python -m src.nlp.theme_extractor
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    extractor = ThemeExtractor()

    test_entries = [
        (
            "entry_001",
            "I don't really know how to put this into words yet. The boundary between me "
            "and the room dissolved. I feel a low hum of something that might be fear. "
            "At the same time there's this residue of something enormous and beautiful. "
            "I keep staring out the window at the trees."
        ),
        (
            "entry_004",
            "I've been thinking about my dad a lot. During the session I saw his face and "
            "started crying harder than I have in years. Now that things are quieter, that "
            "grief is sitting there waiting for me. It's like weather that moved in."
        ),
        (
            "entry_009",
            "I went on a long walk along the river and felt grateful. Not for anything specific. "
            "For being a thing that can walk and notice and feel. I did a breathwork session "
            "on my own and was able to go pretty deep without panicking."
        ),
        (
            "entry_011",
            "I feel like myself again, except the self feels more spacious. I'm going to keep "
            "journaling. I want to do IFS work with my therapist around the parts I noticed. "
            "This is what I did with it. That feels like enough for now."
        ),
    ]

    for entry_id, text in test_entries:
        print(f"\n{'=' * 60}")
        print(f"ENTRY: {entry_id}")
        print(f"TEXT:  {text[:100]}...")
        themes = extractor.extract(text, verbose=True)
        print(f"FINAL: {themes}")