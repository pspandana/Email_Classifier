import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. FIX: Import BaseModel and Field directly from pydantic
from pydantic import BaseModel, Field, conlist


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

# --- BLUEPRINT FOR THE FINAL RESULT: A list of analyses ---
# NEW Pydantic v2 style
from typing import List
class TriageResults(BaseModel):
    analyses: List[EmailAnalysis] = Field(min_length=1, description="A list containing the analysis for each email.")
# --- DATA: Our sample emails to be processed ---
sample_emails = [
  {
    "id": "email_001",
    "content": "Hi, I ordered a blue sweater last week (order #123) and the tracking says it was delivered, but I never got it! Can you help? This is very frustrating. - Angry Anna"
  },
  {
    "id": "email_002",
    "content": "Just wanted to say I LOVE the new headphones I bought. The sound quality is amazing and they arrived a day early. You guys are the best! - Happy Henry"
  },
  {
    "id": "email_003",
    "content": "Hello, I was wondering if you ship to Canada? Thanks. - Curious Carla"
  },
  {
    "id": "email_004",
    "content": "Hello, I need help with setting up my sound system. - Jimmy"
  },
  {
    "id": "email_005",
    "content": "Hello, I need to return my order, item is not working as expected. - John"
  },
  {
    "id": "email_006",
    "content": "I need my refund ASAP, Item broke into pieces and packing horrible. I am not happy with the Seller and going to give the negetive review. - Jane"
  }
]


# --- THE PROMPT: Our carefully engineered instructions ---
prompt_template_string = """
You are "Eva," a world-class AI customer service assistant. You are empathetic, efficient, and an expert at understanding customer needs. Your mission is to analyze a list of incoming customer emails. For each email, you must perform the following tasks based on the provided rules: 1. **Classify** the email into one of the predefined categories. 2. **Prioritize** the email based on its urgency. 3.you will provide customer service representative number to get the assitence if needed   4. **Draft** a high-quality, empathetic response.
**--- RULES AND LOGIC ---**
**1. Classification Categories:** You MUST classify each email into ONE of the following categories: - Enquiry - Missing Order - Canceling Order - Waiting for Refund - Item Not Delivered (but marked as delivered) - Return Request - Technical Issue - Happy Customer
**2. Prioritization Logic:** You MUST assign a priority level based on these rules: - **High Priority:** Issues that are time-sensitive and causing significant customer distress. (Item Not Delivered, Missing Order, Canceling Order) - **Medium Priority:** Issues that require action but are less time-critical. (Waiting for Refund, Return Request, Technical Issue) - **Low Priority:** Non-urgent communications. (Enquiry, Happy Customer)
**3. Response Style:** - Your tone must be professional and appropriate for the situation. For example, for 'Missing Order' use a **Reassuring & Confident** tone. For 'Happy Customer', use an **Appreciative & Enthusiastic** tone. - Your response MUST be structured with a clear opening, bullet points for key information or next steps, and a closing. - **Special Rule:** If the classification is "Happy Customer," your response MUST include a friendly request for them to leave a review on our website.
**--- INPUT DATA ---**
You will receive a list of emails to process. Here is the list:
{email_list}
**--- REQUIRED OUTPUT FORMAT ---**
You MUST provide your analysis as a single JSON object that perfectly matches the following structure. Do not add any extra text or explanations outside of the JSON structure.
{format_instructions}
"""

def main():
    """ The main function to run the AI Email Triage System """
    parser = JsonOutputParser(pydantic_object=TriageResults)
    prompt = ChatPromptTemplate.from_template(
        template=prompt_template_string,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | parser
    print("🤖 Eva is analyzing the batch of emails...")
    email_list_str = json.dumps(sample_emails, indent=2)

    # 2. FIX: This line was missing. It runs the AI and creates the 'result' variable.
    result = chain.invoke({"email_list": email_list_str})

    print("\n✅ Triage Complete! Eva has prioritized the emails.\n")
    all_analyses = result['analyses']

    # This is a set to keep track of the emails we have already handled
    handled_indices = set()

    # This while True loop will run forever until we choose to exit
    while True:
        # --- Create the interactive menu for the user ---
        print("--- EMAILS PENDING ---")
        for i, analysis in enumerate(all_analyses):
            # Add a checkmark if the email has been handled
            status = "[✅ HANDLED]" if i in handled_indices else ""
            print(f"{i + 1}. ID: {analysis['email_id']} | Priority: {analysis['priority']} {status}")
        print("-" * 22)

        # --- Ask the user which email to handle next ---
        choice_str = input("\nWhich email would you like to handle? (Enter number, or type 'exit' to quit): ")

        # Check if the user wants to quit
        if choice_str.lower() == 'exit':
            print("Exiting the Triage System. Goodbye!")
            break  # This command breaks out of the while loop

        # --- Process the user's choice ---
        try:
            choice_index = int(choice_str) - 1 # Convert to a list index (e.g., 1 -> 0)

            # Check if the choice is valid
            if 0 <= choice_index < len(all_analyses):
                # Get the specific email analysis the user chose
                selected_analysis = all_analyses[choice_index]

                # Display the full details for the chosen email
                print("\n--- HANDLING EMAIL ---")
                print(f"ID:         {selected_analysis['email_id']}")
                print(f"Priority:   {selected_analysis['priority']} ({selected_analysis['priority_reasoning']})")
                print(f"Category:   {selected_analysis['classification']}")
                print("\n--- Suggested Draft Response ---")
                print(selected_analysis['draft_response'])
                print("------------------------\n")

                # Add the index to our set of handled emails
                handled_indices.add(choice_index)
            else:
                print("--> Invalid number. Please try again.\n")

        except ValueError:
            print("--> That's not a valid number. Please try again.\n")

if __name__ == "__main__":
    main()