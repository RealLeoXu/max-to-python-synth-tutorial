"""Build the 'Max to Python Synth' notebooks.

usage: python3 build.py OUT_DIR [episode numbers...]
"""
import importlib
import os
import re
import sys

import nbformat as nbf

OUT = sys.argv[1]
WANTED = [int(a) for a in sys.argv[2:]] or list(range(0, 11))

MARK = re.compile(r"\[\[(.*?)\|\|(.*?)\]\]")

# difficulty per episode, 1-3 stars
LEVEL = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 2, 9: 2, 10: 2}


def stars(n):
    return "★" * n + "☆" * (3 - n)


def localize_code(code, lang):
    return MARK.sub(lambda m: m.group(1) if lang == "zh" else m.group(2), code)


def add_level(text, num, lang):
    if num not in LEVEL:
        return text
    label = "难度" if lang == "zh" else "Difficulty"
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("⏱"):
            lines[i] = f"{line} · {label} {stars(LEVEL[num])}"
            break
    return "\n".join(lines)


def build(lang, subdir):
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    for num in WANTED:
        ep = importlib.import_module(f"ep{num:02d}").EP
        nb = nbf.v4.new_notebook()
        nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
        nb.metadata["language_info"] = {"name": "python"}
        first = True
        for cell in ep["cells"]:
            if cell[0] == "md":
                text = cell[1] if lang == "zh" else cell[2]
                if first:
                    text = add_level(text, num, lang)
                    first = False
                nb.cells.append(nbf.v4.new_markdown_cell(text))
            else:
                code = localize_code(cell[1], lang)
                assert "||" not in code, (num, code)
                nb.cells.append(nbf.v4.new_code_cell(code))
        name = ep["zh_file"] if lang == "zh" else ep["en_file"]
        nbf.write(nb, os.path.join(d, name + ".ipynb"))
        print("wrote", os.path.join(subdir, name + ".ipynb"))


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
build("zh", "中文")
build("en", "English")
