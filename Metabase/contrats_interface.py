#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecondMind Rules:
Agents import their managers and external modules.
Semi imports everyone and injects dependencies.
Agents do not import each other.

STANDARDIZED INTERFACE CONTRACTS - FINAL VERSION
=================================================
This file is the absolute source of truth for the system's
vocabulary and data structures.

RULES:
1. This file is the unique reference for Enums and Dataclasses.
2. All inter-agent communication MUST use these contracts.
3. This contract is the reference for data objects exchanged between agents.
"""
import json
import uuid
from dataclasses import dataclass, field, fields
from typing import Dict, List, Any, Optional
from dataclasses import asdict, is_dataclass
from pydantic import BaseModel, Field, validator
from pathlib import Path
from datetime import datetime
from enum import Enum
import unicodedata
from agentique.base.utils_text import EnumFlexible

# This class serves only as a "translator". It does not change the data.
class FlexibleEnum(Enum):
    @classmethod
    def _missing_(cls, value):
        # If the exact value is not found, attempt normalization
        if isinstance(value, str):
            def clean(text):
                # Remove accents and set to lowercase
                return "".join(c for c in unicodedata.normalize('NFD', text)
                             if unicodedata.category(c) != 'Mn').lower().strip()

            search_value = clean(value)

            # Compare with all existing options
            for member in cls:
                if clean(member.value) == search_value:
                    return member
        return None

# ========================================
# 1. ENUMERATIONS (Strict Vocabulary)
# ========================================
@dataclass
class Subject(EnumFlexible):
    SECONDMIND = "SecondMind" # Everything regarding my AI system in general
    SETUP = "Setup"           # Everything regarding installation/hardware/configuration
    SCRIPT = "Script"         # Python code or .yaml files
    FILE = "File"             # Non-code files (.txt, README, .md, .pdf, etc.)
    GENERAL = "General"       # Everything unrelated to my AI system

class Action(EnumFlexible):
    DO = "Do"
    THINK = "Think"
    SPEAK = "Speak"
    CODE = "Code"
    DEBUG = "Debug"

class Category(EnumFlexible):
    PLAN = "Plan"
    TEST = "Test"
    CONFIGURE = "Configure"
    DOCUMENT = "Document"
    ANALYZE = "Analyze"
    DEFINE = "Define"
    COMPARE = "Compare"
    ASK = "Ask"
    CONFIRM = "Confirm"
    GREET = "Greet"
    # Categories for CODE & DEBUG
    AGENT = "Agent"
    SYSTEM = "System"   # Any script/file of my system that is not an agent
    BACKEND = "Backend" # Everything regarding backend (server, API, DB, etc.)
    TEST_DEV = "Test"
    OTHER = "Other"

class MemoryType(Enum):
    """Memory types"""
    WORKING = "working"
    HISTORY = "history"
    REFLEXIVE = "reflexive"
    RULES = "rules"
    FEEDBACK = "feedback"
    RAW = "raw"
    PERSISTENT = "persistent"
    KNOWLEDGE = "knowledge"
    VECTORIAL = "vectorial"
    TEMP = "temp"
    TRAINING_MODULES = "training_modules"

class SearchMode(Enum):
    """
    Search modes EXCLUSIVELY driven by the frontend interface.
    The AI is not allowed to initiate a search on its own.
    """
    NONE = "none"               # Default: No external search
    WEB = "web"                 # Force Web search
    MANUAL_CONTEXT = "manual_context"  # Force use of manual Slots

# ========================================
# 2. JSON UTILITIES
# ========================================

class CustomJSONEncoder(json.JSONEncoder):
    """Universal encoder for Dataclasses and Enums."""
    def default(self, o):
        if is_dataclass(o): return asdict(o)
        if isinstance(o, Enum): return o.value
        if isinstance(o, Path): return str(o)
        if isinstance(o, datetime): return o.isoformat()
        return super().default(o)

# ========================================
# 3. STANDARDIZED METADATA
# ========================================
"""
How AgentSemi handles this:

Beginning:
Creation of file_meta = MetadataFile(...)
Creation of pipeline_meta = MetadataPipeline(...)

Execution:
Semi fills pipeline_meta progressively (time, tokens).
Semi fills file_meta with contextual info (found files).

End:
Save: Semi records the Interaction object (containing file_meta).
Logging: Semi sends pipeline_meta to its Logger.
"""

@dataclass
class MetadataFile:
    """
    PERSISTENT: Contextual information kept in the ARCHIVE.
    Contains EVERYTHING that is not the conversation text.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: Optional[str] = None
    message_turn: Optional[int] = None
    source_agent: str = "Semi"
    memory_type: str = "history"

    # Traceability
    consulted_files: List[str] = field(default_factory=list)

    # --- QUALITY (JUDGE) ---
    judge_validation: bool = False
    quality_score: float = 0.0
    issue_count: int = 0
    judge_details: Optional[str] = None

    # --- TECHNICAL INDEXING ---
    content_len: int = 0
    vector_ref: Optional[int] = None
    whoosh_ref: Optional[str] = None

    # --- EXTENSION ---
    free_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetadataPipeline:
    """
    VOLATILE: Performance and debug info.
    Sent to Semi's logs, does not pollute long-term memory.
    """
    interaction_id: str
    # Timing
    total_time: float = 0.0
    intention_time: float = 0.0
    search_time: float = 0.0
    generation_time: float = 0.0

    # Technical details
    model_used: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    success: bool = True
    error: Optional[str] = None

# ========================================
# 4. ATOMS (Elementary Bricks)
# ========================================

@dataclass
class MemorySnippet:
    """
    ATOM 2: Unified output of AgentRecherche.
    The smallest common denominator of memory.
    """
    content: str        # Raw text to read
    title: str          # Identifier
    type: str
    score: float        # Relevance (1.0 = Max/Forced)

@dataclass
class Rule:
    """RULE ATOM: Exclusively for governance."""
    content: str
    title: str          # Rule ID (ex: R01)
    type: str = "rule"  # Fixed
    score: float = 10.0 # Always priority

@dataclass
class ReadmeFile:
    """ATOM: INTERNAL project documentation (README.md, local specs)."""
    content: str
    title: str
    path: str = ""      # Location in project
    type: str = "readme"
    score: float = 1.0

@dataclass
class TechnicalDocumentation:
    """ATOM: EXTERNAL documentation (Libraries, API, Web Scraping)."""
    content: str
    title: str
    source_url: str = "" # To cite external source
    type: str = "tech_doc"
    score: float = 1.0

@dataclass
class CognitiveModifiers:
    """
    ATOM 3: Configuration coming from UI
    """
    search_mode: SearchMode
    enable_cot: bool = False
    enable_thinking: bool = False

# ========================================
# 5. AGENT OUTPUT FORMATS (System Core)
# ========================================

@dataclass
class IntentionResult:
    """
    OUTPUT FROM: IntentionDetector
    """
    prompt: str           # Original signal
    subject: Subject
    action: Action
    category: Category

    def __post_init__(self):
        if not self.prompt:
            raise ValueError("❌ IntentionResult: empty prompt - mandatory data missing!")
        if not isinstance(self.subject, Subject):
            raise TypeError(f"❌ IntentionResult: subject must be a Subject, received {type(self.subject)}")
        if not isinstance(self.action, Action):
            raise TypeError(f"❌ IntentionResult: action must be an Action, received {type(self.action)}")
        if not isinstance(self.category, Category):
            raise TypeError(f"❌ IntentionResult: category must be a Category, received {type(self.category)}")

@dataclass
class SearchResult:
    """
    OUTPUT FROM: AgentRecherche
    """
    raw_snippets: List[MemorySnippet]
    scanned_files_count: int = 0
    search_time: float = 0.0

    def __post_init__(self):
        if self.scanned_files_count < 0:
            raise ValueError(f"❌ SearchResult: invalid scanned_files_count ({self.scanned_files_count})")
        if self.search_time < 0:
            raise ValueError(f"❌ SearchResult: invalid search_time ({self.search_time})")

@dataclass
class WebSearchResult:
    url: str
    title: str
    full_content: str     # Scraped text
    relevant_summary: str  # Extracted utility
    relevance_score: int  # 0-10

@dataclass
class ContextResult:
    """
    OUTPUT FROM: AgentContexte
    Strict typing for Auditor validation.
    """
    memory_context: List[MemorySnippet]
    active_rules: List[Rule]
    history: List[str]
    readme_files: List[ReadmeFile]
    detected_intention: IntentionResult

    def __post_init__(self):
        if not self.memory_context:
            raise ValueError("❌ ContextResult: empty memory_context!")
        if not self.active_rules:
            raise ValueError("❌ ContextResult: empty active_rules!")
        if not self.readme_files:
             raise ValueError("❌ CONTRACT VIOLATION (ContextResult): 'readme_files' is an EMPTY list [] !")

@dataclass
class JudgeResult:
    """
    OUTPUT FROM: AgentJuge
    """
    valid: bool
    score: float
    reason: str
    details: Dict[str, Any]

    def __post_init__(self):
        if not isinstance(self.valid, bool):
            raise TypeError(f"❌ JudgeResult: valid must be a bool, received {type(self.valid)}")
        if not 0.0 <= self.score <= 5.0:
            raise ValueError(f"❌ JudgeResult: score must be between 0 and 5, received {self.score}")
        if not self.reason:
            raise ValueError("❌ JudgeResult: empty reason!")

@dataclass
class Interaction:
    """
    Final object saved to disk (JSON).
    """
    prompt: str
    response: str
    system: Optional[str]
    intention: IntentionResult
    memory_context : List[MemorySnippet]
    meta: MetadataFile

@dataclass
class CodeContext:
    """
    CODE ATOM: Standard format for code context injection.
    Flexible for Classes, Methods, and Functions.
    """
    id: str
    type: str
    module: str
    name: str

    signature: str = ""
    docstring: str = ""
    code_summary: str = ""
    content: str = ""

    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    variables_used: List[str] = field(default_factory=list)

    bases: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    methods: List[str] = field(default_factory=list)

    return_type: Optional[str] = None
    score: float = 0.0

@dataclass
class ContentAnalysis:
    """Detailed AST code analysis structure"""
    mode: str
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    errors: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CodeArtifact:
    """
    ATOM: Transit object for an analyzed snippet or file.
    """
    id: str
    hash: str
    language: str
    content: str
    timestamp: str
    analysis: ContentAnalysis
    type: str

@dataclass
class CodeChunk:
    """
    Represents a technical source code fragment.
    """
    content: str
    path: str
    type: str
    language: str

@dataclass
class CodeResult:
    """
    Represents the physical state of the project code at time T.
    """
    skeleton: str                         # Project Tree
    vector_chunks: List[CodeContext]      # Similar code fragments (RAG)

# ========================================
# 6. STANDARDIZED PROMPT FORMATS
# ========================================

class PromptMixin:
    def get_unused_fields(self) -> List[str]:
        """Returns empty fields (None, empty list, empty str)."""
        empty = []
        for f in fields(self):
            val = getattr(self, f.name)
            if val is None:
                empty.append(f.name)
            elif isinstance(val, (list, dict, set, str)) and len(val) == 0:
                empty.append(f.name)
        return empty

@dataclass
class StandardPrompt(PromptMixin):
    """Recipe 1: Standard Chat."""
    original_prompt: str
    system_instructions: str
    modifiers: CognitiveModifiers
    intention: IntentionResult
    history: List[str]
    memory_context: List[MemorySnippet]
    rules: List[Rule]
    readme_files: List[ReadmeFile]

    def __post_init__(self):
        if not self.original_prompt or not self.original_prompt.strip():
            raise ValueError("❌ StandardPrompt: 'original_prompt' is empty!")
        if not self.system_instructions:
            raise ValueError("❌ StandardPrompt: 'system_instructions' missing!")
        if not self.memory_context:
            raise ValueError("❌ StandardPrompt: 'memory_context' list is empty!")
        if not self.rules:
            raise ValueError("❌ StandardPrompt: 'rules' list is empty (Governance missing)!")
        if not self.readme_files:
             raise ValueError("❌ StandardPrompt: 'readme_files' list is empty!")

@dataclass
class StandardPromptCode(PromptMixin):
    """Prompt dedicated to Software Engineering."""
    original_prompt: str
    code_prompt_instructions: str
    modifiers: CognitiveModifiers
    intention: IntentionResult
    history: List[str]
    rules: List[Rule]
    readme_files: List[ReadmeFile]
    code_chunks: List[CodeChunk]

    def __post_init__(self):
        if not self.original_prompt:
            raise ValueError("❌ StandardPromptCode: empty original_prompt!")
        if not self.code_prompt_instructions:
            raise ValueError("❌ StandardPromptCode: empty code_prompt_instructions!")
        if not self.code_chunks:
            raise ValueError("❌ StandardPromptCode: empty code_chunks!")

@dataclass
class NewChatPrompt(PromptMixin):
    """First message of a new chat."""
    original_prompt: str
    first_prompt_instructions: str
    modifiers: CognitiveModifiers
    intention: IntentionResult
    recent_chat_history: List[str]
    system_summary: str

@dataclass
class ManualContextCodePrompt(PromptMixin):
    """Prompt dedicated to 'Manual Context' mode."""
    original_prompt: str
    manual_context_instructions: str
    manual_context: str
    intention: IntentionResult
    history: List[str]
    rules: List[Rule]
    readme_files: List[ReadmeFile]
    modifiers: CognitiveModifiers

@dataclass
class MemorySearchPrompt(PromptMixin):
    """Recipe 3: Memory Search (Reflexive Loop)."""
    original_prompt: str
    memory_search_prompt_instructions: str
    memory_results: List[MemorySnippet]
    previous_reasoning: str
    intention: IntentionResult

@dataclass
class ActionStep:
    """An atomic step of the agent's action plan."""
    index: int
    description: str
    status: str = "WAITING" # WAITING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED
    result: Optional[str] = None

@dataclass
class ExecutionPlan:
    """The strategic state of the agent."""
    global_objective: str
    steps: List[ActionStep] = field(default_factory=list)
    current_step_index: int = 0
    is_completed: bool = False

@dataclass
class CartographyPrompt(PromptMixin):
    """STEP 1: STRATEGIC VISION."""
    original_prompt: str
    cartography_instructions: str
    project_cartography: str            # project_map.json content
    battle_plan: List[str]
    intention: IntentionResult

@dataclass
class FileInspectionPrompt(PromptMixin):
    """STEP 2: TACTICAL ANALYSIS."""
    original_prompt: str
    inspection_instructions: str
    current_file: MemorySnippet
    previous_notes: str
    intention: IntentionResult

@dataclass
class StagingReviewPrompt(PromptMixin):
    """STEP 3: CONSOLIDATION."""
    original_prompt: str
    review_instructions: str
    current_staging_state: str           # etat_systeme_resume.md content
    last_action: str
    intention: IntentionResult

@dataclass
class WebSearchPrompt(PromptMixin):
    """Recipe 2: Forced Web Search."""
    query: str
    web_search_prompt_instructions: str
    web_results: List[Dict[str, str]]

@dataclass
class ProtocolPrompt(PromptMixin):
    """Recipe 4: ALERT Intervention Protocol (!!!)."""
    original_prompt: str
    protocol_content: str
    recent_history: List[str]
    intention: IntentionResult
    rules: List[Rule]

# ========================================
# 7. GOVERNANCE & REFLEXIVITY
# ========================================

class GapType(EnumFlexible):
    """Categorization of reflexive errors."""
    HALLUCINATION = "Hallucination"       # Invention of facts/files
    GOVERNANCE = "Governance"             # Failure to follow explicit instructions
    LOGIC = "Logic"                       # Reasoning error or contradiction
    BIAS = "Bias"                         # Inherited patterns
    VISUAL = "Visual"                     # Contradiction between image/text
    TECHNICAL = "Technical"               # Execution or path error

@dataclass
class ReflexiveJournalEntry:
    """ATOM: Strict structure for reflexive doubt journal."""
    error_committed: str
    gap_type: GapType
    context: str
    violated_rule: str
    causal_hypothesis: str
    injected_correction: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def to_markdown(self) -> str:
        gap_str = self.gap_type.value if isinstance(self.gap_type, Enum) else str(self.gap_type)
        return (
            f"\n🔁 Reflexive Entry — {self.timestamp}\n"
            f"- **Error committed**: {self.error_committed}\n"
            f"- **Gap type**: {gap_str}\n"
            f"- **Context**: {self.context}\n"
            f"- **Violated rule**: {self.violated_rule}\n"
            f"- **Causal hypothesis**: {self.causal_hypothesis}\n"
            f"- **Injected correction**: {self.injected_correction}\n"
        )

# ========================================
# 8. STATS_MANAGER - STANDARDIZED STATISTICS
# ========================================

@dataclass
class BaseStats:
    agent_name: str
    total_calls: int = 0
    total_errors: int = 0
    last_execution: Optional[str] = None
    creation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    specific_stats: Dict[str, Any] = field(default_factory=dict)
    avg_time_ms: Optional[float] = None

    def increment_call(self) -> None:
        self.total_calls += 1
        self.last_execution = datetime.now().isoformat()

    def increment_error(self) -> None:
        self.total_errors += 1

    def get_stats(self) -> Dict[str, Any]:
        success_rate = 0.0
        if self.total_calls > 0:
            success_rate = ((self.total_calls - self.total_errors) / self.total_calls) * 100
        return {
            "agent": self.agent_name,
            "total_calls": self.total_calls,
            "total_errors": self.total_errors,
            "success_rate": round(success_rate, 2),
            "last_activity": self.last_execution,
            "creation_timestamp": self.creation_timestamp,
            "specific_stats": self.specific_stats.copy()
        }

# ========================================
# 9. DATASETS & EVALUATION
# ========================================

@dataclass
class DataFormat:
    """INGESTION CONTRACT: Standard for future training dataset."""
    text: str                       # Markdown recommended
    title: str                      # Source identifier

    subject: str                    # Science, Music, etc.
    category: str                   # Manual, Research_Paper, Snippet

    source_url: Optional[str] = None
    scraping_date: str = field(default_factory=lambda: datetime.now().isoformat())
    token_count: int = 0
    initial_quality_score: float = 1.0
    logical_strength: float = 1.0
    transversal_link_potential: List[str] = field(default_factory=list)
    bias_alert: Dict[str, Any] = field(default_factory=dict)

    language: str = "en"
    complexity_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecondMindEvaluationCriteria:
    """TRUTH GRID: Evaluates relevance across 10 pillars (0.0 to 1.0)."""
    # PHASE 1: DEBUG & VALIDATION
    bias_debug_index: float = 0.0
    fractality_score: float = 0.0
    causality_weight: float = 0.0

    # PHASE 2: FOUNDATION & EMERGENCE
    axiom_density: float = 0.0
    emergence_potential: float = 0.0

    # PHASE 3: LIMITS & REALITY
    incompleteness_score: float = 0.0
    empirical_validation: float = 0.0

    # PHASE 4: SYNTHESIS & INTUITION
    convergence_strength: float = 0.0
    compression_capacity: float = 0.0
    transposability: float = 0.0

    def global_score(self) -> float:
        f_fields = fields(self)
        return sum(getattr(self, f.name) for f in f_fields) / len(f_fields)
