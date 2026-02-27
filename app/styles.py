"""
app/styles.py
Shared styles, color tokens, and component helpers for the Integra Streamlit app.
"""

import streamlit as st


COLORS = {
    "bg":             "#1c1a18",
    "surface":        "#242220",
    "surface_raised": "#2e2b28",
    "border":         "#3a3733",
    "text_primary":   "#e8e3db",
    "text_secondary": "#8a8480",
    "text_muted":     "#5a5652",
    "accent":         "#c4956a",
    "accent_soft":    "rgba(196, 149, 106, 0.10)",
}

EMOTION_COLORS = {
    "awe":        "#7b9ea6",
    "overwhelm":  "#9b7fa6",
    "fear":       "#a67b7b",
    "grief":      "#7a8fa6",
    "confusion":  "#a69b7b",
    "joy":        "#a6c47b",
    "gratitude":  "#c4956a",
    "calm":       "#7ba68f",
}


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

        /* --- hide sidebar --- */
        [data-testid="stSidebar"]          { display: none !important; }
        [data-testid="collapsedControl"]   { display: none !important; }
        [data-testid="stSidebarCollapse"]  { display: none !important; }

        /* --- base --- */
        html, body, [class*="css"] {
            font-family: 'DM Sans', system-ui, sans-serif;
            font-size: 16px;
        }

        h1 {
            font-family: 'DM Serif Display', Georgia, serif !important;
            font-size: 36px !important;
            font-weight: 400 !important;
            letter-spacing: -0.01em !important;
            color: #e8e3db !important;
            line-height: 1.15 !important;
            margin-bottom: 0 !important;
        }

        h2 {
            font-family: 'DM Serif Display', Georgia, serif !important;
            font-size: 24px !important;
            font-weight: 400 !important;
            color: #e8e3db !important;
            line-height: 1.25 !important;
        }

        h3 {
            font-family: 'DM Sans', system-ui, sans-serif !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            letter-spacing: 0.10em !important;
            text-transform: uppercase !important;
            color: #5a5652 !important;
        }

        p, li {
            font-size: 16px !important;
            line-height: 1.7 !important;
            color: #e8e3db;
        }

        /* --- page container --- */
        [data-testid="stAppViewContainer"] > .main > .block-container {
            animation: fadeUp 0.35s ease both;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-top: 2.5rem !important;
            max-width: 780px !important;
            margin: 0 auto !important;
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* --- buttons --- */
        .stButton > button {
            background-color: transparent;
            border: 1px solid #3a3733;
            color: #8a8480;
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            font-weight: 400;
            padding: 10px 20px;
            transition: border-color 0.15s ease, color 0.15s ease;
        }

        .stButton > button:hover {
            border-color: #5a5652;
            color: #e8e3db;
            background-color: transparent;
        }

        .primary-btn .stButton > button,
        .stButton > button[kind="primary"] {
            background-color: #c4956a !important;
            border-color: #c4956a !important;
            color: #1c1a18 !important;
            font-weight: 500 !important;
        }

        .primary-btn .stButton > button:hover,
        .stButton > button[kind="primary"]:hover {
            opacity: 0.88;
            color: #1c1a18 !important;
            background-color: #c4956a !important;
        }

        /* equal height button rows */
        .btn-row-equal .stButton > button {
            height: 46px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* --- inputs --- */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #2e2b28 !important;
            border: 1px solid #3a3733 !important;
            border-radius: 8px !important;
            color: #e8e3db !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 16px !important;
            font-weight: 300 !important;
            transition: border-color 0.15s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #c4956a !important;
            box-shadow: none !important;
        }

        /* --- selectbox --- */
        .stSelectbox > div > div {
            background-color: #2e2b28 !important;
            border: 1px solid #3a3733 !important;
            border-radius: 8px !important;
            color: #e8e3db !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 15px !important;
        }

        /* --- popover --- */
        [data-testid="stPopover"] button {
            background: rgba(196,149,106,0.10) !important;
            border: 1px solid rgba(196,149,106,0.25) !important;
            border-radius: 20px !important;
            color: #c4956a !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 5px 16px !important;
        }

        /* --- divider --- */
        hr {
            border-color: #3a3733 !important;
            margin: 28px 0 !important;
        }

        /* --- chat input --- */
        [data-testid="stChatInput"] {
            background-color: #2e2b28 !important;
            border: 1px solid #3a3733 !important;
            border-radius: 8px !important;
        }

        [data-testid="stChatInput"] textarea {
            color: #e8e3db !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 15px !important;
        }

        /* --- hide branding --- */
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }

        /* ----------------------------------------------------------------
           RESPONSIVE
        ---------------------------------------------------------------- */

        @media (max-width: 640px) {
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            [data-testid="stAppViewContainer"] > .main > .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1.25rem !important;
            }

            h1 { font-size: 26px !important; }
            h2 { font-size: 20px !important; }

            .stButton > button {
                width: 100% !important;
                padding: 12px 16px !important;
            }

            .stTextArea > div > div > textarea,
            .stTextInput > div > div > input {
                font-size: 16px !important;
            }

            .vega-embed { overflow-x: auto !important; }
        }

        @media (max-width: 400px) {
            h1  { font-size: 22px !important; }
            p, li { font-size: 15px !important; }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Component helpers
# ---------------------------------------------------------------------------

def emotion_badge(emotion: str) -> str:
    color = EMOTION_COLORS.get(emotion.lower(), "#8a8480")
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'padding:6px 14px;border-radius:20px;'
        f'background:rgba({r},{g},{b},0.12);color:{color};'
        f'font-family:DM Sans,sans-serif;font-size:13px;font-weight:500;'
        f'letter-spacing:0.02em;margin:2px 3px 2px 0;">'
        f'<span style="width:7px;height:7px;border-radius:50%;'
        f'background:{color};opacity:0.9;display:inline-block;"></span>'
        f'{emotion.lower()}</span>'
    )


def emotion_badge_row(emotions: list) -> str:
    badges = "".join(emotion_badge(e) for e in emotions)
    return f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin:10px 0;">{badges}</div>'


def theme_badge_row(themes: list) -> str:
    badges = ""
    for theme in themes:
        badges += (
            f'<span style="display:inline-flex;align-items:center;'
            f'padding:5px 13px;border-radius:20px;'
            f'background:rgba(196,149,106,0.10);color:#8a8480;'
            f'font-family:DM Sans,sans-serif;font-size:13px;font-weight:400;'
            f'letter-spacing:0.02em;margin:2px 3px 2px 0;">'
            f'{theme}</span>'
        )
    return f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin:10px 0;">{badges}</div>'


def section_label(text: str):
    st.markdown(
        f'<p style="font-family:DM Sans,sans-serif;font-size:11px;font-weight:500;'
        f'letter-spacing:0.12em;text-transform:uppercase;color:#5a5652;'
        f'margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid #3a3733;">'
        f'{text}</p>',
        unsafe_allow_html=True,
    )


def disclaimer_chip(text: str = "You are talking with Indy, an AI companion, not a therapist."):
    """Centered amber disclaimer chip."""
    st.markdown(
        f'<div style="display:flex;justify-content:center;">'
        f'<div style="display:inline-flex;align-items:center;gap:8px;'
        f'background:rgba(196,149,106,0.10);'
        f'border:1px solid rgba(196,149,106,0.20);'
        f'border-radius:6px;padding:10px 18px;'
        f'font-family:DM Sans,sans-serif;font-size:13px;'
        f'color:#c4956a;font-weight:400;">'
        f'<span style="width:6px;height:6px;border-radius:50%;'
        f'background:#c4956a;flex-shrink:0;display:inline-block;"></span>'
        f'{text}</div></div>',
        unsafe_allow_html=True,
    )


def profile_pill_header(page_title: str):
    """
    Page header with title left and profile popover pill right.
    Instant switch on selection.
    """
    user = st.session_state.get("user", "Alex")
    col_title, col_pill = st.columns([5, 1])

    with col_title:
        st.markdown(f'<h1>{page_title}</h1>', unsafe_allow_html=True)

    with col_pill:
        with st.popover(user, use_container_width=False):
            st.markdown(
                '<p style="font-size:12px;font-weight:500;letter-spacing:0.10em;'
                'text-transform:uppercase;color:#5a5652;margin-bottom:10px;">'
                'Switch profile</p>',
                unsafe_allow_html=True,
            )
            new_user = st.radio(
                label="profile",
                options=["Alex", "Jordan"],
                index=0 if user == "Alex" else 1,
                label_visibility="collapsed",
            )
            if new_user != user:
                st.session_state["user"] = new_user
                st.session_state["selected_entry_index"] = 0
                st.session_state["chat_history"] = []
                st.session_state["chat_entry_context"] = None
                st.session_state["context_injected"] = False
                st.session_state["journal_mode"] = "browse"
                st.rerun()