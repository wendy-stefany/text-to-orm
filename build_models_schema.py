import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

class EloquentSchemaExtractor:
    """
    Analiza de forma estática los archivos de código fuente PHP en app/Models
    para extraer nombres de modelos, tablas asociadas, atributos comentados/visibles
    y relaciones de Eloquent (hasMany, belongsTo, belongsToMany, etc.).
    """
    def __init__(self, models_dir: str):
        self.models_dir = models_dir

    def extract_schema(self) -> dict:
        if not os.path.exists(self.models_dir):
            raise FileNotFoundError(f"❌ La ruta especificada no existe: {self.models_dir}")

        schema = {}

        for root, _, files in os.walk(self.models_dir):
            for file in files:
                if file.endswith(".php"):
                    file_path = os.path.join(root, file)
                    model_info = self._parse_php_model(file_path)
                    if model_info:
                        schema[model_info["model_name"]] = model_info

        return schema

    def _parse_php_model(self, file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extraer nombre de la clase/modelo
        class_match = re.search(r'class\s+([A-Za-z0-9_]+)\s+extends\s+', content)
        if not class_match:
            return None

        model_name = class_match.group(1)

        # Extraer nombre de la tabla (si está explícito)
        table_match = re.search(r'protected\s+\$table\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        table_name = table_match.group(1) if table_match else f"{model_name.lower()}s"

        # Extraer atributos/propiedades de PHPDoc (@property)
        properties = re.findall(r'@property(?:-read)?\s+([^\s]+)\s+\$([A-Za-z0-9_]+)', content)
        attributes = [prop[1] for prop in properties]

        # Extraer atributos dentro de $fillable o $guarded si no hay PHPDoc
        fillable_match = re.search(r'protected\s+\$fillable\s*=\s*\[(.*?)\];', content, re.DOTALL)
        if fillable_match:
            fillable_items = re.findall(r'[\'"]([^\'"]+)[\'"]', fillable_match.group(1))
            attributes = list(set(attributes + fillable_items))

        # Extraer métodos de relación Eloquent
        relations = []
        relation_patterns = [
            (r'public\s+function\s+([A-Za-z0-9_]+)\s*\(\)\s*\{[^}]*?->belongsTo\s*\(\s*([A-Za-z0-9_:]+)', "belongsTo"),
            (r'public\s+function\s+([A-Za-z0-9_]+)\s*\(\)\s*\{[^}]*?->hasMany\s*\(\s*([A-Za-z0-9_:]+)', "hasMany"),
            (r'public\s+function\s+([A-Za-z0-9_]+)\s*\(\)\s*\{[^}]*?->hasOne\s*\(\s*([A-Za-z0-9_:]+)', "hasOne"),
            (r'public\s+function\s+([A-Za-z0-9_]+)\s*\(\)\s*\{[^}]*?->belongsToMany\s*\(\s*([A-Za-z0-9_:]+)', "belongsToMany"),
            (r'public\s+function\s+([A-Za-z0-9_]+)\s*\(\)\s*\{[^}]*?->morphMany\s*\(\s*([A-Za-z0-9_:]+)', "morphMany"),
        ]

        for pattern, rel_type in relation_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                rel_name = match[0]
                target_model = match[1].replace('::class', '').strip().split('\\')[-1]
                relations.append({
                    "relation_name": rel_name,
                    "type": rel_type,
                    "related_model": target_model
                })

        return {
            "model_name": model_name,
            "table_name": table_name,
            "attributes": attributes,
            "relations": relations
        }

def main():
    print("\n" + "="*80)
    print("🛠️ EXTRACCIÓN Y CONSTRUCCIÓN DEL ESQUEMA DE MODELOS PHP (/models_schema)")
    print("="*80 + "\n")

    # Ruta configurable por .env o fallback directo a inventario-ti-laravel
    models_path = os.getenv("MODELS_PATH", "../inventario-ti-laravel/app/Models")
    print(f"📁 Analizando directorio de modelos: '{models_path}'")

    try:
        extractor = EloquentSchemaExtractor(models_path)
        schema_data = extractor.extract_schema()

        if not schema_data:
            print("⚠️ No se encontraron clases o modelos PHP válidos en el directorio especificado.")
            return

        # Crear directorio /models_schema o data/models_schema
        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "models_schema.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Extracción completada exitosamente.")
        print(f"📊 Total de Modelos procesados: {len(schema_data)}")
        print(f"📄 Esquema guardado en: '{output_file}'")

    except Exception as e:
        print(f"❌ Error al procesar el esquema de modelos: {e}")

if __name__ == "__main__":
    main()