import streamlit as st
import time
import traceback
from dotenv import load_dotenv
import os
import requests
import uuid

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

/* ── Global Reset & Typography ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Animated subtle grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.035) 1px, transparent 1px);
    background-size: 45px 45px;
    pointer-events: none;
    z-index: -1;
    opacity: 0.85;
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
    font-size: 0.82rem;
    color: var(--text-muted);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.15);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

/* Card Title */
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.badge-purple { background: rgba(124,58,237,0.15); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success); border: 1px solid rgba(16,185,129,0.3); }

/* ── Buttons & Inputs ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(124, 58, 237, 0.35) !important;
}

/* ── Status Bar ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 1rem;
    background: var(--surface-2);
    border-radius: 10px;
    margin: 0.5rem 0;
    border: 1px solid var(--border);
    font-size: 0.82rem;
}

.status-dot {
    width: 9px; 
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 10px var(--accent-glow); animation: pulse 1.6s infinite; }
.dot-done     { background: var(--success); }
.dot-pending  { background: var(--border); }
.dot-error    { background: var(--danger); box-shadow: 0 0 8px var(--danger); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}

/* ── Chat & Transcript ── */
.chat-container, .transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
}

.transcript-box {
    font-size: 0.83rem;
    line-height: 1.75;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* Chat Bubbles */
.chat-bubble {
    padding: 0.65rem 1rem;
    border-radius: 12px;
    font-size: 0.88rem;
    line-height: 1.65;
    max-width: 88%;
}

.user-bubble  { background: rgba(124,58,237,0.18); border: 1px solid rgba(124,58,237,0.3); }
.bot-bubble   { background: rgba(6,182,212,0.12);  border: 1px solid rgba(6,182,212,0.25); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Misc */
.stProgress > div > div > div { background: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ─────────────────────────────────────────────
DEFAULT_SESSION_STATE = {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
    "processing": False,
    "current_status": "Idle",
    "backend_online": True,
    "session_id": uuid.uuid4().hex,
    "prefill_question": "",
}

for key, default_value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# ─── Pipeline Configuration ───────────────────────────────────────────────────
PIPELINE_STEPS = [
    ("upload",     "📤", "Upload"),
    ("audio",      "🎵", "Audio Processing"),
    ("transcript", "📝", "Transcription"),
    ("title",      "🏷️", "Title Generation"),
    ("summary",    "📋", "Summarisation"),
    ("extract",    "🔍", "Insight Extraction"),
    ("rag",        "🧠", "AI Chat Engine"),
]

# ─── Helper Functions ─────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    """Return CSS class based on step status"""
    status = steps.get(key, "pending")
    
    if status == "done":
        return "dot-done"
    elif status == "active":
        return "dot-active"
    elif status == "error":
        return "dot-error"  
    return "dot-pending"


def render_step_bar(label: str, key: str, icon: str):
    """Render a single pipeline step with status"""
    css_class = step_status(st.session_state.pipeline_steps, key)
    
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css_class}"></div>
        <span>{icon} {label}</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Hero Section
    st.markdown("""
    <div class="hero-title" style="font-size:1.85rem">
        🎬 AI<br>Video
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="hero-sub">Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Backend Status
    backend_status = "🟢 Online" if st.session_state.backend_online else "🔴 Offline"
    st.markdown(f"""
    <div class="card" style="padding:0.8rem 1rem">
        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.3rem;">
            Backend Status
        </div>
        <div style="font-weight:700; font-family:'Syne',sans-serif;">
            {backend_status}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Input Section ─────────────────────────────────────
    st.markdown('<span class="badge badge-purple">Input</span>', unsafe_allow_html=True)

    source = st.text_input(
        "YouTube URL",
        placeholder="https://youtube.com/watch?v=...",
        key="youtube_input"
    )

    uploaded_file = st.file_uploader(
        "Upload Audio / Video",
        type=["mp4", "mp3", "wav", "m4a", "mov", "mpeg4"],
        key="file_uploader"          # ← Important for persistence
    )

    language = st.selectbox(
        "Language",
        ["english", "hinglish"],
        index=0,
        key="language_select"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    run_btn = st.button(
        "⚡ Analyse Audio",
        use_container_width=True,
        type="primary",
        key="analyse_btn"
    )

    # ── Uploaded File Info (Improved) ─────────────────────
    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.success(f"✅ File ready: **{uploaded_file.name}**")
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📁 UPLOADED FILE</div>
            <div class="card-content">
                <strong>{uploaded_file.name}</strong><br><br>
                Size: <strong>{file_size_mb:.2f} MB</strong><br>
                Type: {uploaded_file.type.split('/')[-1].upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Pipeline Status ───────────────────────────────────
    st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)

    if st.session_state.get("processing", False):
        st.markdown(f"""
        <div class="status-bar">
            <div class="status-dot dot-active"></div>
            <span>⚡ {st.session_state.current_status}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-bar">
            <div class="status-dot dot-pending"></div>
            <span>Ready • Waiting for input</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pipeline Steps ────────────────────────────────────
    for step_key, icon, label in PIPELINE_STEPS:
        render_step_bar(label, step_key, icon)


# ─── Main Area Header ──────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Extract · Chat</div>', unsafe_allow_html=True)
st.markdown("---")


# ─── Pipeline Execution ─────────────────────────────────

if run_btn and (source.strip() or uploaded_file):

    try:

        # ====================================================
        # RESET STATE
        # ====================================================

        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        st.session_state.processing = True

        st.session_state.current_status = (
            "Initializing AI pipeline..."
        )

        progress_bar = st.progress(0)

        status_box = st.empty()

        log_container = st.empty()

        backend_status_box = st.empty()

        # ====================================================
        # HELPERS
        # ====================================================

        def update_step(
            step_key: str,
            message: str,
            progress: int,
            status: str = "active"
        ):
            """Update pipeline step status and UI"""
            st.session_state.pipeline_steps[step_key] = status
            st.session_state.current_status = message

            progress_bar.progress(progress)

            if status == "done":
                status_box.success(message)
            elif status == "error":
                status_box.error(message)
            else:
                status_box.info(message)

            # Clean log without complex HTML
            with log_container:
                if status == "done":
                    st.success(f"✅ {message}")
                elif status == "error":
                    st.error(f"❌ {message}")
                else:
                    st.info(f"⏳ {message}")

        def complete_step(step_key: str):

            st.session_state.pipeline_steps[
                step_key
            ] = "done"

        # ====================================================
        # BACKEND STATUS CHECK
        # ====================================================

        try:

            health = requests.get(

                f"{BACKEND_URL}/health",

                timeout=20
            )

            st.session_state.backend_online = (
                health.status_code == 200
            )

        except Exception:

            st.session_state.backend_online = False

            st.error(
                "❌ AI backend is currently offline."
            )

            st.stop()

# ====================================================
# YOUTUBE FLOW
# ====================================================

        if source.strip():

            update_step("upload", "📺 Validating YouTube video...", 10)
            time.sleep(0.5)
            complete_step("upload")

            update_step("transcript", "📝 Fetching transcript...", 20)

            try:
                from utils.youtube_transcript import fetch_youtube_transcript
                
                transcript = fetch_youtube_transcript(source)

                if not transcript or len(transcript.strip()) < 50:
                    raise Exception("Transcript unavailable or too short.")

                complete_step("transcript")

                update_step("summary", "📄 Sending to AI backend...", 35)

                # Clean AI Backend Status Card
                backend_status_box.markdown("""
                <div class="card">
                    <div class="card-title">⚡ AI Backend Processing</div>
                    <div class="card-content">
                        Analyzing transcript using:<br><br>
                        • Mistral AI<br>
                        • LangChain RAG<br>
                        • Advanced Summarization
                    </div>
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

            except Exception as e:
                backend_status_box.empty()
                st.warning("""
                ⚠️ **Subtitles not available for this video**

                Please upload the audio/video file manually 
                for full Whisper transcription support.
                """)
                st.session_state.processing = False
                st.stop()
        # ====================================================
        # FILE FLOW
        # ====================================================

        elif uploaded_file:

            file_size_mb = (
                uploaded_file.size
                / (1024 * 1024)
            )

            if file_size_mb > 50:

                st.error(
                    "❌ File exceeds 50MB limit."
                )

                st.stop()

            update_step(

                "upload",

                "📤 Uploading media file...",

                10
            )

            time.sleep(0.3)

            complete_step("upload")

            update_step(
                "audio",
                "🎵 Whisper AI is processing audio...",
                30
            )

            backend_status_box.info("""
            🧠 **Whisper AI Transcription in Progress**

            Processing uploaded audio file...
            Large files may take several minutes.
            """)
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
                f"Backend Error:\n{response.text}"
            )

            st.session_state.processing = False

            st.stop()

        data = response.json()

        if "error" in data:

            raise Exception(data["error"])

        # ====================================================
        # FINALIZE PIPELINE
        # ====================================================

        complete_step("audio")

        update_step(

            "transcript",

            "📝 Transcription completed",

            78,

            "done"
        )

        update_step(

            "title",

            "🏷️ AI title generated",

            84,

            "done"
        )

        update_step(

            "summary",

            "📄 Executive summary generated",

            90,

            "done"
        )

        update_step(

            "extract",

            "🔍 Video insights extracted",

            95,

            "done"
        )

        update_step(

            "rag",

            "🧠 AI chat engine initialized",

            98,

            "done"
        )

        # ====================================================
        # SAVE RESULTS
        # ====================================================

        st.session_state.result = {

            "title": data.get(
                "title",
                "Video Analysis"
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

        st.session_state.processing = False

        progress_bar.progress(100)

        backend_status_box.empty()

        status_box.success("""
        🎉 Analysis completed successfully!
        """)

        st.balloons()

    except Exception as e:

        st.session_state.processing = False

        update_step(

            "extract",

            "❌ Pipeline execution failed",

            100,

            "error"
        )

        st.error(
            f"❌ Pipeline Failed:\n{str(e)}"
        )

        with st.expander(
            "View Technical Logs"
        ):

            st.code(
                traceback.format_exc()
            )

import re

def format_ai_text(text: str) -> str:

    if not text:
        return ""

    # ====================================================
    # REMOVE MARKDOWN HEADERS
    # ====================================================

    text = re.sub(

        r"^#{1,6}\s*",

        "",

        text,

        flags=re.MULTILINE
    )

    # ====================================================
    # REMOVE BOLD MARKDOWN
    # ====================================================

    text = re.sub(

        r"\*\*(.*?)\*\*",

        r"<strong>\1</strong>",

        text
    )

    # ====================================================
    # CONVERT BULLETS
    # ====================================================

    lines = text.split("\n")

    formatted_lines = []

    inside_list = False

    for line in lines:

        stripped = line.strip()

        if (
            stripped.startswith("- ")
            or
            stripped.startswith("* ")
        ):

            if not inside_list:

                formatted_lines.append("<ul>")

                inside_list = True

            formatted_lines.append(

                f"<li>{stripped[2:]}</li>"
            )

        else:

            if inside_list:

                formatted_lines.append("</ul>")

                inside_list = False

            if stripped:

                formatted_lines.append(

                    f"<p>{stripped}</p>"
                )

    if inside_list:

        formatted_lines.append("</ul>")

    return "".join(formatted_lines)

# ─── Results Display ─────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    transcript = r.get("transcript", "")
    summary = r.get("summary", "")
    action_items = r.get("action_items", "No action items found.")
    key_decisions = r.get("key_decisions", "No key decisions found.")
    open_questions = r.get("open_questions", "No questions found.")

    # ====================================================
    # HERO HEADER
    # ====================================================
    st.markdown(f"""
    <div class="card">
        <div class="badge badge-purple">AI GENERATED SESSION</div>
        <div style="font-family:'Syne',sans-serif; font-size:2.1rem; font-weight:800; margin:1rem 0 0.5rem 0;">
            {r.get("title", "Video Analysis")}
        </div>
        <div style="color:var(--text-muted); font-size:0.9rem; line-height:1.6;">
            AI-powered video intelligence generated using Whisper, Mistral AI & RAG
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ====================================================
    # METRICS ROW
    # ====================================================
    m1, m2, m3, m4 = st.columns(4, gap="small")

    with m1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📝 TRANSCRIPT</div>
            <div style="font-size:1.8rem; font-weight:700; font-family:'Syne',sans-serif;">
                {len(transcript.split()) if transcript else 0}
            </div>
            <div class="hero-sub">words analysed</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown("""
        <div class="card">
            <div class="card-title">⚡ AI ENGINE</div>
            <div style="font-size:1.6rem; font-weight:700; color:var(--success);">ACTIVE</div>
            <div class="hero-sub">backend online</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown("""
        <div class="card">
            <div class="card-title">🔍 INSIGHTS</div>
            <div style="font-size:1.8rem; font-weight:700; font-family:'Syne',sans-serif;">3</div>
            <div class="hero-sub">extracted sections</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown("""
        <div class="card">
            <div class="card-title">🧠 RAG CHAT</div>
            <div style="font-size:1.6rem; font-weight:700; color:var(--accent-2);">READY</div>
            <div class="hero-sub">contextual retrieval</div>
        </div>
        """, unsafe_allow_html=True)

    # ====================================================
    # SUMMARY + TRANSCRIPT
    # ====================================================
    left, right = st.columns([2.5, 1.5], gap="large")

    with left:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 EXECUTIVE SUMMARY</div>
            <div class="card-content">{format_ai_text(summary)}</div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📄 TRANSCRIPT PREVIEW</div>
            <div class="transcript-box">{transcript[:2200]}...</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📝 View Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{transcript}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ====================================================
    # INSIGHTS GRID
    # ====================================================
    st.markdown("""
    <div style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700; margin:1.2rem 0 1rem 0;">
        🔍 Video Intelligence
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ ACTION ITEMS</div>
            <div class="card-content">{action_items}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 KEY DECISIONS</div>
            <div class="card-content">{key_decisions}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ OPEN QUESTIONS</div>
            <div class="card-content">{open_questions}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

# ====================================================
# CHAT SECTION
# ====================================================
st.markdown("""
<div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; margin:2rem 0 1rem 0;">
    💬 AI Video Chat
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
            <div class="chat-msg" style="align-items:flex-end">
                <span class="chat-label user-label">YOU</span>
                <div class="chat-bubble user-bubble">{msg['content']}</div>
            </div>"""
        else:
            chat_html += f"""
            <div class="chat-msg" style="align-items:flex-start">
                <span class="chat-label bot-label">🤖 AI ASSISTANT</span>
                <div class="chat-bubble bot-bubble">{msg['content']}</div>
            </div>"""
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

else:
    # Clean Empty Chat State
    st.markdown("""
    <div class="card" style="text-align:center; padding:3rem 2rem;">
        <div style="font-size:3.5rem; margin-bottom:1rem; opacity:0.7;">💬</div>
        <div style="font-size:1.15rem; font-weight:600; margin-bottom:0.8rem;">
            No conversation yet
        </div>
        <div style="color:var(--text-muted); line-height:1.6;">
            Start chatting with the AI about your video content.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ====================================================
# CHAT INPUT
# ====================================================
col1, col2 = st.columns([6, 1], gap="small")

with col1:
    user_input = st.text_input(
        "Ask a question about the video",
        placeholder="What were the main decisions made?",
        label_visibility="collapsed",
        key="chat_input"
    )

with col2:
    send_btn = st.button("Send", use_container_width=True, key="send_btn")

# ====================================================
# HANDLE CHAT SUBMISSION
# ====================================================
if send_btn and user_input.strip():
    if not st.session_state.result:
        st.warning("Please analyse a video first before asking questions.")
    else:
        with st.spinner("🧠 AI is thinking based on video content..."):
            try:
                transcript = st.session_state.result.get("transcript", "")

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "question": user_input.strip(),
                        "transcript": transcript
                    },
                    timeout=600
                )

                if response.status_code == 200:
                    answer = response.json().get("answer", "I couldn't generate a response.")
                    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    try:

                        error_data = response.json()

                        error_message = error_data.get(
                            "error"
                        )

                        if not error_message:

                            error_message = (
                                f"Status {response.status_code}"
                            )

                    except Exception:

                        error_message = response.text

                    st.error(
                        f"❌ Backend Error:\n{error_message}"
                    )
            except Exception as e:
                st.error(f"Chat error: {str(e)}")

# Clear Chat Button
if st.session_state.chat_history and st.button("🗑️ Clear Chat History", type="secondary"):
    st.session_state.chat_history = []
    st.rerun()


# ========================================================
# EMPTY STATE (Only shown when no result)
# ========================================================
if not st.session_state.result:
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:6rem 2rem; text-align:center;">
        <div style="font-size:6rem; margin-bottom:1.5rem;">🎬</div>
        <h2 style="font-family:'Syne',sans-serif; margin-bottom:0.8rem;">Ready to Analyse Any Video</h2>
        <p style="color:var(--text-muted); max-width:460px; font-size:1rem; line-height:1.7;">
            Paste a YouTube URL or upload an audio/video file to unlock AI-powered transcription, 
            summarization, and intelligent chat.
        </p>
    </div>
    """, unsafe_allow_html=True)