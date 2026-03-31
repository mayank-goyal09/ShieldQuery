import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from engine import final_result, process_uploaded_pdf, warmup, DB_FAISS_PATH


# ──────────────────────────────────────────────────────────────
# Lifespan — pre-load heavy models at startup
# ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm embeddings + LLM so the first request is fast."""
    warmup()
    yield


app = FastAPI(
    title="Document Intelligence",
    description="Upload & analyze any document with AI",
    lifespan=lifespan,
)

# CORS (allow local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and process it into the vector store."""
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Only PDF files are supported. Please upload a .pdf document.",
            },
        )

    contents = await file.read()
    if len(contents) == 0:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "The uploaded file is empty."},
        )

    result = process_uploaded_pdf(contents, file.filename)
    return JSONResponse(content=result)


@app.post("/api/query")
async def query_documents(query: str = Form(...)):
    """Ask a question about the uploaded documents."""
    if not query or not query.strip():
        return JSONResponse(
            status_code=400,
            content={"success": False, "result": "Please enter a question.", "source": ""},
        )

    result = final_result(query.strip())
    return JSONResponse(content=result)


@app.get("/api/status")
async def system_status():
    """Check if documents are loaded and system is ready."""
    has_docs = os.path.exists(os.path.join(DB_FAISS_PATH, "index.faiss"))
    return JSONResponse(content={"documents_loaded": has_docs})


# ──────────────────────────────────────────────────────────────
# Serve static frontend (supports both 'static/' and 'docs/')
# ──────────────────────────────────────────────────────────────
STATIC_DIR = "static" if os.path.isdir("static") else "docs"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# ──────────────────────────────────────────────────────────────
# Run — port 7860 for Hugging Face Spaces
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=7860, reload=True)
