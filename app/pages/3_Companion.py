"""
app/pages/3_Companion.py
Indy -- the Integra RAG chatbot companion.
No sidebar. Works for guest users and profile users.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.styles import (
    inject_css,
    disclaimer_chip,
    section_label,
    EMOTION_COLORS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Companion -- Integra",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state["user"] = "guest"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "chat_entry_context" not in st.session_state:
    st.session_state["chat_entry_context"] = None

if "context_injected" not in st.session_state:
    st.session_state["context_injected"] = False

if "pending_response" not in st.session_state:
    st.session_state["pending_response"] = False

if "pending_context" not in st.session_state:
    st.session_state["pending_context"] = None

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

@st.cache_resource
def load_pipeline():
    from src.rag.rag_pipeline import IntegraRAGPipeline
    return IntegraRAGPipeline()

pipeline_ready = False
pipeline_error = ""
try:
    pipeline = load_pipeline()
    pipeline_ready = True
except Exception as e:
    pipeline = None
    pipeline_error = str(e)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

user = st.session_state.get("user", "guest")
is_guest = user == "guest"

col_title, col_nav = st.columns([4, 1])

with col_title:
    st.markdown('<h1>Companion</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:16px;font-weight:300;color:#8a8480;margin-top:4px;">'
        'Reflect with Indy, your integration companion.</p>',
        unsafe_allow_html=True,
    )

with col_nav:
    st.markdown('<div style="margin-top:10px;">', unsafe_allow_html=True)
    if is_guest:
        if st.button("Home", use_container_width=True):
            st.switch_page("main.py")
    else:
        st.markdown(
            f'<div style="background:rgba(196,149,106,0.10);'
            f'border:1px solid rgba(196,149,106,0.25);border-radius:20px;'
            f'padding:6px 14px;text-align:center;">'
            f'<span style="font-family:DM Sans,sans-serif;font-size:13px;'
            f'font-weight:500;color:#c4956a;">{user}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
disclaimer_chip()

if not is_guest:
    st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
    col_home, col_journal, col_insights = st.columns(3)
    with col_home:
        if st.button("Home", use_container_width=True):
            st.switch_page("main.py")
    with col_journal:
        if st.button("Journal", use_container_width=True):
            st.switch_page("pages/1_Journal.py")
    with col_insights:
        if st.button("Insights", use_container_width=True):
            st.switch_page("pages/2_Insights.py")

st.divider()

# ---------------------------------------------------------------------------
# Pipeline error
# ---------------------------------------------------------------------------

if not pipeline_ready:
    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-radius:12px;'
        'padding:32px;">'
        '<p style="font-family:\'DM Serif Display\',Georgia,serif;font-size:20px;'
        'color:#a67b7b;margin-bottom:10px;">Companion unavailable</p>'
        '<p style="font-size:15px;font-weight:300;color:#8a8480;line-height:1.7;">'
        'The RAG pipeline could not be loaded. Check that your <code>.env</code> '
        'contains a valid <code>OPENAI_API_KEY</code> and that ChromaDB exists at '
        '<code>data/chroma</code>.</p>'
        f'<p style="font-size:12px;color:#5a5652;margin-top:12px;font-family:monospace;">'
        f'{pipeline_error}</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Entry context banner
# ---------------------------------------------------------------------------

entry_context = st.session_state.get("chat_entry_context")

if entry_context and not st.session_state["context_injected"] and not is_guest:
    preview = entry_context[:200].strip()
    if len(entry_context) > 200:
        preview += "..."
    st.markdown(
        f'<div style="background:#242220;border:1px solid #3a3733;'
        f'border-left:3px solid #c4956a;border-radius:8px;'
        f'padding:16px 22px;margin-bottom:24px;">'
        f'<p style="font-size:11px;font-weight:500;letter-spacing:0.10em;'
        f'text-transform:uppercase;color:#5a5652;margin-bottom:8px;">Entry Context</p>'
        f'<p style="font-size:14px;font-weight:300;color:#8a8480;line-height:1.7;'
        f'font-style:italic;">{preview}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

if not st.session_state["chat_history"]:
    if is_guest:
        opening = (
            "Hi, I'm Indy. I'm here to support reflection and integration. "
            "You can ask me about psychedelic integration, what to expect from the process, "
            "or anything you're sitting with."
        )
    elif entry_context and not st.session_state["context_injected"]:
        opening = "I have context from the entry you were just reading. What's coming up for you?"
    else:
        opening = "What's on your mind today? You can ask about anything from your integration process."

    st.markdown(
        f'<div style="margin-bottom:28px;">'
        f'<p style="font-size:11px;font-weight:500;letter-spacing:0.10em;'
        f'text-transform:uppercase;color:#c4956a;margin-bottom:10px;">'
        f'Indy -- your integration companion</p>'
        f'<div style="background:#242220;border:1px solid #3a3733;'
        f'border-radius:12px 12px 12px 4px;padding:16px 20px;">'
        f'<p style="font-size:15px;font-weight:300;color:#8a8480;line-height:1.75;margin:0;">'
        f'{opening}</p>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

else:
    for msg in st.session_state["chat_history"]:
        role = msg["role"]
        content = msg["content"]
        is_crisis = msg.get("is_crisis", False)

        if role == "user":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin-bottom:14px;">'
                f'<div style="background:#2e2b28;border:1px solid #3a3733;'
                f'border-radius:12px 12px 4px 12px;padding:14px 18px;max-width:85%;">'
                f'<p style="font-size:15px;font-weight:300;color:#e8e3db;line-height:1.7;margin:0;">'
                f'{content}</p></div></div>',
                unsafe_allow_html=True,
            )
        else:
            border = "#a67b7b" if is_crisis else "#3a3733"
            st.markdown(
                f'<div style="margin-bottom:18px;">'
                f'<p style="font-size:11px;font-weight:500;letter-spacing:0.10em;'
                f'text-transform:uppercase;color:#c4956a;margin-bottom:8px;">'
                f'Indy -- your integration companion</p>'
                f'<div style="background:#242220;border:1px solid {border};'
                f'border-radius:12px 12px 12px 4px;padding:16px 20px;">'
                f'<p style="font-size:15px;font-weight:300;color:#8a8480;line-height:1.75;margin:0;">'
                f'{content}</p></div></div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Waiting bubble -- renders while pipeline runs on pending_response pass
# ---------------------------------------------------------------------------

WAITING_PHRASES = [
    "Sitting with what you've shared...",
    "Holding this with you...",
    "Letting that settle...",
    "Finding what might help...",
    "Sitting in this with you...",
    "Taking that in...",
]

if st.session_state["pending_response"]:
    import random
    phrase = random.choice(WAITING_PHRASES)
    waiting_slot = st.empty()
    waiting_slot.markdown(
        f'<div style="margin-bottom:18px;">'
        f'<p style="font-size:11px;font-weight:500;letter-spacing:0.10em;'
        f'text-transform:uppercase;color:#3a3733;margin-bottom:8px;">'
        f'Indy</p>'
        f'<div style="background:transparent;border:1px dashed #3a3733;'
        f'border-radius:12px 12px 12px 4px;padding:16px 20px;">'
        f'<p style="font-size:14px;font-weight:300;color:#3a3733;'
        f'line-height:1.75;font-style:italic;margin:0;letter-spacing:0.01em;">{phrase}</p>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Retrieve the last user message and run the pipeline
    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state["chat_history"])
         if m["role"] == "user"),
        "",
    )
    context_to_pass = st.session_state["pending_context"]

    try:
        result = pipeline.chat(
            user_message=last_user_msg,
            entry_context=context_to_pass,
        )
        response_text = result["response"]
        is_crisis = result["is_crisis"]
    except Exception as e:
        response_text = (
            "I'm having trouble connecting right now. "
            "Please check your API configuration and try again."
        )
        is_crisis = False

    waiting_slot.empty()
    st.session_state["chat_history"].append({
        "role": "assistant",
        "content": response_text,
        "is_crisis": is_crisis,
    })
    st.session_state["pending_response"] = False
    st.session_state["pending_context"] = None
    st.rerun()

# ---------------------------------------------------------------------------
# Clear conversation
# ---------------------------------------------------------------------------

if st.session_state["chat_history"]:
    if st.button("Clear conversation", use_container_width=False):
        st.session_state["chat_history"] = []
        st.session_state["context_injected"] = False
        st.session_state["pending_response"] = False
        st.session_state["pending_context"] = None
        pipeline.reset()
        st.rerun()

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

user_input = st.chat_input("Write to Indy...")

if user_input:
    context_to_pass = None
    if entry_context and not st.session_state["context_injected"] and not is_guest:
        context_to_pass = entry_context
        st.session_state["context_injected"] = True

    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    st.session_state["pending_response"] = True
    st.session_state["pending_context"] = context_to_pass
    st.rerun()  # immediately rerun to show user bubble, then pipeline runs above