# Copilot / AI Agent Instructions for this repo

Overview
- Small AI project scaffold. Top-level files: `app.py` (Streamlit UI placeholder), `mcp_server.py` (MCP agent server placeholder), `requirements.txt`, plus `Data/` and `Scr/` directories.
- Current implementation files are empty; guidance below is inferred from `requirements.txt` and directory names. Confirm or correct assumptions when editing.

Big-picture architecture (inferred)
- Frontend: `app.py` — intended to be a `streamlit` UI that drives user interactions and visualization.
- Agent/Backend: `mcp_server.py` — intended to run an MCP-compatible agent/service that orchestrates LLM chains and agents.
- Data and storage: `Data/` likely stores uploaded documents, Chroma DB files, or built indexes. Keep vector DB files out of source control.
- Orchestration: `langchain` coordinates chains/agents; local vector store is `chromadb` with `langchain-chroma` adapter; embeddings use `sentence-transformers` / HuggingFace.

Key integration points and libraries
- `langchain`, `langchain-community`: orchestration and agent frameworks.
- `chromadb`, `langchain-chroma`: local vector database; expect code that instantiates a Chroma client and persists to `Data/`.
- `sentence-transformers`, `langchain-huggingface`: local embedding models (privacy-first embedding flow).
- `pypdf`: PDF parsing for ingestion pipelines.
- `mcp`: the Agent Protocol package — `mcp_server.py` should import and register MCP agents.
- `streamlit`: lightweight UI runner in `app.py`.

Project-specific workflows (how an agent should act)
- Local dev setup:
  - Create a virtual environment and install deps: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  - Quick dependency sanity check: `python -c "import langchain, chromadb, sentence_transformers, streamlit"`
- Run UI: `streamlit run app.py` (if `app.py` implements a Streamlit app).
- Run MCP server: `python mcp_server.py` (the file is currently empty; follow MCP docs to register agents).
- Indexing pipeline: expect ingestion code to parse PDFs with `pypdf`, embed with `sentence-transformers`, and write into Chroma under `Data/` (do long-running indexing offline, not in request handlers).

Coding patterns to follow (specific to this repo)
- Keep heavy initialization (model loading, large embeddings, Chroma clients) in module-level singletons or startup hooks so handlers reuse them.
- Persist Chroma database under `Data/` and never commit built DB files.
- Use environment variables for configurable model names, API keys, and file paths. The presence of `python-dotenv` in `requirements.txt` suggests `.env` usage.
- Avoid synchronous, blocking work in request paths or Streamlit callbacks — run ingestion/indexing as a separate script or background thread/process.

Examples and snippets to follow repository conventions
- Start Streamlit UI (assumes `app.py` exists as an app):
  - `streamlit run app.py`
- MCP server skeleton (place in `mcp_server.py`):
  - `from mcp import AgentServer
    # register agents, load models, start server`

What to look for and verify when coding
- Confirm where Chroma persistence is wired (search for `chromadb.Client` or `Chroma` usage).
- Confirm how embeddings are created — prefer `sentence-transformers` local models over remote calls when present.
- Ensure `Data/` contains only source documents and not large binary DBs. Add `.gitignore` entries if missing.

If you modify or add files
- Update this file with any concrete workflows discovered (e.g., commands, startup flags, specific filenames under `Data/`), so future AI agents can operate deterministically.

Notes / Assumptions
- This guidance is based solely on the repository layout and `requirements.txt`. Several top-level source files are empty; please provide implementation or point to where agent registration and ingestion live so these instructions can be refined.

Questions for the repo owner
- Where are ingestion pipelines and Chroma initialization located (file path)?
- Do you use a `.env` file for configuration? If so, which variables are required (MODEL_NAME, CHROMA_DIR, LOG_LEVEL, etc.)?
- Should built vector DB files live in `Data/` or under a separate `var/` folder excluded from git?

End of file — update with concrete locations when available.
