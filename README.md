# SmartFix — AI-Powered DevOps Equipment Troubleshooting Platform

> 📘 **Comprehensive Documentation**: For the complete start-to-finish architectural rationale, Week 3 & Week 4 objective implementations, Mermaid flowcharts, and cross-platform (Linux/macOS/Windows) setup instructions, see the master guide: **[COMPLETE_PROJECT_GUIDE_WEEK3_WEEK4.md](./COMPLETE_PROJECT_GUIDE_WEEK3_WEEK4.md)**.

SmartFix is an AI-powered equipment troubleshooting and maintenance platform designed for DevOps and industrial/appliance engineering environments.

The safety subsystem is driven by **Meta's Llama Guard 3 (1B)** (`llama-guard3:1b` via the local Ollama API) to classify operational hazards, enforce deterministic circuit breaking before generative model inference, and mandate Lockout/Tagout (LOTO) safety protocols.

It provides six tailored interfaces in the unified Vue 3 frontend:
1. **Technician Troubleshooting**: Diagnostic interface with dynamic model switching (`Qwen 2.5 Coder 1.5B`, `Code Llama 7B`, `StarCoder2 3B`), automated safety alerts, spare parts inventory lookup, and technician dispatch tickets.
2. **Compare Models**: Real-time side-by-side execution comparing Code Llama, StarCoder2, and Qwen 2.5 Coder on identical prompts with latency, CPU/RAM footprint, and token throughput readouts.
3. **7-Category Evaluation Benchmark Dashboard**: Quantitative evaluation scorecard displaying metrics across all 7 software engineering categories (Accuracy, Relevance, Retrieval Quality, Hallucination Rate, Test-Pass Rate, Latency, and Resource Utilization).
4. **Data Layer Architecture**: Interactive visualization of vector embeddings, ChromaDB collections, and SQLite schema storage.
5. **Enterprise AI Safety Guardrails Suite**: Live verification bench powered by **Meta's Llama Guard 3 (1B)** demonstrating semantic circuit breaking, prompt injection defense, sandbox security, fact grounding, and schema validation.
6. **Knowledge Base Admin**: Document management for uploading manuals (`.pdf`, `.txt`, `.md`), chunk inspection, and vector similarity search observability.

---

## Architecture Diagram

```text
                               +----------------------------------+
                               |     Vue 3 + Vite Frontend        |
                               | (Technician, Admin, Guardrails)  |
                               +-----------------+----------------+
                                                 |
                                                 v
                               +----------------------------------+
                               |    Orchestrator Service (:8000)   |
                               |  Coordinates Microservices Flow  |
                               +-----------------+----------------+
                                                 |
        +------------------+------------------+--+-------------------+------------------+
        |                  |                  |                      |                  |
        v                  v                  v                      v                  v
+---------------+  +---------------+  +---------------+      +---------------+  +---------------+
| Equipment Svc |  |  History Svc  |  |  RAG Service  |      | Safety Engine |  |Spare Parts Svc|
|    (:8002)    |  |    (:8004)    |  |    (:8001)    |      |    (:8003)    |  |    (:8005)    |
+---------------+  +---------------+  +-------+-------+      +-------+-------+  +---------------+
                                              |                      |
                                              v                      v
                                    +-------------------+    +---------------+
                                    | ChromaDB + SQLite |    | Local Ollama  |
                                    | (Local Vector DB) |    | Llama Guard 3 |
                                    +-------------------+    +---------------+
                                              |
        +-------------------------------------+-------------------------------------+
        |                                                                           |
        v (BLOCKED: Circuit Breaker Intercept)                                      v (ALLOWED / WARNING)
+---------------+                                                           +---------------+
| Ticket Svc    |                                                           | LLM Svc       |
|    (:8006)    |                                                           |    (:8007)    |
+---------------+                                                           +-------+-------+
                                                                                    |
                                                                                    v
                                                                            +---------------+
                                                                            | Local Ollama  |
                                                                            |  Code Models  |
                                                                            +---------------+
```

---

## Safety Architecture & Llama Guard 3

SmartFix integrates **Meta's Llama Guard 3 (1B)** (`llama-guard3:1b`) as its core safety classification engine.
* **Pre-LLM Circuit Breaking**: When a technician query involves high-voltage live access (>400V), charged capacitors, spinning drum door bypass, or adversarial prompt injection, Llama Guard 3 classifies the request as `unsafe` (`BLOCKED`).
* **Deterministic Circuit Breaker**: The central orchestrator intercepts execution **before** generative LLM inference (`/llm/generate` or `/llm/compare`), prevents model hallucination or jailbreaks, creates a critical service ticket (`/tickets/create`), and returns mandatory Lockout/Tagout (LOTO) precautions.
* **Resilience Fallback**: If the local Ollama server is temporarily offline or unreachable, the safety engine automatically engages a deterministic fallback evaluator to maintain continuous protection without service crashes.

---

## Exercise Progression

- **Exercise 1 — Basic LLM Application**: Vue 3 + Vite frontend, FastAPI backend, Ollama + Code Llama integration, execution-flow visualization.
- **Exercise 2 — Technical Knowledge Base & Vector DB**: Technical manual ingestion (`.txt`, `.md`, `.pdf`), text extraction (`pypdf`), fixed-size overlapping chunking, Ollama embeddings (`nomic-embed-text`), SQLite metadata tracking, and ChromaDB persistent vector storage.
- **Exercise 3 — RAG Pipeline**: Question → Query Embedding → Vector Similarity Search → Top-K Relevant Chunks → Context Construction → Code Llama Answer Synthesis. RAG retrieval & similarity score observability.
- **Exercise 4 — Microservices & Orchestrator**: Decoupled microservices architecture across 8 API services with an AI Safety Engine powered by **Meta's Llama Guard 3 (1B)**, deterministic circuit breaking (`ALLOWED`, `WARNING`, `BLOCKED`), and real step-by-step orchestrator execution traces.
- **Exercise 5 — Containerization with Docker**: Containerized microservices, Nginx frontend, multi-stage Dockerfiles, and `docker-compose.yml` orchestration.

---

## Microservices API Reference

| Service | Port | Key Endpoints | Description |
|---|---|---|---|
| **Orchestrator** | 8000 | `POST /ask`, `POST /orchestrate`, `POST /compare`, `POST /safety/guardrails/evaluate` | Coordinates microservices, enforces circuit breakers, returns diagnostic answers & execution traces |
| **RAG Service** | 8001 | `POST /rag/retrieve`, `POST /documents/upload`, `GET /vectors/{id}`, `GET /kb/stats` | Manages technical manuals, embeddings, and vector similarity search |
| **Equipment Service** | 8002 | `GET /equipment/{id}`, `GET /equipment` | Returns structured specifications for industrial machinery (`EQ-XXXX`) and domestic appliances (`HA-XXXX`) |
| **Safety Engine** | 8003 | `POST /safety/evaluate`, `POST /safety/guardrails/evaluate` | AI Safety Engine powered by **Llama Guard 3 (1B)** via Ollama API returning `ALLOWED`, `WARNING`, or `BLOCKED` |
| **History Service** | 8004 | `GET /history/{id}` | Returns historical maintenance logs, failure events, and past corrective actions |
| **Spare Parts Service** | 8005 | `GET /spare-parts/{id}` | Returns compatible spare parts inventory, stock status, and bin locations |
| **Ticket Service** | 8006 | `POST /tickets/create`, `GET /tickets` | Generates and tracks technician field dispatch tickets (`TKT-XXXX`) |
| **LLM Gateway** | 8007 | `POST /llm/generate`, `POST /llm/compare` | Interfaces with Ollama to run Code Llama, StarCoder2, and Qwen 2.5 Coder |

---

## Running the Application

### Method A: Local Microservices (Development)

1. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r services/knowledge-base/requirements.txt
   ```

2. **Ingest Technical Manuals into ChromaDB**:
   ```bash
   python ingest_manuals.py
   ```

3. **Start Local Ollama & Pull Models**:
   ```bash
   ollama serve
   # Core Models
   ollama pull llama-guard3:1b
   ollama pull nomic-embed-text
   ollama pull qwen2.5-coder:1.5b
   # Optional Comparative Models
   ollama pull codellama:7b
   ollama pull starcoder2:3b
   ```

4. **Start Microservices Platform**:
   ```bash
   # Option 1: Automatic runner for all 8 microservices
   python run_all.py

   # Option 2: Linux/macOS shell script
   chmod +x start_services.sh
   ./start_services.sh
   ```

5. **Start Vue 3 Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://127.0.0.1:5173` in your browser.

---

### Method B: Docker & Docker Compose

1. **Build and Launch Containerized Services**:
   ```bash
   docker-compose up --build
   ```

2. Open `http://localhost:5173` for the Vue 3 Frontend.

---

## Data Sources & Supported Equipment

- **Technical Manuals**: Public/open maintenance specs for industrial hydraulic pressure pumps (`HP-5000`), conveyor belt systems (`CB-200`), 3-phase electric motors (`IM-750`), and household appliances stored in `data/documents/uploads/`.
- **Industrial Equipment Database**:
  - `EQ-1023`: High-Pressure Hydraulic Pump Assembly (`HP-5000`)
  - `EQ-2045`: Automated Package Transport Conveyor (`CB-200`)
  - `EQ-3081`: 75kW 3-Phase AC Induction Motor Drive (`IM-750`)
- **Household Appliance Database**:
  - `HA-MICRO-01`: Panasonic Inverter Microwave/Convection Oven
  - `HA-TOAST-02`: Hamilton Beach 4-Slice Smart Toaster
  - `HA-AIRFRY-03`: PowerXL Vortex Rapid-Air Digital Air Fryer
  - `HA-WASH-04`: Bosch Serie 6 Front-Load Washing Machine
  - `HA-OVEN-05`: Whirlpool 6th Sense Built-In Pyrolytic Oven
  - `HA-CHIM-06`: Faber 90cm Auto-Clean Kitchen Chimney / Range Hood

---

## License

MIT — see [LICENSE](LICENSE).
