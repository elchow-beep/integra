"""
backend/main.py

FastAPI backend for Integra.

How to run:
    cd ~/integra
    source venv/bin/activate
    uvicorn backend.main:app --reload --port 8000
"""

import json
import os
import sys
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

app = FastAPI(title="Integra API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://integra-journal.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_emotion_pipeline = None
_theme_extractor = None
_rag_pipeline = None


def get_emotion_pipeline():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        from src.nlp.emotion_pipeline import EmotionPipeline
        _emotion_pipeline = EmotionPipeline()
    return _emotion_pipeline


def get_theme_extractor():
    global _theme_extractor
    if _theme_extractor is None:
        from src.nlp.theme_extractor import ThemeExtractor
        _theme_extractor = ThemeExtractor()
    return _theme_extractor


def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        from src.rag.rag_pipeline import IntegraRAGPipeline
        _rag_pipeline = IntegraRAGPipeline()
    return _rag_pipeline


USERS_FILE = os.path.join(ROOT, "data", "demo", "users.json")

PROFILE_BLURBS = {
    "user_demo_new": "New user. No entries yet. Shows the onboarding experience.",
    "user_demo_established": "11 entries across 6 weeks. Full arc from awe and overwhelm through grief toward gratitude.",
}


def load_users_data():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users_data(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def find_user(user_id):
    data = load_users_data()
    for user in data["users"]:
        if user["user_id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")


class NewEntryRequest(BaseModel):
    user_id: str
    text: str
    week_number: Optional[int] = None


class ChatRequest(BaseModel):
    user_id: str
    message: str
    entry_context: Optional[str] = None


class ChatResetRequest(BaseModel):
    user_id: str


@app.get("/")
def health_check():
    return {"status": "ok", "app": "Integra API"}


@app.get("/users")
def list_users():
    data = load_users_data()
    profiles = []
    for user in data["users"]:
        user_id = user["user_id"]
        entry_count = len(user.get("entries", []))
        profiles.append({
            "user_id": user_id,
            "display_name": user.get("name", user_id),
            "context_blurb": PROFILE_BLURBS.get(user_id, ""),
            "entry_count": entry_count,
        })
    return {"users": profiles}


@app.get("/users/{user_id}/entries")
def get_entries(user_id: str):
    user = find_user(user_id)
    entries = user.get("entries", [])
    entries_sorted = sorted(entries, key=lambda e: e.get("date", ""), reverse=True)
    return {"user_id": user_id, "entries": entries_sorted}


@app.get("/users/{user_id}/insights")
def get_insights(user_id: str):
    from src.nlp.longitudinal_tracker import (
        emotion_timeline,
        dominant_emotions,
        theme_frequency,
        recommendation_frequency,
        arc_summary,
        weekly_averages,
        EMOTION_COLORS,
    )
    user = find_user(user_id)
    entries = user.get("entries", [])
    if not entries:
        return {"user_id": user_id, "has_data": False, "emotion_colors": EMOTION_COLORS}
    return {
        "user_id": user_id,
        "has_data": True,
        "emotion_timeline": emotion_timeline(entries),
        "dominant_emotions": dominant_emotions(entries),
        "theme_frequency": theme_frequency(entries),
        "recommendation_frequency": recommendation_frequency(entries),
        "arc_summary": arc_summary(entries).get("summary_text", ""),
        "weekly_averages": weekly_averages(entries),
        "emotion_colors": EMOTION_COLORS,
    }


@app.post("/entries")
def create_entry(req: NewEntryRequest):
    ep = get_emotion_pipeline()
    te = get_theme_extractor()
    emotion_result = ep.analyze(req.text)
    emotions = emotion_result.get("integra_emotions", {})
    themes = te.extract(req.text)

    from src.recommender.recommendation_engine import RecommendationEngine
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.recommend(themes)

    entry = {
        "entry_id": str(uuid.uuid4()),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "week_number": req.week_number,
        "text": req.text,
        "emotions": emotions,
        "themes": themes,
        "recommendations": recommendations,
    }

    data = load_users_data()
    for user in data["users"]:
        if user["user_id"] == req.user_id:
            if "entries" not in user:
                user["entries"] = []
            user["entries"].append(entry)
            break
    else:
        raise HTTPException(status_code=404, detail=f"User '{req.user_id}' not found")

    save_users_data(data)
    return {"entry": entry}


@app.post("/chat")
def chat(req: ChatRequest):
    rag = get_rag_pipeline()
    result = rag.chat(
        user_message=req.message,
        entry_context=req.entry_context,
    )
    return {
        "response": result["response"],
        "sources": result.get("sources", []),
        "crisis_detected": result.get("crisis_detected", False),
    }


@app.post("/chat/reset")
def reset_chat(req: ChatResetRequest):
    rag = get_rag_pipeline()
    rag.reset_conversation()
    return {"status": "ok"}