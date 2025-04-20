#!/usr/bin/env python3
"""
マークダウンをPDFに変換するスタンドアロンツール
pypandocライブラリを使用したバージョン
"""

import argparse
import os
import sys
import logging
import re
import tempfile
import shutil
from pathlib import Path
from glob import glob
import pypandoc

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def convert_image_paths_to_absolute(md_path):
    """マークダウンファイル内の画像パスを絶対パスに変換する"""
    try:
        # 入力ファイルの絶対パスとディレクトリパスを取得
        md_path = os.path.abspath(md_path)
        md_dir = os.path.dirname(md_path)
        
        # 一時ファイルを作成
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
        temp_path = temp_file.name
        
        logger.info(f"画像パスを絶対パスに変換しています: {md_path}")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 画像リンクを検索して絶対パスに置換
        def replace_image_path(match):
            image_path = match.group(2)
            if not image_path.startswith('/') and not image_path.startswith('http'):
                # 相対パスの場合、絶対パスに変換
                abs_image_path = os.path.join(md_dir, image_path)
                return f'![{match.group(1)}]({abs_image_path})'
            return match.group(0)
        
        modified_content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image_path, content)
        
        # 変換後のコンテンツを一時ファイルに書き込み
        temp_file.write(modified_content)
        temp_file.close()
        
        logger.info(f"画像パスを絶対パスに変換したファイルを保存しました: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"画像パスの変換に失敗しました: {e}")
        return None

def convert_md_to_pdf(md_path, output_path=None, font="IPAexGothic", template='configs/template.tex', pdf_engine="lualatex"):
    """マークダウンファイルをPDFに変換する"""
    try:
        # 入力ファイルの絶対パスを取得
        md_path = os.path.abspath(md_path)
        
        # 出力PDFのパスを設定
        if output_path is None:
            # 入力ファイルのディレクトリ名を取得
            dir_name = os.path.basename(os.path.dirname(md_path))
            # 親ディレクトリのパスを取得
            parent_dir = os.path.dirname(os.path.dirname(md_path))
            # 出力ファイル名はディレクトリ名.pdf
            output_path = os.path.join(parent_dir, f"{dir_name}.pdf")
        else:
            output_path = os.path.abspath(output_path)
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 画像パスを絶対パスに変換
        temp_md_path = convert_image_paths_to_absolute(md_path)
        if not temp_md_path:
            logger.error("画像パスの変換に失敗したため、変換を中止します")
            return None
        
        logger.info(f"'{temp_md_path}' を '{output_path}' に変換しています...")
        
        # pandocコマンドオプションに相当する引数を設定
        extra_args = []
        
        # PDF出力エンジンを設定
        extra_args.extend(["--pdf-engine", pdf_engine])
        
        # テンプレートを設定（指定されている場合）
        if template:
            extra_args.extend(["--template", template])
        
        # フォントを設定
        if font:
            extra_args.extend(["-V", f"mainfont={font}"])
        
        # pypandocを使って変換
        output = pypandoc.convert_file(
            temp_md_path, 
            'pdf', 
            outputfile=output_path,
            extra_args=extra_args
        )

        
        # 一時ファイルを削除
        try:
            os.unlink(temp_md_path)
            logger.info(f"一時ファイルを削除しました: {temp_md_path}")
        except Exception as e:
            logger.warning(f"一時ファイルの削除に失敗しました: {e}")
        
        
        logger.info(f"マークダウンをPDFに変換しました: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"PDFへの変換に失敗しました: {e}")

        return None

def process_directory(input_dir, output_dir=None, font="IPAexGothic", recursive=False, template=None, pdf_engine="lualatex"):
    """ディレクトリ内のマークダウンファイルをPDFに変換する"""
    logger.info(f"ディレクトリ '{input_dir}' 内のマークダウンファイルを処理しています...")
    
    # 入力ディレクトリの絶対パスを取得
    input_dir = os.path.abspath(input_dir)
    
    # 出力ディレクトリを設定
    if output_dir is None:
        output_dir = os.path.dirname(input_dir)
    else:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    # 検索パターンを設定
    if recursive:
        search_pattern = os.path.join(input_dir, "**", "*.md")
        md_files = glob(search_pattern, recursive=True)
    else:
        search_pattern = os.path.join(input_dir, "*.md")
        md_files = glob(search_pattern)
    
    logger.info(f"{len(md_files)}個のマークダウンファイルを見つけました")
    
    # 各マークダウンファイルを変換
    success_count = 0
    for md_file in md_files:
        # 出力PDFのパスを設定
        rel_path = os.path.relpath(md_file, input_dir)
        # mdファイルが含まれるディレクトリの名前を取得
        dir_name = os.path.basename(os.path.dirname(md_file))
        # 親ディレクトリに保存
        output_path = os.path.join(output_dir, f"{dir_name}.pdf")
        
        # ディレクトリがない場合は作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 変換を実行
        result = convert_md_to_pdf(md_file, output_path, font, template, pdf_engine)
        if result:
            success_count += 1
    
    logger.info(f"処理完了: {success_count}/{len(md_files)}ファイルを変換しました")
    return success_count

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="マークダウンファイルをPDFに変換するツール")
    parser.add_argument("input", help="入力マークダウンファイルまたはディレクトリ")
    parser.add_argument("-o", "--output", help="出力PDFファイルまたはディレクトリ")
    parser.add_argument("-r", "--recursive", action="store_true", help="ディレクトリ内を再帰的に検索")
    parser.add_argument("-f", "--font", default="IPAexGothic", help="PDFで使用するフォント名")
    parser.add_argument("-t", "--template", default="configs/template.tex", help="PDFテンプレートファイルへのパス")
    parser.add_argument("-e", "--engine", default="lualatex", help="PDF変換エンジン (例: lualatex, xelatex)")
    args = parser.parse_args()
    
    # 入力がディレクトリかファイルかを判定
    if os.path.isdir(args.input):
        process_directory(args.input, args.output, args.font, args.recursive, args.template, args.engine)
    elif os.path.isfile(args.input) and args.input.lower().endswith('.md'):
        convert_md_to_pdf(args.input, args.output, args.font, args.template, args.engine)
    else:
        logger.error(f"入力 '{args.input}' は有効なマークダウンファイルまたはディレクトリではありません")
        sys.exit(1)

if __name__ == "__main__":
    main() 