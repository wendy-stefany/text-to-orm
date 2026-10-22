import os
from dotenv import load_dotenv

load_dotenv()

# Gemini Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_TEXT = os.getenv("GEMINI_MODEL_TEXT", "gemini-1.5-flash") # o gemini-2.0-flash / gemini-1.5-pro
