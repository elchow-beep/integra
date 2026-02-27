# Intégra — Project Brief
*AI-Powered Psychedelic Integration Companion*

---

## Overview
Intégra is a generative AI journaling app grounded in real psychedelic therapy frameworks (IFS, ACT, somatic work). Users write journal entries about their psychedelic experiences and integration process. The app analyzes emotional themes, tracks patterns over time, and recommends personalized practices — all powered by a RAG pipeline trained on integration literature.

---

## Capstone Requirements
- **Program:** AI/ML Tech Bootcamp
- **Due Date:** March 15, 2026
- **ML Areas to Showcase:** NLP / Text Analysis, Recommendation Systems, Deep Learning, Generative AI / LLMs

---

## Core Features
1. **Journal Entry Interface** — User writes about their experience/integration process
2. **Emotion & Theme Extraction** — NLP pipeline detects emotional themes (grief, awe, fear, gratitude, confusion, etc.)
3. **Longitudinal Tracking** — Visualizes emotional patterns across entries over time
4. **RAG Chatbot Companion** — Responds to journal entries using integration literature as knowledge base
5. **Recommendation Engine** — Suggests practices (breathwork, somatic exercises, IFS parts work, therapist resources) based on detected themes

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
| NLP / Embeddings | HuggingFace Transformers + Sentence Transformers |
| Emotion Classification | RoBERTa (`j-hartmann/emotion-english-distilroberta-base`) |
| Recommendation | Scikit-learn |
| Frontend | Streamlit |
| Data Storage | Local JSON / CSV (MVP) |

---

## Project Structure
```
integra/
├── data/
│   ├── raw/          # original source documents (MAPS, PubMed, Semantic Scholar)
│   └── processed/    # cleaned, chunked data for RAG
├── notebooks/        # exploratory analysis and prototyping
├── src/
│   ├── nlp/          # emotion & theme extraction pipeline
│   ├── rag/          # RAG pipeline + LLM chatbot
│   └── recommender/  # recommendation engine
├── app/              # Streamlit frontend
├── .env              # API keys (never commit)
├── requirements.txt
├── PROJECT_BRIEF.md
└── README.md
```

---

## Data Sources
- **MAPS Published Protocols** — MDMA therapy manual (V8.1) + Integration Workbook (PDFs)
- **Yale Psilocybin Manual** — Psilocybin-assisted therapy for depression (PDF)
- **Semantic Scholar API** — 159 academic papers on psychedelic-assisted therapy
- **PubMed Open Access** — 200 papers across 8 queries on psilocybin, MDMA, ketamine
- **Chacruna Institute** — Planned for future sessions

---

## ChromaDB Vector Store
- **Location:** `data/chroma`
- **Total vectors:** 4,450
- **Sources:** Semantic Scholar abstracts + PubMed abstracts + 4 therapy manual PDFs
- **Embedding model:** `text-embedding-3-small` (OpenAI)
- **Chunk size:** 500 tokens, 50 overlap
- **Retrieval confirmed working** via `src/rag/test_retrieval.py`

---

## 3-Week Roadmap

### Week 1 (Feb 25 – Mar 2) — Data & Foundation ✅
- [x] Confirm environment setup (Python 3.13.5, venv, all packages installed)
- [x] Add OpenAI API key to `.env` ($10 credit loaded)
- [x] Confirmed OpenAI GPT-4o connection working via `test_openai.py`
- [x] Pull 159 papers from Semantic Scholar API, chunk and load into ChromaDB
- [x] Pull 200 papers from PubMed API, chunk and load into ChromaDB
- [x] Download and load 4 therapy manual PDFs into ChromaDB
- [x] Vector store built: 4,450 vectors, retrieval confirmed working
- [x] Build baseline emotion classifier using RoBERTa

### Week 2 (Mar 3 – Mar 9) — Core ML Pipelines
- [ ] Build emotion remapping layer (base 7 emotions → Intégra-specific: grief, awe, confusion, gratitude, fear, joy, overwhelm)
- [ ] Build NLP theme extraction pipeline
- [ ] Build recommendation engine (themes → practices mapping)
- [ ] Build and test RAG chatbot with LangChain + OpenAI
- [ ] Connect longitudinal tracking logic across entries

### Week 3 (Mar 10 – Mar 15) — App, Polish & Presentation
- [ ] Build Streamlit frontend connecting all components
- [ ] End-to-end integration and testing
- [ ] Evaluation metrics and model documentation
- [ ] Slide deck and live demo preparation

---

## ML Architecture Summary

```
User Journal Entry
       │
       ▼
NLP Pipeline (HuggingFace RoBERTa)
  → Emotion Detection (7 base → Intégra remapped)
  → Theme Extraction
       │
       ├──► Recommendation Engine (Scikit-learn)
       │         → Suggests practices based on themes
       │
       ├──► Longitudinal Tracker
       │         → Stores + visualizes patterns over time
       │
       └──► RAG Chatbot (LangChain + ChromaDB + OpenAI)
                 → Responds using integration literature
                 → Grounded, therapeutic, non-clinical tone
```

---

## Session Log

### Session 1 — Feb 25, 2026 ✅
- Decided on project concept: Intégra
- Chose tech stack
- Created project folder structure
- Set up Python venv and installed all dependencies
- Resolved Anaconda conflict (venv was not activating correctly)
- Added OpenAI API key to `.env`
- Successfully tested GPT-4o connection — model responded in warm, integration-focused tone
- Created PROJECT_BRIEF.md
- Set up Claude Project for ongoing context

### Session 2 — Feb 25, 2026 ✅
- Pulled 159 unique papers from Semantic Scholar API (10 queries, with rate limit handling)
- Pulled 200 papers from PubMed API (8 queries, clean run with no errors)
- Downloaded 4 therapy manual PDFs to `data/raw/`:
  - MAPS MDMA-Assisted Psychotherapy Treatment Manual V8.1
  - MAPS MDMA-Assisted Psychotherapy Treatment Manual V8.1 (duplicate, harmless)
  - MAPS Psychedelic Integration Workbook
  - Yale Psilocybin Depression Therapy Manual (Oct 2019)
- Built ChromaDB vector store: 4,450 vectors across all sources
- Confirmed retrieval working via `test_retrieval.py`
- Installed and ran RoBERTa emotion classifier (`j-hartmann/emotion-english-distilroberta-base`)
- Classifier performing well — strong on joy, fear, sadness; some nuance needed for overwhelm/confusion (emotion remapping planned for Week 2)
- Added HuggingFace token to `.env` for faster model downloads
- Fixed LangChain deprecation warnings (updated to `langchain_chroma` and `langchain_core` imports)

**Key decisions:**
- Semantic Scholar unauthenticated API is sufficient (academic email required for key — skipped)
- Emotion remapping layer needed: base RoBERTa emotions → Intégra-specific labels
- Chacruna scraping deferred — corpus is already rich enough for MVP

**Next session:** Emotion remapping layer, NLP theme extraction, recommendation engine, RAG chatbot

---

## Learner Profile
- Still learning Python
- Familiar with HuggingFace and Scikit-learn
- Using Cursor (AI-assisted IDE) + Warp terminal
- Mac (Anaconda also installed — always activate venv explicitly before working)
- OpenAI API key active with $10 credit loaded
- HuggingFace token added to `.env`

---

## Important Notes
- Always activate venv before working: `source ~/integra/venv/bin/activate`
- Confirm venv is active by checking for `(venv)` in Warp prompt
- Never commit `.env` to GitHub
- Anaconda is installed on this machine — without activating venv, Python defaults to Anaconda
- Always run scripts from `~/integra` (not from inside subdirectories) to avoid path issues

---

## How to Use This Brief
Paste the contents of this file at the start of any new Claude conversation to instantly restore full project context. Keep it updated as the project evolves.

---

*Last updated: February 25, 2026 — Session 2 complete*