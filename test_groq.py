import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Load the secret API key from the .env file
load_dotenv()

# 2. Initialize the LLM
# We are using Llama 3 70B because it is excellent at reasoning and coding tasks.
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("MODEL_NAME")
)

# 3. Send a test prompt to the LLM
print("Sending test message to Groq...")
response = llm.invoke("Hello! Are you ready to diagnose some PySpark jobs?")

# 4. Print the response
print("\n--- Groq Response ---")
print(response.content)