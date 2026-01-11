# **RAG Memory — Multi-Level Persistent Memory System**

Components

| File | Role | Input → Output |
| :---- | :---- | :---- |
| agent\_Recherche.py | Tri-engine search | Query → SearchResult |
| agent\_Contexte.py | Intelligent sorting \+ scoring | Search → ContextResult |
| recherche\_memoire.py | Guided reading (focus) | Files → Structured report |
| agent\_Memoire.py | Raw capture \+ memorization | Interaction → Disk |
| traitement\_brute\_persistante.py | Deferred LLM consolidation | Session → Vectorized summaries |
| moteur\_vecteur.py | Persistent FAISS index | Text → Embedding |

## **Why not a classic RAG?**

### **1\. Tri-Engine Search (3 levels of precision)**

A classic RAG performs a single vector search. SecondMind combines:

| Engine | Speed | Usage |
| :---- | :---- | :---- |
| **Everything** (es.exe) | \~10ms | Pre-filtering by filename |
| **Whoosh** | \~50ms | Full-text search with semantic tags |
| **FAISS** | \~100ms | Vector similarity for meaning |

**Measured Result: 0.08 seconds** for a complete search (tri-engine \+ scoring \+ context assembly). Full-text precision \+ semantic understanding, without sacrificing speed.

### **2\. Focus-Driven Reading**

The RechercheMemoireTool does not dump raw content. It generates a **local system prompt** for each file:

\#\#\# 📄 FILE: traitement.py  
🎯 \*\*READING DIRECTIVE\*\*: "Check the while loop on line 45"

⚠️ Instructions: Analyze the code below ONLY   
   through the lens of the directive above.

The LLM knows **what to look for** before even reading. Fewer tokens wasted, more precise answers.

### **3\. Multi-Type Memory (10+ categories)**

Each type of memory has its own behavior:

| Type | Priority | Content |
| :---- | :---- | :---- |
| reflexive | 🔴 High | Rules learned through introspection |
| regles | 🔴 High | System directives (truth, governance) |
| feedback | 🟠 Medium | User corrections (+1/-1) |
| historique | 🟡 Session | Recent exchanges (continuity) |
| persistante | 🟢 Long-term | Summaries consolidated by LLM |
| connaissances | 🟢 Long-term | Technical documentation |

The AgentContexte automatically sorts and prioritizes based on the request type.

### **4\. Deferred Consolidation by Session**

Raw interactions are not vectorized immediately. The ProcesseurBrutePersistante:

1. **Groups** messages by session (via session\_id)  
2. **Waits** for a timeout (4h) to ensure full context  
3. **Sends the entire transcript** to the LLM for global analysis  
4. **Generates micro-summaries** that are consistent with each other  
5. **Vectorizes each summary** individually

Advantage: The LLM sees the complete conversation, not isolated fragments. Summaries capture **intentions** and **resolutions**, not just words.

### **5\. Hybrid Indexing (Whoosh \+ FAISS)**

Every memory is indexed twice:

\# Whoosh: Explicit tags for fast filtering  
self.agent\_recherche.update\_index(  
    contenu=summary,  
    type\_memoire="persistante",  
    sujet="CODE",  
    action="DEBUG",  
    categorie="TECHNIQUE"  
)

\# FAISS: Embedding for semantic search  
self.moteur\_vectoriel.ajouter\_fragment(summary, meta={...})

One can filter by tags (fast) then refine by similarity (precise).

## **Full Data Flow**

\[User types a message\]  
         │  
         ▼  
    SearchAgent  
         │  
    ┌────┴────┬──────────┐  
    ▼         ▼          ▼  
Everything  Whoosh     FAISS  
    │         │          │  
    └────┬────┴──────────┘  
         │  
         ▼ (Raw memories)  
    ContextAgent  
         │  
    ┌────┼────┬────────┐  
    ▼    ▼    ▼        ▼  
 Rules Docs Memory History  
    │    │    │        │  
    └────┴────┴────────┘  
         │  
         ▼ (Sorted ContextResult)  
       LLM  
         │  
         ▼  
    MemoryAgent ──► Raw save (JSONL)  
         │  
         ▼ (4h later)  
    PersistentRawProcessor  
         │  
         ▼  
    Vectorized Summaries ──► Ready for the next RAG

## **Key Architecture**

**Read/Write Separation**: SearchAgent reads, MemoryAgent writes. No conflicts, no locks.

**Auditor Validation**: Every output passes through auditor.valider\_format\_sortie() to guarantee data contracts.

**Hot-Reload**: The Whoosh and FAISS indexes can be updated without restarting the system.