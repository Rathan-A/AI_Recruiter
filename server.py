# # from fastmcp import FastMCP
# # import chromadb
# # from chromadb.utils import embedding_functions
# # from langchain_community.document_loaders import PyPDFLoader
# # import os


# # --- SERVER SETUP ---
# mcp = FastMCP("Resume Screening MCP Server")

# # Initilialize ChromaDB connection
# CHROMA_PATH = "./chroma_db"
# client = chromadb.PersistentClient(path=CHROMA_PATH)
# # ef = embedding_functions.HuggingFaceEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")
# ef = embedding_functions.SentenceTransformerEmbeddingFunction(
#     model_name="all-MiniLM-L6-v2"
# )
# collection = client.get_or_create_collection(
#     name="resumes_collection", embedding_function=ef
# )


# @mcp.tool()
# def search_candidates(query: str, n_results: int = 5):
#     """
#     Semantic search for candidates based on a job description or skill query.
#     Returns the most relevant resume segments.
#     """
#     results = collection.query(
#         query_texts=[query],
#         n_results=n_results,
#     )

#     """
#     results = {
#         "documents": [[doc1, doc2, ...]],
#         "metadatas": [[meta1, meta2, ...]]
#     }
#     """

#     # Format results for LLM
#     output = []
#     for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
#         source = meta.get("source", "unknown")
#         output.append(f"Source: {source}\nContent: {doc}\n")

#         """
#         SOURCE: file1.txt
#         CONTENT: ChromaDB is a vector database...

#         """

#     return "\n".join(output)


# @mcp.resource("resume://{filename}")
# def get_full_resume(filename: str):
#     """
#     Retrieve the full resume content for a given filename.

#     Args:
#         filename: The name of the resume file located in ./resume folder.
#     """

#     file_path = os.path.join(RESUME_DIR, filename)

#     if not os.path.exists(file_path):
#         return f"Error: File '{filename}' not found in {RESUME_DIR}."

#     try:
#         loader = PyPDFLoader(file_path)
#         pages = loader.load()
#         full_text = f"--- FULL CONTENT OF {filename} ---\n\n"
#         full_text += "\n".join([page.page_content for page in pages])
#         return full_text

#     except Exception as e:
#         return f"Error reading file: {str(e)}"


# if __name__ == "__main__":
#     mcp.run()


from fastmcp import FastMCP
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFLoader
import os
import sys

# --- 1. SETUP PATHS (Dynamic & Absolute) ---
# Get directory of THIS script
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# If server.py is in the root, PROJECT_ROOT is just CURRENT_SCRIPT_DIR
# If server.py is in src/, PROJECT_ROOT is one level up.
# Based on your path '/AI Project/server.py', we assume root:
PROJECT_ROOT = CURRENT_SCRIPT_DIR

# Define paths relative to the project root
RESUME_DIR = os.path.join(PROJECT_ROOT, "data", "resumes")
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_db")
COLLECTION_NAME = "langchain"


# --- 2. LOGGING FUNCTION (Crucial: Writes to stderr, NOT stdout) ---
def log(message):
    print(f"[MCP LOG] {message}", file=sys.stderr)


log(f"🚀 Starting server...")
log(f"📂 Project Root: {PROJECT_ROOT}")
log(f"📂 Database: {CHROMA_PATH}")

# --- 3. INITIALIZE SERVER ---
mcp = FastMCP("Resume Screening MCP Server")

try:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Try to get collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        log(f"✅ Connected to collection: {COLLECTION_NAME}")
    except Exception:
        log("⚠️ Collection not found, creating new one...")
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=ef
        )

except Exception as e:
    log(f"❌ CRITICAL DB ERROR: {e}")


# --- 4. DEFINE TOOLS ---
@mcp.tool()
def search_candidates(query: str, n_results: int = 5) -> str:
    """Semantic search for candidates based on a job description."""
    try:
        log(f"🔎 Searching for: {query}")
        results = collection.query(query_texts=[query], n_results=n_results)

        if not results["documents"] or not results["documents"][0]:
            return "No matching candidates found."

        output = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            source = meta.get("source", "unknown")
            if "/" in source:
                source = source.split("/")[-1]
            output.append(
                f"--- CANDIDATE EVIDENCE ---\nSource: {source}\nContent: {doc}\n"
            )

        return "\n".join(output)
    except Exception as e:
        return f"Error during search: {str(e)}"


@mcp.resource("resume://{filename}")
def get_full_resume(filename: str) -> str:
    """Retrieve full resume content."""
    file_path = os.path.join(RESUME_DIR, filename)
    log(f"📄 Reading file: {file_path}")

    if not os.path.exists(file_path):
        return f"Error: File '{filename}' not found."

    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return "\n".join([page.page_content for page in pages])
    except Exception as e:
        return f"Error reading file: {str(e)}"


if __name__ == "__main__":
    mcp.run()
