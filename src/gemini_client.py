from google import genai
from config.settings import GEMINI_API_KEY

def get_gemini_client() -> genai.Client:
    """Inicializa el cliente oficial de Google Gemini SDK."""
    if not GEMINI_API_KEY:
        raise ValueError("Error: GEMINI_API_KEY no encontrada en el archivo .env")
    return genai.Client(api_key=GEMINI_API_KEY)