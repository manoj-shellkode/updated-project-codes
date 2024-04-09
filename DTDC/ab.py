import streamlit as st
import boto3
import botocore
from langchain_community.document_loaders.s3_file import S3FileLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import BedrockChat
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock

# Set up AWS configurations
config = botocore.config.Config(
    read_timeout=1800,
    connect_timeout=1800,
    retries={"max_attempts": 10}
)

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    config=config,
)

s3 = boto3.client('s3')
bucket_name = "abdullah-sk"
file_formats = ['.docx']
response = s3.list_objects(Bucket=bucket_name)
file_keys = [obj['Key'] for obj in response.get('Contents', []) if any(obj['Key'].endswith(format) for format in file_formats)]

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEmbeddings()

# Initialize PGVector
CONNECTION_STRING = "postgresql+psycopg2://postgres:serverless123@database-1-instance-1.cxbpo87iqdgv.us-east-1.rds.amazonaws.com:5432/database1"
COLLECTION_NAME = "1-pharmacy"
db = PGVector(
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING
)

# Initialize BedrockChat model
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
model_kwargs =  { 
    "max_tokens":10000,
    "temperature": 0.0,
    "top_k": 250,
    "top_p": 1,
    "stop_sequences": ["\n\nHuman"],
}

model = BedrockChat(
    client=bedrock_client,
    model_id=model_id,
    model_kwargs=model_kwargs,
)

# Create a template for the response
template = """
    You are expert at generating answers from the given context.
    Instruction:
             - Strictly Do not include time frame while generating the answers
             - Provide accurate answers do not generate of your own
             - Dont skip any  information in the given context and elaborate your answer.

    {context}
    {question}
"""

# Initialize retrieval-based QA system
retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 3})
qa_prompt = PromptTemplate(template=template, input_variables=["context","question"])
chain_type_kwargs = { "prompt": qa_prompt, "verbose": False }
qa = RetrievalQA.from_chain_type(
    llm=model,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs=chain_type_kwargs,
    verbose=False
)

# Function to load documents from S3
def load_documents_from_s3(bucket_name, file_keys):
    combined_content = ""
    for key in file_keys:
        loader = S3FileLoader(bucket=bucket_name, key=key)
        context_content = loader.load()
        context_content = [str(item) for item in context_content]
        combined_content += '\n'.join(context_content)
    return combined_content

# Function to split documents and store them in the database
def split_and_store_documents_in_db(combined_content):
    class Document:
        def __init__(self, page_content, metadata=None):
            self.page_content = page_content
            self.metadata = metadata if metadata is not None else {}
    documents_list = [Document(page_content=combined_content)]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500)
    context_texts = text_splitter.split_documents(documents_list)
    # Store in database - You might want to implement this part
    # Example: db.store_documents(context_texts)

# Function for question answering
def answer_question(question):
    if question:
        result = qa.run(question)
        return result
    else:
        return "Please enter a question."

# Streamlit app
def main():
    st.title("Document-based Question Answering System")

    question = st.text_input("Enter your question:")
    if st.button("Ask"):
        result = answer_question(question)
        st.write("Answer:", result)

if __name__ == "__main__":
    main()
