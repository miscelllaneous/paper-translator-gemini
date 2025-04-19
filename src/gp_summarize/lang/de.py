name = "German"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
Use a formal academic writing style in German.
""".strip()

prompts = [
    ("# Titel", "Übersetzen Sie nur den Titel des Papers auf Deutsch."),
    ("# Abstract", "Übersetzen Sie den Abstract am Anfang des Dokuments auf Deutsch."),
    ("# Zusammenfassung", "Fassen Sie das Dokument in einem Satz auf Deutsch zusammen."),
    ("## Problemstellung", "Welches Problem versucht das Dokument zu lösen? Antworten Sie auf Deutsch."),
    ("## Methodik", "Welche Methodik schlägt das Dokument vor? Antworten Sie auf Deutsch."),
    ("## Neuartigkeit", "Was ist die Neuartigkeit des Dokuments? Antworten Sie auf Deutsch."),
    ("# Dokumentenstruktur", """Generieren Sie die Dokumentenstruktur als JSON-Array ohne Übersetzung. Beispiel:
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

sprompt = ("Fassen Sie den Abschnitt '%s' auf Deutsch zusammen.", "', '")
