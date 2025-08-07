import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from pydantic import BaseModel, Field
from typing import List

# --- SETUP: Load secret keys ---
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please set it in your .env file.")


# --- 1. BLUEPRINT for the initial analysis ---
class WebsiteAnalysis(BaseModel):
    bot_introduction: str = Field(description="A brief, friendly introduction from the AI bot, introducing itself by its name.")
    strengths: List[str] = Field(description="A list of 3 key strengths of the current website content.")
    improvements: List[str] = Field(description="A list of 3 primary areas for improvement.")
    strategic_recommendations: List[str] = Field(description="A list of 4 high-level, budget-friendly business strategies, formatted as italicized text.")
    homepage_redesign_prompt: str = Field(description="A detailed, actionable prompt for a web designer, formatted with clear headings and bullet points.")


# --- 2. PROMPT for the initial analysis ---
initial_prompt_template_string = """
You are an AI assistant named **Lens AI**. You are a famous-south indian wedding Photographer and brand strategist specializing in photography. Your persona for this task is an expert **{role}**.
Your first job is to perform a complete analysis of the provided website content.

Website Content:
---
{content}
---

Your final JSON output must contain the following sections: Bot Introduction, Strengths, Improvements, Strategic Recommendations, and Homepage Redesign Prompt.
You MUST provide your complete analysis in a single JSON object that perfectly matches this structure:
{format_instructions}
"""

def main():
    """ The main function to run the AI Website Analyzer """

    # --- GET USER INPUT (URL and ROLE) ---
    url = input("Please enter the website URL you want to analyze (or type 'exit' to quit): ")
    if url.lower() in ['exit', 'quit']:
        print("Goodbye!")
        return

    print("\nPlease choose an expert role for the analysis:")
    print("1: Business Analyst")
    print("2: Marketing Expert")
    print("3: UX Designer")
    
    choice = input("Enter the number of your choice (1-3), or type 'exit' to quit: ")
    if choice.lower() in ['exit', 'quit']:
        print("Goodbye!")
        return

    roles = {
        "1": "Business Analyst",
        "2": "Marketing Expert",
        "3": "UX Designer"
    }
    
    if choice not in roles:
        print("Invalid choice. Exiting.")
        return
        
    role = roles[choice]
    
    print(f"\n🤖 Activating Lens AI as a {role} to analyze {url}...")

    # --- RUN THE INITIAL ANALYSIS (Happens only once) ---
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        content_limit = content[:15000]
    except Exception as e:
        print(f"Sorry, I couldn't load or read that website. Error: {e}")
        return

    parser = JsonOutputParser(pydantic_object=WebsiteAnalysis)
    prompt = ChatPromptTemplate.from_template(
        template=initial_prompt_template_string,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    initial_chain = prompt | llm | parser
    initial_result = initial_chain.invoke({"role": role, "content": content_limit})

    # --- DISPLAY THE INITIAL RESULTS (with new formatting) ---
    print("\n\n" + "="*50)
    print(initial_result['bot_introduction'])
    print(f"Here is my initial analysis for {url} from the perspective of a {role}:")

    print("\n🔑 KEY STRENGTHS")
    print("-----------------")
    for item in initial_result['strengths']:
        print(f"• {item}")

    print("\n⚠️ AREAS FOR IMPROVEMENT")
    print("-------------------------")
    for item in initial_result['improvements']:
        print(f"• {item}")

    print("\n🚀 STRATEGIC RECOMMENDATIONS")
    print("---------------------------")
    for item in initial_result['strategic_recommendations']:
        print(item)

    print("\n🎨 KEY PROMPT FOR HOMEPAGE REDESIGN")
    print("------------------------------------")
    print(initial_result['homepage_redesign_prompt'])

    print("\n" + "="*50)
    print("\nAnalysis complete. You can now ask follow-up questions about the strategy.")

    # --- START THE CONVERSATIONAL LOOP ---
    chat_history = [
        {"role": "assistant", "content": f"I have just completed an analysis of {url} from the perspective of a {role}. Here is a summary of my findings: {initial_result}"}
    ]

    follow_up_prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are Lens AI, a helpful photography business strategist acting as a {role}. Continue the conversation based on your initial analysis and the user's questions. Be friendly and concise."),
        ("placeholder", "{chat_history}"),
        ("human", "{question}"),
    ])

    follow_up_chain = follow_up_prompt | llm | StrOutputParser()

    while True:
        try:
            user_input = input("\nYour question (or type 'exit' to quit): ")
            if user_input.lower() in ['exit', 'quit']:
                feedback = input("\nHow was your experience with the AI assistant? Your feedback is valuable!\n> ")
                print("Thank you for your feedback! Goodbye!")
                break

            chat_history.append({"role": "user", "content": user_input})
            
            print("\nLens AI is thinking...")
            ai_response = follow_up_chain.invoke({
                "chat_history": chat_history,
                "question": user_input
            })
            
            chat_history.append({"role": "assistant", "content": ai_response})
            
            print(f"\nLens AI: {ai_response}")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting conversation. Goodbye!")
            break

if __name__ == "__main__":
    main()