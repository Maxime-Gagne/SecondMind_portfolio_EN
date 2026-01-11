\[\!NOTE\]

# **💻 Code RAG — Intelligent Search System**

Hybrid search (vector \+ symbolic) on the project's source code, featuring automated dependency expansion.

User Question  
       │  
       ▼  
  ┌─────────────────┐  
  │   AgentCode     │  ← Public API (provide\_context)  
  │   Orchestrator  │  
  └────────┬────────┘  
           │ Hybrid Search  
    ┌──────┴──────┐  
    ▼             ▼  
  FAISS       AST Graph  
 (Vectors)   (Dependencies)  
    └──────┬──────┘  
           ▼  
   Enriched Context → LLM

## **Components**

| File | Role | Input → Output |
| :---- | :---- | :---- |
| agent\_Code.py | RAG Orchestrator | Question → List\[CodeContext\] |
| moteur\_vecteur\_code.py | Indexer (AST scan \+ FAISS) | Project → Disk Index |
| code\_extractor\_manager.py | LLM Stream Analyzer | Raw Response → CodeArtifact |

## **Why not a naive RAG?**

A classic RAG slices code into fixed lines or tokens, then performs a similarity search. This results in truncated chunks without context, forcing the LLM to guess the logic.

### **1\. Enriched Semantic Chunks**

Each chunk is a **logical unit** (function, class, method) containing its own metadata:

CodeContext(  
    signature="def provide\_context(self, question: str, top\_k: int \= 8\) \-\> List\[Any\]",  
    docstring="Main method: receives a question, returns context...",  
    dependencies=\["search\_code", "\_generate\_partial\_skeleton"\],  
    variables\_used=\["self.arch", "self.vector\_engine"\],  
    return\_type="List\[Any\]",  
    key\_concepts=\["rag", "context", "search"\]  
)

The LLM receives everything it needs to understand **what the function does**, **what it calls**, and **what it manipulates**.

### **2\. Dependency Graph Expansion**

A search for "MemoryAgent" does not return just that module. The system:

* Parses imports to find outbound dependencies.  
* Traverses the call graph for inbound dependencies.  
* Expands across N depth levels.

**Result:** The LLM sees the **integration context**, not an isolated file.

### **3\. Filtered Dynamic Skeleton**

Instead of injecting 50 full files, the system generates a **targeted** tree view:

📦 MODULE: agent\_Memory (agentic/agent\_Memory.py)  
  └── class AgentMemory  
      └── def save\_memory  
      └── def search\_memories  
  └── def \_format\_context

The LLM perceives the project structure without being overwhelmed by irrelevant code.

### **4\. Scalable Architecture (JSONL Offsets)**

* **In RAM:** FAISS Index \+ offset table (byte position of each chunk).  
* **On Disk:** Full chunks in JSONL format.

Upon request, only the relevant chunks are read via seek(). This prevents the entire index from being loaded into memory.

## **Read/Write Separation**

| Mode | Component | Responsibility |
| :---- | :---- | :---- |
| **Read** | AgentCode | Queries the index, assembles the context. |
| **Write** | CodeVectorEngine | AST Scan, generates chunks, builds FAISS index. |

This separation allows for **hot-reloading**: the index can be rebuilt in the background without interrupting active queries.

*Maxime Gagné — Cognitive Architect — SecondMind*