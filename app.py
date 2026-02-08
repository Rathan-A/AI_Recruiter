import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.agents import get_screener_chain, get_scoring_agent

# Setting up db connection for app
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 5}) # Turn my database into a search tool

st.title("AI-Powered Resume Screener")
st.subheader("Multi-Agent RAG System for Technical Recruitment")

# Input
jd = st.text_area("Enter Job Description / Skill Set:", height=200)

if st.button("Screen Candidates"):
    with st.spinner("Screening candidates..."):

        # 1. Retrival and Screening
        screener_chain = get_screener_chain(retriever)
        screening_analysis = screener_chain.invoke(jd)

        # 2. Scoring
        scoring_agent = get_scoring_agent()
        score = scoring_agent.invoke({"analysis": screening_analysis})

        # Display Results
        st.success("Screening Complete!. Relevance Score: " + score)

        col1, col2 = st.columns(2)  # 2 columns for side by side display

        with col1:
            st.markdown("### Screening Analysis")
            st.write(screening_analysis)

        with col2:
            st.markdown("### Context Retrieved")
            docs = docs = retriever.invoke(jd)
            for i, doc in enumerate(docs):
                with st.expander(
                    f"Evidence {i+1} (Source: {doc.metadata.get('source', 'N/A')})"
                ):
                    st.caption(doc.page_content)
