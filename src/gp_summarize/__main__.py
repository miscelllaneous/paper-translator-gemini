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
import json
import logging
from datetime import datetime

# ロガーの取得
logger = logging.getLogger(__name__)

# ログの設定
def setup_logging():
    """ロギングの設定を行う"""
    # ログディレクトリの作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # ログファイル名の設定（日付付き）
    log_file = log_dir / f"gp_summarize_{datetime.now().strftime('%Y%m%d')}.log"
    
    # ログフォーマットの設定
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 既存のハンドラをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # ファイルハンドラ
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

# ログファイルの設定
LOG_FILE = "pdf_processing_log.json"
if os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            processing_log = json.load(f)
        logger.info(f"既存のログファイルを読み込みました: {len(processing_log)}件のエントリがあります")
    except json.JSONDecodeError:
        logger.warning(f"ログファイルの形式が不正です。新しいログファイルを作成します: {LOG_FILE}")
        processing_log = {}
else:
    logger.info(f"新しいログファイルを作成します: {LOG_FILE}")
    processing_log = {}

def update_log(file_path, status, error=None):
    """ログファイルを更新する"""
    # 絶対パスを正規化して保存
    normalized_path = str(Path(file_path).resolve())
    
    # 現在の処理情報
    current_entry = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "error": str(error) if error else None
    }
    
    # 新しいパスの場合は初期化
    if normalized_path not in processing_log:
        processing_log[normalized_path] = {}
    
    # 既存のエントリがある場合は履歴として保存
    if "status" in processing_log[normalized_path]:
        # 履歴フィールドがなければ作成
        if "history" not in processing_log[normalized_path]:
            processing_log[normalized_path]["history"] = []
        
        # 現在の内容を履歴に追加
        old_entry = {
            "status": processing_log[normalized_path].get("status"),
            "timestamp": processing_log[normalized_path].get("timestamp"),
            "error": processing_log[normalized_path].get("error")
        }
        processing_log[normalized_path]["history"].append(old_entry)
    
    # 現在の処理情報を更新
    processing_log[normalized_path].update(current_entry)
    
    # ログファイルに書き込み
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(processing_log, f, ensure_ascii=False, indent=2)
        logger.debug(f"ログファイルを更新しました: {normalized_path}, 状態: {status}")
    except Exception as e:
        logger.error(f"ログファイルの更新に失敗しました: {e}")

def process_pdf_file(pdf_path, output_dir, args):
    """個々のPDFファイルを処理する"""
    try:
        if pdf_path in processing_log:
            if processing_log[pdf_path]["status"] == "success":
                logger.info(f"スキップ: {pdf_path} は既に処理済みです")
                return
            elif processing_log[pdf_path]["status"] == "processing":
                logger.info(f"スキップ: {pdf_path} は処理中です")
                return
            elif processing_log[pdf_path]["status"] == "failed":
                logger.info(f"再試行: {pdf_path} は処理に失敗しました")

        logger.info(f"PDFファイルを処理中: {pdf_path}")
        update_log(pdf_path, "processing")
        
        _, md_path = create_md(pdf_path, output_dir)
        
        summary, output, stats = summarize(
            args.model,
            generation_config,
            lang_module.system_instruction,
            args.rpm,
            lang_module,
            md_path,
            None,
            output_dir,
            args.suffix,
            "",
            args.ccache,
        )

        md_dir = os.path.dirname(md_path)
        summary_path = os.path.join(md_dir, "summary.md")
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        logger.info(f"要約を保存しました: {summary_path}")
        
        # 統計情報をログに記録
        logger.warning("要約の統計情報:")
        for key, value in stats.items():
            logger.warning(f"- {key}: {value}")
        
        update_log(pdf_path, "success")
        
    except Exception as e:
        logger.error(f"エラー: {pdf_path} の処理中にエラーが発生しました: {str(e)}")
        update_log(pdf_path, "failed", e)

def process_directory(input_dir, output_dir, args):
    """ディレクトリ内のPDFファイルを再帰的に処理する"""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    logger.info(f"ディレクトリ処理開始: {input_dir}")
    for pdf_file in input_dir.rglob("*.pdf"):
        relative_path = pdf_file.relative_to(input_dir)
        output_path = output_dir / relative_path.parent / pdf_file.stem
        
        # 出力ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        process_pdf_file(str(pdf_file), str(output_path), args)
    logger.info(f"ディレクトリ処理完了: {input_dir}")

parser = argparse.ArgumentParser(description='Summarize academic papers using Gemini API')
parser.add_argument('paths', nargs='+', help='Path(s) to one or more PDF files or directories')
parser.add_argument('-o', '--output-dir', required=True, help='Output directory for summaries')
parser.add_argument('-l', '--language', choices=['de', 'en', 'es', 'fr', 'ja', 'ko', 'zh'], default='ja', help='Specify the output language')
parser.add_argument('-m', '--model', default='gemini-2.0-flash', help='Specify the Gemini model to use')
parser.add_argument('--rpm', type=int, default=15, help='Maximum requests per minute (default: 15)')
parser.add_argument('--version', action='version', version=f'{name} {__version__}')
parser.add_argument('--suffix', help='Suffix to add to the output file name')
parser.add_argument('--ccache', action='store_true', default=False, help='Enable context caching')
args = parser.parse_args()

# Gemini APIの設定
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

lang_module = selector.init(args.language)

model_name = args.model
if not model_name.startswith("models/"):
    model_name = "models/" + args.model

generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

def main():
    # ロギングの設定
    setup_logging()
    
    logger.info("処理を開始します")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for path in args.paths:
        path = Path(path)
        if path.is_dir():
            process_directory(path, output_dir, args)
        elif path.is_file() and path.suffix.lower() == '.pdf':
            relative_path = path.relative_to(path.parent)
            output_path = output_dir / relative_path.parent / path.stem
            output_path.parent.mkdir(parents=True, exist_ok=True)
            process_pdf_file(str(path), str(output_path), args)
        else:
            logger.warning(f"無効なパスまたはファイル形式です: {path}")
    
    logger.info("処理を完了しました")

if __name__ == "__main__":
    main()
