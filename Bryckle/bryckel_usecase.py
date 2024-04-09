from langchain_community.document_loaders import AmazonTextractPDFLoader
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import LLMChain
import boto3
import botocore

config = botocore.config.Config(
    read_timeout=900,
    connect_timeout=900,
    retries={"max_attempts": 3}
)

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    config=config,
)

textract_client = boto3.client("textract", region_name="us-west-2")
textract_features=["LAYOUT"]
file_path = input("Enter the S3 URI : ")
print("Extracting Datas...")
loader = AmazonTextractPDFLoader(file_path,textract_features,client=textract_client)
docs = loader.load()

file_path = r"C:\Users\Lenovo\Documents\Project-vs code\Amazon Transcribe\Bryckle\Clause_pdf.pdf"
loader = PDFPlumberLoader(file_path)
clauses = loader.load()
print("Waiting for model Response...")

template = """
    You are provided with two input documents: a rental agreement document{docs} and a separate clauses document{clauses}. Your task is to compare the clauses specified in the clauses document with those present in the rental agreement document. Follow these steps to accomplish the task:

       - Parse the text of both documents to extract individual clauses.
       - Match corresponding clauses between the rental agreement and clauses document.
       - Analyze each pair of matched clauses to identify similarities and differences.
       - Generate a structured output presenting the comparison results, including:
            - For matched clauses: indicate similarities or differences in language or content.
            - For clauses present in one document but not the other: notify that the document is silent on the specific question.
       - Ensure the tool handles unanswered questions gracefully, encouraging users to review both documents for any overlooked clauses.
       - The output should be presented in a clear and understandable format, facilitating easy interpretation by users.
       - Prioritize accuracy in the comparison process, minimizing errors in clause extraction and matching.
       - Provide good and accurate answers
       - if you make sure and verified that the answer for the clause(question) is not found on the given rental agreement print 'this document is silent on this'
       - Try to give the brief answers so that user can understand easily
       - If there is a table datas in the answers kindly print full answers don't skip anything
       - If any table datas present ,print the table content fully
       - provide answers in the format like
                                        question:(mention in detail)
                                        answer:(provide detailed answers)
                                    
          and assign serial number for all
     


"""
qa_prompt = PromptTemplate(template=template, input_variables=["docs","clauses"])
llm = Bedrock(model_id="anthropic.claude-v2:1",client=bedrock_client,model_kwargs = {"temperature":1e-10,"max_tokens_to_sample": 40000})
llm_chain = LLMChain(prompt=qa_prompt, llm=llm, verbose= False)
result = llm_chain.run(docs=docs,clauses=clauses)
print(result)