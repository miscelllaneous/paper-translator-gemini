import os, json, mimetypes
import google.generativeai as genai

from .section import Section
from . import gemini

def summarize(
    model_name,
    generation_config,
    system_instruction,
    max_rpm,
    lang_module,
    path,
    output=None,
    output_dir=None,
    output_suffix=None,
    prefix="",
    use_cache=False,
):
    prompts = lang_module.prompts
    sprompt = lang_module.sprompt
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
    file = None
    cache = None
    result = ""
    i = 0
    sections = Section()
    seclen = 0
    stats = {}
    try:
        while True:
            pnum = i
            i += 1
            if i <= len(prompts):
                title = prompts[pnum][0]
                prompt = prompts[pnum][1]
            elif (j := i - len(prompts) - 1) < seclen:
                title = "## " + sections.children[j].title
                prompt = sprompt[0] % sprompt[1].join(sections.children[j].flatten())
            else:
                break
            md = os.path.join(outdir, f"{pnum:03d}.md")
            if os.path.exists(md):
                print(f"Skipping existing file: {md}")
                with open(md, "r", encoding="utf-8") as f:
                    text = f.read()

                # Get the section structure
                if i == len(prompts) and "```json" in text:
                    json_str = text.split("```json")[2].split("```")[0]
                    sections.append(json.loads(json_str))
                    seclen = len(sections.children)
                lines = text.rstrip().splitlines()

                # Get the statistics and the response
                k = -1
                for j, line in enumerate(lines):
                    if line.startswith("> "):
                        k = j
                    elif k < 0:
                        gemini.update_stats(stats, *gemini.get_kv(line))
                k += 1
                while k < len(lines) and not lines[k]:
                    k += 1
                rtext = "\n".join(lines[k:]) + "\n"
            else:
                # Upload the file (and cache it)
                if not file:
                    # マークダウンファイルとして扱う
                    file = genai.upload_file(path, mime_type="text/markdown")
                    print(f"Uploaded markdown file '{file.display_name}' as: {file.uri}")
                    if use_cache:
                        print("Caching file...")
                        cache = genai.caching.CachedContent.create(
                            model=model_name,
                            system_instruction=system_instruction,
                            contents=[file],
                        )

                # Prepare the prompt
                plines = prompt.rstrip().splitlines()
                text = f"# Prompt {pnum}\n\n"
                plen = f"/{len(prompts) + seclen - 1}" if seclen else ""
                print(f"---- {prefix}Prompt {pnum}{plen}: {plines[0]}")

                # Get the response and statistics
                if cache:
                    model = genai.GenerativeModel.from_cached_content(cache)
                    model.generation_config = generation_config
                    rtext, usage = gemini.generate_content(model, max_rpm, prompt)
                else:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=generation_config,
                        system_instruction=system_instruction,
                    )
                    rtext, usage = gemini.generate_content(model, max_rpm, file, prompt)

                # Get the section structure
                if i == len(prompts) and "```json" in rtext:
                    json_str = rtext.split("```json")[1].split("```")[0]
                    sections.append(json.loads(json_str))
                    seclen = len(sections.children)
                    rtext += "\n" + str(sections)

                # Calculate and show the statistics
                for k, v in gemini.iter_stats(usage):
                    gemini.update_stats(stats, k, v)
                    text += f"{k}: {v}\n"
                text += "\n"
                gemini.show_stats(usage)

                # Add the prompt and response
                for line in plines:
                    text += f"> {line}\n"
                text += "\n" + rtext

                # Save the file
                os.makedirs(outdir, exist_ok=True)
                with open(md, "w", encoding="utf-8") as f:
                    f.write(text)

            # Remove JSON from the section structure
            if i == len(prompts) and (json_start := rtext.find("```json")) >= 0:
                if (json_end := rtext.find("```", json_start + 7)) >= 0:
                    if (section_start := rtext.find("\n\n", json_end)) >= 0:
                        rtext = rtext[section_start+2:]

            # Add to the result
            if i > 1:
                result += "\n"
            result += title + "\n\n" + rtext
    finally:
        if cache:
            cache.delete()
            print("Deleted cache")
        if file:
            genai.delete_file(file.name)
            print(f"Deleted file '{file.display_name}' from: {file.uri}")

    gemini.set_stats(stats)
    return result, output, stats
