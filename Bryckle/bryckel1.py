import streamlit as st
import os

import boto3
import botocore

from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.vectorstores import FAISS

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

#hashed_passwords = stauth.Hasher(['SKDemo@24']).generate()
#print('Hashed password: ', hashed_passwords)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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

llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client, model_kwargs={"temperature": 1e-10, "max_tokens_to_sample": 20000})


with open('access_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login('Login', 'main' )
if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def data_ingestion():
    loader = PDFPlumberLoader(r"C:\Users\Lenovo\Documents\Project-vs code\Amazon Transcribe\Bryckle\Dallas, TX Olympus, Master Lease Agreement, Brillio LLC.pdf")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    
    db = FAISS.from_documents(texts, embeddings)
    
    return db.as_retriever(search_type='similarity', search_kwargs={"k": 3})


def save_chat_message(question):
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    retriever = data_ingestion()

    template = """
        You will be given a query, Your task is to find an answer or give information about the query with respect to the document by performing a similarity search.
        {context}
            Consider the following conditions,
            - If query is a topic, look for information or statements or sentences which are related to the query in the document.
            - The answer does not need to be specifically related, it can be loosely related as well.
            - If you find any statements that are directly related to the query, then explain those statements in easy or layman terms, so someone with no expertise in that field can understand.
            - If query is a question, understand the context of query and then look for similar statements or sentences in the document which also have the same context.
            - It is not necessary to return direct statements from the document as an answer. You can also return loosely related answers to the query.
            - If you cannot find any direct statements or directly relevant answers, do not return that you cannot find any direct statements. Then, you have to perform a semantic search instead of looking for exact words in the document, that is, understanding the context from the query and looking for something similar in the document.
            - It is not mandatory to look for direct statements, you can also look at statements with a similar meaning and context.
            - It is fine if you cannot find any directly related statements in the document. You can look for sentences with similar meaning and can also return loosely related answers.
            - Elaborate the answer as much as you can.
            Instructions:
                    - If the exact answer to the question is not found on the given document simply print 'The document is silent on this'
                    for example:(if the question is)
                    Example question: Does the lessee have option of purchasing the space and under what conditions?
                                            so if the exact answer is present in the document then print that answer or else print 'There is no mention of a purchase option' and'The document is silent on this'
                follow the same instruction for all the questions don't mention anything other than this
            {question}
    """
     
    
    # docs_with_score = store.similarity_search_with_score(question)
    # print('DB Response: ', docs_with_score)

    qa_prompt = PromptTemplate(template=template, input_variables=["context","question"])
    chain_type_kwargs = { "prompt": qa_prompt, "verbose": False }
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
        verbose=False
    )
    
    result = qa.run(question)
    print('RESULT: ', result)

    _=""" with st.chat_message("user"):
        st.markdown(question)
    
    st.session_state.messages.append({"role": "user", "content": question}) """

    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)

def main():
    authenticator.logout('Logout', 'sidebar', key='auth_logout')

    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    os.environ['LANGCHAIN_API_KEY'] = "ls__fdf6b34054124890847791d04ef49b8a"
    os.environ['LANGCHAIN_PROJECT'] = 'negotiation'

    st.title("Demo - Bryckel")

    ## Call this function whenever it is needed to ingest the data
    #data_ingestion(COLLECTION_NAME, CONNECTION_STRING, True)
    
    with st.sidebar:
        if st.sidebar.button('Reset chat history'):
            st.session_state.messages = []
    
    if len(st.session_state.messages) <= 1:
        message = st.chat_message("assistant")
        message.write("How may I assist you?")
            
    if prompt := st.chat_input("Ask a question", key="primary_chat"):
        #message = st.chat_message("user")
        #message.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
            
        save_chat_message(prompt)
    
if st.session_state["authentication_status"]:
    #q1: What is the quantity of oil in the Transaxel
    main()