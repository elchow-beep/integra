# Integra -- Project Brief
*AI-Powered Psychedelic Integration Companion*

---

## Overview
Integra is a generative AI journaling app grounded in real psychedelic therapy frameworks (IFS, ACT, somatic work). Users write journal entries about their psychedelic experiences and integration process. The app analyzes emotional themes, tracks patterns over time, and recommends personalized practices -- all powered by a RAG pipeline trained on integration literature.

---

## Capstone Requirements
- **Program:** AI/ML Tech Bootcamp
- **Due Date:** March 15, 2026
- **ML Areas to Showcase:** NLP / Text Analysis, Recommendation Systems, Deep Learning, Generative AI / LLMs

---

## Core Features
1. **Journal Entry Interface** -- User writes about their experience/integration process
2. **Emotion & Theme Extraction** -- NLP pipeline detects emotional themes (grief, awe, fear, gratitude, confusion, etc.)
3. **Longitudinal Tracking** -- Visualizes emotional patterns across entries over time
4. **RAG Chatbot Companion** -- Responds to journal entries using integration literature as knowledge base
5. **Recommendation Engine** -- Suggests practices (breathwork, somatic exercises, IFS parts work, therapist resources) based on detected themes
6. **Emotion Quick Check-In** -- Tapping an emotion pill on the Home screen opens a bottom sheet with two paths: "Just log it" silently records the emotion to the longitudinal tracker with no redirect; "Chat with Indy" opens Companion with the selected emotion passed as context so Indy opens with a targeted prompt ("You checked in as [emotion] -- want to tell me what's going on?"). At the end of the Indy session, a "Save as journal entry" CTA posts the chat log to the `/entries` endpoint with an `entry_type: "checkin"` flag so Insights can distinguish quick check-ins from full journal entries.

---

## Tech Stack
| Component | Tool |
|---|---|
| Language | Python 3.13.5 |
| IDE | Cursor |
| Terminal | Warp |
| Virtual Env | venv (located at `~/integra/venv`) |
| LLM | OpenAI API (GPT-4o) |
| RAG Framework | LangChain + ChromaDB |
| NLP / Inference | HuggingFace Inference API (`huggingface_hub.InferenceClient`) |
| Emotion Classification | RoBERTa (`j-hartmann/emotion-english-distilroberta-base`) via Inference API |
| Zero-Shot Theme Classification | `facebook/bart-large-mnli` via Inference API |
| Recommendation | Weighted mapping + score ranking (pure Python) |
| Backend | FastAPI + Uvicorn |
| Frontend | React (Vite) + react-router-dom + Recharts |
| Backend Hosting | Railway (Docker, port 8000) |
| Frontend Hosting | Vercel (auto-deploy from GitHub, `frontend/` root) |
| Version Control | GitHub (`github.com/elchow-beep/integra`) |
| Portfolio Site | Framer (links to live app -- redirect URL TBD, post-March 15) |
| Data Storage | Local JSON (data/demo/users.json) |

---

## Project Structure
```
integra/
├── data/
│   ├── raw/          # original source documents (MAPS, PubMed, Semantic Scholar)
│   ├── processed/    # cleaned, chunked data for RAG
│   └── demo/         # seed data for demo user entities (Alex, Jordan)
│       └── users.json
├── notebooks/        # exploratory analysis and prototyping
├── src/
│   ├── __init__.py
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── emotion_pipeline.py      # RoBERTa via Inference API + remapping layer
│   │   ├── theme_extractor.py       # keyword matching + zero-shot via Inference API
│   │   └── longitudinal_tracker.py  # cross-entry pattern analysis
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── system_prompt.py         # chatbot system prompt
│   │   ├── crisis_detection.py      # pre-LLM crisis check (keyword + semantic)
│   │   └── rag_pipeline.py          # LangChain + ChromaDB + OpenAI pipeline
│   └── recommender/
│       ├── __init__.py
│       └── recommendation_engine.py # theme -> practice mapping + ranking
├── backend/
│   └── main.py                      # FastAPI server exposing all ML pipelines as HTTP endpoints
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.jsx                 # React entry point
│   │   ├── App.jsx                  # Router + user state + protected routes
│   │   ├── api.js                   # All fetch calls to FastAPI backend
│   │   ├── assets/
│   │   │   └── logo.svg             # Gradient logo (imported via vite-plugin-svgr)
│   │   ├── styles/
│   │   │   └── tokens.css           # Design tokens (colors, fonts, radius, spacing)
│   │   ├── pages/
│   │   │   ├── Login.jsx            # Profile cards, guest mode, disclaimer chip
│   │   │   ├── Home.jsx             # Greeting, mood check-in, last entry, arc summary, loading skeleton, empty state
│   │   │   ├── Journal.jsx          # Entry list + new entry submission + analysis results + Reflect with Indy CTA
│   │   │   ├── Insights.jsx         # Emotion timeline (Recharts), theme frequency chart, arc summary
│   │   │   └── Companion.jsx        # Indy chat interface with crisis detection, rotating thinking phrases, 988 call button
│   │   └── components/
│   │       ├── BottomNav.jsx        # Persistent tab bar (Home / Journal / Insights / Indy)
│   │       └── EmotionPill.jsx      # Reusable colored emotion chip
│   ├── vercel.json                  # Client-side routing fix for Vercel
│   ├── vite.config.js               # Vite config with svgr plugin
│   └── package.json
├── app/                             # Legacy Streamlit frontend (preserved, no longer active)
├── hf-integra/                      # Legacy HuggingFace Space repo clone (preserved)
├── Dockerfile                       # Railway deployment (FastAPI, port 8000)
├── .env                             # API keys (never commit)
├── .gitignore
├── requirements.txt
├── PROJECT_BRIEF.md
├── OPEN_TASKS.md
└── README.md
```

---

## Data Sources
- **MAPS Published Protocols** -- MDMA therapy manual (V8.1) + Integration Workbook (PDFs)
- **Yale Psilocybin Manual** -- Psilocybin-assisted therapy for depression (PDF)
- **Semantic Scholar API** -- 159 academic papers on psychedelic-assisted therapy
- **PubMed Open Access** -- 200 papers across 8 queries on psilocybin, MDMA, ketamine
- **Chacruna Institute** -- Planned for future sessions

---

## ChromaDB Vector Store
- **Location:** `data/chroma`
- **Total vectors:** 4,450
- **Sources:** Semantic Scholar abstracts + PubMed abstracts + 4 therapy manual PDFs
- **Embedding model:** `text-embedding-3-small` (OpenAI)
- **Chunk size:** 500 tokens, 50 overlap
- **Retrieval confirmed working** via `src/rag/test_retrieval.py`

---

## Demo User Entities

Two seed users are required for the capstone demo. Data lives in `data/demo/users.json`.

### User A: Alex (new user, empty state)
Demonstrates the onboarding flow, empty states, and first-time journal entry experience. Shows what the chatbot and recommendation engine look like before any data exists. No entries, no tracked emotions, no longitudinal data.

### User B: Jordan (established user, rich history)
Demonstrates longitudinal emotion tracking, pattern visualization over time, RAG chatbot with accumulated context, and personalized recommendations. Has 14 entries spread across 6 weeks (Jan 22 - Mar 5) tracing a realistic integration arc.

**Emotional arc -- confirmed working in longitudinal tracker:**
- Weeks 1-2: awe (0.83 avg) and overwhelm (0.79 avg) dominating
- Weeks 3-4: confusion (0.70-0.77 avg) and grief (0.56-0.61 avg) active
- Weeks 5-7: gratitude (0.68-0.84 avg) and joy (0.65-0.71 avg) resolving

**Top themes across Jordan's entries:** nature connection, meaning-making, family relationships, boundary dissolution, integration difficulty, identity shift

**Top recommendations across Jordan's entries:** IFS parts work, gratitude journaling, grounding breathwork, reflective journaling, somatic grounding

**Entry schema:**
```json
{
  "entry_id": "entry_001",
  "date": "2026-01-22",
  "text": "...",
  "emotions": {"awe": 0.88, "overwhelm": 0.76, "fear": 0.58},
  "themes": ["boundary dissolution", "awe and transcendence", "nature connection"],
  "recommendations": ["grounding breathwork", "nature journaling", "body scan meditation"]
}
```

---

## ML Pipeline Details

### Emotion Pipeline (`src/nlp/emotion_pipeline.py`)
- Uses HuggingFace Inference API via `InferenceClient.text_classification()` -- no local model download
- RoBERTa base model outputs 7 labels: anger, disgust, fear, joy, neutral, sadness, surprise
- Remapping matrix converts base scores to 8 Integra-specific labels: awe, overwhelm, fear, grief, confusion, joy, gratitude, calm
- Key mappings: surprise -> awe (0.8), sadness -> grief (0.9), joy -> gratitude (0.5) + calm (0.3)
- Emotions below 0.2 confidence threshold filtered from output
- Retry loop: 3 attempts with 5s delay for cold-start resilience
- Known limitation: gratitude-dominant text returns joy as dominant (RoBERTa has no gratitude label); scores are still meaningful
- `analyze()` returns a dict with keys `base_emotions`, `integra_emotions`, `dominant_emotion` -- backend extracts `integra_emotions` for entry storage

### Theme Extractor (`src/nlp/theme_extractor.py`)
- Uses HuggingFace Inference API via `InferenceClient.zero_shot_classification()` -- no local model download
- 16 integration-specific themes across categories: ego/boundary, emotional states, relational, somatic, spiritual, practice-oriented
- Layer 1: keyword/phrase matching against curated integration lexicon (fast, high precision)
- Layer 2: zero-shot classification via `facebook/bart-large-mnli` on themes keyword layer missed (flexible, catches plain-language expressions)
- Retry loop: 3 attempts with 8s delay (bart-large-mnli has longer cold-start)
- Zero-shot gracefully skipped on persistent failure -- keyword layer results still returned

### Recommendation Engine (`src/recommender/recommendation_engine.py`)
- Pure Python weighted mapping: theme -> list of practices with weights
- Score ranking returns top 3 practices per entry
- 16 themes mapped to practices across categories: breathwork, somatic, IFS, journaling, nature, therapist resources
- Exposed as `RecommendationEngine` class -- call via `RecommendationEngine().recommend(themes)`

### RAG Pipeline (`src/rag/rag_pipeline.py`)
- LangChain + ChromaDB + OpenAI GPT-4o
- Retrieves top-k relevant chunks from vector store based on user message
- Crisis detection runs pre-LLM on every message -- bypasses RAG entirely if triggered
- Multi-turn conversation history maintained per session
- Entry context injected on first message after journal submission

### Crisis Detection (`src/rag/crisis_detection.py`)
- Keyword layer: exact match against curated list of crisis phrases
- Semantic layer: cosine similarity against crisis reference sentences
- If triggered: returns shortened 988 Suicide and Crisis Lifeline message (2 sentences), skips LLM call entirely
- Frontend shows a tappable `<a href="tel:988">` call button below the crisis message

### Longitudinal Tracker (`src/nlp/longitudinal_tracker.py`)
- Computes emotion timeline, dominant emotions, theme frequency, recommendation frequency, weekly averages, arc summary
- `arc_summary()` returns a dict -- backend extracts `summary_text` field for frontend consumption
- `EMOTION_COLORS` dict is single source of truth for chart colors

---

## Backend API (`backend/main.py`)

FastAPI server wrapping all ML pipelines as HTTP endpoints.

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/users` | GET | List demo profiles with display names and entry counts |
| `/users/{user_id}/entries` | GET | All journal entries for a user, sorted newest first |
| `/users/{user_id}/insights` | GET | Full longitudinal analytics (timeline, themes, arc summary) |
| `/entries` | POST | Save new entry + run emotion/theme/recommendation pipelines |
| `/chat` | POST | Send message to Indy RAG chatbot |
| `/chat/reset` | POST | Clear conversation history |

CORS allowlist: `localhost:5173`, `localhost:3000`, `https://integra-journal.vercel.app`

---

## Frontend (`frontend/src/`)

React app built with Vite. All pages are protected routes -- redirects to `/login` if no user in state.

### Design Tokens (`styles/tokens.css`)
- Background: `#1c1a18`
- Surface: `#242220`
- Surface raised: `#2e2b28`
- Border: `#3a3733`
- Text primary: `#e8e3db`
- Text secondary: `#8a8480`
- Text muted: `#5a5652`
- Accent: `#c4956a`
- Fonts: DM Serif Display (display), DM Sans (body)

### Pages
- **Login** -- gradient logo SVG, profile cards (tap to select, amber border on selection), "Continue to Journal" primary button, "Chat with Indy as a guest" ghost button, disclaimer chip
- **Home** -- greeting with time of day, date eyebrow, quick mood check-in pills, "Write an entry" CTA card, pulsing skeleton loading state, last entry preview with emotion pills, arc summary card, "Getting started" empty state for new users, "Switch profile" button in header
- **Journal** -- entry list sorted newest first, emotion pills per entry, "+ New entry" button, entry submission form with pipeline results, "Reflect with Indy" primary CTA after submission, styled empty state for new users
- **Insights** -- arc summary card, emotion timeline line chart (Recharts), recurring themes horizontal bar chart
- **Companion** -- Indy chat interface, disclaimer chip, rotating thinking phrases, "Clear chat" button with confirmation banner, 988 call button on crisis responses, guest mode welcome note

### Key decisions
- `App.jsx` holds user state and passes `onSwitchProfile` down to Home
- `api.js` uses `VITE_API_URL` env variable with localhost fallback
- Logo imported as React component via `vite-plugin-svgr` using `?react` query syntax
- `vercel.json` rewrites all routes to `index.html` for client-side routing
- `theme_frequency` from backend is an array of `[name, count]` pairs -- `Insights.jsx` handles this directly without `Object.entries()`
- Guest users bypass all fetch calls in `Home.jsx` useEffect -- `setDataLoaded(true)` fires immediately so skeleton blocks don't hang

---

## Deployment

### Live URLs
- **Frontend:** `https://integra-journal.vercel.app`
- **Backend:** `https://integra.up.railway.app`

### GitHub Repo
`https://github.com/elchow-beep/integra`

### Frontend (Vercel)
- Auto-deploys from `frontend/` directory on every push to `main`
- Environment variable: `VITE_API_URL=https://integra.up.railway.app`
- `vercel.json` in `frontend/` handles client-side routing

### Backend (Railway)
- Deploys from root of repo using `Dockerfile`
- Port: 8000 (hardcoded in Dockerfile CMD)
- Environment variables set in Railway dashboard: `OPENAI_API_KEY`, `HF_TOKEN`
- Health check path: `/`

### To update the deployed app
```bash
cd ~/integra
# make changes
git add .
git commit -m "description"
git push origin main
# Vercel and Railway both auto-redeploy from main
```

### Legacy HuggingFace Space
- Still live at `https://huggingface.co/spaces/el-chow/integra` (Streamlit version)
- No longer being updated -- React/FastAPI stack is now the active version
- Local clone at `~/integra/hf-integra` preserved for reference

---

## Local Development

### Run backend
```bash
cd ~/integra
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

### Run frontend
```bash
cd ~/integra/frontend
npm run dev
# runs on http://localhost:5173
```

### Environment variables needed locally
Create `~/integra/.env`:
```
OPENAI_API_KEY=your_key
HF_TOKEN=your_token
```

---

## Learner Profile
- Still learning Python
- Familiar with HuggingFace and Scikit-learn
- Using Cursor (AI-assisted IDE) + Warp terminal
- Mac (Anaconda also installed -- always activate venv explicitly before working)
- OpenAI API key active
- HuggingFace token added to `.env`

---

## Important Notes
- Always activate venv before working: `source ~/integra/venv/bin/activate`
- Confirm venv is active by checking for `(venv)` in Warp prompt
- Never commit `.env` to GitHub
- Anaconda is installed on this machine -- without activating venv, Python defaults to Anaconda
- Always run scripts from `~/integra` using `-m` flag: `python -m src.rag.rag_pipeline`
- Never run scripts from inside subdirectories -- import paths will break
- Both Vercel and Railway auto-deploy on every push to `main`

---

## Session Log

### Session 1 -- Feb 25, 2026
- Decided on project concept: Integra
- Chose tech stack
- Created project folder structure
- Set up Python venv and installed all dependencies
- Resolved Anaconda conflict (venv was not activating correctly)
- Added OpenAI API key to `.env`

### Session 2 -- Feb 25, 2026
- Pulled 159 unique papers from Semantic Scholar API (10 queries, with rate limit handling)
- Pulled 200 papers from PubMed API (8 queries, clean run with no errors)
- Downloaded 4 therapy manual PDFs to `data/raw/`
- Built ChromaDB vector store: 4,450 vectors across all sources
- Confirmed retrieval working via `test_retrieval.py`
- Installed and ran RoBERTa emotion classifier
- Added HuggingFace token to `.env` for faster model downloads
- Fixed LangChain deprecation warnings (updated to `langchain_chroma` and `langchain_core` imports)

**Key decisions:**
- Semantic Scholar unauthenticated API is sufficient
- Emotion remapping layer needed: base RoBERTa emotions -> Integra-specific labels
- Chacruna scraping deferred -- corpus already rich enough for MVP

### Session 3 -- Feb 26, 2026
- Confirmed capstone demo requires two user entities
- Defined Alex (new user, empty state) and Jordan (established user, 6-week arc)
- Defined entry schema for Jordan's fake dataset
- Researched mental health chatbot best practices (JMIR Mental Health, PMC, medRxiv 2024/2025)
- Incorporated safety principles into design spec

**Key decisions:**
- Crisis detection runs before RAG pipeline -- bypasses LLM entirely for safety
- RAG grounding framed as a safety feature in the slide deck
- Jordan's emotional arc to be centerpiece of longitudinal demo

### Session 4 -- Feb 26, 2026
- Generated Jordan's full 11-entry fake dataset and saved to `data/demo/users.json`
- Built and tested emotion remapping layer
- Built and tested theme extraction pipeline
- Built and tested recommendation engine
- Built and tested RAG chatbot
- Wrote system prompt covering all safety checklist items
- Built and tested crisis detection
- Built and tested longitudinal tracker
- Fixed psychosis keyword case bug in crisis_detection.py

**Key decisions:**
- Recommendation engine as pure Python weighted mapping -- simpler, more interpretable
- Zero-shot classifier only runs on themes not caught by keyword layer
- EMOTION_COLORS dict in longitudinal_tracker.py as single source of truth

### Session 5 -- Feb 26, 2026
- Planned deployment and portfolio hosting strategy
- Selected HuggingFace Spaces as host
- Confirmed Framer portfolio site will link to live app via short redirect URL
- Decided to defer Inference API swap until after frontend is complete

### Session 6 -- Feb 26, 2026
- Built complete Streamlit frontend: main.py, 1_Journal.py, 2_Insights.py, 3_Companion.py, styles.py
- Implemented Grounded Depth visual aesthetic: dark palette (#1c1a18 bg, #c4956a accent), DM Serif Display + DM Sans typography
- Wired all ML pipelines into Journal entry submission
- Built browse / write / result mode system on Journal page
- Implemented longitudinal charts on Insights page using Altair
- Built Indy chatbot interface with entry context injection, multi-turn history, crisis detection
- Added mobile responsive CSS

### Session 7 -- Feb 26, 2026
- Restructured navigation: removed sidebar entirely
- Profile selection via dropdown; profile switching via st.popover pill
- Added guest mode for Companion
- Fixed write mode content bleed via st.stop() pattern

### Session 8 -- Feb 26, 2026
- Added animated logo loading screen
- Implemented optimistic chat UI with rotating waiting bubble phrases
- Replaced weekly averages chart with single-emotion filter system on Insights

### Session 9 -- Feb 27, 2026
- Swapped local HuggingFace model loading for Inference API in both NLP files
- Cleaned up requirements.txt (removed torch, transformers, etc.)
- Initialized git repo, pushed to GitHub
- Created and deployed HuggingFace Space (Docker/Streamlit)
- Resolved Git LFS requirement for large chroma files

### Session 10 -- March 2, 2026
- Migrated frontend from Streamlit to React (Vite) + FastAPI
- Built FastAPI backend (`backend/main.py`) wrapping all ML pipelines as HTTP endpoints
- Built full React frontend: Login, Home, Journal, Insights, Companion pages + BottomNav, EmotionPill components
- Fixed users.json field mapping (backend was looking for `display_name`, actual field is `name`)
- Fixed arc_summary bug (backend was returning full dict instead of `summary_text` string)
- Fixed logo rendering using `vite-plugin-svgr` with `?react` import syntax
- Added "Switch profile" button to Home header
- Deployed backend to Railway (Dockerfile, port 8000, hardcoded to avoid $PORT shell expansion issues)
- Deployed frontend to Vercel (auto-detects Vite, root directory `frontend/`)
- Fixed CORS to include Vercel production URL
- Fixed client-side routing on Vercel via `vercel.json` rewrites
- Fixed trailing slash in `VITE_API_URL` causing double-slash in API requests
- App confirmed live and functional at `https://integra-journal.vercel.app`

**Key decisions:**
- Streamlit replaced entirely -- React/FastAPI gives full control over UX, animations, mobile layout
- Railway chosen over HuggingFace Spaces for backend -- simpler Docker deployment, auto-deploy from GitHub
- Vercel chosen for frontend -- purpose-built for React/Vite, instant deploys
- Both services auto-deploy on every push to `main` -- no manual deploy step needed
- HuggingFace Space preserved but no longer updated

### Session 11 -- March 4, 2026
- Fixed page title: changed from "Vite App" to "Integra" in `frontend/index.html`
- Fixed favicon: removed duplicate vite.svg link, confirmed logo SVG favicon rendering in browser tab
- Added max-width container in `App.jsx`: 480px centered column with `#111010` gutter background, `position: relative` on inner div for BottomNav containment
- Fixed `BottomNav.jsx`: replaced `left: 0, right: 0` with `left: 50%` + `transform: translateX(-50%)` + `maxWidth: 480px` so nav bar stays within the content column on desktop
- Fixed `Home.jsx` writeCard overflow: removed `width: "100%"`, added `boxSizing: "border-box"` so margin-based inset works correctly

### Session 12 -- March 9, 2026
- Fixed recurring themes chart label bug in `Insights.jsx`: backend returns `theme_frequency` as an array of `[name, count]` pairs, not a dict -- `Object.entries()` on an array produces numeric keys, causing index numbers on the Y axis and concatenated label+count strings. Updated data mapping to handle the array shape directly.
- Fixed recurring themes chart axis bug: resolved by the same fix -- index numbers (0, 1, 2...) were a symptom of the same `Object.entries()` misuse.
- Wrote demo script (`integra_demo_script.md`): 7-part flow covering login, home, journal browse, live entry submission, insights, Indy chat, and Alex empty state. Includes exact text to type, timing targets per section, and a backup recovery table for common failure modes.
- Built slide deck in Canva: 13 slides covering context, problem, solution, ML pipeline, knowledge base, safety design, Jordan's arc, tech stack, limitations, and live demo transition.
- Wrote slide deck outline (`integra_slide_outline.md`) and style guide (`integra_style_guide.md`) as reference documents.

**Key decisions:**
- theme_frequency bug was a frontend data-shape mismatch, not a backend issue -- fix was one line change in Insights.jsx, no backend changes needed

### Session 13 -- March 11, 2026
- Completed evaluation metrics and model documentation for capstone submission.
- Tier 1 now fully complete.

### Session 14 -- March 11, 2026
- Completed all Tier 2 polish items:
  - Rotating Indy thinking phrases via `randomThinkingPhrase()` in `Companion.jsx`
  - 1500ms thinking delay before crisis response renders in `Companion.jsx`
  - Shortened 988 crisis response to 2 sentences in `crisis_detection.py`
  - 988 call button (`<a href="tel:988">`) renders below crisis message in `Companion.jsx`
  - "Reflect with Indy" primary CTA on entry results screen in `Journal.jsx`
  - Home empty state for new users: "Getting started" card with three numbered steps in `Home.jsx`
  - Journal empty state: styled card with "Write your first entry" CTA in `Journal.jsx`
  - Clear chat confirmation banner with Clear/Cancel buttons in `Companion.jsx`
  - Guest mode welcome note in Indy empty state in `Companion.jsx`
  - Pulsing skeleton blocks on Home while data fetches in `Home.jsx`
- Fixed `backend/main.py` bug: `ep.analyze()` returns a nested dict -- updated `create_entry` to extract `integra_emotions` key instead of storing the full result.
- Fixed `backend/main.py` bug: recommendation engine is a class -- updated `create_entry` to use `RecommendationEngine().recommend(themes)` instead of the nonexistent `recommend_practices()` function.
- Fixed guest user 404s: added `user.user_id === "guest"` guard in `Home.jsx` useEffect with immediate `setDataLoaded(true)` so skeleton blocks don't hang indefinitely for guest users.
- Fixed slide deck typo: "GOT-4o" corrected to "GPT-4o" on RAG slide in Canva.

**Key decisions:**
- Guest path on Home bypasses both fetch calls entirely and goes straight to loaded state -- no empty state shown for guests since they have no profile context to display
- Confirm dialog skipped for guest chat clear -- no history worth protecting, clears immediately

### Session 15 -- March 11, 2026
- Fixed week number on journal entries: computed `week_number` from entry date relative to user's first entry date instead of leaving it null. · *~30min*
- Added page transition animations: `pageFadeIn` keyframe (opacity 0->1, translateY 6px->0, 0.18s ease-out) added to `tokens.css`. `.page-transition` class applied via keyed wrapper div in `App.jsx`.
- Refactored `App.jsx` to extract `AppRoutes` inner component so `useLocation` can be called inside `BrowserRouter` -- required for the transition key pattern.

**Key decisions:**
- `useLocation` must live inside `BrowserRouter` -- extracting `AppRoutes` as a named inner component is the clean pattern for this, avoids wrapping the entire router
- Transition duration kept at 0.18s to feel snappy on mobile rather than sluggish

### Session 16 -- March 11, 2026
- Built quick check-in emotion pill flow (Tier 3).
- Added `BottomSheet.jsx` component (`frontend/src/components/`): reusable slide-up sheet with backdrop, scroll lock, drag handle, and `sheetSlideUp` keyframe animation.
- Updated `Home.jsx`: tapping a mood pill calls `handlePillTap(emotion)`, opens BottomSheet with the selected emotion displayed, two action buttons: "Chat with Indy" navigates to `/companion` with `checkinEmotion` in router state; "Just log it" calls `POST /checkin` and shows inline "Logging..." / "Logged" feedback before auto-closing.
- Updated `api.js`: added `postCheckin(userId, emotion)` calling `POST /checkin`.
- Updated `Companion.jsx`: reads `checkinEmotion` from `useLocation().state`; if present, injects Indy's opening message on mount ("You checked in as [emotion] -- want to tell me what's going on?"); tracks `userMessageCount` on every send; after 3 user messages shows a "Save as journal entry" banner above the input; banner has Dismiss and "Save as entry" buttons; saving posts transcript to `POST /entries` with `entry_type: "checkin"`.
- Updated `backend/main.py`: added `CheckinRequest` Pydantic model and `POST /checkin` endpoint; appends a minimal entry (entry_type "checkin", emotion score 1.0, empty text/themes/recs) to the user's entries in `users.json`; added `entry_type: str = "journal"` and `checkin_emotion: str | None = None` optional fields to existing `EntryRequest` model; `create_entry` passes `entry_type` through to the stored entry dict.

**Key decisions:**
- `BottomSheet.jsx` extracted as its own component -- reusable if needed elsewhere later
- Checkin opening message injected client-side on mount rather than via a backend call -- keeps the flow fast and avoids an extra round trip
- Save banner appears after 3 user messages and only once per session -- `saveBannerVisible` stays false until threshold is crossed, then dismissing hides it permanently for that session
- `entry_type: "checkin"` flag stored on the entry so Insights can distinguish check-ins from full journal entries in future filtering

### Session 17 -- March 11, 2026
- Fixed BottomSheet z-index: raised from 200 to 300 so sheet renders above the bottom nav bar.
- Fixed BottomSheet bottom padding: increased from 40px to 88px (64px nav height + 24px clearance) so buttons are not obscured by the nav bar.
- Fixed page transition animation: removed `translateY` from `pageFadeIn` keyframe in `tokens.css`. Transition is now a pure opacity fade (0.18s ease-out). The previous vertical movement read as layout reflow rather than intentional animation on mobile.

**Key decisions:**
- Pure fade chosen over slide variants -- no directional movement avoids the viewport-adjustment visual artifact on mobile
- `App.jsx` unchanged -- the fix was entirely in `tokens.css`


---

## How to Use This Brief
Paste the contents of this file at the start of any new Claude conversation to instantly restore full project context. Keep it updated as the project evolves.

---

*Last updated: March 11, 2026 -- Session 15 complete*