name = "English"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
Use a formal academic writing style.
""".strip()

prompts = [
    ("# Title", "Translate only the paper title into English."),
    ("# Abstract", "Translate the Abstract at the beginning of the paper into English."),
    ("# Overview", "Summarize the paper in a single sentence in English."),
    ("## Problem Statement", "What problem is the paper trying to solve? Answer in English."),
    ("## Methodology", "What methodology does the paper propose? Answer in English."),
    ("## Novelty", "What is the novelty of the paper? Answer in English."),
    ("# Chapter Structure", """Output the chapter structure as a JSON array without translation. Example:
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

sprompt = ("Summarize section '%s' in English.", "', '")
