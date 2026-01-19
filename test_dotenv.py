import os
from dotenv import load_dotenv, find_dotenv

print("CWD:", os.getcwd())
print("Found .env:", find_dotenv())

load_dotenv(override=True)

print("OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY") or "Not found")
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY") or "Not found")
print("DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY") or "Not found")
