<div align="center">

# 🔍 DocIntel — Private-First Document RAG

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Outfit&weight=700&size=32&duration=3500&pause=1000&color=6C5CE7&center=true&vCenter=true&multiline=true&width=900&height=100&lines=Private-First+Retrieval-Augmented+Generation+🔒;Contextually+Grounded+AI+Intelligence;FAISS+Vector+Search+%7C+Llama-3.3-70B+%7C+PyMuPDF)](https://git.io/typing-svg)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-VectorDB-00599C?style=for-the-badge&logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

<br/>

[![🚀 Demo Experience](https://img.shields.io/badge/🚀_DEMO_EXPERIENCE-DocIntel-6c5ce7?style=for-the-badge&labelColor=0f1117)](https://github.com/mayank-goyal09/project-55-private-hr-rag)
[![Data Sovereignty](https://img.shields.io/badge/🛡️_DATA_SOVEREIGNTY-100%25-success?style=for-the-badge)](https://github.com/mayank-goyal09/project-55-private-hr-rag)

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6c5ce7,100:a29bfe&height=200&section=header&text=Secure%20Document%20Intelligence&fontSize=70&animation=fadeIn&fontColor=ffffff" width="1000" alt="DocIntel Banner"/>

<br/>

### 🧠 **Bridging the gap between static local documentation and generative AI intelligence** 

### **Knowledge-Vault Architecture → Hallucination-Free Responses** 🛡️

</div>

---

## ⚡ **PROJECT AT A GLANCE**

<table>
<tr>
<td width="55%">

### 🎯 **What We Have Done**

DocIntel is a high-performance **Private-First Retrieval-Augmented Generation (RAG)** system designed for organizations that demand 100% data sovereignty. It transforms sensitive internal datasets—contracts, NDAs, policies, and reports—into searchable, interactive knowledge repositories.

**Key Technical Achievements:**
- 🛡️ **No-Leak Architecture**: Local embeddings ensure sensitive data never touches the cloud during vectorspace creation.
- 📐 **Layout-Aware Parsing**: Custom PyMuPDF engine that detects formatting (Titles, Headings, Bold) to inject structural markers into the knowledge graph.
- ⚡ **Lightning Fast**: Blazing-fast inference using **Groq API** with Llama-3.3-70B.
- 🎨 **Premium UI**: A glassmorphism-inspired dark interface with real-time insight generation.

</td>
<td width="45%">

### ✨ **System Highlights**

| Feature | Technology |
|---------|------------|
| 🧠 **LLM Engine** | Llama-3.3-70B (Groq) |
| 🗄️ **Vector DB** | FAISS |
| 🔢 **Embeddings** | HuggingFace (MiniLM-L6) |
| 📄 **PDF Parser** | PyMuPDF (fitz) |
| ⚡ **Latency** | <500ms Search |
| 🎨 **Frontend** | Streamlit + Custom CSS |
| 🛡️ **Privacy** | Local Vector Storage |
| 🔍 **Insights** | Automatic Topic Detection |

</td>
</tr>
</table>

---

## 🛠️ **TECHNOLOGY STACK**

<div align="center">

![Tech Stack](https://skillicons.dev/icons?i=python,fastapi,github,vscode,docker)

</div>

| **Category** | **Technologies** | **Role in Ecosystem** |
|:------------:|:-----------------|:------------|
| 🐍 **Core Engine** | Python 3.10+ | Backbone of the RAG pipeline |
| 🧠 **LLM Orchestration** | LangChain / Groq | Managing LLM completions & retrieval logic |
| 🗄️ **Vector Store** | FAISS | High-speed semantic similarity search |
| 🔢 **Embedding Model** | all-MiniLM-L6-v2 | Locally converting text to high-dimensional vectors |
| 📄 **Structured Parsing** | PyMuPDF (fitz) | Layout-aware text extraction with formatting detection |
| 🎨 **UI Engineering** | Streamlit / FastAPI | Delivering a premium dashboard and API layer |
| 🚀 **Performance** | Singleton Cache | Optimizing model load & response latency |

---

## 🔬 **THE KNOWLEDGE VAULT WORKFLOW**

```mermaid
graph TD
    A[📂 Upload PDF] --> B[📄 Layout-Aware Extraction]
    B --> C{🔍 Formatting Check}
    C -->|Title/Heading| D[🏷️ Structural Marker Injection]
    C -->|Paragraph| E[📝 Raw Text Extraction]
    D --> F[🧩 Recursive Chunking]
    E --> F
    F --> G[🔢 Local Embeddings]
    G --> H[📦 FAISS Vector Store]
    H --> I[🛡️ Knowledge Vault]
    
    J[👤 User Query] --> K[🔎 Semantic Search]
    I --> K
    K --> L[🧠 LLM Context Injection]
    L --> M[✅ Hallucination-Free Answer]
    
    style I fill:#6c5ce7,color:#fff,stroke:#a29bfe,stroke-width:2px
    style M fill:#00cec9,color:#000,stroke:#fff,stroke-width:2px
```

---
