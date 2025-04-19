import argparse
from .__init__ import name, __version__
import os
from dotenv import load_dotenv
import google.generativeai as genai
from .summarize import summarize
from . import gemini
from .lang import selector
from pathlib import Path
from .create_md import create_md

parser = argparse.ArgumentParser(description='Summarize academic papers using Gemini API')
parser.add_argument('paths', nargs='+', help='Path(s) to one or more PDF or markdown files')
parser.add_argument('-d', '--output-dir', help='Output directory for intermediate files')
parser.add_argument('-o', '--output', help='Output file for summary')
parser.add_argument('-l', '--language', choices=['de', 'en', 'es', 'fr', 'ja', 'ko', 'zh'], default=None, help='Specify the output language')
parser.add_argument('-m', '--model', default='gemini-2.0-flash', help='Specify the Gemini model to use')
parser.add_argument('--rpm', type=int, default=15, help='Maximum requests per minute (default: 15)')
parser.add_argument('--version', action='version', version=f'{name} {__version__}')
parser.add_argument('--suffix', help='Suffix to add to the output file name')
parser.add_argument('--ccache', action='store_true', default=False, help='Enable context caching')
parser.add_argument('--markdown', action='store_true', default=False, help='Convert PDF to Markdown before summarization')
args = parser.parse_args()

if os.name == 'nt':  # Check if the system is Windows
    from glob import glob
    paths = []
    for path in args.paths:
        paths.extend(glob(path))
else:
    paths = args.paths

# 入力ファイルの処理
processed_paths = []
for path in paths:
    file_path = Path(path)
    file_ext = file_path.suffix.lower()
    
    if file_ext in ['.pdf']:
        print(f"PDFファイルを処理中: {path}")
        _, md_path = create_md(path, args.output_dir)
        processed_paths.append(md_path)
    elif file_ext in ['.md', '.markdown']:
        processed_paths.append(path)
    else:
        parser.error(f"サポートされていないファイル形式です: {path} (対応: .pdf, .md, .markdown)")

paths = processed_paths
markdowns = len(paths)

if args.output:
    if args.output_dir:
        parser.error("Output directory (-d) cannot be specified when an output file (-o) is provided.")
    if markdowns > 1:
        parser.error("Output file (-o) cannot be specified when multiple files are provided.")

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

lang_module = selector.init('ja')

model_name = args.model
if not model_name.startswith("models/"):
    model_name = "models/" + args.model

generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

def main():
    for i, path in enumerate(paths, 1):
        if i > 1:
            print()
        print(f"==== 要約中 {i}/{markdowns}: {path}")
        
        summary, output, stats = summarize(
            model_name,
            generation_config,
            lang_module.system_instruction,
            args.rpm,
            lang_module,
            path,
            args.output,
            args.output_dir,
            args.suffix,
            f"処理中 {i}/{markdowns}, ",
            args.ccache,
        )
        with open(output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"要約を保存しました: {output}")
        print("統計:")
        gemini.show_stats(stats, "- ")

if __name__ == "__main__":
    main()
