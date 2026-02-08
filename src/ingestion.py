import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DATA_PATH = "./data/resumes"
DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def ingest_resumes():
    # 1. Load PDF documents
    documents = []
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_PATH, filename))
            documents.extend(loader.load()) # load all pages of the PDF
    
    # 2. splitting the documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
    )
    chucks = text_splitter.split_documents(documents)

    # 3. Embed and Store
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # 4. Create/Update ChromaDB
    db = Chroma.from_documents(
        documents=chucks,
        embedding=embeddings,
        persist_directory=DB_PATH,
    )

    print(f"Ingested {len(chucks)} document chunks into ChromaDB at {DB_PATH}")

if __name__ == "__main__":
    ingest_resumes()


