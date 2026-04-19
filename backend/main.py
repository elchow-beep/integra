"""
backend/main.py

FastAPI backend for Indigo.

How to run:
    cd ~/indigo
    source venv/bin/activate
    uvicorn backend.main:app --reload --port 8000
"""

import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from backend.database import get_db
from backend import models

app = FastAPI(title="Indigo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
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


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class CreateUserRequest(BaseModel):
    name: str
    experience_date: str  # YYYY-MM-DD


class NewEntryRequest(BaseModel):
    user_id: str
    text: str
    week_number: Optional[int] = None
    entry_type: Optional[str] = "journal"
    checkin_emotion: Optional[str] = None


class ChatRequest(BaseModel):
    user_id: str
    message: str
    entry_context: Optional[str] = None


class ChatResetRequest(BaseModel):
    user_id: str


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    return {"status": "ok", "app": "Indigo API"}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    profiles = []
    for user in users:
        entry_count = db.query(models.Entry).filter(
            models.Entry.user_id == user.id
        ).count()
        if entry_count == 0:
            context_blurb = "New user. No entries yet."
        else:
            context_blurb = f"{entry_count} entries"
        profiles.append({
            "user_id": user.id,
            "display_name": user.display_name,
            "context_blurb": context_blurb,
            "entry_count": entry_count,
        })
    return {"users": profiles}


@app.post("/users")
def create_user(req: CreateUserRequest, db: Session = Depends(get_db)):
    name = req.name.strip()
    if not name or len(name) > 40:
        raise HTTPException(status_code=422, detail="Name must be between 1 and 40 characters")

    user_id = "user_" + str(uuid.uuid4())[:8]

    new_user = models.User(
        id=user_id,
        display_name=name,
        email=f"{user_id}@placeholder.indigo",  # placeholder until auth is built
        hashed_password="placeholder",           # placeholder until auth is built
        integration_phase="integration",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "user_id": new_user.id,
        "display_name": new_user.display_name,
        "context_blurb": "New user",
        "entry_count": 0,
        "experience_date": req.experience_date,
        "entries": [],
        "is_new": True,
    }


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------

@app.get("/users/{user_id}/entries")
def get_entries(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    entries = db.query(models.Entry).filter(
        models.Entry.user_id == user_id
    ).order_by(models.Entry.date.desc()).all()

    return {
        "user_id": user_id,
        "entries": [
            {
                "entry_id": e.id,
                "date": e.date.strftime("%Y-%m-%d") if e.date else None,
                "week_number": e.week_number,
                "text": e.text,
                "entry_type": e.entry_type,
                "emotions": e.emotions,
                "themes": e.themes,
                "recommendations": e.recommendations,
            }
            for e in entries
        ],
    }


@app.post("/entries")
def create_entry(req: NewEntryRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{req.user_id}' not found")

    ep = get_emotion_pipeline()
    te = get_theme_extractor()
    emotion_result = ep.analyze(req.text)
    emotions = emotion_result.get("integra_emotions", {})
    themes = te.extract(req.text)

    from src.recommender.recommendation_engine import RecommendationEngine
    recommendations = RecommendationEngine().recommend(themes)

    entry = models.Entry(
        id=str(uuid.uuid4()),
        user_id=req.user_id,
        text=req.text,
        week_number=req.week_number,
        entry_type=req.entry_type or "journal",
        emotions=emotions,
        themes=themes,
        recommendations=recommendations,
        date=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "entry": {
            "entry_id": entry.id,
            "date": entry.date.strftime("%Y-%m-%d"),
            "week_number": entry.week_number,
            "text": entry.text,
            "entry_type": entry.entry_type,
            "emotions": entry.emotions,
            "themes": entry.themes,
            "recommendations": entry.recommendations,
        }
    }


@app.delete("/users/{user_id}/entries/{entry_id}")
def delete_entry(user_id: str, entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(models.Entry).filter(
        models.Entry.id == entry_id,
        models.Entry.user_id == user_id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry '{entry_id}' not found")
    db.delete(entry)
    db.commit()
    return {"status": "ok", "deleted_entry_id": entry_id}


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

@app.get("/users/{user_id}/insights")
def get_insights(user_id: str, db: Session = Depends(get_db)):
    from src.nlp.longitudinal_tracker import (
        emotion_timeline,
        dominant_emotions,
        theme_frequency,
        recommendation_frequency,
        arc_summary,
        weekly_averages,
        EMOTION_COLORS,
    )
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    entries = db.query(models.Entry).filter(
        models.Entry.user_id == user_id
    ).order_by(models.Entry.date.asc()).all()

    if not entries:
        return {"user_id": user_id, "has_data": False, "emotion_colors": EMOTION_COLORS}

    # Convert ORM objects to dicts for the longitudinal tracker functions
    entries_as_dicts = [
        {
            "entry_id": e.id,
            "date": e.date.strftime("%Y-%m-%d") if e.date else None,
            "week_number": e.week_number,
            "emotions": e.emotions or {},
            "themes": e.themes or [],
            "recommendations": e.recommendations or [],
        }
        for e in entries
    ]

    return {
        "user_id": user_id,
        "has_data": True,
        "emotion_timeline": emotion_timeline(entries_as_dicts),
        "dominant_emotions": dominant_emotions(entries_as_dicts),
        "theme_frequency": theme_frequency(entries_as_dicts),
        "recommendation_frequency": recommendation_frequency(entries_as_dicts),
        "arc_summary": arc_summary(entries_as_dicts).get("summary_text", ""),
        "weekly_averages": weekly_averages(entries_as_dicts),
        "emotion_colors": EMOTION_COLORS,
    }


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

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


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    rag = get_rag_pipeline()

    def generate():
        yield from rag.chat_stream(
            user_message=req.message,
            entry_context=req.entry_context,
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/chat/reset")
def reset_chat(req: ChatResetRequest):
    rag = get_rag_pipeline()
    rag.reset_conversation()
    return {"status": "ok"}