import json
import re

class SQLAgent:
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client

    def _call_gemini(self, prompt: str):
        """Maneja la llamada a la API adaptándose tanto a SDKs antiguos como nuevos de Gemini."""
        if hasattr(self.gemini_client, 'models') and hasattr(self.gemini_client.models, 'generate_content'):
            return self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
        elif hasattr(self.gemini_client, 'generate_content'):
            return self.gemini_client.generate_content(prompt)
        else:
            raise AttributeError("El cliente de Gemini proporcionado no tiene un método de generación conocido.")

    def generate_sql_query(self, question: str, schema_context: str) -> dict:
        """
        Genera una consulta SQL estándar basada en la pregunta del usuario y el esquema.
        Devuelve un diccionario con la consulta limpia y el objeto de respuesta con metadatos.
        """
        prompt = f"""
        Eres un experto Administrador de Bases de Datos (DBA) especializado en SQL ANSI / MySQL.
        Tu ÚNICA tarea es generar la consulta SQL exacta que responda a la pregunta del usuario.

        ### ESQUEMA DEL REPOSITORIO / TABLAS:
        {schema_context}

        ### PREGUNTA DEL USUARIO:
        "{question}"

        ### INSTRUCCIONES:
        1. Genera una consulta SQL válida que devuelva la información solicitada.
        2. Mantén las palabras clave SQL en MAYÚSCULAS (SELECT, FROM, WHERE, JOIN, etc.).
        3. Responde EXCLUSIVAMENTE en formato JSON plano sin bloques de código Markdown adicionales.

        Ejemplo de Salida esperada:
        {{
            "c_sql": "SELECT * FROM users WHERE is_account_administrator = 1;"
        }}
        """

        try:
            # Llamada adaptable a Gemini
            response = self._call_gemini(prompt)
            
            # Extraer el texto devuelto
            if hasattr(response, 'text'):
                raw_text = response.text.strip()
            else:
                raw_text = str(response).strip()

            if not raw_text:
                print("⚠️ SQLAgent: La respuesta de Gemini vino vacía.")
                return {"query": "", "response": response}

            extracted_sql = ""

            # 1. INTENTO A: Parseo JSON
            clean_text = re.sub(r'```(?:json)?', '', raw_text).replace('```', '').strip()
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            
            if json_match:
                parsed_response = json.loads(json_match.group(0))
                sql_query = parsed_response.get("c_sql", "").strip()
                if sql_query:
                    extracted_sql = sql_query

            # 2. INTENTO B (FALLBACK): Extraer directamente la sentencia SELECT mediante Regex
            if not extracted_sql:
                sql_match = re.search(r'(SELECT\s+.*?;)', raw_text, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    extracted_sql = sql_match.group(1).strip()
                else:
                    sql_match_no_semi = re.search(r'(SELECT\s+.*)', raw_text, re.DOTALL | re.IGNORECASE)
                    if sql_match_no_semi:
                        extracted_sql = sql_match_no_semi.group(1).strip() + ";"

            if not extracted_sql:
                print(f"⚠️ SQLAgent: No se pudo extraer SQL de la respuesta bruta:\n{raw_text}")

            return {
                "query": extracted_sql,
                "response": response
            }

        except Exception as e:
            print(f"❌ Error en SQLAgent al generar SQL: {e}")
            return {"query": "", "response": None}