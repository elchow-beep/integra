from transformers import pipeline

# Load pretrained emotion classifier
print("Loading RoBERTa emotion classifier...")
classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None  # return scores for all emotions
)

# Test with sample journal entries
test_entries = [
    "I felt completely overwhelmed during the experience. There was so much grief I didn't know I was carrying.",
    "It was the most beautiful thing I've ever felt. Pure love and gratitude for everything.",
    "I'm confused about what I saw. Parts of it felt meaningful but I can't make sense of it.",
    "There was a moment of pure terror when I lost sense of who I was.",
    "I feel lighter today. Like something heavy has finally lifted."
]

print("\n--- Emotion Classification Results ---\n")
for entry in test_entries:
    results = classifier(entry)[0]
    # Sort by score descending
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    top = results[0]
    print(f"Entry: {entry[:60]}...")
    print(f"  Top emotion: {top['label']} ({top['score']:.2%})")
    print(f"  All scores:")
    for r in results:
        bar = "█" * int(r["score"] * 20)
        print(f"    {r['label']:10s} {r['score']:.2%} {bar}")
    print()