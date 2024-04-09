import boto3
import streamlit as st
from langchain_community.document_loaders import AmazonTextractPDFLoader

def load_from_s3(file_path):
    textract_client = boto3.client("textract", region_name="us-west-2")
    textract_features=["FORMS"]
    loader = AmazonTextractPDFLoader(file_path, textract_features, client=textract_client)
    docs = loader.load()
    all_page_content = ""
    for doc in docs:
        all_page_content += doc.page_content
    return all_page_content

st.title("Invoice Extraction :")

s3_uri = st.text_input("Enter S3 URI:", "")
if st.button("Load Document"):
    if s3_uri:
        try:
            content = load_from_s3(s3_uri)
            st.write(content)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter an S3 URI.")
