

# **🔄 Self-Feeding Training Loop**

## **The AI That Generates Its Own Training Data**

## **The Problem**

Fine-tuning a model requires **quality data**. Traditional options include:

| Approach | Disadvantage |
| :---- | :---- |
| **Manual annotation** | Expensive, slow, tedious |
| **Synthetic data** (GPT) | Biased, not representative of real usage |
| **Commercial datasets** | Expensive, generic, not domain-specific |

**The paradox**: To improve my intent classifier, I need data that reflects *my* usage—but this data only exists after using the system.

## **The Insight**

What if every interaction **automatically became** potential training data?

The system is used → generates data → improves → works better → generates better data...

**A virtuous circle of self-improvement.**

## **The Solution**

### **Two-Loop Architecture**

**Loop 1: Normal Usage (Real-time)**

User → SecondMind → Response
              ↓
        MemoryAgent (Save)
              ↓
        AutoDatasetBuilder (Quality evaluation)
              ↓
        JSONL Dataset (If qualified)

**Loop 2: Training (Asynchronous)**

JSONL Dataset (Threshold reached)
              ↓
        TrainerAgent (Merge \+ Training)
              ↓
        New .pth classifiers
              ↓
        IntentDetector (Improved model)

## **The Quality Gate**

Not all interactions deserve to be learned. The **AutoDatasetBuilder** applies a strict filter:

### **Exclusion Criteria**

| Criterion | Reason |
| :---- | :---- |
| Too short (\< 10 chars) | "ok", "yes" → no clear intent |
| Too few words (\< 3\) | Minimal context required |
| System commands | \!\!\!, \+1, \-1 → technical noise |
| "Unknown" classification | If the model isn't sure, we don't learn from its error |

### **Inclusion Criteria**

| Criterion | Reason |
| :---- | :---- |
| Natural prompt | Reflects real usage |
| Confident classification | The Subject/Action/Category triplet is clear |
| Reasonable length | Enough context for SBERT |

## **The Data Pipeline**

### **Merged Sources**

The TrainerAgent combines several sources with deduplication:

| File | Source | Role |
| :---- | :---- | :---- |
| intentions\_base.jsonl | Manual | Initial Seed (\~50 annotated examples) |
| batch\_dataset.jsonl | Auto-generated | Grows with normal usage |
| live\_dataset.jsonl | Real-time | Explicit feedback (optional) |

### **Data Format**

Each line is an intent triplet:

{"prompt": "Can you analyze agent\_Semi.py?", "subject": "Script", "action": "Think", "category": "Agent"}

This is exactly what SBERT needs to train the 3 classifiers.

## **Training Triggers**

The **TrainerAgent** can be triggered by:

| Trigger | Description |
| :---- | :---- |
| **Example threshold** | E.g., every 100 new examples |
| **Manual command** | When I want to force retraining |
| **Schedule** | E.g., every Sunday night |

Training is **non-blocking**—the system continues to operate while the new models are being prepared.

## **Benefits**

### **1\. Representative Data**

The dataset reflects **my actual usage**, not theoretical or generic examples.

### **2\. Continuous Improvement**

The more I use SecondMind, the more accurate it becomes. The learning curve follows the usage curve.

### **3\. Zero Manual Annotation**

After the initial seed, I only need to use the system normally. The rest is automatic.

### **4\. Integrated Quality Control**

The Quality Gate filters out noise without intervention. Only "clean" interactions feed the model.

### **5\. Full Traceability**

Each training data point is linked to a real, timestamped interaction with its context.

## **The Virtuous Circle**

┌─────────────────────────────────────────────┐
│                                             │
│   Usage → Data → Training → Usage           │
│     ↑                                 │     │
│     └────────── Improvement ──────────┘     │
│                                             │
└─────────────────────────────────────────────┘

The system **learns from itself** without expensive fine-tuning, manual annotation, or external data.

## **Key Files**

* auto\_dataset\_builder.py — Quality Gate \+ triplet extraction
* agent\_Trainer.py — Source merging \+ PyTorch training
* intent\_detector.py — Consumer of the trained models

*Maxime Gagné — Cognitive Architect — SecondMind*
