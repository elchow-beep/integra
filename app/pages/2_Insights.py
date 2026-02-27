"""
app/pages/2_Insights.py
Longitudinal emotion tracking and pattern visualization for Integra.
Emotion timeline filtered by clickable pill buttons.
Weekly averages removed.
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.styles import (
    inject_css,
    section_label,
    profile_pill_header,
    EMOTION_COLORS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Insights -- Integra",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ---------------------------------------------------------------------------
# Session state guard
# ---------------------------------------------------------------------------

if not st.session_state.get("user") or st.session_state["user"] == "guest":
    st.switch_page("main.py")

if "insights_selected_emotion" not in st.session_state:
    st.session_state["insights_selected_emotion"] = None

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo", "users.json")
)


@st.cache_data
def load_users():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


data = load_users()
user_map = {u["name"]: u for u in data["users"]}
active_user = user_map[st.session_state["user"]]
entries = active_user["entries"]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

profile_pill_header("Insights")

st.markdown(
    '<p style="font-size:16px;font-weight:300;color:#8a8480;'
    'margin-top:4px;margin-bottom:20px;">'
    'Emotional patterns across your integration journey.</p>',
    unsafe_allow_html=True,
)

col_home, col_journal = st.columns([1, 1])
with col_home:
    if st.button("Home", use_container_width=True):
        st.switch_page("main.py")
with col_journal:
    if st.button("Journal", use_container_width=True):
        st.switch_page("pages/1_Journal.py")

st.divider()

# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

if st.session_state["user"] == "Alex" or len(entries) == 0:
    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-radius:12px;'
        'padding:40px;margin-top:16px;">'
        '<p style="font-family:\'DM Serif Display\',Georgia,serif;font-size:24px;'
        'color:#5a5652;margin-bottom:12px;">No entries yet.</p>'
        '<p style="font-size:15px;font-weight:300;color:#5a5652;line-height:1.7;">'
        'Your emotional patterns will appear here once you\'ve written your first entry.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Compute analytics
# ---------------------------------------------------------------------------

@st.cache_data
def compute_analytics(entries_json: str):
    entries = json.loads(entries_json)

    # Emotion timeline
    timeline_rows = []
    for entry in entries:
        for emotion, score in entry["emotions"].items():
            timeline_rows.append({
                "date": entry["date"],
                "emotion": emotion,
                "score": round(score, 3),
            })
    timeline_df = pd.DataFrame(timeline_rows)
    timeline_df["date"] = pd.to_datetime(timeline_df["date"])

    # Dominant emotion per entry
    dominant_rows = []
    for entry in entries:
        if entry["emotions"]:
            dominant = max(entry["emotions"], key=entry["emotions"].get)
            dominant_rows.append({
                "date": entry["date"],
                "dominant_emotion": dominant,
                "score": entry["emotions"][dominant],
            })
    dominant_df = pd.DataFrame(dominant_rows)
    dominant_df["date"] = pd.to_datetime(dominant_df["date"])

    # Theme frequency
    theme_counts: dict = defaultdict(int)
    for entry in entries:
        for theme in entry.get("themes", []):
            theme_counts[theme] += 1
    theme_df = pd.DataFrame(
        [{"theme": t, "count": c} for t, c in theme_counts.items()]
    ).sort_values("count", ascending=False)

    # Recommendation frequency
    rec_counts: dict = defaultdict(int)
    for entry in entries:
        for rec in entry.get("recommendations", []):
            rec_counts[rec] += 1
    rec_df = pd.DataFrame(
        [{"practice": r, "count": c} for r, c in rec_counts.items()]
    ).sort_values("count", ascending=False)

    # Arc summary
    total = len(entries)
    phase_size = max(1, total // 3)

    def phase_dominant(phase_entries):
        counts: dict = defaultdict(float)
        for e in phase_entries:
            for em, sc in e["emotions"].items():
                counts[em] += sc
        return max(counts, key=counts.get) if counts else "unknown"

    arc_summary = (
        f"Jordan's arc spans {total} entries from {entries[0]['date']} to {entries[-1]['date']}. "
        f"Early entries are dominated by {phase_dominant(entries[:phase_size])}, "
        f"moving through {phase_dominant(entries[phase_size:phase_size*2])} in the middle weeks, "
        f"and resolving toward {phase_dominant(entries[phase_size*2:])} by the final entries."
    )

    # Emotions present in this user's data
    present_emotions = sorted(timeline_df["emotion"].unique().tolist())

    return timeline_df, dominant_df, theme_df, rec_df, arc_summary, present_emotions


timeline_df, dominant_df, theme_df, rec_df, arc_summary, present_emotions = compute_analytics(
    json.dumps(entries)
)

# ---------------------------------------------------------------------------
# Altair axis style
# ---------------------------------------------------------------------------

axis_style = dict(
    labelColor="#5a5652",
    tickColor="#3a3733",
    domainColor="#3a3733",
    gridColor="#2e2b28",
    labelFontSize=12,
)

# ---------------------------------------------------------------------------
# Arc summary
# ---------------------------------------------------------------------------

section_label("Integration Arc")
st.markdown(
    f'<div style="background:#242220;border:1px solid #3a3733;border-radius:10px;'
    f'padding:22px 26px;margin-bottom:32px;">'
    f'<p style="font-family:\'DM Serif Display\',Georgia,serif;font-style:italic;'
    f'font-size:17px;color:#8a8480;line-height:1.75;">{arc_summary}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Emotion Timeline with pill filter
# ---------------------------------------------------------------------------

section_label("Emotion Timeline")
st.markdown(
    '<p style="font-size:14px;font-weight:300;color:#5a5652;margin-bottom:16px;">'
    'Select an emotion to view its arc over time.</p>',
    unsafe_allow_html=True,
)

# Pill buttons -- one per emotion present in the data
# Selected emotion stored in session state; clicking same pill deselects
pill_cols = st.columns(len(present_emotions))

for i, emotion in enumerate(present_emotions):
    color = EMOTION_COLORS.get(emotion, "#8a8480")
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    is_selected = st.session_state["insights_selected_emotion"] == emotion

    with pill_cols[i]:
        # Active pill: solid colored background. Inactive: transparent with colored border.
        if is_selected:
            bg = f"rgba({r},{g},{b},0.25)"
            border = color
            text_color = color
        else:
            bg = f"rgba({r},{g},{b},0.08)"
            border = f"rgba({r},{g},{b},0.30)"
            text_color = f"rgba({r},{g},{b},0.70)"

        if st.button(
            emotion,
            key=f"pill_{emotion}",
            use_container_width=True,
        ):
            if st.session_state["insights_selected_emotion"] == emotion:
                st.session_state["insights_selected_emotion"] = None
            else:
                st.session_state["insights_selected_emotion"] = emotion
            st.rerun()

        # Overlay colored style on this specific button via targeted CSS
        st.markdown(
            f'<style>'
            f'div[data-testid="column"]:nth-child({i+1}) .stButton > button {{'
            f'    background-color: {bg} !important;'
            f'    border-color: {border} !important;'
            f'    color: {text_color} !important;'
            f'    font-size: 12px !important;'
            f'    padding: 6px 8px !important;'
            f'    border-radius: 20px !important;'
            f'}}'
            f'</style>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)

# Chart -- filtered or all
selected_emotion = st.session_state["insights_selected_emotion"]

if selected_emotion:
    chart_df = timeline_df[timeline_df["emotion"] == selected_emotion].copy()
    line_color = EMOTION_COLORS.get(selected_emotion, "#8a8480")

    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True, strokeWidth=2.5, color=line_color)
        .encode(
            x=alt.X(
                "date:T",
                title=None,
                axis=alt.Axis(format="%b %-d", **axis_style),
            ),
            y=alt.Y(
                "score:Q",
                title=None,
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(tickCount=5, **axis_style),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%B %-d, %Y"),
                alt.Tooltip("score:Q", title="Score", format=".2f"),
            ],
        )
        .properties(
            height=280,
            background="#1c1a18",
            padding={"left": 8, "right": 8, "top": 16, "bottom": 16},
            title=alt.TitleParams(
                text=selected_emotion,
                color=line_color,
                fontSize=14,
                fontWeight="normal",
                anchor="start",
            ),
        )
        .configure_view(strokeWidth=0)
        .configure_point(size=60, color=line_color)
    )
else:
    # No selection -- show a prompt to pick one
    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-radius:10px;'
        'padding:40px;text-align:center;">'
        '<p style="font-size:15px;font-weight:300;color:#5a5652;">'
        'Select an emotion above to view its arc.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    chart = None

if chart:
    st.altair_chart(chart, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Theme frequency
# ---------------------------------------------------------------------------

section_label("Top Themes")
st.markdown(
    '<p style="font-size:14px;font-weight:300;color:#5a5652;margin-bottom:16px;">'
    'Most frequently detected across all entries.</p>',
    unsafe_allow_html=True,
)

st.altair_chart(
    alt.Chart(theme_df.head(8))
    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#c4956a", opacity=0.75)
    .encode(
        x=alt.X("count:Q", title=None, axis=alt.Axis(tickMinStep=1, **axis_style)),
        y=alt.Y(
            "theme:N",
            title=None,
            sort="-x",
            axis=alt.Axis(
                labelColor="#8a8480",
                tickColor="#3a3733",
                domainColor="#3a3733",
                labelFontSize=13,
                labelLimit=240,
            ),
        ),
        tooltip=[
            alt.Tooltip("theme:N", title="Theme"),
            alt.Tooltip("count:Q", title="Entries"),
        ],
    )
    .properties(
        height=280,
        background="#1c1a18",
        padding={"left": 8, "right": 8, "top": 8, "bottom": 8},
    )
    .configure_view(strokeWidth=0),
    use_container_width=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Recommendation frequency
# ---------------------------------------------------------------------------

section_label("Top Recommended Practices")
st.markdown(
    '<p style="font-size:14px;font-weight:300;color:#5a5652;margin-bottom:16px;">'
    'Most frequently suggested across all entries.</p>',
    unsafe_allow_html=True,
)

st.altair_chart(
    alt.Chart(rec_df.head(8))
    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#7ba68f", opacity=0.75)
    .encode(
        x=alt.X("count:Q", title=None, axis=alt.Axis(tickMinStep=1, **axis_style)),
        y=alt.Y(
            "practice:N",
            title=None,
            sort="-x",
            axis=alt.Axis(
                labelColor="#8a8480",
                tickColor="#3a3733",
                domainColor="#3a3733",
                labelFontSize=13,
                labelLimit=240,
            ),
        ),
        tooltip=[
            alt.Tooltip("practice:N", title="Practice"),
            alt.Tooltip("count:Q", title="Entries"),
        ],
    )
    .properties(
        height=280,
        background="#1c1a18",
        padding={"left": 8, "right": 8, "top": 8, "bottom": 8},
    )
    .configure_view(strokeWidth=0),
    use_container_width=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Dominant emotion per entry
# ---------------------------------------------------------------------------

section_label("Dominant Emotion Per Entry")
st.markdown(
    '<p style="font-size:14px;font-weight:300;color:#5a5652;margin-bottom:16px;">'
    'Strongest emotion detected in each entry.</p>',
    unsafe_allow_html=True,
)

for _, row in dominant_df.iterrows():
    emotion = row["dominant_emotion"]
    color = EMOTION_COLORS.get(emotion, "#8a8480")
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:16px;'
        f'padding:11px 0;border-bottom:1px solid #2e2b28;flex-wrap:wrap;">'
        f'<span style="font-size:13px;color:#5a5652;min-width:130px;">'
        f'{row["date"].strftime("%B %-d, %Y")}</span>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'padding:5px 13px;border-radius:20px;background:rgba({r},{g},{b},0.12);'
        f'color:{color};font-size:13px;font-weight:500;">'
        f'<span style="width:6px;height:6px;border-radius:50%;background:{color};display:inline-block;"></span>'
        f'{emotion}</span>'
        f'<span style="font-size:13px;color:#5a5652;">{row["score"]:.2f}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )