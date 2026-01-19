import os
from dotenv import load_dotenv, find_dotenv

print("Current working directory:", os.getcwd())
print("Found .env at:", find_dotenv())

load_dotenv(override=True)

print("OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY"))
print("GROK_API_KEY:", os.getenv("GROK_API_KEY"))
print("DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY"))
