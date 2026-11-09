from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import config

try:
    llm = ChatGroq(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY)
    print("GROQ OK:", llm.invoke("Say hello in Gujarati in one line").content)
except Exception as e:
    print("GROQ FAILED:", e)

try:
    llm = ChatGoogleGenerativeAI(model=config.GEMINI_MODEL, google_api_key=config.GOOGLE_API_KEY)
    print("GEMINI OK:", llm.invoke("Say hello in Hindi in one line").content)
except Exception as e:
    print("GEMINI FAILED:", e)