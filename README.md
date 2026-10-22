# Text-to-ORM: Multi-Agent Architecture for Enterprise Query Generation

Este repositorio contiene el código fuente, la arquitectura multiagente y el marco de evaluación experimental para la investigación de tesis sobre la generación automática de consultas utilizando capas de abstracción ORM (Eloquent) frente al enfoque tradicional Text-to-SQL.

## 📌 Resumen de la Investigación

* **Problema:** Los enfoques tradicionales *Text-to-SQL* (C1) operan sobre esquemas relacionales físicos (DDL), exponiendo la infraestructura subyacente, ignorando reglas de negocio a nivel de aplicación (ej. *Soft Deletes*) y colapsando ante sesgos idiomáticos en el código fuente.
* **Solución Propuesta:** La arquitectura C2 (*Text-to-ORM*) combina recuperación contextual via RAG sobre modelos PHP/Eloquent con un agente de sanitización estática que aísla la base de datos y garantiza la validez sintáctica.
* **Resultados:** 
  * **Match Rate Global:** C2 (57.0%) vs C1 (28.0%) — un incremento de +29.0 puntos porcentuales.
  * **Resistencia al Sesgo Idiomático:** En el proyecto en español (*Inventario TI*), C2 mantuvo un 56.0% de aciertos frente al colapso del 12.0% en C1.

---

## 🏗️ Arquitectura del Sistema (C2)

El pipeline C2 se compone de los siguientes módulos:

1. **AST PHP Parser & Indexador RAG:** Extrae firmas de clases, atributos (`$fillable`, `$casts`) y relaciones (`hasMany`, `belongsTo`) de los archivos en `app/Models/` para generar incrustaciones semánticas en ChromaDB (`text-embedding-3-small`).
2. **Agente Especialista Eloquent:** Recibe la intención en lenguaje natural y el contexto del modelo PHP recuperado por RAG para sintetizar código Eloquent Query Builder.
3. **Agente Sanitizador:** Intercepta la salida, reescribe llamadas a SQL crudo (`DB::raw`) y sustituye referencias a tablas físicas por sus correspondientes clases PHP (`User::class`).

---

## 📂 Estructura del Repositorio

```text
├── src/
│   ├── ast_parser/         # Analizador sintáctico para extraer metadata de modelos PHP
│   ├── rag/                # Módulo de recuperación vectorial y embeddings (ChromaDB)
│   ├── agents/             # Prompts y orquestación de agentes (Especialista + Sanitizador)
│   └── evaluator/          # Motor de evaluación y comparación sintáctica (Match Rate)
├── benchmark/              # Dataset consolidado de pruebas (N=100)
├── config/                 # Configuraciones de entorno y modelos
├── .gitignore              # Exclusión de scripts de generación y credenciales
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación principal

---

## 🚀 Reproducibilidad y Ejecución

Para garantizar la auditabilidad y reproducibilidad de los experimentos presentados en la investigación, el entorno puede replicarse mediante los siguientes pasos.

### Prerrequisitos

* **Python 3.10+**
* Clave de API válida para los modelos de lenguaje (OpenAI / Google Gemini según la configuración seleccionada)

### 1. Instalación y Configuración del Entorno

Clona el repositorio e instala las dependencias necesarias en un entorno virtual aislado:

```bash
# Clonar el repositorio de la investigación
git clone https://github.com/wendy-stefany/text-to-orm 
cd text-to-orm

# Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate  

# En Windows: 
venv\Scripts\activate

# Instalar dependencias del proyecto
pip install -r requirements.txt

### 2. Configuración de Variables de Entorno

# Crea un archivo .env en la raíz del proyecto basándote en la plantilla de ejemplo y configura tus credenciales de API
cp .env.example .env

# Asegúrate de definir las claves requeridas dentro de .env

GEMINI_API_KEY=tu_api_key_aqui

### 3. Ejecución del Benchmark Comparativo

# 1. (Opcional) Extraer el esquema contextual de los modelos PHP mediante AST
python build_models_schema.py

# 2. Ejecutar la evaluación del benchmark experimental (C1 vs C2)
python evaluate_benchmark.py

# 3. Procesar resultados, generar gráficos (PNG) y reportes sintéticos (MD)
python analyze_qualitative.py