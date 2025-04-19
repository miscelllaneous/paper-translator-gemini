from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.output import save_output
import os
from pathlib import Path

def create_md(filepath: str, output_dir: str = None) -> tuple[str, str]:
    """
    PDFファイルを処理してマークダウンに変換する関数
    
    Args:
        filepath (str): 処理するPDFファイルのパス
        output_dir (str, optional): 出力先ディレクトリ。指定されない場合はPDFと同じ場所に作成
        
    Returns:
        tuple[str, str]: 生成されたマークダウンの内容とマークダウンファイルの保存パス
    """
    # PDFファイル名を取得（拡張子なし）
    pdf_name = Path(filepath).stem
    
    # 出力ディレクトリが指定されていない場合は、PDFと同じ場所に作成
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(filepath), pdf_name)
    else:
        output_dir = os.path.join(output_dir, pdf_name)
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # PDFを変換
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )
    rendered = converter(filepath)
    
    # 結果を保存
    save_output(rendered, output_dir, 'result')
    
    # テキストと画像を抽出
    text, _, images = text_from_rendered(rendered)
    
    # マークダウンファイルのパス
    md_path = os.path.join(output_dir, f"{pdf_name}.md")
    
    # マークダウンファイルに保存
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return text, md_path

if __name__ == "__main__":
    # テスト用のコード
    filepath = "/Users/misc/gemini-paper-summarizer/tests/Uchino and Ishihara 2021 - Type 4 persistent primitive olfactory artery ... g from the fenestrated segment of the distal anterior cerebral artery.pdf"  # ここに実際のPDFファイルのパスを指定
    text, md_path = create_md(filepath)
    print(f"マークダウンファイルが保存されました: {md_path}")
    print(f"抽出されたテキストの長さ: {len(text)}")
    
