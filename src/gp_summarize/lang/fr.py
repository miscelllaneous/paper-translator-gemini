name = "French"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
Use a formal academic writing style in French.
""".strip()

prompts = [
    ("# Titre", "Traduisez uniquement le titre de l'article en français."),
    ("# Abstract", "Traduisez l'Abstract au début du document en français."),
    ("# Résumé", "Résumez le document en une seule phrase en français."),
    ("## Énoncé du Problème", "Quel problème le document cherche-t-il à résoudre ? Répondez en français."),
    ("## Méthodologie", "Quelle méthodologie le document propose-t-il ? Répondez en français."),
    ("## Nouveauté", "Quelle est la nouveauté du document ? Répondez en français."),
    ("# Structure du Document", """Générez la structure du document sous forme de tableau JSON sans traduction. Exemple :
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

sprompt = ("Résumez la section '%s' en français.", "', '")
