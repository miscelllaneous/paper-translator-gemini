import os
import google.generativeai as genai
import gps.prompts as prompts
from . import gemini

def summarize(
    model_name,
    generation_config,
    system_instruction,
    max_rpm,
    path,
    output=None,
    output_dir=None,
    output_suffix=None,
    prefix="",
    use_cache=False,
):
    # 単一のプロンプトを使用
    prompt = prompts.single_prompt
    
    if output:
        outdir, ext = os.path.splitext(output)
        if not ext:
            output += ".md"
    else:
        outdir = os.path.splitext(path)[0]
        if output_suffix:
            outdir += output_suffix
        output = outdir + ".md"
    if output_dir:
        outdir = os.path.join(output_dir, os.path.basename(outdir))
        output = os.path.join(output_dir, os.path.basename(output))
    
    # 出力ファイル名をtranslation.mdに変更
    translation_output = os.path.join(os.path.dirname(path), "translation.md")
    
    file = None
    cache = None
    result = ""
    stats = {}
    retry_count = 0  # 再試行回数を追跡
    
    try:
        md = os.path.join(outdir, "translation.md")
        
        if os.path.exists(md):
            print(f"Skipping existing file: {md}")
            with open(md, "r", encoding="utf-8") as f:
                result = f.read()
                
            # 統計情報を取得
            lines = result.rstrip().splitlines()
            k = -1
            for j, line in enumerate(lines):
                if line.startswith("> "):
                    k = j
                elif k < 0:
                    gemini.update_stats(stats, *gemini.get_kv(line))
        else:
            # マークダウンファイルをアップロード
            file = genai.upload_file(path, mime_type="text/markdown")
            print(f"Uploaded markdown file '{file.display_name}' as: {file.uri}")
            if use_cache:
                print("Caching file...")
                cache = genai.caching.CachedContent.create(
                    model=model_name,
                    system_instruction=system_instruction,
                    contents=[file],
                )
            
            # プロンプトの準備
            text = "# Translation\n\n"
            print(f"---- {prefix}Translating markdown file")
            
            # モデルの準備
            if cache:
                model = genai.GenerativeModel.from_cached_content(cache)
                model.generation_config = generation_config
            else:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction,
                )
            
            # 初回の翻訳
            if cache:
                result, usage = gemini.generate_content(model, max_rpm, prompt)
            else:
                result, usage = gemini.generate_content(model, max_rpm, file, prompt)
            
            # 初回の統計情報を保存
            total_usage = usage.copy() if usage else {}
            
            # <EOF>タグがない場合、翻訳が途中で終わった可能性があるため、続きを取得（1回のみ）
            if "<EOF>" not in result[-10:] and retry_count < 1:
                retry_count += 1
                print("\n---- 翻訳が途中で終わった可能性があります。続きを取得します。")
                
                # 続きを取得するためのプロンプト
                continuation_prompt = prompts.get_continuation_prompt(result)
                
                # 続きを取得
                continuation_result, continuation_usage = gemini.generate_content(model, max_rpm, continuation_prompt)
                
                # 統計情報をマージ
                for k, v in gemini.iter_stats(continuation_usage):
                    gemini.update_stats(total_usage, k, v)
                
                # 結果を連結
                result += "\n" + continuation_result
                
                # 統計情報を表示
                print("\n---- 続きの翻訳の統計情報:")
                gemini.show_stats(continuation_usage)
                
                # 合計統計情報を作成
                usage = total_usage
            
            # <EOF>タグを削除（もし存在すれば）
            if "<EOF>" in result[-10:]:
                result = result[:-5].rstrip()
            else:
                print("\n---- 警告: 翻訳が<EOF>タグで終わっていません。翻訳が不完全な可能性があります。")
            
            # 統計情報を計算して表示
            for k, v in gemini.iter_stats(usage):
                gemini.update_stats(stats, k, v)
                text += f"{k}: {v}\n"
            text += "\n"
            gemini.show_stats(usage)
            
            # プロンプトとレスポンスを追加
            text += f"> {prompt}\n\n" + result
            # 元のマークダウンと同じディレクトリにtranslation.mdとして保存
            os.makedirs(os.path.dirname(translation_output), exist_ok=True)
            with open(translation_output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Translation saved to: {translation_output}")
            
    finally:
        if cache:
            cache.delete()
            print("Deleted cache")
        if file:
            genai.delete_file(file.name)
            print(f"Deleted file '{file.display_name}' from: {file.uri}")
    
    gemini.set_stats(stats)
    return result, output, stats
