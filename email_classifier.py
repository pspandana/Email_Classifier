import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# --- SETUP: Load the secret API key ---
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please set it in your .env file.")


# --- BLUEPRINT: Define the structure for ONE email analysis ---
class EmailAnalysis(BaseModel):
    email_id: str = Field(description="The original ID of the email from the input list")
    classification: str = Field(description="The category chosen from the predefined list")
    priority: str = Field(description="High, Medium, or Low, based on the prioritization logic")
    priority_reasoning: str = Field(description="A brief, one-sentence explanation for the priority choice")
    draft_response: str = Field(description="The complete, well-formatted email response drafted for the customer")
    customer_name: str = Field(description="The name of the customer, extracted from the email content")
    customer_email: str = Field(description="The email address of the customer, extracted from the email content")
    support_phone_number: Optional[str] = Field(description="The customer service phone number to provide, if needed. Default to null if not needed.")

class TriageResults(BaseModel):
    analyses: List[EmailAnalysis] = Field(min_length=1, description="A list containing the analysis for each email.")


# --- DATA: Our complete list of 6 sample emails ---
sample_emails = [
  {
    "id": "email_001",
    "content": "Hi, I ordered a blue sweater last week (order #123) and the tracking says it was delivered, but I never got it! Can you help? This is very frustrating. - Angry Anna (anna.r@example.com)"
  },
  {
    "id": "email_002",
    "content": "Just wanted to say I LOVE the new headphones I bought. The sound quality is amazing and they arrived a day early. You guys are the best! - Happy Henry (henry.h@example.com)"
  },
  {
    "id": "email_003",
    "content": "Hello, I was wondering if you ship to Canada? Thanks. - Curious Carla (carla@example.com)"
  },
  {
      "id": "email_004",
      "content": "Hello, I need help with setting up my new sound system. The instructions are confusing. - Jimmy (jimmy@example.com)"
  },
  {
      "id": "email_005",
      "content": "I would like to return my order #456. The item is not working as I expected. Please send instructions. - John (john@example.com)"
  },
  {
      "id": "email_006",
      "content": "I need my refund ASAP for order #789. The item I received was broken into pieces and the packing was horrible. I am not happy at all and will be giving a negative review. - Jane (jane@example.com)"
  }
]


# --- THE PROMPT: Our carefully engineered instructions ---
prompt_template_string = """
You are "Eva," a world-class AI customer service assistant. You are empathetic, efficient, and an expert at understanding customer needs. Your mission is to analyze a list of incoming customer emails. For each email, you must perform the following tasks: 1. **Extract** the customer's name and email address. 2. **Classify** the email into one of the predefined categories. 3. **Prioritize** the email based on its urgency. 4. **Decide** if a customer service phone number is needed. Provide '1-800-555-1234' for urgent issues like 'Item Not Delivered' or 'Missing Order'. For all other cases, this should be null. 5. **Draft** a high-quality, empathetic response.
**--- RULES AND LOGIC ---**
**1. Classification Categories:** You MUST classify each email into ONE of the following categories: - Enquiry - Missing Order - Canceling Order - Waiting for Refund - Item Not Delivered (but marked as delivered) - Return Request - Technical Issue - Happy Customer
**2. Prioritization Logic:** You MUST assign a priority level based on these rules: - **High Priority:** (Item Not Delivered, Missing Order, Canceling Order, Refund for Damaged Item) - **Medium Priority:** (Standard Return Request, Technical Issue, Waiting for Refund) - **Low Priority:** (Enquiry, Happy Customer)
**3. Response Style:** Your tone must be professional and appropriate. For 'Missing Order', use a 'Reassuring' tone. For 'Happy Customer', use an 'Appreciative ' tone. Your response MUST be structured with a clear opening, bullet points for next steps, and a closing. If the customer is happy, your response MUST ask for a review.
**4. support_phone_number: Optional[str] = Field(description="The customer service phone number to provide, if needed. Default to null if not needed.")
**--- INPUT DATA ---**
{email_list}
**--- REQUIRED OUTPUT FORMAT ---**
You MUST provide your analysis as a single JSON object that matches this structure. Do not add any text outside the JSON.
{format_instructions}
"""

def main():
    """ The main function to run the AI Email Drafting System """
    parser = JsonOutputParser(pydantic_object=TriageResults)
    prompt = ChatPromptTemplate.from_template(
        template=prompt_template_string,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    chain = prompt | llm | parser
    
    print("🤖 Eva is analyzing the batch of emails...")
    email_list_str = json.dumps(sample_emails, indent=2)
    result = chain.invoke({"email_list": email_list_str})
    all_analyses = result['analyses']
    handled_indices = set()

    refinement_prompt_template = """
    You are Eva, a customer service assistant. Your user has requested changes to an email draft you wrote. Your task is to revise the draft based on the user's feedback. Maintain the original empathetic tone but incorporate the requested changes. Only output the new, complete email draft. Do not add any other commentary.
    ORIGINAL CUSTOMER EMAIL: --- {original_email} ---
    CURRENT DRAFT: --- {current_draft} ---
    USER'S FEEDBACK FOR CHANGES: --- {feedback} ---
    REVISED DRAFT:
    """
    refinement_prompt = ChatPromptTemplate.from_template(refinement_prompt_template)
    refinement_chain = refinement_prompt | llm

    while True:
        print("\n--- EMAILS PENDING ---")
        for i, analysis in enumerate(all_analyses):
            status = "[✅ HANDLED]" if i in handled_indices else ""
            print(f"{i + 1}. To: {analysis['customer_name']} | Priority: {analysis['priority']} {status}")
        print("-" * 22)

        choice_str = input("\nWhich email would you like to handle? (Enter number, or type 'exit','stop' to quit): ")
        if choice_str.lower() == 'exit' or choice_str.lower() == 'stop':
            print("Exiting the Triage System. Goodbye!")
            break

        try:
            choice_index = int(choice_str) - 1
            if 0 <= choice_index < len(all_analyses):
                selected_analysis = all_analyses[choice_index]
                
                current_draft = selected_analysis['draft_response']
                while True:
                    print("\n--- CURRENT DRAFT ---")
                    print(current_draft)
                    if selected_analysis['support_phone_number']:
                         print(f"\nSuggested contact number to include: {selected_analysis['support_phone_number']}")
                    print("-----------------------")
                    
                    feedback = input("--> Is this draft okay? Type 'yes' to approve, or type your requested changes: ")
                    if feedback.lower() == 'yes':
                        break

                    print("\n🤖 Eva is revising the draft based on your feedback...")
                    revised_result = refinement_chain.invoke({
                        "original_email": sample_emails[choice_index]['content'],
                        "current_draft": current_draft,
                        "feedback": feedback
                    })
                    current_draft = revised_result.content

                print("\nDraft approved! Marked as handled.")
                handled_indices.add(choice_index)

            else:
                print("--> Invalid number. Please try again.\n")
        except ValueError:
            print("--> That's not a valid number. Please try again.\n")

if __name__ == "__main__":
    main()