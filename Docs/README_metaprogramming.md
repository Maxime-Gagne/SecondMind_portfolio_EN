\[\!NOTE\]

# **⚙️ Metaprogramming — Zero Boilerplate**

## **How a Metaclass Automatically Instruments 10 Agents**

## **The Problem**

In a multi-agent system, every agent requires the same core tools:

* A **logger** to trace its actions.  
* A **stats\_manager** to count calls and errors.  
* An **auditor** to validate paths and exchanges.  
* A shared **RAM memory** for the working context.

The naive approach: copy-pasting this initialization code into every single agent.

\# ❌ Without metaclass — Code repeated 10 times  
class ResearchAgent:  
    def \_\_init\_\_(self):  
        self.logger \= CognitiveLogger("Research", ...)  
        self.stats\_manager \= StatsBase("Research")  
        self.auditor \= AuditorBase("research")  
        self.ram\_memory \= WorkingMemoryRAM()  
        \# ... the actual agent logic

**Result**: 40+ lines of boilerplate per agent. High risk of oversight. Maintenance nightmare.

## **The Insight**

What if the **class itself** could self-configure at the moment of its creation?

Python allows control over *how* a class is instantiated via **metaclasses**. Instead of writing boilerplate, we generate it.

## **The Solution: MetaAgent**

### **Architecture**

class MetaAgent(type):  
    """Metaclass that injects tools AND automatic monitoring."""

def \_\_call\_\_(cls, \*args, \*\*kwargs):  
    \# 1\. Standard instance creation  
    instance \= cls.\_\_new\_\_(cls)

    \# 2\. Automatic identification  
    display\_agent\_name \= cls.\_\_name\_\_.replace("Agent", "")  
    audit\_agent\_name \= display\_agent\_name.lower()

    \# 3\. Component injection (strict order)  
    instance.ram\_memory \= WorkingMemoryRAM()  
    instance.stats\_manager \= StatsBase(display\_agent\_name)  
    instance.auditor \= AuditorBase(audit\_agent\_name)  
    instance.logger \= CognitiveLogger(  
        agent\_name=display\_agent\_name,  
        auditor=instance.auditor,  
        console\_output=True  
    )

    \# 4\. Automatic method instrumentation  
    for attr\_name in dir(cls):  
        if not attr\_name.startswith("\_") and callable(getattr(cls, attr\_name)):  
            original\_method \= getattr(cls, attr\_name)  
            decorated\_method \= MetaAgent.\_create\_stats\_wrapper(  
                instance, original\_method, attr\_name  
            )  
            setattr(instance, attr\_name, decorated\_method)

    \# 5\. Standard initialization  
    cls.\_\_init\_\_(instance, \*args, \*\*kwargs)

    return instance

\#\#\# Usage — One Line Is Enough

\# ✅ With metaclass — The agent simply inherits  
class ResearchAgent(AgentBase):  
    def \_\_init\_\_(self):  
        super().\_\_init\_\_(agent\_name="ResearchAgent")  
        \# Actual business logic, zero boilerplate

def hybrid\_search(self, query: str):  
    \# self.logger, self.auditor, and self.stats\_manager  
    \# are already available and configured  
    self.logger.info(f"Searching: {query}")  
    ...

\*\*10 agents × 40 lines saved \= 400 lines of code eliminated.\*\*

## **Auto-Instrumentation: Invisible Monitoring**

The metaclass does more than just inject tools. It **automatically wraps every public method** to collect metrics.

### **The Stats Wrapper**

@staticmethod  
def \_create\_stats\_wrapper(instance, method, method\_name):  
    """Creates a wrapper that logs calls and errors automatically."""

@functools.wraps(method)  
def wrapper(\*method\_args, \*\*method\_kwargs):  
    \# Global call counter  
    instance.stats\_manager.increment\_call()

    \# Method-specific counter  
    instance.stats\_manager.increment\_specific\_stat(f"calls\_{method\_name}")

    start\_time \= time.perf\_counter()  
    success \= False

    try:  
        result \= method(instance, \*method\_args, \*\*method\_kwargs)  
        success \= True  
        return result

    except Exception as e:  
        instance.stats\_manager.increment\_error()  
        instance.stats\_manager.increment\_specific\_stat(f"errors\_{method\_name}")  
        raise e

    finally:  
        duration\_ms \= (time.perf\_counter() \- start\_time) \* 1000  
        instance.auditor.record\_stat(method\_name, {  
            "success": success,  
            "duration\_ms": duration\_ms  
        })

return wrapper

\#\#\# Concrete Outcome

Without writing a single line of monitoring code, every agent automatically produces:

{  
  "ResearchAgent": {  
    "total\_calls": 847,  
    "total\_errors": 3,  
    "calls\_hybrid\_search": 412,  
    "calls\_vector\_search": 298,  
    "errors\_hybrid\_search": 1,  
    "average\_duration\_ms": 82.4  
  }  
}

**The developer writes the business logic. The metaclass writes the observability.**

## **Singleton Pattern for Shared Memory**

WorkingMemoryRAM uses the Singleton pattern to ensure all agents share the same workspace:

class WorkingMemoryRAM:  
    """  
