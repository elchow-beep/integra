"""
src/nlp/longitudinal_tracker.py

Longitudinal tracking for Integra.

Reads a user's full entry history from users.json and produces structured
data for visualization in the Streamlit frontend.

Outputs:
    - emotion_timeline:     emotion scores per entry over time (for line chart)
    - dominant_emotions:    most prominent emotion per entry (for annotation)
    - theme_frequency:      how often each theme appears across all entries
    - recommendation_freq:  how often each practice is recommended
    - arc_summary:          plain-language summary of the emotional arc
    - weekly_averages:      emotion scores averaged by week (for area chart)
"""

import json
import os
from collections import Counter
from datetime import datetime


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

USERS_FILE = "data/demo/users.json"

INTEGRA_EMOTIONS = [
    "awe", "overwhelm", "fear", "grief", "confusion", "joy", "gratitude", "calm"
]

# Color map for consistent chart styling across the Streamlit frontend
EMOTION_COLORS = {
    "awe":        "#7C6AF7",  # violet
    "overwhelm":  "#F97316",  # orange
    "fear":       "#EF4444",  # red
    "grief":      "#64748B",  # slate
    "confusion":  "#F59E0B",  # amber
    "joy":        "#22C55E",  # green
    "gratitude":  "#06B6D4",  # cyan
    "calm":       "#A3E635",  # lime
}


def load_user(user_id: str, users_file: str = USERS_FILE) -> dict:
    """Load a single user dict from users.json by user_id."""
    with open(users_file, "r") as f:
        data = json.load(f)

    for user in data["users"]:
        if user["user_id"] == user_id:
            return user

    raise ValueError(f"User '{user_id}' not found in {users_file}")


# ---------------------------------------------------------------------------
# Core tracking functions
# ---------------------------------------------------------------------------

def emotion_timeline(entries: list) -> list:
    """
    Return a list of dicts, one per entry, with date and all emotion scores.
    Emotions not present in an entry default to 0.0.

    Output format (ready for Streamlit line chart via pandas DataFrame):
        [
            {"date": "2026-01-22", "awe": 0.88, "overwhelm": 0.76, ...},
            ...
        ]
    """
    timeline = []

    for entry in entries:
        row = {"date": entry["date"], "entry_id": entry["entry_id"]}
        emotions = entry.get("emotions", {})
        for emotion in INTEGRA_EMOTIONS:
            row[emotion] = emotions.get(emotion, 0.0)
        timeline.append(row)

    # Sort by date ascending
    timeline.sort(key=lambda x: x["date"])
    return timeline


def dominant_emotions(entries: list) -> list:
    """
    Return a list of (date, dominant_emotion, score) tuples -- one per entry.
    Dominant is the highest-scoring emotion in that entry.
    """
    result = []

    for entry in sorted(entries, key=lambda x: x["date"]):
        emotions = entry.get("emotions", {})
        if not emotions:
            continue
        dominant = max(emotions, key=emotions.get)
        score = emotions[dominant]
        result.append({
            "date": entry["date"],
            "entry_id": entry["entry_id"],
            "dominant_emotion": dominant,
            "score": score,
        })

    return result


def theme_frequency(entries: list) -> list:
    """
    Count how often each theme appears across all entries.

    Returns list of (theme, count) tuples sorted by count descending.
    """
    counter = Counter()

    for entry in entries:
        for theme in entry.get("themes", []):
            counter[theme] += 1

    return counter.most_common()


def recommendation_frequency(entries: list) -> list:
    """
    Count how often each practice is recommended across all entries.

    Returns list of (practice, count) tuples sorted by count descending.
    """
    counter = Counter()

    for entry in entries:
        for rec in entry.get("recommendations", []):
            counter[rec] += 1

    return counter.most_common()


def weekly_averages(entries: list) -> list:
    """
    Group entries by week number relative to the first entry and compute
    average emotion scores per week.

    Week is defined as 7-day buckets from the first entry date.

    Output format:
        [
            {"week": 1, "awe": 0.84, "overwhelm": 0.79, ...},
            {"week": 2, "awe": 0.71, "overwhelm": 0.63, ...},
            ...
        ]
    """
    if not entries:
        return []

    sorted_entries = sorted(entries, key=lambda x: x["date"])
    first_date = datetime.strptime(sorted_entries[0]["date"], "%Y-%m-%d")

    # Bucket entries by week
    weeks = {}
    for entry in sorted_entries:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
        delta_days = (entry_date - first_date).days
        week_num = (delta_days // 7) + 1

        if week_num not in weeks:
            weeks[week_num] = []
        weeks[week_num].append(entry.get("emotions", {}))

    # Average emotion scores within each week
    result = []
    for week_num in sorted(weeks.keys()):
        week_entries = weeks[week_num]
        row = {"week": week_num}
        for emotion in INTEGRA_EMOTIONS:
            scores = [e.get(emotion, 0.0) for e in week_entries]
            row[emotion] = round(sum(scores) / len(scores), 4)
        result.append(row)

    return result


def arc_summary(entries: list) -> dict:
    """
    Generate a plain-language summary of the user's emotional arc.

    Returns a dict with:
        total_entries:      int
        date_range:         str  e.g. "Jan 22 - Mar 5"
        opening_emotions:   list of dominant emotions in first 2 entries
        closing_emotions:   list of dominant emotions in last 2 entries
        peak_emotion:       emotion with highest single-entry score overall
        most_common_theme:  most frequently appearing theme
        summary_text:       one paragraph plain-language arc description
    """
    if not entries:
        return {"summary_text": "No entries yet."}

    sorted_entries = sorted(entries, key=lambda x: x["date"])
    dom = dominant_emotions(sorted_entries)
    tf = theme_frequency(sorted_entries)

    opening = [d["dominant_emotion"] for d in dom[:2]]
    closing = [d["dominant_emotion"] for d in dom[-2:]]

    # Find peak emotion (highest single score across all entries)
    peak_emotion = None
    peak_score = 0.0
    for entry in sorted_entries:
        for emotion, score in entry.get("emotions", {}).items():
            if score > peak_score:
                peak_score = score
                peak_emotion = emotion

    most_common_theme = tf[0][0] if tf else None

    first_date = datetime.strptime(sorted_entries[0]["date"], "%Y-%m-%d")
    last_date = datetime.strptime(sorted_entries[-1]["date"], "%Y-%m-%d")
    date_range = f"{first_date.strftime('%b %d')} - {last_date.strftime('%b %d')}"

    # Build summary text
    opening_str = " and ".join(set(opening))
    closing_str = " and ".join(set(closing))
    summary_text = (
        f"Over {len(sorted_entries)} entries from {date_range}, your integration "
        f"process moved from a place of {opening_str} in the early weeks toward "
        f"{closing_str} as the process deepened. "
        f"The peak emotional intensity was {peak_emotion} "
        f"(score: {round(peak_score, 2)}). "
        f"The theme that appeared most consistently across your entries "
        f"was '{most_common_theme}'."
    )

    return {
        "total_entries": len(sorted_entries),
        "date_range": date_range,
        "opening_emotions": opening,
        "closing_emotions": closing,
        "peak_emotion": peak_emotion,
        "peak_score": round(peak_score, 2),
        "most_common_theme": most_common_theme,
        "summary_text": summary_text,
    }


# ---------------------------------------------------------------------------
# Main tracker class -- wraps all functions for a given user
# ---------------------------------------------------------------------------

class LongitudinalTracker:
    """
    Usage:
        tracker = LongitudinalTracker("user_demo_established")
        print(tracker.summary["summary_text"])
        print(tracker.timeline)       # for line chart
        print(tracker.weekly)         # for area chart
        print(tracker.themes)         # for bar chart
    """

    def __init__(self, user_id: str, users_file: str = USERS_FILE):
        user = load_user(user_id, users_file)
        entries = user.get("entries", [])

        self.user_id = user_id
        self.name = user.get("name", "")
        self.entries = entries
        self.timeline = emotion_timeline(entries)
        self.dominant = dominant_emotions(entries)
        self.themes = theme_frequency(entries)
        self.recommendations = recommendation_frequency(entries)
        self.weekly = weekly_averages(entries)
        self.summary = arc_summary(entries)


# ---------------------------------------------------------------------------
# Quick test
# Usage: python -m src.nlp.longitudinal_tracker
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("LONGITUDINAL TRACKING TEST -- Jordan")
    print("=" * 60)

    tracker = LongitudinalTracker("user_demo_established")

    print(f"\nUSER: {tracker.name} ({tracker.user_id})")
    print(f"ENTRIES: {tracker.summary['total_entries']}")
    print(f"DATE RANGE: {tracker.summary['date_range']}")

    print("\n--- ARC SUMMARY ---")
    print(tracker.summary["summary_text"])

    print("\n--- DOMINANT EMOTION PER ENTRY ---")
    for d in tracker.dominant:
        print(f"  {d['date']}  {d['dominant_emotion']:12s}  {d['score']:.2f}")

    print("\n--- WEEKLY AVERAGES ---")
    for week in tracker.weekly:
        week_num = week["week"]
        top = sorted(
            [(e, week[e]) for e in INTEGRA_EMOTIONS if week[e] > 0],
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        top_str = ", ".join(f"{e}={s:.2f}" for e, s in top)
        print(f"  Week {week_num}: {top_str}")

    print("\n--- TOP THEMES ---")
    for theme, count in tracker.themes[:6]:
        print(f"  {count}x  {theme}")

    print("\n--- TOP RECOMMENDATIONS ---")
    for rec, count in tracker.recommendations[:5]:
        print(f"  {count}x  {rec}")

    print("\n--- EMOTION COLORS (for Streamlit) ---")
    for emotion, color in EMOTION_COLORS.items():
        print(f"  {emotion:12s}  {color}")

    print("\n--- EMPTY STATE TEST (Alex) ---")
    tracker_alex = LongitudinalTracker("user_demo_new")
    print(f"Alex summary: {tracker_alex.summary}")