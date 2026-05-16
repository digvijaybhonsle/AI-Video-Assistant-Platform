# 🎥 AI Video Assistant Platform

**Multilingual AI-Powered Video Understanding & Conversational RAG Assistant**

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://langchain.com)
[![Chroma](https://img.shields.io/badge/ChromaDB-4B0082?logo=chroma&logoColor=white)](https://trychroma.com)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Transform any video into an intelligent, interactive knowledge base.**  
Process YouTube videos or local uploads, generate accurate transcripts (with strong Hindi/Hinglish support), create smart summaries & notes, and chat naturally with the content using Retrieval-Augmented Generation (RAG).

Built with production-grade tools and a clean, modular architecture.

---

## ✨ Features

- **📹 YouTube & Local Video Support** — Process videos directly from YouTube links or uploaded files
- **🎙️ High-Quality Transcription** — Powered by OpenAI Whisper with robust multilingual capabilities
- **🇮🇳 Hindi/Hinglish Excellence** — Enhanced speech-to-text using Sarvam AI (Saaras model)
- **📝 Intelligent Summarization** — AI-generated concise summaries and structured bullet-point notes
- **❓ Key Insights Extraction** — Automatically identify important questions and topics
- **💬 Conversational RAG Chat** — Ask anything about the video content with contextual, accurate answers
- **🔍 Fast Vector Search** — Powered by ChromaDB + Sentence Transformers embeddings
- **⚡ Modern UI** — Beautiful, intuitive interface built with Streamlit
- **🏗️ Clean Modular Architecture** — Production-ready, maintainable codebase
- **🔄 End-to-End Pipeline** — Audio extraction → Transcription → Chunking → Embedding → RAG

---

## 🏗️ Architecture Flow

flowchart TD
    A[User Input<br/>YouTube URL or Video Upload] --> B[Audio Extraction<br/>yt-dlp + FFmpeg]
    B --> C[Transcription<br/>Whisper + Sarvam AI]
    C --> D[Text Chunking & Preprocessing]
    D --> E[Embedding Generation<br/>Sentence Transformers]
    E --> F[Vector Storage<br/>ChromaDB]
    F --> G[RAG Pipeline<br/>Retrieval + Context]
    G --> H[LLM Response<br/>Mistral AI]
    H --> I[Interactive Chat & Insights]

---

## 🛠️ Tech Stack

| Category              | Technology                          | Purpose |
|-----------------------|-------------------------------------|--------|
| **Backend**           | FastAPI + Python                    | API layer & orchestration |
| **Frontend**          | Streamlit                           | Interactive UI |
| **AI Framework**      | LangChain                           | RAG pipelines & agents |
| **Speech-to-Text**    | Whisper + Sarvam AI (Saaras)        | Transcription (Multilingual) |
| **LLM**               | Mistral AI                          | Summarization & Chat |
| **Embeddings**        | Sentence Transformers               | High-quality vector embeddings |
| **Vector Database**   | ChromaDB                            | Persistent vector storage |
| **Media Processing**  | yt-dlp + FFmpeg                     | Video/Audio handling |
| **Deployment**        | Streamlit Cloud / Render / Hugging Face Spaces | Easy hosting |

---

## 📁 Project Structure

```bash
AI-Video-Assistant-Platform/
├── app.py                      # Main Streamlit application
├── test.py                     # testing of features
├── requirements.txt
├── README.md
├── .env.example
├── .env                        # (gitignore'd)
├── core/
│   ├── extractor.py
│   ├── rag_engine.py                  # RAG pipeline
│   ├── transcriber.py
│   ├── summarizer.py
│   └── vector_store.py
├── utils/
│   ├── audio_processor.py
├── uploads/                    # Temporary video storage
├── downloads/                  # Processed outputs
├── chunks/                     # Text chunks
├── chroma_db/                  # Persistent vector database
└── docs/                       # Additional documentation
```

**Key Folders:**
- `core/` — Core business logic and AI pipelines
- `utils/` — Reusable helper functions
- `chroma_db/` — Persistent vector store (auto-created)
- `uploads/` — Temporary storage for processing

---

## 🚀 Installation Guide

### Prerequisites
- Python 3.10+
- FFmpeg installed on your system
- Git

### Steps (Windows)

```powershell
# 1. Clone the repository
git clone https://github.com/yourusername/ai-video-assistant-platform.git
cd ai-video-assistant-platform

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install FFmpeg (recommended: use winget or chocolatey)
# winget install Gyan.FFmpeg

# 6. Copy environment variables
copy .env.example .env
```

**Edit `.env`** with your API keys (see below).

### Run the Application

```powershell
streamlit run app.py
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# AI API Keys
MISTRAL_API_KEY=your_mistral_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here

# Whisper Settings
WHISPER_MODEL=small

# Sarvam AI Settings
SARVAM_STT_MODEL=saaras:v2.5

# Optional
CHROMA_PERSIST_DIR=./chroma_db
```

---

## 📖 Usage Guide

1. **Launch the app** → `streamlit run app.py`
2. **Choose input method**:
   - Paste a YouTube URL, or
   - Upload a local video file
3. **Process the video** — Click "Process Video"
4. **Explore Results**:
   - View full transcript
   - Read AI-generated summary & notes
   - Extracted key questions
5. **Chat with the Video** — Ask any question in the conversational interface

The system automatically saves embeddings for future sessions.

---

## 📸 Screenshots

### Home Page & Video Input
![Home Page](https://via.placeholder.com/800x450/1a1a2e/ffffff?text=Home+Page+with+YouTube+Input)

### Transcript & Summary View
![Transcript & Summary](https://via.placeholder.com/800x450/16213e/ffffff?text=Transcript+%26+AI+Summary)

### Interactive RAG Chat
![AI Chat Interface](https://via.placeholder.com/800x450/0f3460/ffffff?text=Conversational+RAG+Chat)

### Insights Dashboard
![Insights](https://via.placeholder.com/800x450/533483/ffffff?text=Key+Insights+%26+Notes)

*(Replace placeholder images with actual screenshots after deployment)*

---

## 🔄 RAG Pipeline Explained

The system uses a **Retrieval-Augmented Generation** approach for accurate, context-aware responses:

1. **Chunking** — Long transcripts are split into meaningful overlapping segments
2. **Embeddings** — Each chunk is converted into high-dimensional vectors using Sentence Transformers
3. **Vector Database** — Embeddings are stored in ChromaDB for fast similarity search
4. **Retrieval** — User queries are embedded and matched against stored vectors
5. **Generation** — Retrieved context + query is sent to Mistral AI for grounded, natural responses

This ensures answers are **faithful to the video content** and reduces hallucinations.

---

## 🚀 Future Enhancements

- **Multi-Agent Workflow** — Specialized agents for different analysis tasks
- **Timestamp-based QA** — Jump directly to video segments
- **PDF/Report Export** — Beautiful downloadable summaries
- **Advanced Multilingual Translation**
- **User Authentication & History**
- **Analytics Dashboard** — Usage insights and video library
- **Cloud Deployment** with Docker + FastAPI backend separation
- **Real-time processing** optimizations

---

## ☁️ Deployment

### Streamlit Community Cloud
1. Fork the repo
2. Connect to Streamlit Cloud
3. Add secrets in the dashboard

### Render.com / Hugging Face Spaces
- Use the provided `requirements.txt`
- Set environment variables in the platform dashboard
- Recommended: Separate FastAPI backend for production scale

---

## 💼 Resume Value

This project demonstrates **strong expertise** in:

- **Generative AI & RAG** — End-to-end implementation of production RAG systems
- **Multimodal AI** — Video → Audio → Text pipelines
- **Multilingual NLP** — Handling English + Hindi/Hinglish content
- **Full-Stack AI Development** — FastAPI + Streamlit + Vector DBs
- **Production Engineering** — Clean architecture, modular design, and deployment readiness

**Ideal for roles in:**
- AI/ML Engineer
- Generative AI Engineer
- NLP Engineer
- Full-Stack AI Developer
- MLOps / LLM Engineer

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Digvijay Bhonsle**  
*BE Computer Science Engineering Student*  
**AI/ML & Gen-AI Developer**

- **GitHub**: [@digvijaybhonsle](https://github.com/digvijaybhonsle)
- **LinkedIn**: [Digvijay Bhonsle](https://www.linkedin.com/in/digvijay-bhonsle/)

---

**⭐ If you found this project helpful, please star the repository!**

Built with ❤️ for the AI community.

---