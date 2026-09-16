# SmartFix System Bug Analysis & Root-Cause Remediation Report

## 1. Executive Summary

This document presents a comprehensive **Bug Analysis & System Vulnerability Audit** for the **SmartFix AI Equipment Troubleshooting System**. The analysis categorizes software defects, architectural anti-patterns, data retrieval anomalies, and LLM integration failures identified across the SmartFix microservice ecosystem.

Each identified bug is analyzed using standard software engineering diagnostic fields:
- **Bug ID & Classification**
- **Symptom & Stack Trace / Impact**
- **Root Cause Analysis**
- **Code snippet comparison (Flawed vs. Remediated Code)**
- **Verification & Testing Protocol**

---

## 2. Category 1: Vector Database & RAG Pipeline Bugs

### Bug BUG-01: ChromaDB NumPy Array Truthiness Evaluation (`ValueError`)

- **Classification**: Data Pipeline / Runtime Crash
- **Affected File**: `services/knowledge-base/vector_store.py`
- **Symptom**:
  ```python
  ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
  ```
- **Root Cause**:
  When ChromaDB returns vector embeddings as a multi-dimensional `numpy.ndarray`, performing Python's native boolean check (`if embedding:`) fails because NumPy overrides `__bool__()` to prevent ambiguous array truthiness checks.
- **Flawed Implementation**:
  ```python
  # FLAWED CODE
  sample = collection.get(limit=1, include=["embeddings"])
  embeddings = sample.get("embeddings")
  if embeddings:  # Raises ValueError when embeddings is numpy.ndarray
      return len(embeddings[0])
  ```
- **Remediated Implementation**:
  ```python
  # REMEDIATED CODE
  sample = collection.get(limit=1, include=["embeddings"])
  embeddings = sample.get("embeddings")
  if embeddings is not None and len(embeddings) > 0 and embeddings[0] is not None:
      return len(embeddings[0])
  ```
- **Verification**: Verified using unit test `test_vector_store_numpy_truthiness()` with a mock 384-dimensional NumPy array embedding.

---

### Bug BUG-02: Boundary Truncation of Technical Specs in Fixed-Length Chunking

- **Classification**: RAG Pipeline / LLM Hallucination Vulnerability
- **Affected File**: `services/knowledge-base/extractors.py`
- **Symptom**:
  The LLM generates incorrect operating parameters (e.g. claiming an oven door unlocks at `500°C` instead of `260°C`).
- **Root Cause**:
  The flat character-based chunking extractor splits text strictly at `400` characters without preserving sentence boundaries or numeric specification tables. Crucial numbers (e.g. `260°C` safe threshold) get severed across adjacent vector chunks, leaving incomplete context for vector retrieval.
- **Flawed Implementation**:
  ```python
  # FLAWED CODE: Fixed character slicing
  chunks = [text[i:i+400] for i in range(0, len(text), 400)]
  ```
- **Remediated Implementation**:
  ```python
  # REMEDIATED CODE: Sentence and layout-aware recursive chunking with 100-char overlap
  from langchain_text_splitters import RecursiveCharacterTextSplitter

  splitter = RecursiveCharacterTextSplitter(
      chunk_size=500,
      chunk_overlap=100,
      separators=["\n\n", "\n", ". ", "; ", " "]
  )
  chunks = splitter.split_text(text)
  ```
- **Verification**: Verified via RAG trajectory trace on `TASK-05` (pyrolytic oven door unlock temperature).

---

### Bug BUG-03: Unhandled Empty Vector Search Results (`KeyError` / Prompt Degradation)

- **Classification**: RAG Service / Null Pointer Risk
- **Affected File**: `services/rag/rag_engine.py`
- **Symptom**:
  When a query yields zero matching vector chunks in ChromaDB, context string construction attempts to index missing fields, or passes raw empty constructs to LLM prompt formatters.
- **Root Cause**:
  Lack of default fallback initialization when `raw_matches` is empty.
- **Remediated Implementation**:
  ```python
  # REMEDIATED CODE
  constructed_context = (
      "\n\n".join(context_blocks)
      if context_blocks
      else "No relevant technical documentation chunks found in vector database."
  )
  ```

---

## 3. Category 2: LLM Service & Model Identifier Bugs

### Bug BUG-04: Ollama Model Identifier Mismatch (`HTTP 404 Not Found`)

- **Classification**: Integration / HTTP API Error
- **Affected File**: `evaluation/benchmark.py` & `services/llm/main.py`
- **Symptom**:
  During benchmark execution, querying model `codellama:7b` returns `HTTP 404 Not Found` from Ollama's `/api/generate` endpoint.
- **Root Cause**:
  The local Ollama instance registered the model under `codellama:latest` or `codellama`, whereas the evaluation harness passed hardcoded string `codellama:7b`.
- **Remediated Implementation**:
  Added dynamic candidate tag probing:
  ```python
  candidates = [model_id, fallback_id, f"{fallback_id}:latest"]
  active_model = model_id
  for cand in candidates:
      if cand in installed_ollama_models:
          active_model = cand
          break

  # Fallback HTTP probe loop across candidates if HTTP 404 is encountered
  for try_tag in tags_to_try:
      resp = await client.post(OLLAMA_URL, json={"model": try_tag, "prompt": prompt})
      if resp.status_code == 200:
          active_model = try_tag
          break
  ```
- **Verification**: Verified clean execution of `evaluation/benchmark.py` across all 4 LLM models without 404 errors.

---

### Bug BUG-05: Gateway Time-Out (`HTTP 504`) on Heavyweight Reasoning Models

- **Classification**: Network / Performance Bottleneck
- **Affected File**: `frontend/nginx.conf` & microservice HTTP clients
- **Symptom**:
  `HTTP 504 Gateway Time-out` when requesting troubleshooting guidance with `codellama` (7B).
- **Root Cause**:
  On CPU-only hardware or unaccelerated laptops, 7B parameter LLMs take 20–40 seconds to finish generation. Default Nginx/HTTPX timeouts were set to 10 or 15 seconds.
- **Remediated Implementation**:
  - Increased Nginx proxy timeouts (`proxy_read_timeout 300s; proxy_connect_timeout 300s;`).
  - Set `httpx.AsyncClient(timeout=300.0)` across Python microservice connectors.

---

## 4. Category 3: Deterministic Safety Engine & Compliance Bugs

### Bug BUG-06: Potential Safety Override by Generative LLMs

- **Classification**: Safety Compliance / Security Risk
- **Affected File**: `services/safety/main.py` & `services/llm/main.py`
- **Symptom**:
  An LLM might recommend probing live 400V AC terminals with a standard multimeter if pre-training bias overrides prompt directives.
- **Root Cause**:
  Relying solely on LLM prompt engineering for safety compliance is non-deterministic and susceptible to jailbreaking or prompt leakage.
- **Remediated Implementation**:
  Implemented an architectural **Deterministic Circuit Breaker**:
  1. The Safety Engine microservice evaluates safety rules *before* invoking the LLM.
  2. If safety decision is `BLOCKED`, the Orchestrator intercepts execution, prevents LLM inference, and directly returns safety enforcement LOTO guidelines.
- **Code Reference**:
  ```python
  # Hard deterministic block for live 400V terminal inspection
  if "400v" in q_lower and "live" in q_lower:
      decision = "BLOCKED"
      warnings.append("BLOCKED: Accessing live 400V terminals poses lethal arc flash risk.")
  ```

---

## 5. Category 4: Microservice Resilience & Exception Handling

### Bug BUG-07: Orchestrator Cascading Failure on Downstream Microservice Unavailability

- **Classification**: Architecture / Resilience
- **Affected File**: `backend/main.py` / Orchestrator main loop
- **Symptom**:
  If the `spare-parts` or `equipment` microservice crashes or is offline, the entire Orchestrator returns `HTTP 500 Internal Server Error`.
- **Root Cause**:
  Unwrapped HTTP calls without `try-except` blocks or microservice fallback synthesis.
- **Remediated Implementation**:
  Graceful fallback wrappers around all downstream service HTTP clients:
  ```python
  try:
      parts_resp = await client.get(f"{SPARE_PARTS_URL}/spare-parts/{eq_id}")
      parts_data = parts_resp.json() if parts_resp.status_code == 200 else {"parts": []}
  except Exception as exc:
      logger.warning(f"Spare parts service offline: {exc}")
      parts_data = {"parts": [], "note": "Service offline"}
  ```

---

## 6. Summary Matrix of Bugs & Status

| Bug ID | Component | Description | Impact Level | Status |
|---|---|---|:---:|:---:|
| **BUG-01** | Vector Store | ChromaDB NumPy array truthiness `ValueError` | **CRITICAL** | FIXED |
| **BUG-02** | RAG Extractor | Character chunk boundary spec truncation | **HIGH** | FIXED |
| **BUG-03** | RAG Engine | Unhandled empty search result context formatting | **MEDIUM** | FIXED |
| **BUG-04** | LLM Gateway | Ollama model tag mismatch `HTTP 404` | **HIGH** | FIXED |
| **BUG-05** | Nginx Proxy | Gateway Timeout `HTTP 504` on 7B models | **HIGH** | FIXED |
| **BUG-06** | Safety Engine | Risk of LLM overriding lethal hazard LOTO directives | **CRITICAL** | FIXED |
| **BUG-07** | Orchestrator | Cascading microservice failure on downstream disconnect | **MEDIUM** | FIXED |

---

## 7. Conclusion & Best Practices

To ensure long-term stability and reliability in industrial AI applications like SmartFix, the following engineering standards are established:
1. **Never evaluate array truthiness directly** on NumPy/ChromaDB data structures; always check explicit length or identity (`is not None and len(...) > 0`).
2. **Enforce deterministic safety circuit breakers** before LLM generation to prevent safety policy violations.
3. **Implement multi-candidate model resolution** and standard 300s timeout thresholds to prevent HTTP 404 / 504 errors across local LLM runtimes.
