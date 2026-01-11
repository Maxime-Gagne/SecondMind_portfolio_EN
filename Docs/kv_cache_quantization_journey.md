\[\!NOTE\]

# **🧠 130K Context Tokens on an RTX 3090**

**LLM Optimization | KV Cache Quantization | Client-Server Architecture**

### **📊 Key Results**

* **130,000 Context Tokens**  
* **\-50% VRAM Usage**  
* **\+179% Throughput (23 → 64 t/s)**  
* **Dual-LLM Workflow (14B \+ 3B simultaneously)**

**Hardware:** NVIDIA RTX 3090 (24 GB VRAM) — *Consumer-grade hardware, professional-grade results.*

## **🎯 The Challenge**

My cognitive AI system, **SecondMind**, relies on a dual-LLM architecture: a primary model (**Qwen2.5-14B**) for reasoning and a judge model (**Qwen2.5-3B**) for validation. The objective was to extend the context window from 32K to 128K tokens for long-document analysis.

### **The Mathematical Problem**

A 128K token context with an FP16 KV cache theoretically requires **36.2 GB of VRAM** — impossible on a 24 GB card. The obvious solution was KV cache quantization, promising a 50% to 75% reduction in memory footprint.

**The problem: It didn't work.**

## **🔍 Investigation**

A systematic approach revealed three critical issues:

1. **Corrupted CUDA Bindings:** The pre-compiled wheel for llama-cpp-python was compiled without CUDA support despite its labeling. Diagnostic: llama\_print\_system\_info() mentioned no CUDA device.  
2. **Missing DLLs:** ggml-cuda.dll and cublas64\_12.dll were absent from the installed package.  
3. **Flash Attention Incompatibility:** KV quantization requires Flash Attention, which does not compile correctly on Windows with Python bindings. An architectural dead-end.

## **🚀 Architectural Pivot**

Rather than fighting the limitations of Python bindings, I pivoted to the **native llama.cpp server (CLI)** using HTTP communication.

**Why this choice:**

* **Official CUDA Builds:** Pre-compiled and tested.  
* **Out-of-the-box Functionality:** Flash Attention and KV quantization work immediately.  
* **Better Isolation:** A server crash does not kill the main orchestration process.  
* **Negligible Overhead:** HTTP latency (\~1-2ms) is insignificant compared to inference time (\~15ms/token).

## **📈 Benchmarking & Optimization**

### **Verification Methodology**

For each configuration, a 4-step validation protocol was used:

1. **Server Log Validation:** Checking llama\_kv\_cache: CUDA0 KV buffer size to confirm effective quantization.  
2. **GPU Monitoring:** Real-time VRAM usage measurement via nvidia-smi.  
3. **Performance Testing:** Generating 1000 tokens with a constant prompt to measure throughput.  
4. **Quality Check:** Validating coherence over multi-turn conversations to detect degradation.

### **Detailed Results**

| Config | Context | Cache | VRAM Cache | Total VRAM | Throughput | 1K Tokens Time |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Baseline** | 32K | FP16 | 6,144 MB | 14.5 GB | 23 t/s | 43.5 s |
| **Config A** | 32K | Q8\_0 | 3,264 MB | 10.6 GB | 63.9 t/s | 15.6 s |
| **Config B** | 64K | Q8\_0 | 6,528 MB | 21.4 GB | 65.8 t/s | 15.2 s |
| **Config C**\* | 128K | Q4\_0 | 6,912 MB | 21.9 GB | 64.2 t/s | 15.6 s |

\* *Selected configuration.*

## **💡 Key Observations**

1. **VRAM Savings (Config A):** 47% reduction in cache size (6144 → 3264 MB) and 27% reduction in total VRAM usage.  
2. **Counter-intuitive Performance Boost:** Throughput increased by **2.7x (23 → 64 t/s)**. Cause: Better CUDA kernel efficiency with quantized operations.  
3. **The Ideal Compromise (Config B):** 2x context extension (32K → 64K) while maintaining high throughput and a comfortable VRAM margin (2.6 GB free).  
4. **Maximum Configuration (Config C):** 4x context extension (32K → 128K). Q4 quantization offsets the 2x larger context. No quality degradation detected in multi-turn tests.

## **🌎 Real Impact**

| Metric | Baseline | Optimized | Gain |
| :---- | :---- | :---- | :---- |
| **Max Context** | 32,768 | 131,072 | **\+300%** |
| **VRAM (128K theoretical)** | 36.2 GB | 21.9 GB | **\-39%** |
| **Throughput** | 23 t/s | 64.2 t/s | **\+179%** |
| **VRAM Efficiency** | 2,257 tok/GB | 5,983 tok/GB | **\+165%** |

## **📜 Principles**

"Pre-compiled wheels lie."  
Always verify CUDA support with diagnostic tools. Labels guarantee nothing.  
"Architectural flexibility \> Monolithic optimization."  
The pivot to a client-server architecture solved issues that were insoluble in an integrated approach.  
"Measure, don't assume."  
Systematic benchmarking contradicted the "obvious": throughput increased where degradation was expected.  
"Don't accept limitations as finality."  
"128K won't fit on 24 GB" — proven false. "23 t/s is the maximum" — reached 64 t/s. Technical investigation opens possibilities.

*Maxime Gagné — Cognitive Architect — SecondMind | November 2025*