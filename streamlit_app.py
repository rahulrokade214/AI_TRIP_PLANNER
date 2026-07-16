import streamlit as st
import requests
import datetime
import os

# Falls back to localhost for local dev; set BASE_URL as an env var
# in deployment (Cloud Run, etc.) to point at the live backend.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Travel Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------
# Professional theme: deep teal + slate, clean sans-serif,
# native st.chat_message bubbles (fixes markdown/code-fence
# rendering issues from the old hand-rolled HTML bubbles).
# ----------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {
        --bg: #F7F9FA;
        --surface: #FFFFFF;
        --text: #1A2B33;
        --text-muted: #64748B;
        --accent: #0F6B62;
        --accent-hover: #0B5049;
        --accent-soft: #E6F3F1;
        --border: #E2E8F0;
    }

    html {
        color-scheme: light !important;
    }

    .stApp { background-color: var(--bg) !important; }
    #MainMenu, footer, header {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text) !important;
    }

    /* Force readable text everywhere — prevents dark-mode/browser
       theme inheritance from making titles or chat text invisible. */
    h1, h2, h3, p, li, span, label {
        color: var(--text) !important;
    }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stMarkdownContainer"] {
        color: var(--text) !important;
    }
    div[data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
    }

    .block-container {
        max-width: 860px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }

    /* ---------------- Sidebar ---------------- */
    section[data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 1px solid var(--border);
    }
    .sb-brand {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--accent);
        margin-bottom: 0.2rem;
    }
    .sb-tagline {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-bottom: 1.6rem;
    }
    .sb-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 1.2rem 0 0.5rem 0;
    }
    .sb-tip {
        font-size: 0.85rem;
        color: var(--text);
        background: var(--accent-soft);
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }

    /* ---------------- Header ---------------- */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.3rem;
    }
    .app-header .icon {
        font-size: 1.7rem;
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text) !important;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: var(--text-muted) !important;
        margin: 0 0 1.6rem 2.4rem;
    }

    /* ---------------- Chat bubbles (native st.chat_message) ---------------- */
    div[data-testid="stChatMessage"] {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.4rem 0.2rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 3px rgba(15, 23, 33, 0.04);
    }

    /* ---------------- Chat input (native st.chat_input) ---------------- */
    /* The outer fixed-bottom wrapper Streamlit renders around chat_input
       defaults to the app's dark theme if the browser prefers dark mode.
       Force it light explicitly, not just the inner pill. */
    div[data-testid="stBottom"],
    div[data-testid="stBottomBlockContainer"],
    div[data-testid="stChatInputContainer"] {
        background-color: var(--bg) !important;
    }
    div[data-testid="stChatInput"] {
        background-color: var(--surface) !important;
        border-radius: 999px;
        border: 1.5px solid var(--border) !important;
        box-shadow: 0 4px 18px rgba(15, 23, 33, 0.06);
    }
    div[data-testid="stChatInput"]:focus-within {
        border: 1.5px solid var(--accent) !important;
        outline: none !important;
        box-shadow: 0 4px 18px rgba(15, 23, 33, 0.06) !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }
    div[data-testid="stChatInput"] * {
        background-color: transparent !important;
    }
    textarea, input {
        color-scheme: light !important;
        background-color: var(--surface) !important;
        color: var(--text) !important;
    }
    div[data-testid="stChatInput"] textarea {
        font-size: 0.98rem;
        color: var(--text) !important;
        background-color: transparent !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }
    div[data-testid="stChatInput"] button {
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
    }

    /* ---------------- All Streamlit buttons ---------------- */
    /* Buttons are native <button> elements, subject to the same
       browser dark-mode color-scheme issue as the chat textarea.
       Force them light everywhere, not just inside columns. */
    button {
        color-scheme: light !important;
    }
    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px;
        font-weight: 500;
    }
    div[data-testid="stButton"] button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background-color: var(--accent-soft) !important;
    }
    div[data-testid="stButton"] button p,
    div[data-testid="stFormSubmitButton"] button p {
        color: inherit !important;
    }

    /* ---------------- Quick-start chips ---------------- */
    div[data-testid="column"] .stButton button {
        text-align: left;
        padding: 0.6rem 0.9rem;
        font-size: 0.86rem;
        width: 100%;
    }

    /* ---------------- Empty state ---------------- */
    .empty-state {
        text-align: center;
        padding: 3.5rem 1rem;
        color: var(--text-muted);
    }
    .empty-state .icon {
        font-size: 2.4rem;
        margin-bottom: 0.6rem;
    }
    .empty-state .title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# State
# ----------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

def call_backend(question: str) -> str:
    try:
        response = requests.post(f"{BASE_URL}/query", json={"question": question}, timeout=120)
        if response.status_code == 200:
            return response.json().get("answer", "No answer returned.")
        return (
            f"Something went wrong on the backend (status {response.status_code}).\n\n"
            f"```\n{response.text}\n```"
        )
    except Exception as e:
        return (
            "Couldn't reach the planner backend.\n\n"
            f"`{e}`\n\n"
            "Make sure your FastAPI server is running:\n"
            "```\nuvicorn main:app --reload --port 8000\n```"
        )

def send_query(question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Planning your trip..."):
        answer = call_backend(question)
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "time": datetime.datetime.now().strftime("%b %d, %H:%M"),
    })

# ----------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-brand">🧭 Travel Planner</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-tagline">AI-powered trip planning — itineraries, budgets, and local tips.</div>',
        unsafe_allow_html=True,
    )

    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="sb-label">Tips for better plans</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tip">Mention your budget level — budget, mid-range, or luxury.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tip">Include trip length and who\'s traveling (solo, couple, family).</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tip">Ask follow-ups — "make it cheaper" or "add more nightlife."</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------
# Header
# ----------------------------------------------------------------
st.markdown(
    '<div class="app-header"><span class="icon">🧭</span><h1 class="app-title">Where would you like to go?</h1></div>'
    '<div class="app-subtitle">Tell me your destination and I\'ll put together a full plan — stays, spots, and budget.</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# Empty state + quick starts
# ----------------------------------------------------------------
if not st.session_state.messages:
    st.markdown(
        '<div class="empty-state"><div class="icon">🗺️</div>'
        '<div class="title">Start planning your next trip</div>'
        'Type your destination, dates, and budget to get started.</div>',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------
# Chat history (native chat_message renders markdown/code correctly)
# ----------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🧭"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["role"] == "assistant" and "time" in msg:
            st.caption(f"Travel Planner · {msg['time']}")
        st.markdown(msg["content"])

# ----------------------------------------------------------------
# Composer — native st.chat_input, pinned to the bottom automatically
# ----------------------------------------------------------------
user_input = st.chat_input("Plan a trip to Goa for 5 days")
if user_input and user_input.strip():
    send_query(user_input)
    st.rerun()