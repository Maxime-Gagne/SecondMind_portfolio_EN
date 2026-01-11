# **📚 LiveDocs RAG — "Real-Time" Technical Knowledge Base**

Specialized RAG micro-service for technical documentation (Port 5000). Enables local AI agents to write up-to-date code (Pydantic V2, TRL, PEFT) by bypassing their knowledge cutoff date.

## **🎯 The Problem**

Local Large Language Models (LLMs) such as Llama-3 or Qwen are excellent at reasoning, but their knowledge of Python libraries evolves more slowly than the code itself.

| Aspect | Description |
| :---- | :---- |
| **Symptom** | The AI generates obsolete code (e.g., Pydantic V1's @validator instead of V2's @field\_validator) |
| **Cause** | The Knowledge Cutoff (training end date) precedes the latest major framework updates |
| **Consequence** | Syntactic hallucinations and code that crashes at execution |

## **💡 The Solution: LiveDocs RAG**

Instead of re-training the model (expensive and slow), I designed a **living external memory** system. It is an autonomous micro-service that monitors, scrapes, vectorizes, and serves the most recent official documentation.

### **Micro-Service Architecture**

The system is decoupled from the main brain (SecondMind) to ensure stability and avoid dependency conflicts.

┌─────────────────────────────────────────────────────────────────┐  
│                    External World                               │  
│               PyPI / HuggingFace Docs                           │  
└──────────────────────────┬──────────────────────────────────────┘  
                           │  
                           ▼  
┌─────────────────────────────────────────────────────────────────┐  
│               Port 5000 \- LiveDocs Service                      │  
│                                                                 │  
│   Auto Scraper ──► Semantic Chunker ──► SBERT Embedder          │  
│                                                   │             │  
│                                                   ▼             │  
│                                            ┌──────────────┐     │  
│                     Flask API ◄───────────►│ FAISS Index  │     │  
│                         │                  └──────────────┘     │  
└─────────────────────────┼───────────────────────────────────────┘  
                          │ HTTP POST  
                          ▼  
┌─────────────────────────────────────────────────────────────────┐  
│               Port 3000 \- Main AI Agent                         │  
│                                                                 │  
│                        Code Agent                               │  
│                    (Up-to-date Context)                         │  
└─────────────────────────────────────────────────────────────────┘

## **⚙️ Technical Stack**

| Component | Technology |
| :---- | :---- |
| **Vector Search Engine** | FAISS (Facebook AI Similarity Search) — latency \< 50ms |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 (384 dimensions, optimized for local CPU/GPU) |
| **Backend** | Flask (Lightweight REST API) |
| **Scraping** | BeautifulSoup4 \+ Version detection logic |
| **Infrastructure** | Local (RTX 3090), runs in parallel with the main LLM |

## **🔄 Data Pipeline**

### **1\. Automated Ingestion (doc\_scraper\_phase2.py)**

The system does more than just read text files; it seeks the truth at the source:

* Detection of installed packages via requirements.txt.  
* Targeted scraping of official documentation (e.g., HuggingFace TRL, Pydantic).  
* **Intelligent Chunking**: Splitting by logical sections (500 tokens) with overlap to preserve context.

### **2\. Semantic Indexing**

* Each documentation snippet is converted into a vector.  
* **Rich Metadata**: Each vector contains the exact source (URL), package name, and version.  
* **Incremental Updates**: Only modified packages are re-indexed.

### **3\. Querying (Inference)**

When Code Agent (on port 3000\) detects a technical intent (e.g., "Code an SFTTrainer"), it queries LiveDocs:

\# Internal call example by the Code Agent  
response \= requests.post("http://localhost:5000/api/search", json={  
    "query": "SFTTrainer configuration QLoRA",  
    "k": 3  
})  
\# Result: Immediate injection of the SFTConfig class (TRL v0.8+) into the prompt

## **🚀 Key Features**

| Feature | Description |
| :---- | :---- |
| ✅ **Anti-Obsolescence** | Forces the LLM to use 2024/2025 syntaxes |
| ✅ **Auto-Healing** | If a library changes, simply re-run the scraping script; no need to touch the LLM |
| ✅ **Performance** | Decoupled search, does not impact GPU VRAM dedicated to inference |
| ✅ **Debug Interface** | Dedicated web UI on http://localhost:5000 to verify what the AI "knows" |

## **📊 Impact on the SecondMind Project**

**Before LiveDocs RAG integration:**

* The agent generated deprecated Pydantic V1 code **80% of the time** on complex structures.

**After integration:**

* The agent generates valid Pydantic V2 code (model\_validator, field\_validator) **95% of the time**, as it has the exact example directly in its context.

## **🛠️ Installation & Startup**

\# 1\. Install dependencies  
pip install \-r requirements\_docs.txt

\# 2\. Launch the server (via the unified launcher)  
START\_SECONDMIND.bat  
\# \-\> Launches the Doc server on port 5000  
\# \-\> Launches the Main Brain on port 3000

## **Data-Centric AI Approach**

This module demonstrates a **Data-Centric AI** approach: rather than asking the model to learn everything by heart, we provide it with the tools to verify its knowledge in real-time.

*Maxime Gagné — Cognitive Architect — SecondMind*