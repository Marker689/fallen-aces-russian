#!/usr/bin/env python3
"""
Fallen Aces — экстрактор оставшихся переводимых поверхностей.
Обрабатывает (на уровне ФАЙЛА, не строки — важно для многострочных записок):
- Записки (Notes): text = "..."  (включая многострочные с rich-text тегами)
- chapterInfo.txt: title, over_title_text, description_text, faction_name
- episodeInfo.txt: title
- Корневые: title = "..." (имена предметов в props/consumables/weaponPickups/decals)
- loadingScreenTips.txt: каждая строка-совет

Для каждой записи: {file, id, orig (точный фрагмент для replace), surface}.
Инжектор делает file_content.replace(orig, translated) — безопасно, т.к. orig уникален в файле.
"""
import os, re, json, hashlib

GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"
OUT = os.path.expanduser("~/fallenaces-rus")

def make_id(file, orig):
    return hashlib.md5(f"{file}|{orig}".encode()).hexdigest()[:16]

def extract_notes():
    """Записки: text = "..." и print_name = "..." (многострочные)."""
    recs = []
    pat = re.compile(r'(text\s*=\s*")((?:[^"\\]|\\.)*)(")', re.S)
    pn = re.compile(r'(print_name\s*=\s*")((?:[^"\\]|\\.)*)(")')
    for root, _, files in os.walk(os.path.join(GAME, "AcesData/Episodes")):
        for fn in files:
            if "/Notes/" not in root + "/":
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    txt = f.read()
            except Exception:
                continue
            rel = os.path.relpath(p, GAME)
            for patx, surf in ((pat, "note"), (pn, "print_name")):
                for m in patx.finditer(txt):
                    content = m.group(2)
                    if not content.strip():
                        continue
                    if not re.search(r"[A-Za-zА-Яа-я]", content):
                        continue
                    recs.append({
                        "file": rel, "id": make_id(rel, m.group(0)),
                        "orig": m.group(0), "surface": surf,
                        "prefix": m.group(1), "content": content, "suffix": m.group(3),
                    })
    return recs

def extract_chapterinfo():
    """chapterInfo: title/over_title_text/description_text/faction_name"""
    recs = []
    fields = ["title", "over_title_text", "description_text"]
    pats = [re.compile(f'({f}\\s*=\\s*")((?:[^"\\\\]|\\\\.)*)(")') for f in fields]
    fac_pat = re.compile(r'(faction_name\s*=\s*\d+\s*")((?:[^"\\]|\\.)*)(")')
    for root, _, files in os.walk(os.path.join(GAME, "AcesData/Episodes")):
        for fn in files:
            if fn != "chapterInfo.txt":
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    txt = f.read()
            except Exception:
                continue
            rel = os.path.relpath(p, GAME)
            for pat in pats:
                for m in pat.finditer(txt):
                    if not m.group(2).strip():
                        continue
                    recs.append({
                        "file": rel, "id": make_id(rel, m.group(0)),
                        "orig": m.group(0), "surface": "chapterinfo",
                        "prefix": m.group(1), "content": m.group(2), "suffix": m.group(3),
                    })
            for m in fac_pat.finditer(txt):
                # faction_name = N "Name" — переводим имя, не цвет
                recs.append({
                    "file": rel, "id": make_id(rel, m.group(0)),
                    "orig": m.group(0), "surface": "faction",
                    "prefix": m.group(1), "content": m.group(2), "suffix": m.group(3),
                })
    return recs

def extract_episodeinfo():
    recs = []
    pat = re.compile(r'(title\s*=\s*")((?:[^"\\]|\\.)*)(")')
    for root, _, files in os.walk(os.path.join(GAME, "AcesData/Episodes")):
        for fn in files:
            if fn != "episodeInfo.txt":
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    txt = f.read()
            except Exception:
                continue
            rel = os.path.relpath(p, GAME)
            for m in pat.finditer(txt):
                if not m.group(2).strip():
                    continue
                recs.append({
                    "file": rel, "id": make_id(rel, m.group(0)),
                    "orig": m.group(0), "surface": "episode",
                    "prefix": m.group(1), "content": m.group(2), "suffix": m.group(3),
                })
    return recs

def extract_root_titles():
    """Корневые .txt: title = "..." и inGameName = "..." (имена предметов).
    НЕ sprites/icon."""
    recs = []
    files = ["props.txt", "consumables.txt", "weaponPickups.txt", "decals.txt", "misc.txt"]
    pat = re.compile(r'(inGameName\s*=\s*")((?:[^"\\]|\\.)*)(")')
    pat2 = re.compile(r'(title\s*=\s*")((?:[^"\\]|\\.)*)(")')
    for fn in files:
        p = os.path.join(GAME, "AcesData", fn)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                txt = f.read()
        except Exception:
            continue
        rel = os.path.relpath(p, GAME)
        # inGameName приоритетнее (это отображаемое имя в инвентаре)
        for patx, surf in ((pat, "item_name"), (pat2, "item_title")):
            for m in patx.finditer(txt):
                content = m.group(2)
                if not content.strip():
                    continue
                if not re.search(r"[A-Za-z]", content):
                    continue
                recs.append({
                    "file": rel, "id": make_id(rel, m.group(0)),
                    "orig": m.group(0), "surface": surf,
                    "prefix": m.group(1), "content": m.group(2), "suffix": m.group(3),
                })
    return recs

def extract_tips():
    """loadingScreenTips: каждая строка-совет в кавычках."""
    recs = []
    p = os.path.join(GAME, "AcesData", "loadingScreenTips.txt")
    if not os.path.exists(p):
        return recs
    with open(p, encoding="utf-8") as f:
        lines = f.read().split("\n")
    rel = os.path.relpath(p, GAME)
    for i, line in enumerate(lines):
        m = re.match(r'^\s*"(?P<c>(?:[^"\\]|\\.)*)"\s*$', line)
        if m and m.group("c").strip():
            recs.append({
                "file": rel, "id": make_id(rel, line),
                "orig": line, "surface": "tip",
                "prefix": '"', "content": m.group("c"), "suffix": '"',
                "full_line": line,
            })
    return recs

def main():
    all_recs = []
    all_recs += extract_notes()
    all_recs += extract_chapterinfo()
    all_recs += extract_episodeinfo()
    all_recs += extract_root_titles()
    all_recs += extract_tips()
    print(f"Всего записей (остаток): {len(all_recs)}")
    from collections import Counter
    print("По поверхностям:", dict(Counter(r['surface'] for r in all_recs)))
    with open(os.path.join(OUT, "rest_strings.json"), "w", encoding="utf-8") as f:
        json.dump(all_recs, f, ensure_ascii=False, indent=1)
    print("rest_strings.json сохранён")

if __name__ == "__main__":
    main()
