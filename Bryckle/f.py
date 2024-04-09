import streamlit as st
from langchain_community.document_loaders import AmazonTextractPDFLoader
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import LLMChain
import boto3
import re
import botocore

# Initialize Streamlit
st.title("Rental Agreement Clause Comparison")
st.sidebar.image("sk-logo-trans.png", use_column_width=True)


# Langchain setup
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

# Streamlit components
file_path = st.text_input("Enter the S3 URI for the rental agreement document:")
if file_path:
    st.write("Extracting Datas...")
    loader = AmazonTextractPDFLoader(file_path, textract_features, client=textract_client)
    docs = loader.load()

    # Prompt template and LLM setup
    clauses = """ Address of Premises:
Describe the complete physical address of the premises leased with city, state, zipcode as per the document.
Rentable Area [sf or number of seats]:
What is the square footage or number of seats/workstation leased? Explain the terms and conditions associated with how it is calculated.
Tenant:
What is full and accurate legal name of the lessee's company that executed this lease?
Landlord:
What is full and accurate legal name of the lessor's company that executed this lease?
Lease Commencement Date:
What is the lease start date and describe the conditions based on which it is calculated in the agreement in a few sentences.
Rent Abatement:
Is there rent abatement granted? Describe the conditions based on which it is calculated and how long is the abatement period in a few sentences? If none, state "There is no mention of any abatement."
Rent Commencement Date:
What is the rent start date and describe the conditions based on which it is calculated in the agreement in a few sentences?
Lease Expiration Date:
What is the lease end date and describe the conditions based on which it is calculated in the agreement in a few sentences?
Initial Term:
What is the duration of the initial term specified in the agreement and any conditions associated with it- describe and convert the term from years into exact number of months.
Lock In Period:
Does the lease reference a "lock in period" within the initial term which implies that the agreement can be terminated with notice after lock in period, describe its terms and conditions." If none, state "The agreement is binding until expiration date"
Rent Payment Date:
What is the frequency and specific date of rent payment?
Currency:
What is the currency the lease rent is quoted in? Capture in acronym not symbol or text.
Base Rent:
What is the base rent/fee at the beginning period of the agreement? Provide a detailed summary of the terms and conditions associated with how it is stated?
Base Rent Escalation:
Identify and extract all information about the adjustments, escalations, variable conditions that affect the starting base rent over time. Extract any table that exists for rent increases or changes during the lease term.
Tenants' Proportionate Share:
If applicable, what is the percentage of shared expenses the tenant is responsible for, based on their leased space compared to the total leasable area? if there is no percentage expressed then state " The document is silent on this"
Additional Rent - Operating Expenses/Service Fee/CAM per month:
Explain how operating expenses, CAM or service fee will be calculated by the landlord, presented to tenant and when is it payable. State the amount, if it is mentioned and specify if it is monthly or by size such as per square foot or square meter or per workstation. if there is none, state " The document is silent on this".
Additional Rent - Operating Expenses/Service Fee/CAM escalation:
Identify and extract all information about the adjustments, escalations, or variable conditions that affect the starting CAM/maintenance fee/operating expenses/service fee over time.
Additional Rent: Landlords' Insurance:
Landlord typically incurs a property insurance cost for the property within which the lease space exists and charges a proportionate share to the tenant. Is property insurance cost for the tenants share included in base rent or operating expenses? If yes, state " Property insurance costs are included in base rent" or "Property insurance costs are included in operating expenses" as applicable. If not, explain what is the amount the tenant has to pay, how will it be calculated, how will it be presented to tenant and when will it have to be paid? If there is absolutely no mention of this cost then state " The document is silent on this"
Additional Rent - Property Tax:
Landlord typically incurs a property tax for the property within which the lease space exists and charges a proportionate share to the tenant. Is property tax cost for the tenants share included in base rent or operating expenses? If yes, state " Property taxes are included in base rent" or "Property taxes are included in operating expenses" as applicable. If not, what is the amount the tenant has to pay, how will it be calculated, how will it be presented to tenant and when will it have to be paid? If there is absolutely no mention of this cost then state " The document is silent on this"
Additional Rent - Parking:
Identify and extract all information about parking. Are there any assigned parking spots specified in the document, for what type of vehicles, their location, fee and conditions for fee increases?
Variable Rent: Utilities:
Is there any variable rent payable payable directly to the landlord based on lessee's consumption of utlities such as electricity, airconditioning,water and internet ? How is it calculated and payable? If there is none, state " The document is silent on this"
Variable Rent: Percentage of gross sales/receipts:
Is there any reference to paying percentage of sales/revenue as additional rent to lessor? If yes, what are the specifications? f there is none, state " The document is silent on this"
One-time Fee:
Is there a one time set up/onboarding or activation fee charged and what are the details? f there is none, state " The document is silent on this"
Tenant Improvement Allowance:
If there an amount of the tenant improvement allowance/construction allowance specified in the agreement, explain any conditions or requirements associated with the use? If there is none, state " The document is silent on this"
Security Deposit:
What is the security deposit/ service retainer to be paid and is it refundable?Capture if it is paid in instalments and also the type of instrument- money order, check or letter of credit?
Prepaid Rent:
Excluding the security deposit , is any type of rent due in advance at the execution of this agreement such as first and last month ? How many months rent is it and how will it be applied ?
Late Payment:
What is the penalty for rent payment after the due date , grace period and notification requirements? f there is none, state " The document is silent on this"
Residual Value Guarantee:
Is there any reference to residual value gaurantee ie after all rent payments, a guarantee of value of the underlying asset returned to the lessor at the end of the lease will be at least a specified amount? if yes , what is the amount? If there is none, state " The document is silent on this"
Renewal Option:
Is there an option for renewal or extension after the initial term and what are the conditions- describe in a few sentences? Include the process to exercise renewal option, give notices and deadline for its execution. If there is none state " The document is silent on this"
Purchase Option:
Does the lessee have option of purchasing the space and under what conditions? If none, state " There is no mention of a purchase option."
Permitted Use:
Extract all information about the permitted business operations or activities allowed and any restrictions
Exclusive Use:
Does the lease state any provision of exclusive use for lessee. If yes, capture the scope, period, limitations and enforcement details. If not state " The document is silent on this"
Building Hours:
What are the building hours of operation. If none are mentioned, state " The document is silent on this"
Compliance with Laws and Regulations:
Summarize all clauses that references federal, state , city lor town laws and regulations the tenant needs to comply with
Alterations and Improvements:
Summarize all clauses that references alterations or improvements permitted, restrictions, performance of work limitations and enforcment. If none are mentioned, state " The document is silent on this"
Access and Entry:
Summarize all clauses that reference landlords rights to access and entry as well as any limitations on it. If none are mentioned, state " The document is silent on this"
Subleasing and Assignment:
Summarize the clause on subleasing and assignments. Identify and extract all information for obtaining consent or approval for both , the specific conditions and procedures for getting approval from the original landlord
Holdover:
Summarize the holdover clause. Identify and extract all information on the duration and conditions under which a holdover fee may apply, the amount and consequences associated with holdover. If none are mentioned, state " The document is silent on this"
Surrender of Premises:
Summarize the clause on surrender of premises. Extract the dates or timeline, condition in which to surrender the space, repairs and restoration, removal of property, notice & inspection and keys & access
Co-Tenancy:
Are there any terms and conditions of the co-tenancy specified in the document and the consequences or implications of changes in co-tenancy?f there is none, state " The document is silent on this"
Repairs & Maintenance:
What does the agreement specify regarding the obligation of the tenant for regular upkeep/regular maintenance/AMC's of certain systems or facilities within the space by the tenant? Describe all. If there is none, state " The document is silent on this"
Tenants' Insurance:
What insurance coverage is the tenant required to obtain for coverage of their business or leased space ? List all of them such as general liability, workers comp etc , the amount of coverage specified and who all should be covered - describe all the conditions?
Utilities:
What is the responsibility of tenant to obtain utilities directly from providers, list all specific ones and any conditions. If there is none, state " The document is silent on this"
Services:
Summarize the tenant services and amenities provided by the landlord, legal and financial compliance by landlord, emergency response and security.
Repairs & Maintenance (Landlord):
Summarize the clauses on landlord obligations for repairs and maintenance, landscaping, cleaning common areas, and ensuring the proper functioning of utilities, as well as promptly addressing repair requests from tenants
Utilities (Landlord):
Summarize the clauses on utilities provided by the landlord as part of base rent or opearting expenses and what happens if there are any overages. If there is none, state " The document is silent on this"
Events of Default:
Summarize what are the specific conditions or actions that could trigger a lessee default under the agreement
Landlord Remedies:
Explain in detail what happens in the event of default , what are landlord remedies and cure period.
Termination Notice Period:
If the tenant does not wish to renew is there a notice period required for ending the initial term or does it automatically end? Explain, what are the conditions and procedures? f there is none, state " The document is silent on this"
Unilateral Tenant Termination Rights:
Does the tenant have the right to terminate the lease early, within the binding period of the agreement? if yes what conditions can trigger it, what is the notice required to do so and penalties if applicable? If tenant does not have any option to terminate state " Tenant cannot terminate this lease early"
Subordination, Attornment:
Summarize all the clauses on subordination and attornment- listing both separately. If there is none, state " The document is silent on this"
Destruction, Fire & Casualty:
Summarize all the clauses on destruction of property, what happens in the event of fire or any such similar event of casualty. If there is none, state " The document is silent on this"
Estoppel:
Summarize in simple english the clause on estoppel, scope, preclusion of contradictory claims and enforceability. If there is none, state " The document is silent on this"
Indemnity:
Summarize all clauses in simple english on scope of indemnification, indemnification trigger events, limitations and exclusions, notice and defense obligations, survival of indemnity obligations and enforceability and remedies. If there is none, state " The document is silent on this"
Eminent Domain, Condemnation:
Summarize all clauses insimple english on emninent domain and condemnation. If there is none state, " The document is silent on this"
Landlord Address for Notices:
What is the complete physical address to send notices to lessor
Landlord Contact:
Who is the landlord contact for notices- capture the first and last name?
Landlord Contact Information:
If email or phone number is provided for the landlord contact for notices, capture that
Tenant Address for Notices:
What is the complete physical address to send notices to lessee?
Tenant Contact:
Who is the tenant contact for notices- capture the first and last name
Tenant Contact Information:
If email or phone number is provided for the tenant contact for notices, capture that
"""

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
                                        Question:(mention in detail)
                                        Answer:(provide detailed answers)
                                        Page No:(mention the page number where the answer is found)
                                                    Each page contains metadata at the end, so take the page number accurately from the metadata(page:)
                                    
          and assign serial number for all
     


    """

    qa_prompt = PromptTemplate(template=template, input_variables=["docs","clauses"])
    llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client, model_kwargs={"temperature":1e-10, "max_tokens_to_sample": 40000})
    llm_chain = LLMChain(prompt=qa_prompt, llm=llm, verbose=False)

    # Run the Langchain process
    result = llm_chain.run(docs=docs, clauses=clauses)

    # Display the result
# Split the result into individual clauses
    formatted_result = re.sub(r'(Question:|Answer:|Page Number:)', r'**\1**', result)

    # Split the formatted result into individual clauses
    clauses = formatted_result.strip().split("\n\n")

    # Display each clause with proper formatting
    for clause in clauses:
        # Use markdown syntax for each line
        lines = clause.strip().split('\n')
        for line in lines:
            # Replace $ symbol with Unicode character
            line = line.replace('$', '＄')
            st.markdown(f'{line.strip()}')

