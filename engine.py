import os
import logging
import tempfile
import time
import fitz  # PyMuPDF — layout-aware PDF parsing
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# Removed deprecated langchain.chains import
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ──────────────────────────────────────────────────────────────
# Setup
# ──────────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_FAISS_PATH = "vectorstores/db_faiss"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Friendly error messages — NEVER show raw tracebacks to users
# ──────────────────────────────────────────────────────────────
FRIENDLY_ERRORS = {
    "api_key": (
        "I'm currently unable to connect to my knowledge engine. "
        "Please ensure the API key is configured correctly and try again."
    ),
    "vector_store": (
        "I don't have any documents loaded yet. "
        "Please upload a document first so I can analyze it for you."
    ),
    "empty_document": (
        "The document you uploaded appears to be empty or contains only "
        "images/scanned content that I'm unable to read as text. "
        "Please try uploading a text-based PDF."
    ),
    "corrupt_file": (
        "I wasn't able to process this file. It may be corrupted, "
        "password-protected, or in a format I can't read. "
        "Please try uploading a different PDF document."
    ),
    "image_content": (
        "This document appears to contain mostly images or scanned pages. "
        "I work best with text-based PDFs. I'm unable to extract meaningful "
        "text from image-only documents at this time. "
        "Please try a text-based version if available."
    ),
    "general": (
        "I apologize, but I'm unable to process your request right now. "
        "Please try rephrasing your question or uploading a different document."
    ),
    "query_failed": (
        "I'm sorry, I encountered a difficulty while searching through "
        "the documents. Could you try rephrasing your question? "
        "If the issue persists, try re-uploading your document."
    ),
    "no_relevant_info": (
        "I couldn't find specific information related to your question "
        "in the uploaded documents. Try asking about a different topic "
        "covered in the document, or upload additional documents."
    ),
}


# ══════════════════════════════════════════════════════════════
# LATENCY OPTIMIZATION — Singletons & Caching
# ══════════════════════════════════════════════════════════════

class ModelCache:
    """
    Singleton cache for all heavy objects.
    Loaded ONCE at server startup, reused on every request.
    This is the #1 latency optimization — avoids reloading
    embeddings (~2-4s) and LLM client on every query.
    """
    _embeddings = None
    _llm = None
    _qa_chain = None
    _qa_chain_version = 0     # bump when vector store changes
    _vector_version = 0

    class CustomQAChain:
        def __init__(self, llm, retriever, prompt):
            self.llm = llm
            self.retriever = retriever
            self.prompt = prompt

        def __call__(self, inputs):
            query = inputs["query"]
            docs = self.retriever.invoke(query)
            context = "\n\n".join(d.page_content for d in docs)
            prompt_val = self.prompt.format(context=context, question=query)
            res = self.llm.invoke(prompt_val)
            # handle both string outputs and AIMessage outputs from models
            result_text = res.content if hasattr(res, "content") else str(res)
            return {"result": result_text, "source_documents": docs}

    @classmethod
    def get_embeddings(cls):
        if cls._embeddings is None:
            t = time.time()
            cls._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )
            logger.info(f"[CACHE] Embeddings loaded in {time.time()-t:.2f}s")
        return cls._embeddings

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            if not GROQ_API_KEY:
                raise EnvironmentError(FRIENDLY_ERRORS["api_key"])
            cls._llm = ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model_name="llama-3.3-70b-versatile",
                temperature=0.1,
            )
            logger.info("[CACHE] LLM client created")
        return cls._llm

    @classmethod
    def invalidate_chain(cls):
        """Call after uploading a new document so chain rebuilds."""
        cls._vector_version += 1
        cls._qa_chain = None
        logger.info("[CACHE] QA chain invalidated — will rebuild on next query")

    @classmethod
    def get_qa_chain(cls):
        if cls._qa_chain is not None and cls._qa_chain_version == cls._vector_version:
            return cls._qa_chain

        embeddings = cls.get_embeddings()
        faiss_index = os.path.join(DB_FAISS_PATH, "index.faiss")
        if not os.path.exists(faiss_index):
            raise FileNotFoundError(FRIENDLY_ERRORS["vector_store"])

        t = time.time()
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        llm = cls.get_llm()
        prompt = _build_prompt()

        cls._qa_chain = cls.CustomQAChain(
            llm=llm,
            retriever=db.as_retriever(search_kwargs={"k": 3}),
            prompt=prompt
        )
        cls._qa_chain_version = cls._vector_version
        logger.info(f"[CACHE] QA chain built in {time.time()-t:.2f}s")
        return cls._qa_chain


def warmup():
    """Pre-load heavy models at server startup."""
    logger.info("[WARMUP] Pre-loading embeddings model...")
    ModelCache.get_embeddings()
    try:
        ModelCache.get_llm()
    except Exception as e:
        logger.warning(f"[WARMUP] LLM pre-load skipped: {e}")
    # Pre-load QA chain if vector store already exists
    if os.path.exists(os.path.join(DB_FAISS_PATH, "index.faiss")):
        try:
            ModelCache.get_qa_chain()
        except Exception as e:
            logger.warning(f"[WARMUP] QA chain pre-load skipped: {e}")
    logger.info("[WARMUP] Complete ✓")


# ──────────────────────────────────────────────────────────────
# Prompt
# ──────────────────────────────────────────────────────────────
CUSTOM_PROMPT_TEMPLATE = """You are a professional Document Analyst. Use the following context 
extracted from uploaded documents to answer the user's question accurately.

The documents may include: resumes, assignments, contracts, NDAs, company policies, reports, memos, 
research papers, guidelines, or any other office/professional documents.

IMPORTANT — Understanding Document Structure Markers:
The context may contain structural markers like [TITLE], [HEADING], [BOLD], [SECTION].
These indicate formatting from the original document:
- [TITLE] = Large, prominent text (e.g., a person's name at the top of a resume)
- [HEADING] = Section header (e.g., "Experience", "Education", "Terms & Conditions")
- [BOLD] = Emphasized/important text (e.g., key terms, names, dates)
- [SECTION] = A labeled section of the document
Use these markers to understand the document's structure and answer questions accurately.
For example, if a resume has "[TITLE] John Smith", then "John Smith" is the candidate's name.

IMPORTANT — Understanding User Questions:
Users may write in informal, broken, or grammatically incorrect language. Always interpret their
intent generously and answer what they MEAN, not just what they literally typed. Examples:
- "name of person" or "who is this" → the person/candidate/author mentioned in the document
- "experience by person" or "how many year work" → total work experience and employment history
- "tell salary" or "money" → compensation, salary, pay details mentioned in the document
- "what he study" → educational qualifications or academic background
- "deadline" or "when finish" → due dates, deadlines, or timelines mentioned
- "rules" or "what not allowed" → restrictions, terms, prohibited actions

Rules you MUST follow:
1. If the answer is NOT in the provided context, say: "I don't have enough information in the 
   uploaded documents to answer this question."
2. NEVER fabricate information, numbers, dates, clauses, or any details not present in the context.
3. When referencing content, mention the section or topic if available.
4. Be professional, clear, and concise.
5. If the context seems garbled, incomplete, or incoherent (possibly from image-based content), 
   politely mention that the relevant section may not have been extracted properly.
6. If asked to help with an assignment, provide explanations and guidance based on the document content.

Context:
{context}

Question: {question}

Professional Answer:
"""

def _build_prompt():
    return PromptTemplate(
        template=CUSTOM_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )


# ──────────────────────────────────────────────────────────────
# Document Processing (upload flow)
# ──────────────────────────────────────────────────────────────
def _extract_structured_text(pdf_path: str) -> list[Document]:
    """
    Layout-aware PDF extraction using PyMuPDF.
    Detects bold text, large fonts, and injects structural markers:
      [TITLE]   — very large text (likely document title or person's name)
      [HEADING] — medium-large text (section headers)
      [BOLD]    — bold-weight text (emphasized content)
    This costs ZERO API tokens — all processing is local.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.warning(f"PyMuPDF open failed: {e}")
        raise

    pages = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

        # Collect all font sizes on this page to detect relative importance
        all_sizes = []
        for block in blocks:
            if block.get("type") != 0:  # skip image blocks
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["text"].strip():
                        all_sizes.append(span["size"])

        if not all_sizes:
            continue

        avg_size = sum(all_sizes) / len(all_sizes)
        max_size = max(all_sizes)

        # Thresholds: TITLE = very large, HEADING = moderately large
        title_threshold = avg_size * 1.6 if max_size > avg_size * 1.5 else max_size + 1
        heading_threshold = avg_size * 1.25

        structured_lines = []
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                line_text = ""
                line_size = 0
                is_bold = False

                for span in line.get("spans", []):
                    text = span["text"]
                    if not text.strip():
                        line_text += text
                        continue

                    size = span["size"]
                    flags = span.get("flags", 0)
                    bold = bool(flags & 2 ** 4)  # bit 4 = bold

                    line_size = max(line_size, size)
                    if bold:
                        is_bold = True
                    line_text += text

                line_text = line_text.strip()
                if not line_text:
                    continue

                # Apply structural markers
                if line_size >= title_threshold and len(line_text) < 80:
                    structured_lines.append(f"[TITLE] {line_text}")
                elif line_size >= heading_threshold and len(line_text) < 100:
                    structured_lines.append(f"[HEADING] {line_text}")
                elif is_bold and len(line_text) < 120:
                    structured_lines.append(f"[BOLD] {line_text}")
                else:
                    structured_lines.append(line_text)

        if structured_lines:
            page_content = "\n".join(structured_lines)
            pages.append(Document(
                page_content=page_content,
                metadata={"source": pdf_path, "page": page_num},
            ))

    doc.close()
    return pages


def process_uploaded_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Process uploaded PDF bytes:
      1. Save to temp
      2. Extract text via PyMuPDF (layout-aware, detects bold/headings)
      3. Validate content quality
      4. Chunk & embed into FAISS
      5. Return status + document insights
    """
    tmp_path = None
    try:
        # Save to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Load pages with structure-aware extraction
        try:
            pages = _extract_structured_text(tmp_path)
        except Exception as e:
            logger.warning(f"PDF load error: {e}")
            return _fail(FRIENDLY_ERRORS["corrupt_file"])

        if not pages:
            return _fail(FRIENDLY_ERRORS["empty_document"])

        # Check for meaningful text
        total_text = " ".join(p.page_content.strip() for p in pages)
        if len(total_text) < 50:
            return _fail(FRIENDLY_ERRORS["image_content"], page_count=len(pages))

        # Chunk
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(pages)
        if not chunks:
            return _fail(FRIENDLY_ERRORS["empty_document"], page_count=len(pages))

        # Embed & store
        embeddings = ModelCache.get_embeddings()
        db = FAISS.from_documents(chunks, embeddings)

        faiss_index = os.path.join(DB_FAISS_PATH, "index.faiss")
        if os.path.exists(faiss_index):
            try:
                existing = FAISS.load_local(
                    DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True
                )
                existing.merge_from(db)
                existing.save_local(DB_FAISS_PATH)
            except Exception:
                db.save_local(DB_FAISS_PATH)
        else:
            os.makedirs(DB_FAISS_PATH, exist_ok=True)
            db.save_local(DB_FAISS_PATH)

        # Invalidate cached chain so next query uses new docs
        ModelCache.invalidate_chain()

        # Quick insights
        insights = _extract_insights(chunks)

        return {
            "success": True,
            "message": f"'{filename}' processed successfully!",
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "insights": insights,
        }

    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {e}")
        return _fail(FRIENDLY_ERRORS["general"])
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _fail(message, page_count=0, chunk_count=0):
    return {
        "success": False,
        "message": message,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "insights": [],
    }


def _extract_insights(chunks, max_insights=6) -> list:
    """Use LLM to pull key topics, fallback to heuristics."""
    try:
        llm = ModelCache.get_llm()
        sample = "\n".join(c.page_content[:300] for c in chunks[:10])
        resp = llm.invoke(
            f"From the following document excerpts, list the 4-6 main topics or "
            f"key areas covered. Return ONLY a numbered list, nothing else.\n\n{sample}"
        )
        lines = resp.content.strip().split("\n")
        insights = []
        for line in lines:
            cleaned = line.strip().lstrip("0123456789.-) ").strip()
            if cleaned and len(cleaned) > 3:
                insights.append(cleaned)
        return insights[:max_insights]
    except Exception as e:
        logger.warning(f"LLM insight extraction failed: {e}")
        return _fallback_insights(chunks)


def _fallback_insights(chunks, max_insights=6) -> list:
    insights, seen = [], set()
    for chunk in chunks:
        for line in chunk.page_content.split("\n"):
            line = line.strip()
            if (10 < len(line) < 80 and line[0].isupper()
                    and line.lower() not in seen and not line.endswith(".")):
                seen.add(line.lower())
                insights.append(line)
            if len(insights) >= max_insights:
                return insights
    return insights


# ──────────────────────────────────────────────────────────────
# Query
# ──────────────────────────────────────────────────────────────
def final_result(query: str) -> dict:
    """
    Public API — ALL errors are caught and converted to friendly messages.
    Returns { success, result, source, response_time_ms }
    """
    t = time.time()
    try:
        qa = ModelCache.get_qa_chain()
        response = qa({"query": query})

        result_text = response.get("result", "").strip()
        sources = response.get("source_documents", [])

        if not result_text or len(result_text) < 5:
            result_text = FRIENDLY_ERRORS["no_relevant_info"]

        source_name = ""
        try:
            if sources:
                raw = sources[0].metadata.get("source", "")
                source_name = os.path.basename(raw) if raw else ""
        except Exception:
            pass

        return {
            "success": True,
            "result": result_text,
            "source": source_name,
            "response_time_ms": int((time.time() - t) * 1000),
        }

    except FileNotFoundError:
        return {"success": False, "result": FRIENDLY_ERRORS["vector_store"],
                "source": "", "response_time_ms": int((time.time()-t)*1000)}
    except EnvironmentError as e:
        return {"success": False, "result": str(e),
                "source": "", "response_time_ms": int((time.time()-t)*1000)}
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {"success": False, "result": FRIENDLY_ERRORS["query_failed"],
                "source": "", "response_time_ms": int((time.time()-t)*1000)}