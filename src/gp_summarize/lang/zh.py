name = "Chinese"

system_instruction = """
You are an expert at analyzing and summarizing academic papers.
Please use $TeX$ to write mathematical equations.
Please only return the results, and do not include any comments.
Use a formal academic writing style in Chinese.
""".strip()

prompts = [
    ("# 标题", "仅将论文标题翻译成中文。"),
    ("# Abstract", "将文档开头的摘要翻译成中文。"),
    ("# 概述", "用一句话用中文总结文档。"),
    ("## 问题陈述", "文档试图解决什么问题？用中文回答。"),
    ("## 方法论", "文档提出了什么方法论？用中文回答。"),
    ("## 创新性", "文档的创新性是什么？用中文回答。"),
    ("# 文档结构", """生成文档结构的JSON数组，不需要翻译。示例：
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

sprompt = ("用中文总结章节'%s'。", "', '")
