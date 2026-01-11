\[\!NOTE\]

# **🧠 Session Memory Consolidation**

## **From Granular Chaos to Coherent Memory**

### **Architecture in Two Steps**

**Step 1: Accumulation (Real-time)**

User → SecondMind → Response  
              ↓  
        MemoryAgent  
              ↓  
        history/interaction\_xxx.json (granular)

**Step 2: Consolidation (Delayed, after 4h of inactivity)**

history/\*.json (complete session)  
              ↓  
        RawPersistentProcessor  
              ↓  
        LLM analyzes the ENTIRE transcript  
              ↓  
        Coherent classification per message  
              ↓  
        persistent/\*.json (indexed summaries)

### **Detailed Workflow**

| Step | Action |
| :---- | :---- |
| 1 | Group files by session\_id. |
| 2 | Wait for timeout (4h without activity). |
| 3 | Construct the complete session transcript. |
| 4 | Send to LLM with a "coherence" instruction. |
| 5 | Parse the response block by block. |
| 6 | Save 1 JSON file per message (summary \+ intent). |
| 7 | Vectorize each summary individually. |
| 8 | Mark source files as processed. |

## **LLM Instruction (Excerpt)**

**CRITICAL OBJECTIVE: MAINTAINING INTENT**

Analyze the global context to determine the ACTUAL SUBJECT of the session.

Example: If the user says "Hello" and then "Fix this python script," the "Hello" must be classified as **SCRIPT/CODER** (as it is the goal of the session), not GENERAL/TALK.

The LLM perceives the **intent of the session**, rather than just the isolated message.

## **System Synergy**

Consolidation generates classified summaries  
              ↓  
        AutoDatasetBuilder (Training feed)  
              ↓  
        IntentDetector (Continuous improvement)

Consolidated summaries automatically feed the training dataset — creating a virtuous loop of continuous self-improvement.

## **Built-in Safeguards**

| Mechanism | Protection |
| :---- | :---- |
| **4h Timeout** | Prevents consolidation of an active session. |
| **Persistent State** | Processed files are marked to prevent double-processing. |
| **Stop Signal** | The LLM stops at \=== END OF SESSION \===. |
| **Preserved Source Files** | history/ remains intact; persistent/ holds the consolidation. |

## **Benefits**

### **1\. Intent Coherence**

A "Hello" in a debug session is classified as **DEBUG**, not **TALK**.

### **2\. Actionable Summaries**

The RAG searches through dense summaries instead of verbose exchanges.

### **3\. Training Feed**

Every consolidated session generates high-quality training data.

### **4\. Traceability**

A link is preserved between the summary (persistent/) and the source (history/).

## **Key Files**

* traitement\_brute\_persistante.py — Consolidation processor  
* agent\_Memoire.py — Initial save in history/  
* auto\_dataset\_builder.py — Training feed

*Maxime Gagné — Cognitive Architect — SecondMind*