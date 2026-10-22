import os

class EloquentAgent:
    def __init__(self, client):
        self.client = client
        self.gemini_client = client
        self.model_name = os.getenv("GEMINI_MODEL_TEXT", "gemini-2.5-flash")

    def generate_orm_query(self, question, rag_context):
        prompt = f"""
        Dado el contexto del modelo ORM:
        {rag_context}
        
        Traduce la siguiente pregunta a Eloquent y su equivalente SQL en dialecto SQLite:
        Pregunta: {question}
        
        Responde ESTRICTAMENTE en formato JSON plano con esta estructura:
        {{
          "c_orm": "Client::where('balance', '>', 0)->get()",
          "sql_equivalent": "SELECT * FROM clients WHERE balance > 0;"
        }}
        """

        client_obj = self.gemini_client or self.client

        # 1. Si client_obj es un wrapper con método generate_content
        if hasattr(client_obj, "generate_content"):
            return client_obj.generate_content(prompt)

        # 2. Si client_obj es la nueva SDK de Google (client.models.generate_content)
        elif hasattr(client_obj, "models") and hasattr(client_obj.models, "generate_content"):
            return client_obj.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

        # 3. Si client_obj es un GenerativeModel directo de google.generativeai
        elif hasattr(client_obj, "generate_content"):
            return client_obj.generate_content(prompt)

        # 4. Fallback directo
        else:
            raise AttributeError(f"El cliente {type(client_obj)} no tiene una interfaz de generación compatible.")