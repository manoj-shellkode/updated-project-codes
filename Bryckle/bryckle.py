import streamlit as st
from langchain.llms.bedrock import Bedrock
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
import boto3
import botocore
import os

def upload_and_preprocess():
    st.title("Bryckel")

    config = botocore.config.Config(
        read_timeout=900,
        connect_timeout=900,
        retries={"max_attempts": 0}
    )

    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
        config=config,
    )

    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Save the uploaded file locally
        with open(os.path.join("uploads", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_path = os.path.join("uploads", uploaded_file.name)

        loader = PyPDFLoader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=0)
        texts = text_splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.from_documents(documents=texts, embedding=embeddings)

        template = """
            You will be given a query, Your task is to find an answer or give information about the query with respect to the document by performing a similarity search.
            Consider the following conditions,
            - If query is a topic, look for information or statements or sentences which are related to the query in the document.
            - The answer does not need to be specifically related, it can be loosely related as well.
            - If you find any statements that are directly related to the query, then explain those statements in easy or layman terms, so someone with no expertise in that field can understand.
            - If query is a question, understand the context of query and then look for similar statements or sentences in the document which also have the same context.
            - It is not necessary to return direct statements from the document as an answer. You can also return loosely related answers to the query.
            - If you cannot find any direct statements or directly relevant answers, do not return that you cannot find any direct statements. Then, you have to perform a semantic search instead of looking for exact words in the document, that is, understanding the context from the query and looking for something similar in the document.
            - It is not mandatory to look for direct statements, you can also look at statements with a similar meaning and context.
            - The output should just be a bullet list of points which has the summary of all points obtained from the search
            - It is fine if you cannot find any directly related statements in the document. You can look for sentences with similar meaning and can also return loosely related answers.
            - Elaborate the answer as much as you can.
            Instructions:
                    - If the exact answer to the question is not found on the given document simply print 'The document is silent on this'
                    for example:(if the question is)
                    Example question: Does the lessee have option of purchasing the space and under what conditions?
                                            so if the exact answer is present in the document then print that answer or else print 'There is no mention of a purchase option' and'The document is silent on this'
                follow the same instruction for all the questions don't mention anything other than this
            {context}
            {question}
        """
        qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        # Save variables to session state
        st.session_state.db = db
        st.session_state.qa_prompt = qa_prompt
        st.session_state.bedrock_client = bedrock_client

def answer_question():
    st.title("Answer Question")

    # Check if necessary variables are in session state
    if 'db' not in st.session_state or 'qa_prompt' not in st.session_state or 'bedrock_client' not in st.session_state:
        st.error("Please upload the PDF and preprocess it first.")
        return

    # Retrieve variables from session state
    db = st.session_state.db
    qa_prompt = st.session_state.qa_prompt
    bedrock_client = st.session_state.bedrock_client

    question = st.text_input("Enter your question")

    retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 3})

    llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client, model_kwargs={"temperature": 1e-10, "max_tokens_to_sample": 30000})
    chain_type_kwargs = {"prompt": qa_prompt, "verbose": False}
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, chain_type_kwargs=chain_type_kwargs, verbose=False)

 
    if st.button("Get Answer"):
        result = qa.run(question)
        st.write(result)

def main():
    page = st.sidebar.radio("Navigation", ["Upload PDF and Preprocess", "Answer Question"])

    if page == "Upload PDF and Preprocess":
        upload_and_preprocess()
    elif page == "Answer Question":
        answer_question()

if __name__ == "__main__":
    main()