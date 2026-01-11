\[\!NOTE\]

# **🧠 Intent-Based Semantic Naming**

## **From Prompt to Retrievable Memory in 80ms**

## **The Problem**

Traditional RAG systems store interactions with generic names such as interaction\_001.json or chat\_20241201.json.

**The result:** To find "every time I debugged an agent," the system must **parse the content of every single file**. With thousands of interactions, this becomes a critical performance bottleneck.

## **The Insight**

What if the **filename already encoded the intent**?

Instead of searching through content, we search the filesystem—a near-instantaneous operation.

## **The Solution**

### **Tri-Axis Classification**

Every user prompt passes through the **IntentionDetector**, an SBERT classifier trained on my data, which determines three dimensions:

| Axis | Question | Examples |
| :---- | :---- | :---- |
| **Subject** | What are we talking about? | SecondMind, Script, Setup, File, General |
| **Action** | What are we doing? | Do, Think, Talk, Code, Debug |
| **Category** | In what context? | Agent, System, Backend, Plan, Test... |

### **Automatic Naming**

These three values are concatenated to form the filename:

interaction\_\[subject\]\_\[action\]\_\[category\]\_\[timestamp\].json

**Concrete examples:**

* interaction\_script\_debug\_agent\_20241201143052.json  
* interaction\_setup\_do\_configure\_20241201150823.json  
* interaction\_secondmind\_think\_analyze\_20241201162341.json

### **Ultra-Fast Search**

The name becomes a **primary index**. To find all agent debug sessions:

Pattern: interaction\_\*\_debug\_agent\_\*.json

Everything (threaded) resolves this pattern in **\~10ms**—long before querying vector indexes.

## **Real Performance**

\[CognitiveLogger.Search\] INFO: Strategic Search completed in 0.08s. 10 results.

**80ms** for a complete search including:

* Filesystem pattern filtering (Everything)  
* Indexed full-text search (Whoosh)  
* Semantic vector search (FAISS)

Semantic naming allows for **pre-filtering** before expensive operations.

## **Full Taxonomy**

### **Subject (5 classes)**

| Value | Usage |
| :---- | :---- |
| SecondMind | Discussion regarding the AI system itself |
| Setup | Installation, hardware, configuration |
| Script | Python code, YAML, technical files |
| File | Non-code documents (.txt, .md, .pdf) |
| General | Anything outside the system's scope |

### **Action (5 classes)**

| Value | Usage |
| :---- | :---- |
| Do | Execute a concrete task |
| Think | Reflect, analyze, understand |
| Talk | General conversation |
| Code | Write code |
| Debug | Fix a problem |

|

### **Category (14 classes)**

Agent, System, Backend, Plan, Test, Configure, Document, Analyze, Define, Compare, Ask, Confirm, Greet, Other

## **Benefits**

### **1\. Search Without Parsing**

The filename **is** the metadata. No need to open the JSON to filter.

### **2\. Contextual Strategies**

The RAG adapts its strategy based on the detected intent:

* action=Debug ➡️ Priority to governance rules  
* subject=Script ➡️ Activation of Code RAG  
* category=Agent ➡️ Boost on technical documentation

### **3\. Cognitive Traceability**

Every file carries its "intent signature"—we know **why** it was created, not just **when**.

### **4\. Scalability**

Adding a new category \= updating the enum \+ retraining the classifier. No changes to the search pipeline are required.

## **Key Files**

* intention\_detector.py — Tri-axis SBERT classifier  
* agent\_Memory.py — Semantic name generation  
* interface\_contracts.py — Subject/Action/Category enum definitions  
* agent\_Search.py — Multi-index strategic search

*Maxime Gagné — Cognitive Architect — SecondMind*