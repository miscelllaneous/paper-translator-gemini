import argparse
from .__init__ import name, __version__
import os
from dotenv import load_dotenv
import google.generativeai as genai
from .summarize import summarize
from . import gemini  # geminiモジュールを直接インポート
import gp_summarize.prompts as prompts
from pathlib import Path
from .create_md import create_md
import json
import logging
from datetime import datetime
import subprocess
from .md_to_pdf import convert_md_to_pdf

# ロガーの取得
logger = logging.getLogger(__name__)
# 料金計算用ロガーの取得
cost_logger = logging.getLogger("cost")

# ログの設定
def setup_logging():
    """ロギングの設定を行う"""
    # ログディレクトリの作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # ログファイル名の設定（日付付き）
    log_file = log_dir / f"gp_summarize_{datetime.now().strftime('%Y%m%d')}.log"
    cost_log_file = log_dir / f"gp_summarize_cost_{datetime.now().strftime('%Y%m%d')}.log"
    
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
    
    # 料金計算用ロガーの設定
    cost_logger = logging.getLogger("cost")
    cost_logger.setLevel(logging.INFO)
    
    # 料金計算用ファイルハンドラ
    cost_file_handler = logging.FileHandler(cost_log_file, encoding='utf-8')
    cost_file_handler.setFormatter(logging.Formatter(log_format))
    cost_logger.addHandler(cost_file_handler)
    
    # 料金計算用コンソールハンドラ
    cost_console_handler = logging.StreamHandler()
    cost_console_handler.setFormatter(logging.Formatter(log_format))
    cost_logger.addHandler(cost_console_handler)

# 料金を計算する関数
def calculate_cost(prompt_tokens, candidates_tokens):
    """トークン数から料金を計算する"""
    # 入力トークン: 1Mあたり25円、出力トークン: 1Mあたり100円
    input_cost_per_million = 25
    output_cost_per_million = 100
    
    input_cost = prompt_tokens * input_cost_per_million / 1000000
    output_cost = candidates_tokens * output_cost_per_million / 1000000
    total_cost = input_cost + output_cost
    
    return input_cost, output_cost, total_cost

# ログファイルの設定
LOG_FILE = "logs/pdf_processing_log.json"
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

        # 要約の生成（--nosummaryが指定されていない場合のみ実行）
        if not args.nosummary:
            logger.info(f"要約を生成中: {md_path}")
            
            # 要約用のモデル設定
            summary_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=prompts.system_instruction,
            )
            
            # 要約用のファイルをアップロード
            summary_file = genai.upload_file(md_path, mime_type="text/markdown")
            
            try:
                # 要約を生成
                summary_result, summary_usage = gemini.generate_content(summary_model, args.rpm, summary_file, prompts.summary_prompt)
                
                # 要約の保存先
                summary_dir = os.path.dirname(md_path)
                summary_path = os.path.join(summary_dir, "summary.md")
                
                # 要約を保存
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(summary_result)
                
                logger.info(f"要約を保存しました: {summary_path}")
                
                prompt_tokens = summary_usage.get("prompt_token_count", 0)
                candidates_tokens = summary_usage.get("candidates_token_count", 0)
                input_cost, output_cost, total_cost = calculate_cost(prompt_tokens, candidates_tokens)
                
                # 料金ログの記録
                cost_logger.info(f"要約処理の料金情報 - ファイル: {pdf_path}")
                cost_logger.info(f"入力トークン数: {prompt_tokens}, 入力料金: {input_cost:.2f}円")
                cost_logger.info(f"出力トークン数: {candidates_tokens}, 出力料金: {output_cost:.2f}円")
                cost_logger.info(f"合計料金: {total_cost:.2f}円")


                gemini.show_stats(summary_usage)
            except Exception as e:
                logger.error(f"要約の生成に失敗しました: {e}")
                update_log(pdf_path, "failed", e)
                return
        else:
            logger.info(f"--nosummary オプションが指定されたため、要約をスキップします")
    
        # 翻訳の生成
        logger.info(f"翻訳を生成中: {md_path}")
        translation, output, stats = summarize(
            args.model,
            generation_config,
            prompts.system_instruction,
            args.rpm,
            md_path,
            None,
            output_dir,
            args.suffix,
            "",
            args.ccache,
        )
        

        # 翻訳処理の料金計算
        prompt_tokens = stats.get("prompt_token_count", 0)
        candidates_tokens = stats.get("candidates_token_count", 0)
        input_cost, output_cost, total_cost = calculate_cost(prompt_tokens, candidates_tokens)
        
        # 料金ログの記録
        cost_logger.info(f"翻訳処理の料金情報 - ファイル: {pdf_path}")
        cost_logger.info(f"入力トークン数: {prompt_tokens}, 入力料金: {input_cost:.2f}円")
        cost_logger.info(f"出力トークン数: {candidates_tokens}, 出力料金: {output_cost:.2f}円")
        cost_logger.info(f"合計料金: {total_cost:.2f}円")
        
        # 要約と翻訳を合体させる（--nosummaryが指定されていない場合のみ実行）
        combined_path = None
        if not args.nosummary:
            md_dir = os.path.dirname(md_path)
            summary_path = os.path.join(md_dir, "summary.md")
            combined_path = os.path.join(md_dir, "combined.md")
            
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, "r", encoding="utf-8") as summary_file:
                        summary_content = summary_file.read()
                    
                    translation_path = os.path.join(md_dir, "translation.md")
                    if os.path.exists(translation_path):
                        with open(translation_path, "r", encoding="utf-8") as translation_file:
                            translation_content = translation_file.read()
                        
                        # 合体させた内容
                        combined_content = summary_content + "\n\n---\n\n## 論文全文\n\n" + translation_content
                        
                        # 合体したファイルを保存
                        with open(combined_path, "w", encoding="utf-8") as combined_file:
                            combined_file.write(combined_content)
                        
                        logger.info(f"要約と翻訳を合体させました: {combined_path}")
                        logger.info(f"入力ファイルを削除しました: {md_path}")
                        os.unlink(summary_path)
                        logger.info(f"要約ファイルを削除しました: {summary_path}")
                        os.unlink(translation_path)
                        logger.info(f"翻訳ファイルを削除しました: {translation_path}")
                except Exception as e:
                    logger.error(f"要約と翻訳の合体に失敗しました: {e}")
        else:
            # 要約がない場合は翻訳のみのファイルをPDFに変換
            combined_path = os.path.join(os.path.dirname(md_path), "translation.md")
            
        # マークダウンをPDFに変換
        if args.convert_pdf and combined_path and os.path.exists(combined_path):
            convert_md_to_pdf(combined_path)
        
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
parser.add_argument('-o', '--output-dir', default='./output', help='Output directory for summaries')
parser.add_argument('-l', '--language', choices=['ja'], default='ja', help='Specify the output language')
parser.add_argument('-m', '--model', default='gemini-2.5-flash-preview-04-17', help='Specify the Gemini model to use')
parser.add_argument('--rpm', type=int, default=15, help='Maximum requests per minute (default: 15)')
parser.add_argument('--version', action='version', version=f'{name} {__version__}')
parser.add_argument('--suffix', help='Suffix to add to the output file name')
parser.add_argument('--ccache', action='store_true', default=False, help='Enable context caching')
parser.add_argument('--nosummary', action='store_true', default=False, help='Skip summary generation')
parser.add_argument('--convert-pdf', action='store_true', default=True, help='Convert the generated markdown to PDF')
args = parser.parse_args()

# Gemini APIの設定
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model_name = args.model
if not model_name.startswith("models/"):
    model_name = "models/" + args.model

generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
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
