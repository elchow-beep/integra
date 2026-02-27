"""
app/pages/1_Journal.py
Journal entry browser and new entry submission for Integra.
No sidebar. Profile pill in header via st.popover.
Browse / write / result modes managed via session state.
"""

import json
import os
import sys
from datetime import datetime, date

import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.styles import (
    inject_css,
    section_label,
    emotion_badge_row,
    theme_badge_row,
    profile_pill_header,
    EMOTION_COLORS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Journal -- Integra",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ---------------------------------------------------------------------------
# Session state guard
# ---------------------------------------------------------------------------

if not st.session_state.get("user") or st.session_state["user"] == "guest":
    st.switch_page("main.py")

if "selected_entry_index" not in st.session_state:
    st.session_state["selected_entry_index"] = 0

if "journal_mode" not in st.session_state:
    st.session_state["journal_mode"] = "browse"

if "chat_entry_context" not in st.session_state:
    st.session_state["chat_entry_context"] = None

if "context_injected" not in st.session_state:
    st.session_state["context_injected"] = False

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo", "users.json")
)


@st.cache_data
def load_users():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_entry(user_name: str, new_entry: dict):
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    for user in data["users"]:
        if user["name"] == user_name:
            user["entries"].append(new_entry)
            break
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)
    st.cache_data.clear()


def get_pipelines():
    from app.main import load_emotion_pipeline, load_theme_extractor
    from src.recommender.recommendation_engine import RecommendationEngine
    return load_emotion_pipeline(), load_theme_extractor(), RecommendationEngine()


def render_emotion_bars(emotions: dict):
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    st.markdown(emotion_badge_row([e[0] for e in sorted_emotions]), unsafe_allow_html=True)
    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
    for emotion, score in sorted_emotions:
        color = EMOTION_COLORS.get(emotion, "#8a8480")
        st.markdown(
            f'<div style="margin:6px 0;">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
            f'<span style="font-size:12px;color:#8a8480;">{emotion}</span>'
            f'<span style="font-size:11px;color:#5a5652;">{score:.2f}</span>'
            f'</div>'
            f'<div style="background:#2e2b28;border-radius:4px;height:4px;">'
            f'<div style="background:{color};width:{int(score*100)}%;height:4px;border-radius:4px;"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def render_entry_footer(entry_text: str, show_back: bool = False, back_index: int = 0):
    """
    Renders the two-button footer row.
    Uses st.button type="primary" -- no wrapper divs, guaranteed equal height.
    """
    st.divider()

    if show_back:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Reflect with Indy", use_container_width=True,
                         type="primary", key="reflect_result"):
                st.session_state["chat_entry_context"] = entry_text
                st.session_state["context_injected"] = False
                st.switch_page("pages/3_Companion.py")
        with col_b:
            if st.button("Back to entries", use_container_width=True, key="back_entries"):
                st.session_state["journal_mode"] = "browse"
                st.session_state["selected_entry_index"] = back_index
                st.rerun()
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Reflect with Indy", use_container_width=True,
                         type="primary", key="reflect_browse"):
                st.session_state["chat_entry_context"] = entry_text
                st.session_state["context_injected"] = False
                st.switch_page("pages/3_Companion.py")
        with col_b:
            if st.button("View Insights", use_container_width=True, key="view_insights"):
                st.switch_page("pages/2_Insights.py")


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

data = load_users()
user_map = {u["name"]: u for u in data["users"]}
active_user = user_map[st.session_state["user"]]
entries = active_user["entries"]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

profile_pill_header("Journal")

st.markdown(
    '<p style="font-size:15px;font-weight:300;color:#8a8480;'
    'margin-top:4px;margin-bottom:16px;">'
    'Write about your experience. See what surfaces.</p>',
    unsafe_allow_html=True,
)

if st.button("Home", use_container_width=False):
    st.switch_page("main.py")

st.divider()

# ===========================================================================
# ALEX -- empty state
# ===========================================================================

if st.session_state["user"] == "Alex":

    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-radius:12px;'
        'padding:24px;margin-bottom:28px;">'
        '<p style="font-family:\'DM Serif Display\',Georgia,serif;font-size:20px;'
        'color:#e8e3db;margin-bottom:10px;">Welcome, Alex.</p>'
        '<p style="font-size:14px;font-weight:300;color:#8a8480;line-height:1.7;">'
        'This is your integration space. Write about your experience -- '
        'what came up, what stayed with you, what you\'re still sitting with.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    section_label("New Entry")
    entry_text = st.text_area(
        label="entry_input",
        label_visibility="collapsed",
        placeholder="Start writing here...",
        height=200,
    )

    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    submitted = st.button("Submit Entry", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if entry_text.strip():
            st.markdown(
                '<div style="background:#242220;border:1px solid #3a3733;'
                'border-left:3px solid #c4956a;border-radius:10px;'
                'padding:20px 24px;margin-top:20px;">'
                '<p style="font-family:\'DM Serif Display\',Georgia,serif;'
                'font-size:18px;color:#c4956a;margin-bottom:8px;">Entry received.</p>'
                '<p style="font-size:14px;font-weight:300;color:#8a8480;line-height:1.7;">'
                'In the full app, your emotions, themes, and practices would appear here. '
                'Head to the Companion page to reflect with Indy.</p>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Reflect with Indy", use_container_width=True):
                st.session_state["chat_entry_context"] = entry_text.strip()
                st.session_state["context_injected"] = False
                st.switch_page("pages/3_Companion.py")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<p style="font-size:13px;color:#5a5652;margin-top:8px;">'
                'Write something first.</p>',
                unsafe_allow_html=True,
            )

    st.stop()

# ===========================================================================
# JORDAN -- mode toggle header
# ===========================================================================

col_label, col_btn = st.columns([3, 1])

with col_label:
    if st.session_state["journal_mode"] == "browse":
        section_label(f"{len(entries)} Entries")
    else:
        section_label("New Entry")

with col_btn:
    if st.session_state["journal_mode"] == "browse":
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("+ New Entry", use_container_width=True):
            st.session_state["journal_mode"] = "write"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.button("Cancel", use_container_width=True):
            st.session_state["journal_mode"] = "browse"
            st.rerun()

st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

# Stop everything here if we are in write mode -- prevents any content
# below from rendering while the textarea is idle or processing.
if st.session_state["journal_mode"] == "write":

    new_text = st.text_area(
        label="new_entry_input",
        label_visibility="collapsed",
        placeholder="What are you sitting with today...",
        height=220,
    )

    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    submit_new = st.button("Submit Entry", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not submit_new:
        st.stop()

    if not new_text.strip():
        st.markdown(
            '<p style="font-size:13px;color:#5a5652;margin-top:8px;">'
            'Write something first.</p>',
            unsafe_allow_html=True,
        )
        st.stop()

    # Run pipeline
    with st.spinner("Analyzing your entry..."):
        try:
            emotion_pipeline, theme_extractor, rec_engine = get_pipelines()
            emotion_result = emotion_pipeline.analyze(new_text)
            integra_emotions = emotion_result.get("integra_emotions", {})
            themes = theme_extractor.extract(new_text)
            recommendations = rec_engine.recommend(themes)

            new_entry = {
                "entry_id": f"entry_{len(entries) + 1:03d}",
                "date": date.today().isoformat(),
                "text": new_text.strip(),
                "emotions": integra_emotions,
                "themes": themes,
                "recommendations": recommendations,
            }

            save_entry("Jordan", new_entry)
            st.session_state["new_entry_result"] = new_entry
            st.session_state["journal_mode"] = "result"
            st.rerun()

        except Exception as e:
            st.error(f"Pipeline error: {e}")

    st.stop()

# ===========================================================================
# RESULT MODE
# ===========================================================================

elif st.session_state["journal_mode"] == "result":

    result = st.session_state.get("new_entry_result", {})

    if not result:
        st.session_state["journal_mode"] = "browse"
        st.rerun()

    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;'
        'border-left:3px solid #c4956a;border-radius:10px;'
        'padding:16px 20px;margin-bottom:24px;">'
        '<p style="font-family:\'DM Serif Display\',Georgia,serif;'
        'font-size:18px;color:#c4956a;margin-bottom:4px;">Entry saved.</p>'
        f'<p style="font-size:13px;font-weight:300;color:#5a5652;">'
        f'{result.get("date", "")} -- {result.get("entry_id", "")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-size:15px;font-weight:300;color:#e8e3db;'
        f'line-height:1.8;margin-bottom:24px;">{result.get("text", "")}</p>',
        unsafe_allow_html=True,
    )

    st.divider()
    section_label("Detected Emotions")
    emotions = result.get("emotions", {})
    if emotions:
        render_emotion_bars(emotions)
    else:
        st.markdown('<p style="font-size:13px;color:#5a5652;">No emotions detected above threshold.</p>', unsafe_allow_html=True)

    st.divider()
    section_label("Themes")
    themes = result.get("themes", [])
    st.markdown(
        theme_badge_row(themes) if themes
        else '<p style="font-size:13px;color:#5a5652;">No themes detected.</p>',
        unsafe_allow_html=True,
    )

    st.divider()
    section_label("Recommended Practices")
    for rec in result.get("recommendations", []):
        st.markdown(
            f'<div style="display:flex;gap:10px;margin-bottom:10px;">'
            f'<span style="color:#c4956a;">--</span>'
            f'<span style="font-size:14px;font-weight:300;color:#e8e3db;line-height:1.55;">{rec}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Get the index the new entry will occupy after save
    fresh_data = load_users()
    fresh_entries = [u for u in fresh_data["users"] if u["name"] == "Jordan"][0]["entries"]
    new_entry_index = len(fresh_entries) - 1

    render_entry_footer(
        entry_text=result.get("text", ""),
        show_back=True,
        back_index=new_entry_index,
    )

# ===========================================================================
# BROWSE MODE
# ===========================================================================

else:

    total = len(entries)
    dropdown_options = [f"Entry {i+1} -- {e['date']}" for i, e in enumerate(entries)]

    col_prev, col_select, col_next = st.columns([1, 6, 1])

    with col_prev:
        if st.button("Prev", use_container_width=True):
            if st.session_state["selected_entry_index"] > 0:
                st.session_state["selected_entry_index"] -= 1
                st.session_state["chat_entry_context"] = None
                st.session_state["context_injected"] = False
                st.rerun()

    with col_select:
        selected_label = st.selectbox(
            label="entry_select",
            label_visibility="collapsed",
            options=dropdown_options,
            index=st.session_state["selected_entry_index"],
        )
        new_index = dropdown_options.index(selected_label)
        if new_index != st.session_state["selected_entry_index"]:
            st.session_state["selected_entry_index"] = new_index
            st.session_state["chat_entry_context"] = None
            st.session_state["context_injected"] = False
            st.rerun()

    with col_next:
        if st.button("Next", use_container_width=True):
            if st.session_state["selected_entry_index"] < total - 1:
                st.session_state["selected_entry_index"] += 1
                st.session_state["chat_entry_context"] = None
                st.session_state["context_injected"] = False
                st.rerun()

    st.markdown(
        f'<p style="font-size:12px;color:#5a5652;margin-top:4px;margin-bottom:24px;">'
        f'Entry {st.session_state["selected_entry_index"] + 1} of {total}</p>',
        unsafe_allow_html=True,
    )

    entry = entries[st.session_state["selected_entry_index"]]
    date_str = datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%B %-d, %Y")

    st.markdown(
        f'<p style="font-size:12px;color:#5a5652;margin-bottom:6px;">{date_str}</p>'
        f'<div style="width:32px;height:2px;background:#c4956a;border-radius:2px;margin-bottom:16px;"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-size:15px;font-weight:300;color:#e8e3db;line-height:1.8;margin-bottom:28px;">'
        f'{entry["text"]}</p>',
        unsafe_allow_html=True,
    )

    st.divider()
    section_label("Detected Emotions")
    emotions = entry.get("emotions", {})
    if emotions:
        render_emotion_bars(emotions)

    st.divider()
    section_label("Themes")
    st.markdown(theme_badge_row(entry.get("themes", [])), unsafe_allow_html=True)

    st.divider()
    section_label("Recommended Practices")
    for rec in entry.get("recommendations", []):
        st.markdown(
            f'<div style="display:flex;gap:10px;margin-bottom:10px;">'
            f'<span style="color:#c4956a;">--</span>'
            f'<span style="font-size:14px;font-weight:300;color:#e8e3db;line-height:1.55;">{rec}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    render_entry_footer(entry_text=entry["text"])