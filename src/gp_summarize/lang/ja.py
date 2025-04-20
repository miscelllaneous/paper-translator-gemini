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
    ("## 図表", """論文の図表を日本語で翻訳せよ。ただし、対応する画像の部分も出力せよ。
     入力例：
     ![](_page_1_Figure_2.jpeg)

     **Fig. 1** Left lateral (**a**) and inferosuperior (**b**) projections of maximum-intensity-projection (MIP) images show the A2 segment of the left anterior cerebral artery (ACA) taking an anteroinferior course and making a hairpin turn, and fnally continuing to the left accessory

middle cerebral artery (MCA), indicative of a type 4 persistent primitive olfactory artery (PPOA) (long arrows). Right accessory MCA is also suspected (short arrows)
     
     出力例：
     ![](_page_1_Figure_2.jpeg)
     
     図1最大強度投影（MIP）像の左外側（a）および右下（b）投影では、左前大脳動脈（ACA）のA2セグメントが前内側に向かってヘアピンカーブを描き、最終的に左副中大脳動脈（MCA）に続いている。
中大脳動脈（MCA）は4型持続性原始嗅動脈（PPOA）を示す（長矢印）。右副MCAも疑われる（短い矢印）。
     """),
    ("# 章構成", """章構成を翻訳せずにJSONの配列で出力せよ。ただし、Abstract、Keywords、Author contributions、Declarations、Conflict of interest、Referenceなどは含めない。
     例：
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
