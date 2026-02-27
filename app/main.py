"""
app/main.py
Integra landing page.
Shows an animated logo loading screen while models warm up,
then reveals the profile selection UI.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.styles import inject_css, disclaimer_chip

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Integra",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

defaults = {
    "user": None,
    "selected_entry_index": 0,
    "chat_history": [],
    "chat_entry_context": None,
    "context_injected": False,
    "journal_mode": "browse",
    "models_loaded": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------------------------
# SVG logo -- inline, no file dependency at runtime
# ---------------------------------------------------------------------------

LOGO_SVG = """<svg id="Layer_2" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 129.39 127.65"><defs><style>.cls-1{fill:url(#linear-gradient);stroke-width:0px;}</style><linearGradient id="linear-gradient" x1="0" y1="63.82" x2="129.39" y2="63.82" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#7b9ea6"/><stop offset=".22" stop-color="#a6c47b"/><stop offset=".59" stop-color="#c4956a"/><stop offset="1" stop-color="#9b7fa6"/></linearGradient></defs><g id="Layer_1-2"><path class="cls-1" d="M97.66,105.03c8.48-5.93,14.71-13.66,18.6-23.27,2.67-6.6,3.81-13.47,3.72-20.57,1.25-.27,1.69-1.4,2-2.34,1.03-3.05,3.17-5.48,4.46-8.38.29-.66.77-1.17,1.57-1.21.15,2.28,1.08,4.41,1.23,6.71.26,3.75.11,7.47.02,11.21-.14,6-1.44,11.63-3.59,17.11-4.36,11.11-11.25,20.26-21.32,26.86-3.04,1.99-6.36,3.47-9.65,5.01-.96-.65-.22-1.38-.06-2.03.79-3.11,2.68-5.85,3.01-9.11ZM58.71,81.37c-2.09,3.44-2.85,7.27-3.7,11.09-.31,1.42-.71,2.83-1.16,4.21-.33,1.02-1,1.77-2.21,1.74-.3,5.82-1.45,11.53-2.15,17.29-.33,2.69-.84,5.45.5,8.07,1.5-.43,1.49-2.07,2.35-3.05,2.78-3.21,5.49-6.54,6.18-11,.18-1.2.91-2.25,1.88-3.05,3.99-3.25,6.44-7.52,8.14-12.28,1.26-3.55,3.37-6.71,4.61-10.28.51-1.46.95-2.94,1.03-4.44.08-1.57.65-2.68,1.92-3.52,1.04-.68,1.48-1.56.8-2.75-1.29.85-2.58,1.69-3.87,2.54-.19,1.92-.35,1.99-1.91.87-2.99,1.03-6.09.84-9.17.89-.77,1.48-2.35,2.22-3.22,3.66ZM6.96,81.24c.7-2.97,1.25-5.93,3.54-8.17-.27-2.4-.61-4.8-.8-7.2-.56-7.28.63-14.33,3.01-21.2-.12-.04-.32-.06-.35-.13-1.42-4.29-3.2-8.53-2-13.23.22-.87.83-1.8.12-2.74-1.93,2.33-3.26,5.03-4.58,7.71C.97,46.32-.71,57.03.26,68.12c.6,6.84,2.4,13.42,5.61,19.55,1.42-1.95.58-4.29,1.08-6.43ZM105.71,58.88c-.89,1.18-1.89,2.18-3.48,2.3,0,2.62.31,5.25-.16,7.85-1.56,8.43-6.09,14.91-13.15,19.66-1.57,1.05-3.06,2.1-3.68,3.99-.75,2.29.22,4.06,2.54,4.72,1.84.51,3.4-.22,4.91-1.09,4.99-2.84,8.89-6.87,12.12-11.54,6.73-9.75,7.91-20.38,4.74-31.64-1.78,1.59-2.44,3.92-3.84,5.76ZM28.22,72.55c-.95-4.67-1.33-9.33-.23-14.05,1.22-5.23,3.97-9.64,7.19-13.81-3-.56-4.74-4.5-2.91-6.91.98-1.29,1.09-2.46.5-3.83-2.42,1.82-4.44,4.05-6.28,6.41-6.71,8.62-9.11,18.46-7.8,29.2.6,4.92,2.24,9.54,5.17,13.63,1.98-3.33,2.42-7.29,4.37-10.64ZM52.72,126.84c2.42-2.92,4.78-5.85,5.82-9.63.3-1.11,1.04-2.14,2.23-2.66.28-1.21.46-2.46.85-3.63.91-2.75,1.7-3.32,4.13-3.2.02-.47.25-.83.55-1.19,2.62-3.03,4.26-6.62,5.76-10.28,1.76-4.29,4.02-8.35,5.53-12.78.82-2.41,2.65-4.46,3.9-6.73,3.18-5.79,6.8-11.35,9.53-17.39.37-.81.59-1.69.49-2.61-3.21-.27-5.77,1.32-7.1,4.89-1.68,4.49-3.95,8.53-7.51,11.79.69,1.19.24,2.07-.8,2.75-1.27.84-1.84,1.95-1.92,3.52-.08,1.5-.52,2.98-1.03,4.44-1.24,3.57-3.34,6.73-4.61,10.28-1.7,4.76-4.15,9.03-8.14,12.28-.97.79-1.7,1.85-1.88,3.05-.69,4.45-3.4,7.78-6.18,11-.85.98-.84,2.62-2.35,3.05.45,1.43,1.21,2.58,2.72,3.07ZM68.86,113.78c2.07-.75,3-2.65,4.2-4.25,1.23-1.63,2.09-3.47,2.8-5.39.33-.89.47-2.07,1.78-2.26.06-1.27.19-2.55.17-3.82-.17-8.37,2.46-15.55,8.84-21.2,1.62-1.44,3.16-2.99,4.63-4.59,2.21-2.42,4.16-5.04,4.84-8.35.85-4.13-.41-6.06-4.6-7.17.11.92-.12,1.79-.49,2.61-2.73,6.04-6.34,11.6-9.53,17.39-1.25,2.28-3.08,4.33-3.9,6.73-1.51,4.43-3.77,8.49-5.53,12.78-1.5,3.66-3.14,7.25-5.76,10.28-.3.35-.53.71-.55,1.19,2.04,1.5,2.33,3.91,3.11,6.06ZM56.53,28.73c-.18.87-.43,1.72-.31,2.62,5.19-.87,10.38-1.19,15.59-.15,3.53.7,6.8,2.13,10.08,3.53.63-3.11,2.29-5.64,4.48-7.86-4.1-2.22-8.35-3.91-12.98-4.82-5.24-1.02-10.43-1.29-15.68-.38.23,2.46-.71,4.73-1.18,7.07ZM25.17,25.51c-1.86-1.81-1.99-4.26-2.37-6.59-.21-1.3-.08-2.66-.1-3.99-4.89,3.81-8.93,8.38-12.21,13.63.71.94.1,1.87-.12,2.74-1.2,4.71.59,8.94,2,13.23.02.07.23.09.35.13,2.93-7.18,7.05-13.58,12.45-19.15ZM68.97,122.53c-.21,1.23.37,2.27,1.28,3.04,1.89,1.6,4.09,2.09,6.45,1.4,2.2-.64,3.26-2.35,3.65-4.5.18-1,.36-2.03.29-3.03-.31-4.4-1.38-8.68-2.25-12.98-.31-1.53-.11-8.9-.56-10.7-1.3.19-1.64,7.49-1.97,8.38-.71,1.93-1.57,3.77-2.8,5.39-1.2,1.59-2.13,3.5-4.2,4.25.39,2.91.63,5.82.11,8.75ZM59.05,76.93c-3.64-1.29-6.4-3.8-8.96-6.56-2.54,1.74-4.16,4.14-5.03,7.06-.11.36-.03.76-.39,1.02,3.1,3.4,5.59,7.13,6.32,11.8.42,2.71.62,5.43.66,8.17,1.21.03,1.88-.71,2.21-1.74.45-1.38.84-2.79,1.16-4.21.85-3.83,1.61-7.66,3.7-11.09.88-1.44,2.46-2.17,3.22-3.66-.96-.26-1.95-.46-2.88-.79ZM69.44,8.14c-.08.49-.14.99-.21,1.49,6.5.73,12.76,2.34,18.77,4.92.08-.86.52-1.54,1.05-2.21,1.44-1.81,2.63-3.75,2.86-6.13-6.43-3.21-13.22-5.09-20.38-5.68-.72,2.53-1.68,4.99-2.09,7.61ZM65.72,56.47c-2.71,4.2-5.26,8.5-6.89,13.26,4.82,4.47,12.83,2.37,14.76-3.88.65-2.11.88-4.29.53-6.44-.46-2.82-.95-5.74-4.06-7.1-1.87.95-3.25,2.45-4.35,4.16ZM39.69,15.14c-.66-2.82-.3-5.68-.3-8.53,0-1.17,1.69-1.32,1.81-2.52-6.85,2.43-13.05,5.99-18.49,10.84.02,1.33-.11,2.69.1,3.99.38,2.32.5,4.78,2.37,6.59,4.39-4.09,9.22-7.56,14.52-10.37ZM103.06,24.69c2.17-.59,2.83-2.59,3.83-4.22.65-1.06,1.02-2.28,1.51-3.44-4.92-4.49-10.33-8.21-16.49-10.82-.23,2.38-1.42,4.33-2.86,6.13-.53.67-.97,1.34-1.05,2.21,5.42,2.78,10.49,6.09,15.06,10.14ZM94.78,45.12c2.98-1.82,4.17-4.82,5.22-7.91-3.82-4.4-8.4-7.8-13.63-10.34-2.19,2.22-3.85,4.75-4.48,7.86,4.68,2.98,9.11,6.28,12.89,10.39ZM54.25,10.37c.14-2.39,1.22-4.6,1.35-7.01.05-.93.15-1.88.19-2.82-5.04.46-9.9,1.67-14.59,3.56-.12,1.2-1.81,1.35-1.81,2.52,0,2.84-.37,5.71.3,8.53,4.7-2.07,9.52-3.75,14.57-4.76ZM122.71,35.4c-1.32.32-1.36,1.54-1.73,2.51-1.01,2.59-1.61,5.41-4.13,7.13,1.82,5.23,2.9,10.6,3.13,16.14,1.25-.27,1.69-1.4,2-2.34,1.03-3.05,3.17-5.48,4.46-8.38.29-.66.77-1.17,1.57-1.21-1-4.92-2.62-9.59-5.3-13.86ZM40.87,39.47c1.56-1.46,4.74-3.48,7.09-4.61-.42-.2-2.9.12-2.87-.36.11-1.76-.5-3.32-1.14-4.91-.61-1.52,1.1-2.47,1.06-3.87-4.59,1.99-8.6,4.83-12.24,8.22.59,1.38.48,2.54-.5,3.83-1.83,2.41-.09,6.35,2.91,6.91,1.46-2.22,3.81-3.46,5.69-5.22ZM69.23,9.63c.07-.5.13-.99.21-1.49.42-2.61,1.37-5.08,2.09-7.61-5.25-.74-10.49-.7-15.74,0-.05.94-.14,1.89-.19,2.82-.13,2.42-1.2,4.62-1.35,7.01,4.96-.8,9.95-1.07,14.97-.74ZM58.65,52.75c-4.14,3.82-4.04,14.16.18,16.99,1.63-4.77,4.18-9.06,6.89-13.26,1.1-1.71,2.48-3.21,4.35-4.16-3.33-3.02-8.57-2.2-11.42.43ZM31.77,107.98c.4-.7,1.13-1.27.99-2.21-3.76-2.9-7.46-5.88-10.68-9.4-2.34,3.16-2.47,6.82-2.39,10.53,2.96,2.85,6.23,5.27,9.91,7.13.26-2.18,1.09-4.15,2.17-6.05ZM56.22,31.35c-.11-.9.14-1.74.31-2.62.47-2.34,1.42-4.61,1.18-7.07-4.49.55-8.73,1.87-12.7,4.06.04,1.4-1.67,2.36-1.06,3.87.64,1.58,1.25,3.15,1.14,4.91-.03.48-3.77,2.94-3.35,3.14,3.52-1.21,10.85-5.36,14.48-6.3ZM11.45,97.33c1.33-.32,1.3-1.44,1.31-2.42.05-3.16.66-6.14,2.36-8.85-1.91-4.2-3.4-8.55-4.62-13-2.29,2.25-2.84,5.2-3.54,8.17-.5,2.13.34,4.48-1.08,6.43,1.59,3.38,3.31,6.67,5.57,9.66ZM46.87,64.32c-.69-1.63-1.14-3.4-2.43-4.73-.19-.13-.8-.66-.99-.79-.06-.06-.74-.3-.79-.24-1.22.04-.52,1.67-.81,2.53-1.15,3.47-2.59,6.82-4.13,10.13,1.97,2.74,4.47,4.97,6.95,7.22.36-.26.28-.66.39-1.02.87-2.92,2.49-5.32,5.03-7.06-1.34-1.87-2.32-3.93-3.22-6.04ZM32.7,93.2c.99-2.72.73-6.01,3.6-7.87-3.48-3.76-6.24-7.98-8.08-12.77-1.94,3.35-2.39,7.31-4.37,10.64,2.3,3.91,5.14,7.34,8.84,10.01ZM39.24,118.09c3.22.67,5.38-1.89,4.33-4.99-.4-1.19-1.07-2.24-2.17-2.83-2.85-1.55-5.76-3.01-8.65-4.5.14.94-.59,1.51-.99,2.21-1.08,1.89-1.9,3.87-2.17,6.05,2.97,1.94,6.18,3.35,9.65,4.07ZM111.3,34.35c2.65-1.25,3.31-3.82,3.95-6.29.24-.92.44-1.83.87-2.67-2.13-3.2-4.88-5.82-7.72-8.36-.49,1.15-.86,2.38-1.51,3.44-1,1.63-1.66,3.63-3.83,4.22,2.95,3.04,5.82,6.16,8.24,9.66ZM116.85,45.05c2.52-1.72,3.12-4.54,4.13-7.13.38-.97.41-2.19,1.73-2.51-.07-1-.68-1.75-1.15-2.56-1.55-2.67-3.39-5.14-5.44-7.45-.43.85-.64,1.75-.87,2.67-.64,2.47-1.3,5.04-3.95,6.29,2.1,3.43,4.01,6.97,5.56,10.69ZM19.69,106.9c-.08-3.71.05-7.37,2.39-10.53-2.59-3.25-4.83-6.74-6.95-10.3-1.7,2.71-2.31,5.69-2.36,8.85-.02.97.02,2.1-1.31,2.42,2.17,3.69,5.01,6.8,8.23,9.57ZM38.85,97.29c1.62.62,3.06.29,4.2-.95,1.1-1.2,1.1-2.66.58-4.14-.38-1.06-1.13-1.84-1.99-2.53-1.78-1.45-3.56-2.9-5.35-4.35-2.87,1.86-2.61,5.15-3.6,7.87,1.72,1.86,3.8,3.19,6.15,4.09ZM106.19,45.4c-.97.08-1.04.98-1.44,1.58-1.43,2.15-3.23,3.8-5.9,4.22,1.61,3.16,2.71,6.5,3.39,9.98,1.59-.12,2.58-1.12,3.48-2.3,1.4-1.85,2.06-4.17,3.84-5.76-.6-2.8-1.86-5.31-3.36-7.72ZM37.78,56.89c-2.47.49-4.1,2.13-4.28,4.48-.31,4,1.62,7.08,4.22,9.86,1.54-3.31,2.98-6.66,4.13-10.13.29-.86.62-1.86,1.84-1.9-1.02-1.89-3.36-2.8-5.92-2.3ZM100,37.21c-1.05,3.09-2.25,6.09-5.22,7.91,1.36,2.03,2.71,4.05,4.07,6.08,2.67-.42,4.47-2.07,5.9-4.22.4-.6.46-1.5,1.44-1.58-1.55-3.11-3.64-5.82-6.18-8.19ZM89.66,109.07c-1.19.52-2.17,1.34-2.88,2.44-.86,1.34-.99,2.77-.22,4.17.73,1.34,1.94,1.95,3.48,1.95,1.72,0,3.21-.66,4.67-1.46-.96-.65-.22-1.38-.06-2.03.79-3.11,2.68-5.85,3.01-9.11-2.6,1.49-5.25,2.85-8,4.04ZM58.66,126.62c1.93-1.25,2.56-3.18,2.24-5.33-.34-2.26-.84-4.47-.13-6.74-1.18.52-1.92,1.55-2.23,2.66-1.04,3.78-3.4,6.72-5.82,9.63,2.03,1.19,4.03,1.02,5.94-.22ZM71.11,76.82c1.57,1.12,1.73,1.04,1.91-.87-.65.27-1.38.35-1.91.87ZM43.87,59.19c.19.14.38.27.57.41-.19-.14-.38-.27-.57-.41Z"/></g></svg>"""

# ---------------------------------------------------------------------------
# Model loaders
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def load_emotion_pipeline():
    from src.nlp.emotion_pipeline import EmotionPipeline
    return EmotionPipeline()

@st.cache_resource(show_spinner=False)
def load_theme_extractor():
    from src.nlp.theme_extractor import ThemeExtractor
    return ThemeExtractor()

@st.cache_resource(show_spinner=False)
def load_rag_pipeline():
    from src.rag.rag_pipeline import IntegraRAGPipeline
    return IntegraRAGPipeline()

# ---------------------------------------------------------------------------
# Loading screen -- shown only on first run while models warm up
# ---------------------------------------------------------------------------

if not st.session_state["models_loaded"]:

    loading_placeholder = st.empty()

    loading_placeholder.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400&display=swap');

        @keyframes logoPulse {{
            0%   {{ opacity: 0.5; transform: scale(0.97); }}
            50%  {{ opacity: 1;   transform: scale(1.03); }}
            100% {{ opacity: 0.5; transform: scale(0.97); }}
        }}

        @keyframes wordmarkFade {{
            0%   {{ opacity: 0; transform: translateY(6px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes subtitleFade {{
            0%   {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}

        .integra-loader {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            gap: 0;
        }}

        .integra-loader-logo {{
            width: 80px;
            height: 80px;
            animation: logoPulse 2s ease-in-out infinite;
        }}

        .integra-loader-name {{
            font-family: 'DM Serif Display', Georgia, serif;
            font-size: 36px;
            color: #e8e3db;
            letter-spacing: -0.01em;
            margin-top: 20px;
            animation: wordmarkFade 0.8s ease 0.3s both;
        }}

        .integra-loader-sub {{
            font-family: 'DM Sans', sans-serif;
            font-size: 13px;
            font-weight: 300;
            color: #5a5652;
            margin-top: 8px;
            letter-spacing: 0.04em;
            animation: subtitleFade 0.8s ease 0.8s both;
        }}
        </style>

        <div class="integra-loader">
            <div class="integra-loader-logo">{LOGO_SVG}</div>
            <div class="integra-loader-name">Integra</div>
            <div class="integra-loader-sub">Loading models...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    load_emotion_pipeline()
    load_theme_extractor()
    load_rag_pipeline()

    st.session_state["models_loaded"] = True
    loading_placeholder.empty()
    st.rerun()

# ---------------------------------------------------------------------------
# Landing page content -- only shown after models are loaded
# ---------------------------------------------------------------------------

st.markdown('<h1>Integra</h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="font-size:16px;font-weight:300;color:#8a8480;'
    'margin-top:6px;margin-bottom:40px;">'
    'An AI-powered companion for psychedelic integration.</p>',
    unsafe_allow_html=True,
)

st.divider()

st.markdown(
    '<p style="font-size:15px;font-weight:300;color:#8a8480;line-height:1.8;">'
    'Integra is a journaling space grounded in real integration frameworks -- '
    'IFS, ACT, and somatic work. Write about your experience and Integra surfaces '
    'emotional patterns, suggests practices, and offers reflection through Indy, '
    'an AI companion grounded in published integration literature.</p>',
    unsafe_allow_html=True,
)

st.markdown('<div style="margin-bottom:36px;"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Profile selection
# ---------------------------------------------------------------------------

st.markdown(
    '<p style="font-family:\'DM Serif Display\',Georgia,serif;'
    'font-size:20px;color:#e8e3db;margin-bottom:16px;">Choose how to continue</p>',
    unsafe_allow_html=True,
)

profile_options = ["Select a profile...", "Alex", "Jordan"]
selected = st.selectbox(
    label="profile_select",
    options=profile_options,
    index=0,
    label_visibility="collapsed",
)

if selected == "Alex":
    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-left:3px solid #5a5652;'
        'border-radius:8px;padding:16px 20px;margin-top:12px;">'
        '<p style="font-size:14px;font-weight:300;color:#8a8480;line-height:1.7;margin:0;">'
        'New user. No entries yet. Demonstrates the onboarding experience and empty states.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
elif selected == "Jordan":
    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-left:3px solid #c4956a;'
        'border-radius:8px;padding:16px 20px;margin-top:12px;">'
        '<p style="font-size:14px;font-weight:300;color:#8a8480;line-height:1.7;margin:0;">'
        'Established user. 11 entries across 6 weeks. Full emotional arc from '
        'awe and overwhelm through grief toward gratitude.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)

if selected in ("Alex", "Jordan"):
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("Continue to Journal", use_container_width=True):
        if st.session_state["user"] != selected:
            st.session_state["selected_entry_index"] = 0
            st.session_state["chat_history"] = []
            st.session_state["chat_entry_context"] = None
            st.session_state["context_injected"] = False
            st.session_state["journal_mode"] = "browse"
        st.session_state["user"] = selected
        st.switch_page("pages/1_Journal.py")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div style="background:#242220;border:1px solid #3a3733;border-radius:8px;'
        'padding:10px 18px;text-align:center;">'
        '<span style="font-size:13px;color:#5a5652;">Select a profile to continue</span>'
        '</div>',
        unsafe_allow_html=True,
    )

st.divider()

st.markdown(
    '<p style="font-size:13px;font-weight:300;color:#5a5652;margin-bottom:12px;">'
    'Just want to talk? You can chat with Indy without a profile.</p>',
    unsafe_allow_html=True,
)

if st.button("Chat with Indy as a guest", use_container_width=True):
    st.session_state["user"] = "guest"
    st.session_state["chat_history"] = []
    st.session_state["chat_entry_context"] = None
    st.session_state["context_injected"] = False
    st.switch_page("pages/3_Companion.py")

st.markdown('<div style="margin-top:32px;"></div>', unsafe_allow_html=True)
disclaimer_chip()
st.markdown(
    '<p style="font-size:11px;color:#5a5652;margin-top:12px;line-height:1.6;text-align:center;">'
    'Integra is a journaling and reflection tool, not a substitute '
    'for professional mental health support.</p>',
    unsafe_allow_html=True,
)