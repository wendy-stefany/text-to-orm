import json
import re

class ModelSelectionAgent:
    """
    Agente de Schema Linking robusto y dinámico.
    Identifica clases PHP principales independientemente de minúsculas,
    plurales o formato de respuesta del LLM.
    """
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client

    def select_models(self, question: str, schema_context: str) -> dict:
        # 1. Extraer dinámicamente las clases PHP disponibles en el schema_context
        # Captura cualquier palabra que esté al inicio de una línea o viñeta de modelo
        available_classes = re.findall(r'-\s*([A-Za-z0-9_]+)', schema_context)
        available_classes = list(dict.fromkeys(available_classes)) # Elimina duplicados

        prompt = f"""
Eres un Agente experto en Schema Linking para Laravel Eloquent ORM.
Tu ÚNICA tarea es analizar la pregunta en Lenguaje Natural y seleccionar la Clase PHP (Modelo) exacta.

### CLASES PHP DISPONIBLES EN EL REPOSITORIO:
{available_classes}

### DETALLE DEL ESQUEMA COMPLETO:
{schema_context}

### REGLAS ESTRICTAS DE SELECCIÓN:
1. "primary_model": DEBE ser EXACTAMENTE una de las clases listadas en CLASES PHP DISPONIBLES.
2. Manejo de Variaciones:
   - Si la consulta dice "user", "users", "usuario" o "usuarios", debes seleccionar "User".
   - Si la consulta dice "alumno", "alumnos", "estudiante", "estudiantes", debes seleccionar "Alumno".
   - Ignora diferencias de mayúsculas/minúsculas y convierte los plurales al nombre exacto de la Clase en singular.
3. "required_relations": Lista de métodos de relación requeridos. Si no aplica, usa [].

### PREGUNTA DEL USUARIO:
"{question}"

### RESPUESTA (ÚNICAMENTE JSON PLANO, SIN MARCADORES DE CÓDIGO NI TEXTO EXTRA):
{{
  "primary_model": "<NombreExactoDeLaClase>",
  "required_relations": [],
  "reasoning": "<Breve explicacion>"
}}
"""

        try:
            response = self.gemini_client.generate_content(prompt)
            raw_text = response.text.strip()
            
            # 2. Extracción ultra-limpia del bloque JSON (Evita errores de sintaxis si Gemini agrega markdown)
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            clean_json_str = json_match.group(0) if json_match else raw_text

            parsed_response = json.loads(clean_json_str)
            raw_selected = str(parsed_response.get("primary_model", "")).strip()

            # 3. Mapeo Case-Insensitive y de Plurales contra la lista real de clases
            final_model = self._match_to_available_class(raw_selected, question, available_classes)
            parsed_response["primary_model"] = final_model

            return parsed_response

        except Exception as e:
            # Fallback Dinámico en caso de fallo de red o formato
            fallback_model = self._match_to_available_class("Unknown", question, available_classes)
            return {
                "primary_model": fallback_model,
                "required_relations": [],
                "reasoning": f"Fallo en parsing ({str(e)}). Fallback dinámico -> {fallback_model}"
            }

    def _match_to_available_class(self, candidate: str, question: str, available_classes: list) -> str:
        """
        Garantiza que el modelo devuelto coincida exactamente con una clase real de PHP,
        resolviendo minúsculas, plurales y variaciones comunes de idioma.
        """
        # A) Coincidencia directa con la respuesta del LLM (Case-insensitive)
        for real_cls in available_classes:
            if real_cls.lower() == candidate.lower():
                return real_cls

        # B) Búsqueda directa en la pregunta (Caso de emergencia/fallback)
        q_words = re.findall(r'\b\w+\b', question.lower())
        for real_cls in available_classes:
            cls_lower = real_cls.lower()
            for word in q_words:
                if (word == cls_lower or 
                    word == f"{cls_lower}s" or 
                    word == f"{cls_lower}es" or 
                    cls_lower == f"{word}s" or 
                    cls_lower == f"{word}es" or
                    (cls_lower == "user" and word in ["usuario", "usuarios"])):
                    return real_cls

        return "Unknown"