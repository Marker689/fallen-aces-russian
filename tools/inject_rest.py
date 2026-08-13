#!/usr/bin/env python3
"""
Fallen Aces — инжектор перевода остатка поверхностей (записки/главы/предметы/советы).
Работает на уровне ФАЙЛА: заменяет точное совпадение orig (уникально в файле)
на перевод. Собирает результат в mod-папку, сохраняя структуру AcesData.
"""
import os, json, glob

GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"
BACKUP = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces_backup_txt"
OUT = os.path.expanduser("~/fallenaces-rus")
MOD = os.path.join(OUT, "mod")

def load_translations():
    trans = {}
    for path in glob.glob(os.path.join(OUT, "packs_rest", "*.out.json")):
        d = json.load(open(path, encoding="utf-8"))
        for k, v in d.items():
            if v:
                trans[k] = v
    return trans

def main():
    recs = json.load(open(os.path.join(OUT, "rest_strings.json"), encoding="utf-8"))
    trans = load_translations()
    print(f"Загружено переводов остатка: {len(trans)} из {len(recs)}")

    # Группируем по файлу
    by_file = {}
    for r in recs:
        by_file.setdefault(r["file"], []).append(r)

    changed = 0
    applied = 0
    errors = []
    for file, entries in by_file.items():
        src = os.path.join(BACKUP, file)
        if not os.path.exists(src):
            src = os.path.join(GAME, file)
        if not os.path.exists(src):
            errors.append(f"MISSING SOURCE {file}")
            continue
        with open(src, "r", encoding="utf-8") as f:
            txt = f.read()
        new_txt = txt
        file_changed = False
        for e in entries:
            if e["id"] not in trans:
                continue
            ru = trans[e["id"]]
            if ru == e["content"]:
                continue
            # prefix/suffix уже содержат кавычки ("text = \"" и "\""),
            # поэтому просто склеиваем: prefix + перевод + suffix
            new_fragment = e["prefix"] + ru + e["suffix"]
            if e["orig"] in new_txt:
                new_txt = new_txt.replace(e["orig"], new_fragment, 1)
                applied += 1
                file_changed = True
            else:
                errors.append(f"ORIG NOT FOUND: {file} :: {e['orig'][:60]!r}")
        if file_changed:
            dst = os.path.join(MOD, file[len("AcesData/"):])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "w", encoding="utf-8") as f:
                f.write(new_txt)
            changed += 1

    print(f"\nФайлов изменено: {changed}")
    print(f"Строк применено: {applied}")
    if errors:
        print(f"Ошибок: {len(errors)}")
        for e in errors[:15]:
            print("  ", e)

if __name__ == "__main__":
    main()
