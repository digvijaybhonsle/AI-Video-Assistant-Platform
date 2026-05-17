from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form
)
from fastapi.middleware.cors import (
    CORSMiddleware
)
from fastapi.responses import JSONResponse

import tempfile
import shutil
import traceback
import os
import time

from pipeline import run_pipeline

# ============================================================
# APP
# ============================================================

app = FastAPI()

# ============================================================
# CONFIG
# ============================================================

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "Backend Running"
    }

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }

# ============================================================
# ANALYZE FILE
# ============================================================

@app.post("/analyze-file")
async def analyze_file(

    file: UploadFile = File(...),

    language: str = Form("english")
):

    temp_path = None

    try:

        print("\n" + "=" * 60)
        print("📥 Incoming Analysis Request")
        print("=" * 60)

        print(
            f"📄 Filename: {file.filename}"
        )

        print(
            f"🌍 Language: {language}"
        )

        # ====================================================
        # VALIDATE FILE
        # ====================================================

        contents = await file.read()

        file_size = len(contents)

        print(
            f"📦 File Size: "
            f"{file_size / (1024 * 1024):.2f} MB"
        )

        if file_size > MAX_FILE_SIZE:

            return JSONResponse(

                status_code=400,

                content={
                    "error":
                    "File exceeds 50MB limit."
                }
            )

        # Reset file pointer
        await file.seek(0)

        # ====================================================
        # CREATE TEMP FILE
        # ====================================================

        suffix = os.path.splitext(
            file.filename
        )[1]

        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=suffix

        ) as tmp:

            shutil.copyfileobj(
                file.file,
                tmp
            )

            temp_path = tmp.name

        print(
            f"📂 Temp file created:\n"
            f"{temp_path}"
        )

        # ====================================================
        # RUN PIPELINE
        # ====================================================

        start_time = time.time()

        result = run_pipeline(

            temp_path,

            language
        )

        duration = (
            time.time()
            - start_time
        )

        print(
            f"\n✅ Pipeline completed "
            f"in {duration:.1f}s"
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return JSONResponse(

            status_code=200,

            content=result
        )

    except Exception as e:

        print("\n❌ Backend Error")

        traceback.print_exc()

        return JSONResponse(

            status_code=500,

            content={

                "error":
                f"Backend processing failed: "
                f"{str(e)}"
            }
        )

    finally:

        # ====================================================
        # CLEANUP
        # ====================================================

        try:

            if (
                temp_path
                and
                os.path.exists(temp_path)
            ):

                os.remove(temp_path)

                print(
                    "🧹 Temp file cleaned"
                )

        except Exception as cleanup_error:

            print(
                f"⚠️ Cleanup failed:\n"
                f"{cleanup_error}"
            )

# ============================================================
# CHAT ENDPOINT
# ============================================================

from pydantic import BaseModel

from core.rag_engine import (

    build_rag_chain,

    ask_question,

    get_rag_chain
)

# ------------------------------------------------------------

class ChatRequest(BaseModel):

    transcript: str

    question: str

    session_id: str

# ------------------------------------------------------------

@app.post("/chat")

async def chat_with_meeting(

    request: ChatRequest
):

    try:

        print("\n" + "=" * 60)
        print("💬 Incoming Chat Request")
        print("=" * 60)

        transcript = (
            request.transcript
        )

        question = (
            request.question
        )

        session_id = (
            request.session_id
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if (
            not transcript
            or
            len(transcript.strip()) < 100
        ):

            return JSONResponse(

                status_code=400,

                content={

                    "error":
                    "Transcript is too short."
                }
            )

        if (
            not question
            or
            not question.strip()
        ):

            return JSONResponse(

                status_code=400,

                content={

                    "error":
                    "Question is empty."
                }
            )

        print(
            f"❓ Question:\n{question}"
        )

        # ====================================================
        # GET CACHED RAG
        # ====================================================

        start_time = time.time()

        rag_chain = get_rag_chain(
            session_id
        )

        # ====================================================
        # BUILD IF NOT EXISTS
        # ====================================================

        if rag_chain is None:

            print(
                "🧠 Creating new RAG chain..."
            )

            rag_chain = build_rag_chain(

                transcript,

                session_id
            )

        else:

            print(
                "⚡ Using cached RAG chain"
            )

        if not rag_chain:

            return JSONResponse(

                status_code=500,

                content={

                    "error":
                    "Failed to initialize RAG engine."
                }
            )

        # ====================================================
        # GENERATE ANSWER
        # ====================================================

        answer = ask_question(

            rag_chain,

            question
        )

        duration = (
            time.time()
            - start_time
        )

        print(
            f"✅ Chat response generated "
            f"in {duration:.1f}s"
        )

        return JSONResponse(

            status_code=200,

            content={

                "answer": answer
            }
        )

    except Exception as e:

        print("\n❌ Chat Error")

        traceback.print_exc()

        return JSONResponse(

            status_code=500,

            content={

                "error":
                f"Chat failed:\n{str(e)}"
            }
        )