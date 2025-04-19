name = "Spanish"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
Use a formal academic writing style in Spanish.
""".strip()

prompts = [
    ("# Título", "Traduce solamente el título del artículo al español."),
    ("# Abstract", "Traduce el Abstract al principio del documento al español."),
    ("# Resumen", "Resume el documento en una sola oración en español."),
    ("## Planteamiento del Problema", "¿Qué problema intenta resolver el documento? Responde en español."),
    ("## Metodología", "¿Qué metodología propone el documento? Responde en español."),
    ("## Novedad", "¿Cuál es la novedad del documento? Responde en español."),
    ("# Estructura del Documento", """Genera la estructura del documento como un array JSON sin traducir. Ejemplo:
```json
[
  "1 Introduction",
  "1.1 Background",
  "2 Methods",
  "2.1 Data",
  "2.1.1 Dataset"
]
```"""),
]

sprompt = ("Resume la sección '%s' en español.", "', '")
