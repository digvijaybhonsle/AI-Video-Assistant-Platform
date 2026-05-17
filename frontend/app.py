import streamlit as st
import time
import traceback
from dotenv import load_dotenv
import os
import requests

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_JIT"] = "0"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero Title ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}

.card:hover {
    border-color: var(--accent);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

/* ── Accent Badge ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
}

/* ── Progress / Status ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done     { background: var(--success); }
.dot-pending  { background: var(--border); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Chat ── */
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.chat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
}

.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }

.user-bubble { background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.25); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.1);  border: 1px solid rgba(6,182,212,0.2);   align-self: flex-start; }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Transcript box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Stale Streamlit elements ── */
.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)


# ─── Session State ─────────────────────────────────────

DEFAULT_SESSION_STATE = {

    "result": None,

    "chat_history": [],

    "pipeline_done": False,

    "pipeline_steps": {},

    "processing": False,

    "current_status": "Idle",

    "backend_online": True,
}

for key, value in DEFAULT_SESSION_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ─── Pipeline Config ───────────────────────────────────

PIPELINE_STEPS = [

    ("upload",     "📤", "Upload"),

    ("audio",      "🎵", "Audio Processing"),

    ("transcript", "📝", "Transcription"),

    ("title",      "🏷️", "Title Generation"),

    ("summary",    "📋", "Summarisation"),

    ("extract",    "🔍", "Insight Extraction"),

    ("rag",        "🧠", "AI Chat Engine"),
]

# ─── Helpers ───────────────────────────────────────────

def step_status(
    steps: dict,
    key: str
) -> str:

    status = steps.get(
        key,
        "pending"
    )

    if status == "done":
        return "dot-done"

    if status == "active":
        return "dot-active"

    if status == "error":
        return "dot-error"

    return "dot-pending"

def render_step_bar(

    label: str,

    key: str,

    icon: str
):

    css = step_status(

        st.session_state.pipeline_steps,

        key
    )

    st.markdown(f"""
    <div class="status-bar">

        <div class="status-dot {css}"></div>

        <span>
            {icon} {label}
        </span>

    </div>
    """, unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────

with st.sidebar:

    # ====================================================
    # HERO
    # ====================================================

    st.markdown("""
    <div class="hero-title"
         style="font-size:1.8rem">

         🎬 AI<br>Video

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-sub">

        Meeting Intelligence Platform

    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ====================================================
    # BACKEND STATUS
    # ====================================================

    backend_status = (
        "🟢 Online"
        if st.session_state.backend_online
        else "🔴 Offline"
    )

    st.markdown(f"""
    <div class="card"
         style="padding:0.8rem 1rem">

        <div style="
            font-size:0.8rem;
            color:var(--text-muted);
            margin-bottom:0.3rem
        ">
            Backend Status
        </div>

        <div style="
            font-weight:700;
            font-family:'Syne',sans-serif
        ">
            {backend_status}
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ====================================================
    # INPUTS
    # ====================================================

    st.markdown(
        '<span class="badge badge-purple">'
        'Meeting Input'
        '</span>',
        unsafe_allow_html=True
    )

    source = st.text_input(

        "YouTube URL",

        placeholder=(
            "https://youtube.com/watch?v=..."
        )
    )

    uploaded_file = st.file_uploader(

        "Upload Audio / Video",

        type=[
            "mp3",
            "wav",
            "mp4",
            "m4a"
        ]
    )

    language = st.selectbox(

        "Language",

        [
            "english",
            "hinglish"
        ],

        index=0
    )

    st.markdown("<br>", unsafe_allow_html=True)

    run_btn = st.button(

        "⚡ Analyse Meeting",

        use_container_width=True,

        type="primary"
    )

    # ====================================================
    # FILE INFO
    # ====================================================

    if uploaded_file:

        file_size_mb = (
            uploaded_file.size
            / (1024 * 1024)
        )

        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                📁 Uploaded File
            </div>

            <div class="card-content">

                <strong>
                    {uploaded_file.name}
                </strong>

                <br><br>

                Size:
                {file_size_mb:.2f} MB

            </div>

        </div>
        """, unsafe_allow_html=True)

    # ====================================================
    # LIVE STATUS
    # ====================================================

    st.markdown("---")

    st.markdown(
        '<span class="badge badge-green">'
        'Pipeline Status'
        '</span>',
        unsafe_allow_html=True
    )

    if st.session_state.processing:

        st.markdown(f"""
        <div class="status-bar">

            <div class="status-dot dot-active"></div>

            <span>
                ⚡ {st.session_state.current_status}
            </span>

        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="status-bar">

            <div class="status-dot dot-pending"></div>

            <span>
                Waiting for analysis...
            </span>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ====================================================
    # PIPELINE STEPS
    # ====================================================

    for step, icon, label in PIPELINE_STEPS:

        render_step_bar(
            label,
            step,
            icon
        )

# ─── Main Area ─────────────────────────────────────────

st.markdown("""
<div class="hero-title">

    AI Video Assistant

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-sub">

    Transcribe · Summarise · Extract · Chat

</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Pipeline Execution ─────────────────────────────────

if run_btn and (source.strip() or uploaded_file):

    try:

        # ====================================================
        # RESET SESSION
        # ====================================================

        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_bar = st.progress(0)

        status_box = st.empty()

        log_container = st.container()

        backend_spinner = st.empty()

        # ====================================================
        # HELPERS
        # ====================================================

        def update_step(
            step_key: str,
            message: str,
            progress: int,
            status: str = "active"
        ):

            st.session_state.pipeline_steps[
                step_key
            ] = status

            progress_bar.progress(progress)

            if status == "done":

                status_box.success(message)

            elif status == "error":

                status_box.error(message)

            else:

                status_box.info(message)

            with log_container:
                st.write(message)

        def complete_step(step_key: str):

            st.session_state.pipeline_steps[
                step_key
            ] = "done"

        # ====================================================
        # YOUTUBE FLOW
        # ====================================================

        if source.strip():

            update_step(
                "upload",
                "📺 Validating YouTube URL...",
                10,
                "active"
            )

            time.sleep(0.5)

            complete_step("upload")

            update_step(
                "transcript",
                "📝 Fetching YouTube subtitles...",
                20,
                "active"
            )

            from backend.utils.youtube_transcript import (
                fetch_youtube_transcript
            )

            try:

                transcript = fetch_youtube_transcript(
                    source
                )

                complete_step("transcript")

                update_step(
                    "summary",
                    "📄 Sending transcript to AI backend...",
                    35,
                    "active"
                )

                backend_spinner.markdown("""
                <div class="status-bar">
                    <div class="status-dot dot-active"></div>
                    <span>
                        ⚡ AI backend is analysing your transcript...
                    </span>
                </div>
                """, unsafe_allow_html=True)

                response = requests.post(

                    f"{BACKEND_URL}/analyze-transcript",

                    json={

                        "transcript": transcript,

                        "language": language
                    },

                    timeout=1800
                )

                backend_spinner.empty()

            except Exception:

                st.error(
                    "❌ This YouTube video does not provide subtitles.\n\n"
                    "Please upload the audio/video file manually."
                )

                st.stop()

        # ====================================================
        # FILE FLOW
        # ====================================================

        elif uploaded_file:

            update_step(
                "upload",
                "📤 Uploading media file...",
                10,
                "active"
            )

            time.sleep(0.3)

            complete_step("upload")

            update_step(
                "audio",
                "🎵 Processing audio stream...",
                25,
                "active"
            )

            backend_spinner.markdown("""
            <div class="status-bar">
                <div class="status-dot dot-active"></div>
                <span>
                    ⚡ Whisper AI is transcribing your media...
                </span>
            </div>
            """, unsafe_allow_html=True)

            response = requests.post(

                f"{BACKEND_URL}/analyze-file",

                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        uploaded_file.type
                    )
                },

                data={
                    "language": language
                },

                timeout=1800
            )

            backend_spinner.empty()

        # ====================================================
        # RESPONSE VALIDATION
        # ====================================================

        progress_bar.progress(70)

        if response.status_code != 200:

            update_step(
                "extract",
                "❌ Backend processing failed",
                70,
                "error"
            )

            st.error(
                f"Backend Error: {response.text}"
            )

            st.stop()

        data = response.json()

        # ====================================================
        # PIPELINE COMPLETION
        # ====================================================

        complete_step("audio")

        update_step(
            "transcript",
            "📝 Transcription completed",
            75,
            "done"
        )

        update_step(
            "title",
            "🏷️ AI title generated",
            82,
            "done"
        )

        update_step(
            "summary",
            "📄 Summary generated",
            88,
            "done"
        )

        update_step(
            "extract",
            "🔍 Insights extracted",
            94,
            "done"
        )

        update_step(
            "rag",
            "🧠 AI chat engine ready",
            98,
            "done"
        )

        # ====================================================
        # SAVE RESULTS
        # ====================================================

        st.session_state.result = {

            "title": data.get(
                "title",
                "AI Meeting Analysis"
            ),

            "transcript": data.get(
                "transcript",
                ""
            ),

            "summary": data.get(
                "summary",
                ""
            ),

            "action_items": data.get(
                "action_items",
                ""
            ),

            "key_decisions": data.get(
                "key_decisions",
                ""
            ),

            "open_questions": data.get(
                "open_questions",
                ""
            ),

            "rag_chain": None,
        }

        st.session_state.pipeline_done = True

        progress_bar.progress(100)

        status_box.success(
            "🎉 Analysis Completed Successfully!"
        )

    except Exception as e:

        update_step(
            "extract",
            "❌ Pipeline execution failed",
            100,
            "error"
        )

        st.error(
            f"❌ Pipeline Failed: {str(e)}"
        )

        with log_container:

            st.error(
                traceback.format_exc()
            )

        st.session_state.pipeline_done = False
# ─── Results Display ─────────────────────────────────────

if st.session_state.result:

    r = st.session_state.result

    transcript = r.get(
        "transcript",
        ""
    )

    summary = r.get(
        "summary",
        ""
    )

    action_items = r.get(
        "action_items",
        ""
    )

    key_decisions = r.get(
        "key_decisions",
        ""
    )

    open_questions = r.get(
        "open_questions",
        ""
    )

    # ====================================================
    # HERO HEADER
    # ====================================================

    st.markdown(f"""
    <div class="card">

        <div class="badge badge-purple">
            AI GENERATED SESSION
        </div>

        <div style="
            font-family:'Syne',sans-serif;
            font-size:2rem;
            font-weight:800;
            margin-top:1rem;
            color:var(--text)
        ">
            {r.get("title", "Meeting Analysis")}
        </div>

        <div style="
            margin-top:0.8rem;
            color:var(--text-muted);
            font-size:0.9rem;
            line-height:1.8
        ">
            AI-powered meeting intelligence generated using
            Whisper, Mistral AI and Retrieval-Augmented Generation.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ====================================================
    # ANALYTICS ROW
    # ====================================================

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                📝 Transcript
            </div>

            <div style="
                font-size:1.6rem;
                font-weight:700;
                font-family:'Syne',sans-serif
            ">
                {len(transcript.split())}
            </div>

            <div class="hero-sub">
                words analysed
            </div>

        </div>
        """, unsafe_allow_html=True)

    with metric2:
        st.markdown("""
        <div class="card">

            <div class="card-title">
                ⚡ AI Engine
            </div>

            <div style="
                font-size:1.4rem;
                font-weight:700;
                color:var(--success)
            ">
                ACTIVE
            </div>

            <div class="hero-sub">
                backend online
            </div>

        </div>
        """, unsafe_allow_html=True)

    with metric3:
        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                🔍 Insights
            </div>

            <div style="
                font-size:1.6rem;
                font-weight:700;
                font-family:'Syne',sans-serif
            ">
                3
            </div>

            <div class="hero-sub">
                extracted sections
            </div>

        </div>
        """, unsafe_allow_html=True)

    with metric4:
        st.markdown("""
        <div class="card">

            <div class="card-title">
                🧠 RAG Chat
            </div>

            <div style="
                font-size:1.4rem;
                font-weight:700;
                color:var(--accent-2)
            ">
                READY
            </div>

            <div class="hero-sub">
                contextual retrieval
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ====================================================
    # SUMMARY + TRANSCRIPT
    # ====================================================

    left, right = st.columns(
        [2.4, 1.2],
        gap="large"
    )

    with left:

        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                📋 Executive Summary
            </div>

            <div class="card-content">
                {summary}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with right:

        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                📄 Transcript Preview
            </div>

            <div class="transcript-box">
                {transcript[:2500]}
            </div>

        </div>
        """, unsafe_allow_html=True)

        with st.expander(
            "📝 View Full Transcript"
        ):

            st.markdown(f"""
            <div class="transcript-box">
                {transcript}
            </div>
            """, unsafe_allow_html=True)

    # ====================================================
    # INSIGHTS GRID
    # ====================================================

    st.markdown("""
    <div style="
        font-family:'Syne',sans-serif;
        font-size:1.3rem;
        font-weight:700;
        margin:1rem 0
    ">
        🔍 Meeting Intelligence
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(
        3,
        gap="medium"
    )

    with c1:

        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                ✅ Action Items
            </div>

            <div class="card-content">
                {action_items}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                🔑 Key Decisions
            </div>

            <div class="card-content">
                {key_decisions}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown(f"""
        <div class="card">

            <div class="card-title">
                ❓ Open Questions
            </div>

            <div class="card-content">
                {open_questions}
            </div>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ====================================================
    # CHAT SECTION
    # ====================================================

    st.markdown("""
    <div style="
        font-family:'Syne',sans-serif;
        font-size:1.5rem;
        font-weight:800;
        margin-bottom:1rem
    ">
        💬 AI Meeting Chat
    </div>
    """, unsafe_allow_html=True)

    # ====================================================
    # CHAT HISTORY
    # ====================================================

    if st.session_state.chat_history:

        chat_html = '<div class="chat-container">'

        for msg in st.session_state.chat_history:

            if msg["role"] == "user":

                chat_html += f"""
                <div class="chat-msg"
                     style="align-items:flex-end">

                    <span class="chat-label user-label">
                        YOU
                    </span>

                    <div class="chat-bubble user-bubble">
                        {msg['content']}
                    </div>

                </div>
                """

            else:

                chat_html += f"""
                <div class="chat-msg"
                     style="align-items:flex-start">

                    <span class="chat-label bot-label">
                        AI ASSISTANT
                    </span>

                    <div class="chat-bubble bot-bubble">
                        {msg['content']}
                    </div>

                </div>
                """

        chat_html += "</div>"

        st.markdown(
            chat_html,
            unsafe_allow_html=True
        )

    # ====================================================
    # CHAT INPUT
    # ====================================================

    chat_col1, chat_col2 = st.columns(
        [6, 1]
    )

    with chat_col1:

        user_input = st.text_input(
            "Question",
            placeholder="Ask anything about the meeting...",
            label_visibility="collapsed"
        )

    with chat_col2:

        send_btn = st.button(
            "Send",
            use_container_width=True
        )

    # ====================================================
    # CHAT API CALL
    # ====================================================

    if send_btn and user_input.strip():

        with st.spinner(
            "🧠 AI is analysing meeting context..."
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/chat",

                    json={

                        "question":
                        user_input.strip(),

                        "transcript":
                        transcript
                    },

                    timeout=600
                )

                if response.status_code != 200:

                    st.error(
                        "Chat backend failed"
                    )

                    st.stop()

                data = response.json()

                answer = data.get(
                    "answer",
                    "No response generated"
                )

                st.session_state.chat_history.append({

                    "role": "user",

                    "content":
                    user_input.strip()
                })

                st.session_state.chat_history.append({

                    "role": "assistant",

                    "content":
                    answer
                })

                st.rerun()

            except Exception as e:

                st.error(
                    f"Chat error: {e}"
                )

    # ====================================================
    # CLEAR CHAT
    # ====================================================

    if (
        st.session_state.chat_history
        and
        st.button(
            "🗑️ Clear Conversation",
            type="secondary"
        )
    ):

        st.session_state.chat_history = []

        st.rerun()

# ========================================================
# EMPTY STATE
# ========================================================

else:

    st.markdown("""
    <div style="
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        padding:5rem 2rem;
        text-align:center
    ">

        <div style="
            font-size:4rem;
            margin-bottom:1rem
        ">
            🎬
        </div>

        <div style="
            font-family:'Syne',sans-serif;
            font-size:1.5rem;
            font-weight:700;
            color:var(--text);
            margin-bottom:0.5rem
        ">
            Ready to Analyse
        </div>

        <div style="
            color:var(--text-muted);
            font-size:0.85rem;
            max-width:420px;
            line-height:1.7
        ">

            Upload an MP3/M4A audio file or
            paste a YouTube video with subtitles
            to generate AI-powered meeting insights.

        </div>

    </div>
    """, unsafe_allow_html=True)