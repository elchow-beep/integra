"""
src/nlp/emotion_pipeline.py

Emotion detection pipeline for Integra.

Step 1: Run text through RoBERTa classifier (7 base emotions) via HuggingFace
        Inference API -- no local model download required.
Step 2: Remap base emotions to Integra-specific labels using a weighted
        combination matrix.
Step 3: Return a scored dict of Integra emotions, filtered to those above
        a confidence threshold.

Integra emotion labels:
    awe, overwhelm, fear, grief, confusion, joy, gratitude, calm
"""

import os
import time
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Remapping matrix
# Each RoBERTa base label maps to one or more Integra labels with weights.
# Weights represent how much a base emotion contributes to each Integra label.
# Rows are base labels; values are {integra_label: weight} dicts.
# Weights per row do not need to sum to 1 -- they are applied independently.
# ---------------------------------------------------------------------------

REMAPPING_MATRIX = {
    "anger": {
        "overwhelm": 0.5,
        "confusion": 0.4,
        "grief": 0.2,
    },
    "disgust": {
        "confusion": 0.5,
        "overwhelm": 0.3,
    },
    "fear": {
        "fear": 0.9,
        "overwhelm": 0.5,
        "confusion": 0.3,
    },
    "joy": {
        "joy": 0.8,
        "gratitude": 0.7,
        "awe": 0.4,
        "calm": 0.3,
    },
    "neutral": {
        "calm": 0.7,
        "confusion": 0.2,
    },
    "sadness": {
        "grief": 0.9,
        "overwhelm": 0.4,
        "confusion": 0.2,
    },
    "surprise": {
        "awe": 0.8,
        "overwhelm": 0.5,
        "confusion": 0.4,
    },
}

INTEGRA_LABELS = ["awe", "overwhelm", "fear", "grief", "confusion", "joy", "gratitude", "calm"]

CONFIDENCE_THRESHOLD = 0.2

MODEL_ID = "j-hartmann/emotion-english-distilroberta-base"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries on transient errors


def _remap(base_scores: dict) -> dict:
    """
    Apply remapping matrix to a dict of {base_label: score} and return
    a dict of {integra_label: score}, clipped to [0, 1].
    """
    integra_scores = {label: 0.0 for label in INTEGRA_LABELS}

    for base_label, base_score in base_scores.items():
        mappings = REMAPPING_MATRIX.get(base_label, {})
        for integra_label, weight in mappings.items():
            integra_scores[integra_label] += base_score * weight

    integra_scores = {k: min(round(v, 4), 1.0) for k, v in integra_scores.items()}

    return integra_scores


def _filter(integra_scores: dict, threshold: float = CONFIDENCE_THRESHOLD) -> dict:
    """Remove emotions below the confidence threshold."""
    return {k: v for k, v in integra_scores.items() if v >= threshold}


class EmotionPipeline:
    """
    Usage:
        ep = EmotionPipeline()
        result = ep.analyze("I felt completely overwhelmed but also filled with awe.")
        print(result)
        # {
        #     "base_emotions": {"fear": 0.12, "joy": 0.08, "surprise": 0.71, ...},
        #     "integra_emotions": {"awe": 0.78, "overwhelm": 0.64, "confusion": 0.41},
        #     "dominant_emotion": "awe"
        # }

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
        print("EmotionPipeline ready (Inference API).")

    def analyze(self, text: str) -> dict:
        """
        Run the full emotion pipeline on a string of text.

        Returns:
            dict with keys:
                base_emotions    -- raw RoBERTa output {label: score}
                integra_emotions -- remapped and filtered {label: score}
                dominant_emotion -- highest-scoring Integra label
        """
        if not text or not text.strip():
            return {
                "base_emotions": {},
                "integra_emotions": {},
                "dominant_emotion": None,
            }

        # Retry loop for transient API / cold-start errors
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                # Returns a list of {"label": str, "score": float} dicts
                raw = self._client.text_classification(
                    text=text,
                    model=MODEL_ID,
                )
                break
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    print(f"EmotionPipeline: attempt {attempt + 1} failed ({e}), retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
        else:
            raise RuntimeError(
                f"EmotionPipeline failed after {MAX_RETRIES} attempts. Last error: {last_error}"
            )

        # InferenceClient returns a list of ClassificationOutput objects
        # Each has .label and .score attributes (also supports dict-style access)
        base_scores = {item.label: round(item.score, 4) for item in raw}

        integra_scores = _remap(base_scores)
        filtered = _filter(integra_scores)

        dominant = max(filtered, key=filtered.get) if filtered else None

        return {
            "base_emotions": base_scores,
            "integra_emotions": filtered,
            "dominant_emotion": dominant,
        }


# ---------------------------------------------------------------------------
# Quick test -- run this file directly to verify the pipeline works
# Usage: python -m src.nlp.emotion_pipeline
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ep = EmotionPipeline()

    test_entries = [
        "I felt completely overwhelmed but also filled with awe. The boundary between me and the world dissolved.",
        "I've been sitting with grief about my dad. It's like weather that moved in and won't leave.",
        "Something is settling. I feel grateful just to be a thing that can walk and notice and feel.",
        "I don't know what to do with any of this. Everything feels confusing and strange.",
    ]

    for text in test_entries:
        print("\n" + "-" * 60)
        print(f"TEXT: {text[:80]}...")
        result = ep.analyze(text)
        print(f"BASE:     {result['base_emotions']}")
        print(f"INTEGRA:  {result['integra_emotions']}")
        print(f"DOMINANT: {result['dominant_emotion']}")