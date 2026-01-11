## **SecondMind Global Architecture**

SecondMind is a multi-agent AI brain orchestrated by AgentSemi.  
The objective: a local, explainable, and governable system capable of combining text RAG \+ code RAG \+ LLM tri-model (main \+ mini \+ vector).

### **1\. Overview (Subway Map)**

          ┌───────────────────────────────────────────────────┐  
          │                    SemiAgent                      │  
          │         (main orchestrator, pipeline)             │  
          └───────────────────────────────────────────────────┘  
                  │  
                  │ think(prompt, search\_mode, raw\_history)  
                  ▼  
        ┌────────────────┐  
        │ IntentDetector (SBERT \+ Mini LLM)               │  
        │ → IntentResult (Subject / Action / Category)    │  
        └────────────────┘  
                  │  
                  ▼  
        ┌────────────────┐  
        │ SearchAgent (Whoosh \+ Vector \+ Everything)      │  
        │ → SearchResult (List\[Memory\])                   │  
        └────────────────┘  
                  │  
                  ▼  
        ┌────────────────┐  
        │ ContextAgent                                    │  
        │ → ContextResult (context, rules, history)       │  
        └────────────────┘  
                  │  
          \+-------+------------------------+  
          |                                |  
          | (if code question)             |  
          ▼                                |  
  ┌─────────────────────┐                  |  
  │  CodeSearchAdapter  │                  |  
  │  \+ CodeSearchAgent  │                  |  
  │  (Code RAG \+ graph) │                  |  
  └─────────────────────┘                  |  
          │                                |  
          ▼                                |  
    Code Context (Memory type="code")      |  
          │                                |  
          \+--------------------------------+  
                  │  
                  ▼  
        ┌────────────────┐  
        │ SpeechAgent    │  
        │ → StandardPrompt → final ChatML prompt          │  
        └────────────────┘  
                  │  
                  ▼  
        ┌────────────────┐  
        │ LLMEngine      │  
        │ (Local Qwen / Mistral, GGUF or Transformers)   │  
        └────────────────┘  
                  │  
                  ▼  
            Text Response  
                  │  
                  ▼  
        ┌────────────────┐  
        │ CodeSearchExtractor                             │  
        │ (code extraction)                               │  
        └────────────────┘  
                  │  
                  ▼  
        ┌────────────────┐  
        │ JudgeAgent     │  
        │ (Mini LLM)     │  
        │ → JudgeResult  │  
        └────────────────┘  
                  │  
                  ▼  
        ┌───────────────────────────────────────────────┐  
        │ MemoryAgent                                   │  
        │ \- JSONL raw logs                              │  
        │ \- history \+ persistent \+ reflexive            │  
        │ \- FAISS engine (VectorEngine)                 │  
        └───────────────────────────────────────────────┘  
                  │  
                  ▼  
        ┌────────────────┐  
        │ PersistentRawProcessor                        │  
        │ (history → persistent \+ RAG \+ vector)         │  
        └────────────────┘

In parallel:  
\- \`ReflexorAgent\` analyzes alert signals (\`\!\!\!\`) and creates governance rules.  
\- \`AuditorAgent\` audits code, interface contracts, and LLM ↔ memory consistency.  
\- \`ProjectGuardian\` monitors critical files, triggers \`SemiAgent\` and stats synchronization.

### **2\. 7-Step Cognitive Pipeline (think)**

The central method of SemiAgent is think(...):

1. **System Commands & Forced Modes**  
   * \+1 / \-1 → explicit feedback recorded by ReflexorAgent (+ Whoosh update / code versioning).  
   * \-1 intention → saves a misclassified intent case to memory/reflexive/feedback.  
   * \!\!\! → triggers the reflexive loop (ReflexorAgent.launch\_governance\_analysis) and activates an alert protocol in the prompt.  
2. **Information Source Selection (search\_mode)**  
   * web → \_web\_search(...) (DuckDuckGo \+ Google fallback), synthesized by the LLM.  
   * memory → pure memory search, without the full pipeline.  
   * manual\_context → manual slots sent from the UI, converted into Memory(type="manual") to override normal context.  
   * none / auto → normal pipeline with RAG.  
3. **Intent Detection (IntentDetector)**  
   * Returns an IntentResult(prompt, subject, action, category) used everywhere: RAG, filenames, stats.  
4. **Hybrid Search (SearchAgent)**  
   * Combines:  
     * FAISS (VectorEngine) via content, file, subject/action/category metadata.  
     * Whoosh (update\_index \+ MultifieldParser queries).  
     * Everything (es.exe) to instantly find rules files and READMEs.  
   * \_define\_search\_strategy strategy:  
     * priority to rules (reflexive/rules),  
     * then reflexive, knowledge, history, training\_modules, persistent.  
5. **Context Construction (ContextAgent)**  
   * Selects the best Memory via JudgeAgent.calculate\_semantic\_relevance.  
   * Adds:  
     * active\_rules (found rules),  
     * technical\_documentation (READMEs detected in the prompt),  
     * Conversation history (RAM \+ continuity from memory/history).  
   * If the question involves code/files, SemiAgent calls CodeSearchAdapter to inject a special "LIVE CODE CONTEXT" Memory.  
6. **ChatML Prompt Construction (SpeechAgent)**  
   * Assembles a StandardPrompt:  
     * original\_prompt,  
     * modifiers (search\_mode, enable\_thinking),  
     * intent,  
     * history,  
     * used\_context, rules, documentation.  
   * Produces a structured ChatML prompt:  
     \<|im\_start|\>system  
     \[System instructions \+ governance\]  
     \<|im\_end|\>  
     \<|im\_start|\>user  
     \#\#\# USEFUL\_DOCUMENTATION  
     ...  
     \#\#\# RULES  
     ...  
     \#\#\# MEMORY\_CONTEXT  
     ...  
     \#\#\# CONVERSATION\_HISTORY  
     ...  
     \#\#\# CURRENT\_QUESTION  
     \[original\_prompt\]  
     \<|im\_end|\>  
     \<|im\_start|\>assistant

   * Updates the **Prompt Viewer** via a shared cache (/api/last\_prompt).  
7. **Generation, Judgment & Memory**  
   * LLMEngine.generate\_stream(...) (Local Qwen/Mistral, GGUF or Transformers).  
   * CodeSearchExtractor.process\_llm\_response:  
     * extracts code blocks,  
     * replaces them with a compact placeholder,  
     * returns a list of artifacts to save (MemoryAgent.save\_code\_artifacts).  
   * JudgeAgent.evaluate\_response\_consistency(...) (Mini LLM) produces a JudgeResult (valid, score, reason, details).  
     * Deterministic Validation: Unlike binary validation, the JudgeAgent issues a normalized consistency score (float 0.0 \- 1.0). The system applies a strict rejection threshold at 0.6: any response below this score is blocked, logged as an incident, and never reaches the user.  
   * MemoryAgent:  
     * captures raw interaction in JSONL (raw/),  
     * serializes a complete Interaction (meta \= FileMetadata),  
     * saves it in history/,  
     * updates FAISS \+ Whoosh,  
     * PersistentRawProcessor then transfers to persistent/ and updates indexes.  
8. **Limits**  
   * Each agent has an explicit 'Negative Scope' in its documentation (Section: What it never does), contractually prohibiting responsibility overflows (e.g., SearchAgent cannot write, SpeechAgent cannot call the LLM).