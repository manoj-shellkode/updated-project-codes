import streamlit as st
import re

# Assuming 'result' contains the text output from your llm_chain.run() function
result = """
Waiting for model Response...
 Here is the comparison of clauses between the rental agreement document and the clauses document:

1. Address of Premises:  
Question: Describe the complete physical address of the premises leased with city, state, zipcode as per the document
Answer: 10770 East Briarwood Avenue, Centennial, Colorado 80112  
Page Number: 1

2. Rentable Area:
Question: What is the square footage or number of seats/workstation leased? Explain the terms and conditions associated with how it is calculated.  
Answer: The rentable area is 74,736 square feet. This is based on the entire building which is specified as 74,736 rentable square feet.  
Page Number: 1  

3. Tenant:  
Question: What is full and accurate legal name of the lessee's company that executed this lease?
Answer: Quantum Corporation
Page Number: 22

4. Landlord: 
Question: What is full and accurate legal name of the lessor's company that executed this lease?  
Answer: Briarwood Acquisition LLC
Page Number: 21

5. Lease Commencement Date:  
Question: What is the lease start date and describe the conditions based on which it is calculated in the agreement in a few sentences.
Answer: The lease commencement date is March 1, 2022. This is specified explicitly in the lease.  
Page Number: 2

6. Rent Abatement:
Question: Is there rent abatement granted? Describe the conditions based on which it is calculated and how long is the abatement period in a few sentences? If none, state "There is no mention of any abatement."
Answer: Yes, there is rent abatement for months 1-6 of the lease term where tenant shall not be responsible for paying Fixed Rent and Additional Rent.  
Page Number: 3

7. Rent Commencement Date: 
Question: What is the rent start date and describe the conditions based on which it is calculated in the agreement in a few sentences?  
Answer: The rent commencement date is month 7 of the lease term, which is September 2022 based on the March 1, 2022 commencement date. Rent abatement is provided for months 1-6 so rent payments start on month 7.  
Page Number: 3

8. Lease Expiration Date:  
Question: What is the lease end date and describe the conditions based on which it is calculated in the agreement in a few sentences?
Answer: The lease expiration date is August 31, 2037. This end date is explicitly specified in the lease agreement.
Page Number: 2

9. Initial Term:  
Question: What is the duration of the initial term specified in the agreement and any conditions associated with it- describe and convert the term from years into exact number of months
Answer: The initial term of the lease is 186 months. This is explicitly stated in the document as 186 months.
Page Number: 2

10. Lock In Period:   
Question: Does the lease reference a "lock in period" within the intital term which implies that the agreement can be terminated with notice after lock in period, describe its terms and conditions." If none, state "The agreement is binding until expiration date"
Answer: The agreement is binding until the expiration date. There is no reference to a lock in period.  
Page Number: This document is silent on this

11. Rent Payment Date:
Question: What is the frequency and specific date of rent payment?
Answer: Rent is payable in monthly installments, due on the first day of each month. 
Page Number: 3  

12. Currency:  
Question: What is the currency the lease rent is quoted in? Capture in acronym not symbol or text.  
Answer: The currency is USD - US Dollars.
Page Number: This document is silent on this

13. Base Rent: 
Question: What is the base rent/fee at the beginning period of the agreement? Provide a detailed summary of the terms and conditions associated with how it is stated?
Answer: The base rent schedule is:

Months 1-6: No Fixed Rent  
Months 7-18: $13.00 per square foot, monthly amount of $80,964
Months 19-30: $13.50 per square foot, monthly amount of $84,078  
Months 31-42: $14.00 per square foot, monthly amount of $87,192
Months 43-54: $14.50 per square foot, monthly amount of $90,306
Months 55-66: $15.00 per square foot, monthly amount of $93,418.75
Months 67-78: $15.50 per square foot, monthly amount of $96,534  
Months 79-90: $16.00 per square foot, monthly amount of $99,648
Months 91-102: $16.75 per square foot, monthly amount of $104,319
Months 103-114: $17.50 per square foot, monthly amount of $108,990
Months 115-126: $18.25 per square foot, monthly amount of $113,661 
Months 127-138: $19.00 per square foot, monthly amount of $118,332
Months 139-150: $19.75 per square foot, monthly amount of $123,003
Months 151-162: $20.50 per square foot, monthly amount of $127,674  
Months 163-174: $21.25 per square foot, monthly amount of $132,345
Months 175-186: $22.00 per square foot, monthly amount of $137,016

Page Number: 3

14. Base Rent Escalation:  
Question: Identify and extract all information about the adjustments, escalations, variable conditions that affect the starting base rent over time. Extract any table that exists for rent increases or changes during the lease term
Answer: The base rent escalates over time on a set schedule as shown in the table extracted under Base Rent. The increments range from $0.50 per square foot to $1.00 per square foot at various intervals over the lease term.
Page Number: 3

15. Tenants' Proportionate Share:   
Question: If applicable, what is the percentage of shared expenses the tenant is responsible for, based on their leased space compared to the total leasable area? if there is no percentage expressed then state " The document is silent on this"
Answer: Tenant's Share of the Building is 100%, which is 74,736 square feet / 74,736 square feet. Tenant's Share of the Building Complex is 36.04653%, which is 74,736 square feet / 207,332 square feet. 
Page Number: 4  

16. Additional Rent: Operating Expenses/Service Fee/CAM per month:   
Question: Explain how operating expenses, CAM or service fee will be calculated by the landlord, presented to tenant and when is it payable. State the amount, if it is mentioned and specify if it is monthly or by size such as per square foot or square meter or per workstation. if there is none, state " The document is silent on this".
Answer: Tenant shall pay in advance Tenant's Share of the Operating Expenses on a monthly basis. The Estimated Operating Expenses for year 2021 are $8.73 per square foot. Operating Expenses are defined and detailed in the agreement. Landlord shall send Tenant a statement of actual Operating Expenses annually and Tenant will pay or receive a credit for any difference between estimated and actual expenses.  
Page Number: 4

17. Additional Rent: Operating Expenses/Service Fee/CAM escalation:   
Question: Identify and extract all information about the adjustments, escalations, or variable conditions that affect the starting CAM/maintenance fee/operating expenses/service fee over time.
Answer: The document does not specify any escalations or adjustments to the Operating Expenses. It states the Estimated Operating Expenses for 2021 are $8.73 per square foot but does not provide details on increases year over year. 
Page Number: This document is silent on this

18. Additional Rent: Landlords' Insurance:    
Question: Landlord typically incurs a property insurance cost for the property within which the lease space exists and charges a proportionate share to the tenant. Is property insurance cost for the tenants share included in base rent or operating expenses? If yes, state " Property insurance costs are included in base rent" or "Property insurance costs are included in operating expenses" as applicable. If not, explain what is the amount the tenant has to pay, how will it be calculated, how will it be presented to tenant and when will it have to be paid? If there is absolutely no mention of this cost then state " The document is silent on this"
Answer: Property insurance costs are included as part of Operating Expenses which are billed to Tenant as Additional Rent. The details of the property insurance costs are not explicitly broken out. 
Page Number: 4

19. Additional Rent: Property Tax:   
Question: Landlord typically incurs a property tax for the property within which the lease space exists and charges a proportionate share to the tenant. Is property tax cost for the tenants share included in base rent or operating expenses? If yes, state " Property taxes are included in base rent" or "Property taxes are included in operating expenses" as applicable. If not, what is the amount the tenant has to pay, how will it be calculated, how will it be presented to tenant and when will it have to be paid? If there is absolutely no mention of this cost then state " The document is silent on this"
Answer: Property taxes are included as part of Operating Expenses which are billed to Tenant as Additional Rent. The details of the property tax costs are not explicitly broken out.
Page Number: 4

20. Additional Rent: Parking: 
Question: Identify and extract all information about parking. Are there any assigned parking spots specified in the document, for what type of vehicles, their location, fee and conditions for fee increases?
Answer: Tenant shall be provided non-exclusive surface parking in the Building Complex's parking lots at a ratio of 6 spaces per 1,000 square feet leased, which equals 448 spaces. This parking will be provided at no expense to Tenant during the lease term. 
Page Number: 17

21. Variable Rent: Utilities:  
Question: Is there any variable rent payable payable directly to the landlord based on lessee's consumption of utlities such as electricity, airconditioning,water and internet? How is it calculated and payable? If there is none, state " The document is silent on this"
Answer: Tenant shall directly pay all electric and gas utilities to the providers. Tenant shall reimburse Landlord for water and sewer utilities which are submetered, paying for consumption costs only.
Page Number: 5  

22. Variable Rent: Percentage of gross sales/receipts: 
Question: Is there any reference to paying percentage of sales/revenue as additional rent to lessor? If yes, what are the specifications? f there is none, state " The document is silent on this"  
Answer: This document is silent on this.

23. One time Fee:  
Question: Is there a one time set up/onboarding or activation fee charged and what are the details? f there is none, state " The document is silent on this"
Answer: This document is silent on this.  

24. Tenant Improvement Allowance:    
Question: If there an amount of the tenant improvement allowance/construction allowance specified in the agreement, explain any conditions or requirements associated with the use? If there is none, state " The document is silent on this"
Answer: Yes, there is a Tenant Improvement Allowance of $80.00 per square foot, totaling $5,978,880. This can be used for constructing tenant improvements per the approved Space Plan. There are additional details on requirements and procedures for using the allowance.  
Page Number: 29

25. Security Deposit: 
Question: What is the security deposit/ service retainer to be paid and is it refundable? Capture if it is paid in instalments and also the type of instrument- money order, check or letter of credit?
Answer: This document is silent on this.

26. Prepaid Rent:  
Question: Excluding the security deposit, is any type of rent due in advance at the execution of this agreement such as first and last month? How many months rent is it and how will it be applied?  
Answer: This document is silent on this.

27. Late Payment:   
Question: What is the penalty for rent payment after the due date, grace period and notification requirements? f there is none, state " The document is silent on this"
Answer: A late fee of 5% of the total payment due shall be charged if rent is not paid within 5 days of the due date. After the first two late payments in a year, any subsequent late payments constitute an Event of Default without additional notice or opportunity to cure. 
Page Number: 13

28. Residual Value Guarantee:    
Question: Is there any reference to residual value gaurantee ie after all rent payments, a guarantee of value of the underlying asset returned to the lessor at the end of the lease will be at least a specified amount? if yes, what is the amount? If there is none, state " The document is silent on this"
Answer: This document is silent on this.

29. Renewal Option:   
Question: Is there an option for renewal or extension after the initial term and what are the conditions- describe in a few sentences? Include the process to exercise renewal option, give notices and deadline for its execution. If there is none state " The document is silent on this"
Answer: Yes, Tenant has the option to extend the lease for two additional 5-year renewal periods by providing written notice between 6-12 months prior to expiration of the then-current term. Rent during the renewal period will be at Fair Market Value. There are additional details on the process for determining Fair Market Value if the parties cannot agree.  
Page Number: 19

30. Purchase Option:    
Question: Does the lessee have option of purchasing the space and under what conditions? If none, state " There is no mention of a purchase option."
Answer: There is no mention of a purchase option.

31. Permitted Use:  
Question: Extract all information about the permitted business operations or activities allowed and any restrictions
Answer: The permitted use is general office use, light assembly, warehousing, manufacturing, and data storage that aligns with the ordinary course of Tenant's business. This is subject to applicable laws and governmental rules. Hazardous materials usage is restricted.
Page Number: 6

32. Exclusive Use:   
Question: Does the lease state any provision of exclusive use for lessee? If yes, capture the scope, period, limitations and enforcement details. If not state " The document is silent on this"  
Answer: This document is silent on this.  

33. Building Hours:  
Question: What are the building hours of operation? If none are mentioned, state " The document is silent on this"
Answer: This document is silent on this.

34. Compliance with Laws and Regulations:  
Question: Summarize all clauses that references federal, state, city lor town laws and regulations the tenant needs to comply with  
Answer: Tenant shall comply with all applicable federal, state and local environmental laws and regulations. Tenant shall comply with all applicable laws, ordinances, orders, notices, rules and regulations of the federal, state and municipal governments.  
Page Number: 7, 15

35. Alterations and Improvements:   
Question: Summarize all clauses that references alterations or improvements permitted, restrictions, performance of work limitations and enforcement. If none are mentioned, state " The document is silent on this"
Answer: Tenant shall not make any Alterations without Landlord's prior written consent. Minor non-structural alterations under $2,500 do not require consent. Tenant shall use responsible contractors and provide plans/specifications. Work shall not damage building or interfere with other tenants. Details on Tenant's responsibilities and limitations for the initial Tenant Improvement Work are specified.  
Page Number: 8  

36. Access and Entry:  
Question: Summarize all clauses that reference landlords rights to access and entry as well as any limitations on it. If none are mentioned, state " The document is silent on this"
Answer: Landlord may enter the Premises at reasonable times upon reasonable notice, or anytime without notice in an emergency. Landlord shall comply with Tenant's security requirements.  
Page Number: 10

37. Subleasing and Assignment: 
Question: Summarize the clause on subleasing and assignments. Identify and extract all information for obtaining consent or approval for both, the specific conditions and procedures for getting approval from the original landlord.
Answer: Tenant cannot sublet or assign without Landlord's prior written consent, which shall not be unreasonably withheld. Details on information Tenant must provide for the request and conditions under which Landlord can withhold consent are specified. Landlord has a right to terminate the lease or recapture the premises if Tenant requests assignment or subletting. A $1,000 fee is due to Landlord for consenting. Reasonable restrictions on transfer to a competitor within the building are outlined. Transfers to a subsidiary or affiliate are pre-approved. 
Page Number: 9

38. Holdover:  
Question: Summarize the holdover clause. Identify and extract all information on the duration and conditions under which a holdover fee may apply, the amount and consequences associated with holdover. If none are mentioned, state " The document is silent on this"
Answer: If Tenant fails to vacate at lease expiration, their occupancy shall be considered a tenancy at sufferance. For the first 90 days of holdover, rent shall be 110% of the then-current rent. After 90 days, rent shall be 150% of then-current rent. Holdover tenancy will be month-to-month.  
Page Number: 19

39. Surrender of Premises:   
Question: Summarize the clause on surrender of premises. Extract the dates or timeline, condition in which to surrender the space, repairs and restoration, removal of property, notice & inspection and keys & access
Answer: At lease expiration, Tenant shall promptly quit and surrender the Premises in good order and condition, removing all furniture, fixtures, equipment, and data/telecom cabling. If Tenant fails to surrender, they shall be considered a holdover tenant. 
Page Number: 19

40. Co-Tenancy:   
Question: Are there any terms and conditions of the co-tenancy specified in the document and the consequences or implications of changes in co-tenancy? If there is none, state " The document is silent on this"
Answer: This document is silent on this.

41. Repairs & Maintenance:    
Question: What does the agreement specify regarding the obligation of the tenant for regular upkeep/regular maintenance/AMC's of certain systems or facilities within the space by the tenant? Describe all. If there is none, state " The document is silent on this"  
Answer: Tenant shall keep and maintain the Premises in good order and condition, free of rubbish, and make all non-structural repairs necessary. Tenant shall provide and pay for its own janitorial services. Tenant has the option to request Landlord make certain repairs at Tenant's expense at competitive market rates.  
Page Number: 10

42. Tenants' Insurance:  
Question: What insurance coverage is the tenant required to obtain for coverage of their business or leased space? List all of them such as general liability, workers comp etc, the amount of coverage specified and who all should be covered - describe all the conditions?
Answer: Tenant shall obtain commercial general liability insurance with limits of $1,000,000 per occurrence, workers compensation insurance with statutory limits, employers liability insurance with limits of $500,000 per occurrence, and commercial excess or umbrella insurance with limits of $2,000,000. Landlord shall be named as additional insured on the policies. Tenant shall also require third-party movers to obtain insurance naming Landlord as additional insured. 
Page Number: 11

43. Utilities:   
Question: What is the responsibility of tenant to obtain utilities directly from providers, list all specific ones and any conditions. If there is none, state " The document is silent on this"
Answer: Tenant shall directly pay all electric and gas utility providers. Tenant shall reimburse Landlord for water and sewer utilities which are separately metered.  
Page Number: 5

44. Services:  
Question: Summarize the tenant services and amenities provided by the landlord, legal and financial compliance by landlord, emergency response and security.
Answer: This document is silent on this.

45. Repairs & Maintenance:   
Question: Summarize the clauses on landlord obligations for repairs and maintenance, landscaping, cleaning common areas, and ensuring the proper functioning of utilities, as well as promptly addressing repair requests from tenants  
Answer: Landlord shall maintain the structural portions of the building including roof, foundation, windows, exterior walls. Landlord shall contract for maintenance of the HVAC system with costs charged to Tenant. Details on replacement or major repairs to HVAC are provided. Landlord will address repair requests from Tenant.  
Page Number: 10  

46. Utilities:    
Question: Summarize the clauses on utilities provided by the landlord as part of base rent or operating expenses and what happens if there are any overages. If there is none, state " The document is silent on this"
Answer: This document is silent on this.

47. Events of Default:  
Question: Summarize what are the specific conditions or actions that could trigger a lessee default under the agreement  
Answer: Failure to pay rent within 5 days of due date (after first 2 late payments), failing to bond over a construction lien within 30 days, vacating the premises while owing rent, or failing to observe or perform any non-monetary agreements within 30 days after notice from Landlord could trigger an Event of Default.  
Page Number: 13

48. Landlord Remedies:  
Question: Explain in detail what happens in the event of default, what are landlord remedies and cure period.
Answer: Upon an Event of Default, Landlord has the right to accelerate all rent for the remainder of the term, collect damages equal to the sum of all accrued and unpaid rent plus reletting costs, repairs, and rent owed for the remainder of the term (less any rent collected from reletting), and cure any Tenant defaults at Tenant's expense. Details on interest, order of applying funds, and no waiver of default from accepting payments are outlined.  
Page Number: 14

49. Termination Notice Period:  
Question: If the tenant does not wish to renew is there a notice period required for ending the initial term or does it automatically end? Explain, what are the conditions and procedures? f there is none, state " The document is silent on this"
Answer: This document is silent on this.  

50. Unilateral Tenant Termination Rights:   
Question: Does the tenant have the right to terminate the lease early, within the binding period of the agreement? if yes what conditions can trigger it, what is the notice required to do so and penalties if applicable? If tenant does not have any option to terminate state " Tenant cannot terminate this lease early"
Answer: Tenant cannot terminate this lease early.

51. Subordination, Attornment:  
Question: Summarize all the clauses on subordination and attornment- listing both separately. If there is none, state " The document is silent on this"
Answer: This lease shall be subordinate to any present or future mortgages on the property. Tenant shall execute any instruments confirming subordination. Tenant shall attorn to any purchaser at a foreclosure sale as the new landlord.  
Page Number: 12

52. Destruction, Fire & Casualty:  
Question: Summarize all the clauses on destruction of property, what happens in the event of fire or any such similar event of casualty. If there is none, state "The document is silent on this"
Answer: If over 30% of the Premises or Building are damaged, repairs will take over 210 days, or the casualty occurs in last 2 years of term, either party may terminate lease within 60 days of casualty. If lease continues, Landlord will restore Premises and rent will abate if space cannot be used.  
Page Number: 12

53. Estoppel:  
Question: Summarize in simple english the clause on estoppel, scope, preclusion of contradictory claims and enforceability. If there is none, state " The document is silent on this"  
Answer: Either party shall within 10 days of a request execute an instrument certifying the status and facts of the lease.  
Page Number: 16

54. Indemnity:  
Question: Summarize all clauses in simple english on scope of indemnification, indemnification trigger events, limitations and exclusions, notice and defense obligations, survival of indemnity obligations and enforceability and remedies. If there is none, state "The document is silent on this"
Answer: Tenant shall defend, indemnify and hold harmless Landlord from any liability or claims arising from Tenant's use of premises or any negligence by Tenant. Landlord shall defend, indemnify and hold harmless Tenant from any liability or claims arising from Landlord's negligence or failure to perform obligations.  
Page Number: 11

55. Eminent Domain, Condemnation:   
Question: Summarize all clauses insimple english on emninent domain and condemnation. If there is none state, " The document is silent on this"
Answer: If a taking renders the premises or building unsuitable, either party may terminate the lease effective when title vests with authority. Rent shall be equitably reduced if lease continues. Tenant may make a claim against the authority for moving and business damages.
Page Number: 16  

56. Landlord Address for Notices:   
Question: What is the complete physical address to send notices to lessor?
Answer: Briarwood Acquisition LLC, 40 Airport Road, Lakewood, NJ 08701  
Page Number: 16

57. Landlord Contact:  
Question: Who is the landlord contact for notices- capture the first and last name?  
Answer: This document does not specify a contact name.

58. Landlord Contact Information:    
Question: If email or phone number is provided for the landlord contact for notices, capture that
Answer: This document does not specify contact information.  

59. Tenant Address for Notices:  
Question: What is the complete physical address to send notices to lessee?
Answer: Prior to Commencement Date: Quantum Corporation, 224 Airport Parkway, Suite 550, San Jose, CA 95110
           After Commencement Date: Quantum Corporation, 10770 East Briarwood Avenue, Centennial, Colorado 80112
Page Number: 24  

60. Tenant Contact:   
Question: Who is the tenant contact for notices- capture the first and last name
Answer: This document does not specify a contact name.  

61. Tenant Contact Information:  
Question: If email or phone number is provided for the tenant contact for notices, capture that
Answer: Prior to Commencement Date: 
           Phone No.: (720) 469-2767
           E-mail: sonny.saluda@quantum.com
Page Number: 24
"""
# Use regular expressions to find and replace question and answer text with bold formatting
formatted_result = re.sub(r'(Question:|Answer:|Page Number:)', r'**\1**', result)

# Split the formatted result into individual clauses
clauses = formatted_result.strip().split("\n\n")

# Display each clause with proper formatting
for clause in clauses:
    lines = clause.strip().split('\n')
    for line in lines:
        st.write(line.strip())
