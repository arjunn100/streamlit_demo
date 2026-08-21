import streamlit as st

from utils import extract_pdf, create_vector_text
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

st.set_page_config(page_title="AI kishmish")

st.title("Kaju")

resume_file = st.file_uploader("Upload resume in PDF", type=["pdf"])

jd_text = st.text_area("Paste job description")

if st.button("Analyze"):

    if resume_file:

        # EXTRACT RESUME
        resume_text = extract_pdf(resume_file)

        # Combine resume + JD
        combine_text = resume_text + "\n\n" + jd_text

        # Create vector store
        vectorstore = create_vector_text(combine_text)

        retrieve = vectorstore.as_retriever()

        # Load and integrate LLM model
        llm = Ollama(model="gemma2:latest")

        # Prompt template design
        prompt = ChatPromptTemplate.from_template("""
        You are an AI placement coach for kishmish.

        Context:
        {context}

        Question:
        {question}

        Provide:

        1. Skills Gap Analysis
        2. Missing Technology
        3. ATS Score (0-100)
        4. Technical interview questions
        5. Resume improvement suggestions
        """)

        chain = (
            {
                "context": retrieve,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(
            "Analyze resume against job description"
        )

        st.subheader("Analysis Result")
        st.write(response)

    else:
        st.warning("Please upload resume and job description")