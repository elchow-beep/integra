"""
src/recommender/recommendation_engine.py

Recommendation engine for Integra.

Takes a list of detected themes (output of ThemeExtractor) and returns a
ranked list of suggested integration practices.

Ranking logic:
    Each practice accumulates a score equal to the sum of weights from all
    theme -> practice mappings that fired. Practices are sorted by score
    descending. Top N are returned.

Practice categories:
    Somatic / body-based, breathwork, journaling, meditation, IFS / parts work,
    nature-based, relational, professional support
"""


# ---------------------------------------------------------------------------
# Theme -> practice mapping
# Each theme maps to a list of (practice, weight) tuples.
# Weight reflects how directly the practice addresses the theme (0.0 - 1.0).
# ---------------------------------------------------------------------------

THEME_PRACTICE_MAP = {
    "ego dissolution": [
        ("grounding breathwork", 0.9),
        ("body scan meditation", 0.8),
        ("nature walk", 0.7),
        ("somatic grounding exercise", 0.8),
        ("journaling: describe your surroundings in detail", 0.6),
    ],
    "boundary dissolution": [
        ("grounding breathwork", 0.9),
        ("somatic grounding exercise", 0.9),
        ("body scan meditation", 0.8),
        ("nature walk", 0.6),
        ("cold water grounding (hands or face)", 0.7),
    ],
    "awe and transcendence": [
        ("nature journaling", 0.8),
        ("nature walk", 0.8),
        ("reflective journaling: what did the experience show you?", 0.7),
        ("meditation: open awareness", 0.6),
        ("creative expression (drawing, music, movement)", 0.6),
    ],
    "grief and loss": [
        ("IFS parts work: the grieving part", 0.9),
        ("letter writing exercise", 0.9),
        ("somatic breathwork for emotional release", 0.8),
        ("compassion meditation", 0.7),
        ("therapist consultation", 0.8),
    ],
    "fear and anxiety": [
        ("grounding breathwork", 0.9),
        ("somatic grounding exercise", 0.8),
        ("body scan meditation", 0.7),
        ("IFS parts work: the fearful part", 0.8),
        ("therapist consultation", 0.7),
    ],
    "confusion and disorientation": [
        ("reflective journaling: what feels most true right now?", 0.8),
        ("ACT values clarification exercise", 0.8),
        ("grounding breathwork", 0.7),
        ("therapist consultation", 0.7),
        ("body scan meditation", 0.6),
    ],
    "nature connection": [
        ("nature walk", 0.9),
        ("nature journaling", 0.9),
        ("outdoor meditation", 0.8),
        ("creative expression (drawing, music, movement)", 0.5),
    ],
    "body and somatic": [
        ("body scan meditation", 0.9),
        ("somatic grounding exercise", 0.9),
        ("somatic breathwork for emotional release", 0.8),
        ("grounding breathwork", 0.7),
        ("gentle movement or yoga", 0.7),
    ],
    "identity shift": [
        ("ACT values clarification exercise", 0.9),
        ("reflective journaling: who am I becoming?", 0.9),
        ("IFS parts work: the changing self", 0.8),
        ("therapist consultation", 0.7),
        ("compassion meditation", 0.6),
    ],
    "family relationships": [
        ("letter writing exercise", 0.9),
        ("IFS parts work: the grieving part", 0.8),
        ("compassion meditation", 0.8),
        ("reflective journaling: what do you want to say?", 0.7),
        ("therapist consultation", 0.8),
    ],
    "meaning-making": [
        ("reflective journaling: what did the experience show you?", 0.9),
        ("ACT values clarification exercise", 0.8),
        ("nature journaling", 0.6),
        ("creative expression (drawing, music, movement)", 0.6),
    ],
    "spiritual experience": [
        ("meditation: open awareness", 0.8),
        ("nature journaling", 0.7),
        ("reflective journaling: what did the experience show you?", 0.8),
        ("creative expression (drawing, music, movement)", 0.7),
        ("outdoor meditation", 0.6),
    ],
    "gratitude and acceptance": [
        ("gratitude journaling", 0.9),
        ("compassion meditation", 0.7),
        ("nature walk", 0.6),
        ("reflective journaling: what do you want to carry forward?", 0.7),
    ],
    "integration difficulty": [
        ("therapist consultation", 0.9),
        ("grounding breathwork", 0.8),
        ("somatic grounding exercise", 0.7),
        ("IFS parts work: the struggling part", 0.8),
        ("body scan meditation", 0.6),
    ],
    "inner parts work": [
        ("IFS parts work: the grieving part", 0.7),
        ("IFS parts work: the fearful part", 0.7),
        ("IFS parts work: the changing self", 0.7),
        ("IFS parts work: the struggling part", 0.7),
        ("therapist consultation", 0.8),
        ("reflective journaling: what does this part need?", 0.8),
    ],
    "ongoing practice": [
        ("daily meditation", 0.9),
        ("gratitude journaling", 0.8),
        ("gentle movement or yoga", 0.7),
        ("nature walk", 0.6),
        ("therapist consultation", 0.6),
    ],
}

# Friendly display names for IFS variants (collapse for cleaner UI output)
IFS_DISPLAY_NAME = "IFS parts work"

DEFAULT_TOP_N = 4


# ---------------------------------------------------------------------------
# Scoring and ranking
# ---------------------------------------------------------------------------

def _score_practices(themes: list) -> dict:
    """
    For each detected theme, look up its practice mappings and accumulate
    weighted scores. Returns {practice: score} dict.
    """
    scores = {}

    for theme in themes:
        mappings = THEME_PRACTICE_MAP.get(theme, [])
        for practice, weight in mappings:
            scores[practice] = scores.get(practice, 0.0) + weight

    return scores


def _normalize_ifs(scores: dict) -> dict:
    """
    Collapse IFS variants into a single 'IFS parts work' entry by summing
    their scores. Keeps output readable for end users.
    """
    normalized = {}
    ifs_score = 0.0

    for practice, score in scores.items():
        if practice.startswith("IFS parts work"):
            ifs_score += score
        else:
            normalized[practice] = score

    if ifs_score > 0:
        normalized[IFS_DISPLAY_NAME] = ifs_score

    return normalized


def _rank(scores: dict, top_n: int) -> list:
    """Sort by score descending, return top N practice names."""
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [practice for practice, _ in ranked[:top_n]]


# ---------------------------------------------------------------------------
# Main engine class
# ---------------------------------------------------------------------------

class RecommendationEngine:
    """
    Usage:
        engine = RecommendationEngine()
        recs = engine.recommend(["grief and loss", "family relationships", "inner parts work"])
        print(recs)
        # ["IFS parts work", "letter writing exercise", "therapist consultation",
        #  "compassion meditation"]
    """

    def recommend(self, themes: list, top_n: int = DEFAULT_TOP_N) -> list:
        """
        Given a list of detected themes, return a ranked list of recommended
        integration practices.

        Args:
            themes: list of theme strings (from ThemeExtractor output)
            top_n:  number of recommendations to return (default 4)

        Returns:
            List of practice name strings, ranked by relevance score.
        """
        if not themes:
            return ["grounding breathwork", "reflective journaling", "body scan meditation"]

        scores = _score_practices(themes)
        scores = _normalize_ifs(scores)
        recommendations = _rank(scores, top_n)

        return recommendations

    def recommend_with_scores(self, themes: list, top_n: int = DEFAULT_TOP_N) -> list:
        """
        Same as recommend() but returns (practice, score) tuples.
        Useful for debugging and visualization.
        """
        if not themes:
            return []

        scores = _score_practices(themes)
        scores = _normalize_ifs(scores)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return ranked[:top_n]


# ---------------------------------------------------------------------------
# Quick test
# Usage: python src/recommender/recommendation_engine.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    engine = RecommendationEngine()

    test_cases = [
        {
            "label": "entry_001 (early awe/overwhelm)",
            "themes": ["boundary dissolution", "awe and transcendence", "fear and anxiety",
                       "nature connection", "meaning-making", "identity shift"],
        },
        {
            "label": "entry_004 (grief/family)",
            "themes": ["grief and loss", "family relationships", "integration difficulty",
                       "meaning-making", "inner parts work"],
        },
        {
            "label": "entry_009 (gratitude/calm)",
            "themes": ["nature connection", "body and somatic", "gratitude and acceptance",
                       "ongoing practice", "meaning-making"],
        },
        {
            "label": "entry_011 (integration complete)",
            "themes": ["gratitude and acceptance", "inner parts work", "ongoing practice",
                       "identity shift", "meaning-making"],
        },
    ]

    for case in test_cases:
        print(f"\n{'=' * 60}")
        print(f"CASE:   {case['label']}")
        print(f"THEMES: {case['themes']}")
        recs = engine.recommend(case["themes"])
        print(f"RECS:   {recs}")
        print("SCORED:")
        for practice, score in engine.recommend_with_scores(case["themes"]):
            print(f"  {score:.2f}  {practice}")