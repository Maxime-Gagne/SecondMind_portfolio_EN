\[\!NOTE\]

# **🧠 SecondMind Interfaces & Cockpit**

To fully exploit SecondMind's multi-agent architecture, I built a comprehensive cockpit around the AgentSemi core.  
Each interface is connected to the same backend (interface\_backend\_hermes.py) and plays a specific role within the cognitive system:

* **Interaction & Training Hub** (formation\_secondmind.html)  
* **Cognitive IDE** (semicode\_ide.html)  
* **Prompt Viewer** (Real-time prompt debugging) (prompt\_viewer.html)  
* **Dual-LLM Benchmark Lab** (benchmark\_dual\_llm.html)

This product layer highlights five of my key strengths: system architecture, governance, memory/RAG, observability, and LLM optimization.

### **1\. Interaction & Training Hub — formation\_secondmind.html**

**Role:** Main user interface, designed for pedagogy and experimentation.

* **Chat connected to the full cognitive pipeline** \> \* Sends requests to /command with:  
  * prompt (user question),  
  * search\_mode (auto / web / memory / manual\_context),  
  * manual\_context (content of activated slots).  
  * On the backend, AgentSemi.think(...) orchestrates:  
    * IntentDetector → IntentResult  
    * AgentSearch.hybrid\_search(...) → SearchResult  
    * AgentContext.get\_intelligent\_context(...) → ContextResult  
    * AgentSpeech.build\_llm\_prompt(...) → ChatML prompt  
    * LLMEngine.generate\_stream(...) → Streamed generation.  
* **Live feedback for reinforcement** \> \* "Reinforcement Feedback" field → /memory with { "feedback": "..." }.  
  * The backend:  
    * Classifies feedback via IntentDetector.  
    * Saves to memory/reflexive/feedback/... via AgentMemory.save\_memory(...).  
    * Special \+1 option: validates the latest code version via VersionTracker and last\_code\_hash.  
* **User-steerable manual context** \> \* 5 slots with token estimation, ON/OFF switches, and local saving.  
  * The frontend concatenates active slots into manual\_context and sends them to /command.  
  * Within AgentSemi, if raw\_history is a list of structured slots, it can:  
    * Replace standard RAG context with a list of Memory(type="manual"),  
    * Force the LLM to consider only what the user has injected.

**What this demonstrates:**

* Ability to design a UI that exposes **the engine's internal levers** (search mode, context) without breaking the architecture.  
* Governance of feedback: these become traceable artifacts in reflexive memory, subsequently usable by the RAG and the Reflexor.

### **2\. Prompt Viewer — prompt\_viewer.html**

**Role:** Debug tool to see **exactly** what is sent to the LLM (full prompt, ChatML format).

* **Backend Mechanism:**  
  * interface\_backend\_hermes.py maintains a shared cache:  
    * prompt\_viewer\_cache \= {"raw\_prompt": "...", "timestamp": ...} protected by a Lock.  
  * AgentSemi injects a callback into AgentSpeech:

\`\`\`python  
def update\_viewer\_callback(prompt\_str):  
    cache \= self.get\_cache()  
    lock \= self.get\_lock()  
    with lock:  
        cache\["raw\_prompt"\] \= full\_raw\_prompt  
        cache\["timestamp"\] \= datetime.now().isoformat()  
    if self.socketio:  
        self.socketio.emit('refresh\_prompt\_viewer', {...})  
self.agent\_speech.\_prompt\_callback \= update\_viewer\_callback  
\`\`\`

  \* \`AgentSpeech.build\_llm\_prompt(...)\` calls \`\_update\_viewer\`, which updates the cache and triggers the callback.

* **Frontend Mechanism:**  
  * prompt\_viewer.html queries /api/last\_prompt every second.  
  * Displays:  
    * raw\_prompt (the complete prompt as sent to LLMEngine),  
    * Timestamp,  
    * Size in characters,  
    * Colorized ChatML tags (\<|im\_start|\>, \<|im\_end|\>, \<s\>, \</s\>).

**What this demonstrates:**

* A culture of **observability**: exposing the final prompt rather than a front-end "summary."  
* Alignment with interface contracts: what is seen in the Viewer is the actual result of StandardPrompt → AgentSpeech, not a hack.

### **3\. SemiCode IDE — semicode\_ide.html**

**Role:** Integrated Development Environment, linked to SecondMind's brain for code assistance.

* **Project Explorer & Editing:**  
  * /api/list\_files: Traverses AGENTIC\_DIR, MEMORY\_DIR (defined in config\_paths.py) to generate the tree.  
  * /api/read\_file / /api/save\_file: Read/Write under ROOT\_DIR, with:  
    * Scope control (no path escapes),  
    * Automatic backup in /backups/YYYYMMDD/,  
    * Triggering of code\_extractor.analyze\_file(...) to enrich the Code RAG base.  
* **Code Execution:**  
  * /api/execute\_code: Executes the script as a temporary file under ROOT\_DIR/temp, with a 10s timeout, then displays stdout/stderr in an integrated terminal.  
* **"Semi Assistant – IDE Mode" Chat:**  
  * User message is enriched with code context:  
    * If code is selected in the editor → included in a python ... block in the prompt.  
    * If the user mentions "this code / this file" → injection of the current file's full content.  
  * Sends to /command with this enriched prompt.  
  * Streamed response:  
    * Detection of lang\\n...\\n code blocks via regex.  
    * "Apply" (replaces editor content) and "Copy" buttons.  
* **Integrated Validation (+1):**  
  * The ✓ button sends a prompt: "+1" to /command.  
  * In AgentSemi.\_handle\_system\_commands, this signal:  
    * Records detailed feedback via AgentReflexor.record\_extended\_feedback(...).  
    * If last\_code\_hash is present, marks the version as validated in VersionTracker.

**What this demonstrates:**

* Ability to **integrate the cognitive engine into a real development workflow** (file read/save, execution, refactoring).  
* Full leverage of Code RAG (Extractor \+ AgentCodeSearch \+ Adapter) to give Semi a structured view of the project.

### **4\. Dual LLM Benchmark Lab — benchmark\_dual\_llm.html**

**Role:** Visual testbed for the tri-model architecture (Main 14B LLM, Mini LLM, full pipeline).

* **Config & Model Discovery:**  
  * /api/config\_benchmark reads via AuditorBase:  
    * LLMEngine config (config\_llmengine.yaml),  
    * MiniLLMEngine config (config\_mini\_llm\_engine.yaml).  
  * Returns to the frontend: model name, context window, GPU layers, etc.  
* **Dedicated Benchmarks:**  
  * /api/benchmark/main\_llm:  
    * Uses agent\_semi.llm\_engine.generate\_stream(prompt) for a real prompt.  
    * Measures: Total time, TTFT (time to first token), average inter-token latency, tokens/s, VRAM usage (via NVML), and number of tokens generated.  
  * /api/benchmark/mini\_llm:  
    * Same logic for MiniLLMEngine.  
  * /api/benchmark/full\_pipeline:  
    * Timestamps: Classification (IntentDetector), RAG \+ Preparation (latency before the 1st token), pure generation, total time, and detected intent.  
* **Graphical Interface:**  
  * Two panels for each LLM (main / mini): tokens/s, VRAM, latency, total time, and Chart.js performance graphs.  
  * A full pipeline panel (classification\_time, rag\_latency, generation\_time, total\_time).  
  * A run history table.

**What this demonstrates:**

* Deep mastery of **LLM engineering** (performance, latency, VRAM) beyond simple "API calls."  
* Ability to tool the tri-model architecture and make it **measurable** and **optimizable**.

### **5\. Unified Orchestral Backend — interface\_backend\_hermes.py**

All these interfaces rely on a central backend, consistent with governance rules:

* **Orchestration:**  
  * Initializes AgentSemi with SocketIO (real-time events), Prompt Viewer callbacks, and ProjectGuardian (file monitoring \+ stat sync).  
  * Injects AgentSemi into external routes (tool routes, Whisper audio, etc.).  
* **Role-Structured Routes:**  
  * /command: Main path for the "brain" (direct token streaming).  
  * /memory: Injection of memory \+ feedback, with classification and routing to the correct memory folders.  
  * /api/last\_prompt: Exposes the Prompt Viewer cache.  
  * /api/\*: Stats, audit, benchmark, discussion history, IDE operations.  
* **Strict Standards Compliance:**  
  * All paths go through AuditorBase \+ config\_paths.py.  
  * Transmitted structures remain aligned with interface\_contracts.py (Enums \+ Dataclasses).  
  * Specialized agents do not import each other; AgentSemi always instantiates and injects.

### **Summary**

This cockpit proves that I can:

* **Industrialize a multi-agent AI engine** into a complete environment: hub, IDE, benchmark lab, and debug tools.  
* Expose **high-level levers** (feedback, search modes, manual context) while respecting governance rules (SSOT, typed contracts, separation of roles).  
* Design tools for myself as a developer/architect (Prompt Viewer, SemiCode IDE, Benchmark Lab), accelerating debugging, observation, and iteration on cognitive architecture.

*Maxime Gagné — Cognitive Architect — SecondMind*