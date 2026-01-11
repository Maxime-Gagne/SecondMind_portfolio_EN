### **AgentAuditor – Guardian of Technical Governance and Static Analysis**

I designed AgentAuditor as a **governance agent** dedicated to the quality and security of the multi-agent architecture. It relies on interface contracts and AuditorBase (the source of truth for paths and configs) to continuously monitor code and data flows.

**Global Role**

* Ensure **compliance with interface contracts** (contrats\_interface.py).
* Protect **memory** and critical folders (memoire/brute, persistante, reflexive…) against unauthorized destructive operations.
* Verify **agent structure** (inheritance from AgentBase, logger usage, adherence to META\_agent).
* Audit **flow consistency** between the LLM and memory (preventing interaction loss).
* Produce a **JSON mapping** of Python files for Code RAG and global project understanding.

#### **1\. Data & Security Audit**

AgentAuditor uses the Python AST to analyze source code without executing it:

* **ContractComplianceVisitor** Verifies that all dataclass instantiations use **only** the fields defined in contrats\_interface.py.
  → Prevents the appearance of "ghost fields" like ResultatIntention(foo="…").
* **ShadowComplianceVisitor** Detects **dictionaries that imitate dataclasses** (same keys as Interaction, ResultatIntention, StandardPrompt, etc.).
  → Forces code to use official interface contracts rather than improvised dict objects.
* **FunctionHygieneVisitor** Analyzes functions to identify **dead variables** (assigned but never used) to keep code readable and maintainable.
* **File Security Audit** Scans files to detect:
  * Usage of destructive operations (.unlink, .remove, rmtree) on **sanctuaries** (critical folders defined in YAML).
  * **Forbidden patterns** (raw eval, uncontrolled access, etc.).
    Legitimate exceptions for backup rotations are recognized (presence of shutil.copy, backup, rotation…), so as not to block backup mechanisms.

#### **2\. Structure & Architecture Audit**

Regarding structure, AgentAuditor ensures that agents comply with your META\_agent standards:

* auditer\_conformite\_structurelle:
  * Ensures that every agent\_\*.py file contains at least one class that **inherits from AgentBase**.
  * Verifies the presence of self.logger to guarantee the usage of the **CognitiveLogger** injected by the metaclass.
* generer\_cartographie:
  * Reads the auditor's YAML configuration (scope, exclusions).
  * Traverses only authorized folders (defaulting to agentique/).
  * Generates a project\_map.json listing all valid Python files (relative paths).
    This mapping serves as the foundation for **Code RAG** (AgentRechercheCode) and architecture views (SemiCode IDE, debug tools).

#### **3\. Flow Audit & LLM ↔ Memory Supervision**

AgentAuditor is not limited to code: it also supervises the consistency of data flows.

* \_charger\_stats\_agent reads, via AuditorBase, the dashboard\_stats section of each agent's YAML (periodically updated by the SynchroniseurStats in the backend).
* auditer\_coherence\_flux compares:
  * The number of calls to the **LLM Engine** (appels\_generer \+ appels\_generer\_stream).
  * The number of saves in **raw memory** (appels\_sauvegarder\_interaction\_brute).
  * The number of entries in **history** (appels\_memoriser\_interaction).

If it detects that:

* The LLM has generated more times than raw memory has logged, it triggers a **data leak alert** to the Guardian (\_signaler\_au\_gardien).
* The history contains more entries than raw memory, it signals a **logical anomaly** (ex-nihilo creation).

This layer ensures that no LLM response can silently disappear from the persistence pipeline.

#### **4\. Global Orchestration: auditer\_systeme()**

The main entry point auditer\_systeme(mode="sanity\_check" | "deep\_scan"):

1. Reads its scope and exclusions from config\_agent\_auditor.yaml.
2. Traverses targeted files.
3. Applies, for each file:
   * Security audit.
   * Structural compliance.
   * Internal hygiene.
   * Contract compliance.
   * Shadow dict detection (in deep\_scan mode).
4. Executes a global audit of LLM ↔ memory flows.
5. Regenerates the project mapping.
6. Writes a complete JSON report to agentique/sous\_agents\_gouvernes/agent\_Auditor/logs/audit\_report.json.

This report is used by **ProjectGuardian** to automate reviews after critical file modifications (agent\_Semi.py, contrats\_interface.py, etc.).

**Impact on Architecture**

With AgentAuditor, I have industrialized the governance of my multi-agent system:

* No drift in paths or interface contracts is tolerated (single source of truth via AuditorBase \+ contrats\_interface).
* Agents remain structurally aligned with **META\_agent**.
* LLM → memory flows are supervised globally (no logging gaps).
* Project structure is constantly mapped to feed **Code RAG** and my tools (SemiCode IDE, Prompt Viewer).

In practice, AgentAuditor acts as an **automatic internal auditor**: it verifies that the brain (SemiAgent) and its sub-agents constantly respect the architectural rules I have defined.
