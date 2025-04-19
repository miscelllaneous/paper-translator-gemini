name = "Japanese"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
日本語は「だ・である調」を使用せよ。
""".strip()

prompts = [
    ("# タイトル", "論文のタイトルのみを日本語に翻訳せよ。"),
    ("# Abstract", "論文の最初にあるAbstractを日本語に翻訳せよ。"),
    ("# 概要", "日本語で、一行の文章で要約せよ。"),
    ("## 問題意識", "論文はどのような問題を解決しようとしているか？日本語で回答せよ。"),
    ("## 手法", "論文はどのような手法を提案しているか？日本語で回答せよ。"),
    ("## 新規性", "論文はどのような新規性があるか？日本語で回答せよ。"),
    ("# 章構成", """章構成を翻訳せずにJSONの配列で出力せよ。例:
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

sprompt = ("セクション「%s」を日本語で要約せよ。", "」「")
