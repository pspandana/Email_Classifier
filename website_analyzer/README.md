## 🤖 Project: Lens AI - The Conversational Website Strategist
This repository contains the code for Lens AI, an advanced, conversational AI assistant designed to analyze any website and provide an expert strategic growth plan. Initially built for photographers, its core logic can be adapted for any industry. The bot acts as a professional consultant, taking on different expert roles to deliver a comprehensive analysis and then allowing the user to ask follow-up questions in a natural conversation.

## ✨ Features & How They Work
Role-Based Expertise

What it is: The bot can adopt different professional personas (like a Business Analyst, Marketing Expert, etc.) to provide analysis from various viewpoints.

How we did it: We used persona prompting by making the expert {role} a variable in our ChatPromptTemplate. The user's choice dynamically changes the AI's personality and the focus of its analysis.

Structured, Reliable Output

What it is: The bot's initial analysis is not a simple paragraph but a highly organized and predictable JSON object.

How we did it: We defined a strict Pydantic BaseModel class that acts as a blueprint. This blueprint is passed to a JsonOutputParser, which forces the AI to structure its response, ensuring the output is always clean and usable by our program.

Live Web Content Analysis

What it is: The bot can analyze any live website, not just pre-written text.

How we did it: We used the WebBaseLoader from langchain-community. This tool takes a URL, fetches the HTML, and automatically extracts the clean text content for the AI to analyze.

Conversational Memory & Follow-Up Questions

What it is: After the initial report, the user can continue the conversation, asking specific follow-up questions to dig deeper into the analysis.

How we did it: We implemented a while loop that runs after the initial analysis. We store the entire conversation in a chat_history list. With every new question, the entire history is passed back to the AI, giving it a "memory" of the conversation and allowing it to provide context-aware answers.

## 🛠️ Tech Stack
Core Language: Python

AI Framework: LangChain

Language Model: OpenAI (GPT-4o-mini)

Data Structuring: Pydantic

Web Scraping: langchain_community.document_loaders.WebBaseLoader

Secret Management: python-dotenv

## 🚀 Setup and Installation
Follow these steps to get the project running on your local machine.

1. Clone the Repository
Clone this project to your local machine.

Bash

git clone <your-repository-url>
cd <project-folder>
2. Create and Activate a Virtual Environment
It's highly recommended to use a virtual environment.

Bash

# Create the environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
3. Install Dependencies
This project requires several Python packages.
(Note: A best practice is to have a requirements.txt file. You can create one by running pip freeze > requirements.txt after installing the packages below).

Bash

pip install -U langchain langchain-openai langchain-community pydantic python-dotenv beautifulsoup4
4. Set Up Your Secret Keys
Create a file named .env in the root directory of the project. This file should never be committed to Git. Add your OpenAI API key to this file.

Code snippet

# Your secret key from https://platform.openai.com/api-keys
OPENAI_API_KEY="sk-..."
## 🏃‍♀️ How to Run
Once the setup is complete, you can run the application from your terminal:

Bash

python website_analyzer.py
The script will first prompt you for a website URL and the expert role you want the AI to take on. After the initial analysis, it will open a prompt for you to ask follow-up questions. Type exit or quit to end the conversation.

## Example Interaction
Please enter the website URL you want to analyze...: https://apple.com

Please choose an expert role for the analysis:
1: Business Analyst
...
Enter the number of your choice...: 1

🤖 Activating Lens AI as a Business Analyst to analyze https://apple.com...

==================================================
Hello! I'm Lens AI, your expert Business Analyst...
Here is my initial analysis for https://apple.com...

🔑 KEY STRENGTHS
-----------------
• The brand messaging is exceptionally clear and focuses on simplicity and innovation...
...

==================================================

Analysis complete. You can now ask follow-up questions about the strategy.

Your question (or type 'exit' to quit): Tell me more about the areas for improvement

Lens AI is thinking...

Lens AI: Of course. Based on my analysis, a key area for improvement is the navigation