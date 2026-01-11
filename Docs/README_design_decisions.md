## **Design Decisions & Best Practices**

My goal was not just to "run an LLM," but to build a **governable AI architecture**. Below are the primary design choices, all visible in the code.

### **Fail-Fast System**

In architecture, context dictates the decision. While a consumer product (B2C) must prioritize high availability (degrading service rather than crashing), SecondMind prioritizes data integrity.

In this personal R\&D context, I have enforced a strict Fail-Fast rule: I consider a "silent error" (masked by a soft fallback) to be infinitely more dangerous than an explicit crash. If a critical rule is missing, the system must stop, not improvise.

### **1\. Single Source of Truth (AuditorBase \+ config\_paths)**

Goal: zero hardcoded paths, zero scattered configurations.

* config\_paths.py defines once and for all:  
  * ROOT\_DIR, AGENTIQUE\_DIR, MEMOIRE\_DIR, DATA\_TRAINING\_CENTER\_DIR, etc.  
* AuditorBase provides paths by **agent logical name** via get\_path("..."):  
  * e.g., for memory:  
    * agent\_memoire uses self.auditor.get\_path("brute"), ("historique"), ("persistante"), ("reflexive"), etc.  
  * for engines:  
    * MoteurLLM reads config\_moteurllm.yaml via a standard path defined in StandardsAgents.moteurllm.  
  * for Code RAG:  
    * AgentRechercheCode reads memoire/code/... and config\_recherche\_code.yaml via AuditorBase.

**Impact:**

* **Portability:** to move the project from D:/... to another environment, I only change the .project\_root marker.  
* **Auditability:** AgentAuditor and GardienProjet can validate that everything correctly passes through the Auditor (no rogue paths).

### **3\. Strict Interface Contracts (contrats\_interface.py)**

All inter-agent data passes through dataclasses:

* **Intentions**: ResultatIntention(prompt, sujet, action, categorie).  
* **Search & Context**: ResultatRecherche(souvenirs\_bruts, ...), ResultatContexte(...).  
* **Judgment**: ResultatJuge(valide, score, raison, details).  
* **Complete Pipeline**: StandardPrompt contains the entire context before the LLM call.  
* **Persistence**: Interaction \+ MetadataFichier for each saved entry.

The AgentAuditor verifies:

* that instantiations of these dataclasses use **only** the defined fields,  
* that no one crafts dict objects that "imitate" these contracts (shadow detection).

**Result:**

* All junctions are typed (RAG, context, LLM, memory, judge).  
* No "magic JSON data" circulating; everything is standardized and verifiable.

### **4\. Clear and Independent Multi-Agent Architecture**

Principle: **AgentSemi is the only one that imports other agents**.

* AgentSemi:  
  * creates AgentMemoire, AgentRecherche, AgentContexte, AgentParole, AgentJuge, AgentReflexor, IntentionDetector, RechercheCodeExtractor, RechercheCodeAdapter, ProcesseurBrutePersistante, MoteurLLM, MoteurMiniLLM, MoteurVectoriel.  
  * explicitly injects dependencies via constructors.  
* Specialized agents do not import each other:  
  * AgentContexte does not perform import AgentMemoire.  
  * It receives agent\_recherche / agent\_juge as parameters provided by AgentSemi.

**Advantages:**

* **Low Coupling:** each agent remains focused on its specific mission (search, context, speech, memory, judge, reflexive…).  
* **Clarity:** the penser() pipeline is **the** map of the system's data flows.

### **5\. LLM Tri-Model (main \+ mini \+ vector)**

I do not use "an LLM," but rather:

1. **Main LLM (MoteurLLM)** for rich generation:  
   * Local Qwen / Mistral (GGUF via llama.cpp or Transformers/LoRA).  
   * Configurable via config\_moteurllm.yaml:  
     * context window, n\_gpu\_layers, quantization, temperature, stop\_tokens, etc.  
2. **Mini LLM (MoteurMiniLLM)** for fast tasks:  
   * Phi-3 or lightweight model for:  
     * IntentionDetector,  
     * AgentJuge,  
     * small reflexive tasks.  
   * Configured via config\_moteur\_mini\_llm.yaml.  
3. **Vector Engine (MoteurVectoriel)**:  
   * SentenceTransformers \+ FAISS for persistent semantic memory.  
   * Each add\_fragment(texte, meta) saves:  
     * the embedding in FAISS,  
     * the metadata (including contenu) in a JSON file.

**What this demonstrates:**

* Mastery of **memory / VRAM management** (GGUF, quantization, context window).  
* Ability to clearly separate:  
  * generation (expensive),  
  * classification/control (fast),  
  * vector memory (long-term).

### **6\. Governance, Audit, and Observability**

Multiple layers work together:

* **GardienProjet**:  
  * monitors critical files (agent\_Semi.py, agent\_Juge.py, agent\_Parole.py, contrats\_interface.py),  
  * triggers AgentSemi's thought process via an internal API (/internal/think),  
  * periodically synchronizes statistics to the backend (/api/stats/sync).  
* **AgentAuditor**:  
  * scans agent code (inheritance from AgentBase, usage of self.logger, adherence to contracts),  
  * audits LLM ↔ memory flows via dashboard\_stats written in YAML files,  
  * generates a project map (mapping\_structure/project\_map.json).  
* **AgentReflexor**:  
  * triggers on the \!\!\! signal,  
  * searches the vector memory for similar cases,  
  * calls the LLM to analyze the root cause and generate a "behavioral correction,"  
  * logs the reflexive trace in memoire/reflexive/journal\_de\_doute\_reflexif.md \+ FAISS \+ Whoosh.  
* **Prompt Viewer**:  
  * shows the final prompt (ChatML) seen by the LLM in real-time (/api/last\_prompt).  
* **Benchmark Lab**:  
  * precisely measures performance (tokens/s, TTFT, inter-token latency, VRAM),  
  * for the main LLM, the mini LLM, and the entire pipeline.

Result:  
My system is instrumented to monitor itself, correct itself, and audit itself, not just to generate text.

### **7\. Integrated Code RAG in the Project Lifecycle**

Code RAG is a first-class citizen:

* **RechercheCodeExtractor**:  
  * intercepts LLM responses, extracts code blocks, and produces:  
    * physical files (memoire/code/code\_extraits/...),  
    * JSONL base for FAISS (code\_chunks.jsonl).  
* **AgentRechercheCode**:  
  * reads the architecture (code\_architecture.json file),  
  * loads FAISS and chunk-related metadata,  
  * enables searching by similarity and dependency graph (chercher\_code).  
* **RechercheCodeAdapter**:  
  * provides AgentSemi with compressed context based on:  
    * modules\_concernes,  
    * context (code chunks),  
    * summary.  
  * AgentSemi transforms this context into a Souvenir(type="code\_source") and injects it with high priority into the prompt.

Impact:  
The LLM does not "guess" the project code; it actually reads the files, the architecture, and the generated artifacts.

### **8\. Atomic Persistence**

To avoid data corruption (truncated JSON files) in the event of a sudden shutdown, AgentMemoire forces physical writing via flush() and os.fsync() for every critical interaction.

By combining these decisions (SSOT, META\_agent, typed contracts, tri-model, multi-layer governance, Code RAG), I have built an AI system that is:

* **local** (no cloud dependency),  
* **auditable** (standards and logs throughout),  
* **composable** (multi-agent, strict contracts),  
* **product-oriented** (Hub interfaces, IDE, Prompt Viewer, Benchmark),  
* and ready to evolve (adding specialized agents, new memories, new LLM profiles).