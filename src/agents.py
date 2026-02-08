import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Define the Gemini LLM function
def get_llm():
    """Returns the Gemini 2.5 Flash model instance."""
    if "GOOGLE_API_KEY" not in os.environ:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0
    )


def get_screener_chain(retriever):
    """
    Agent 1: The Retriever / Screener Agent
    Fetches the context and provide the primary match summary.
    """

    template = """
    You are an expert Technical Recruiter.

    JOB DESCRIPTION: {jd}
    
    CANDIDATE FRAGMENTS:
    {context}

    Task: Identify if the candidates are a potential match.
    Higlight key matching skills/experience and missing skills/experience.
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {
            "context": retriever,
            "jd": RunnablePassthrough(),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    return chain # he variable chain is a specific LangChain object type called a RunnableSequence


def get_scoring_agent():
    """
    Agent 2: The Scorer
    Assigns a numerical score based on the screener analysis.
    """

    template = """
    Based on the following screening analysis, assign a score from 1 to 10

    Analysis: {analysis}

    Return only the numerical score.
    """

    prompt = ChatPromptTemplate.from_template(template)

    return prompt | get_llm() | StrOutputParser()
