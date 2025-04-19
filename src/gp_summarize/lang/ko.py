name = "Korean"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
Use a formal academic writing style in Korean.
""".strip()

prompts = [
    ("# 제목", "논문 제목만 한국어로 번역하세요."),
    ("# Abstract", "문서 시작 부분의 초록을 한국어로 번역하세요."),
    ("# 개요", "문서를 한 문장으로 한국어로 요약하세요."),
    ("## 문제 진술", "문서가 해결하려는 문제는 무엇입니까? 한국어로 대답하세요."),
    ("## 방법론", "문서가 제안하는 방법론은 무엇입니까? 한국어로 대답하세요."),
    ("## 혁신성", "문서의 혁신성은 무엇입니까? 한국어로 대답하세요."),
    ("# 문서 구조", """문서 구조를 번역 없이 JSON 배열로 생성하세요. 예시:
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

sprompt = ("섹션 '%s'을 한국어로 요약하세요.", "', '")
