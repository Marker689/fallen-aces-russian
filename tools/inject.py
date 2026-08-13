#!/usr/bin/env python3
"""
Fallen Aces — инжектор переводов в папку-мод для Steam Workshop.
Собирает переведённые файлы в mod-папку с той же структурой, что и AcesData,
сохраняя относительные пути. Заменяет ТОЛЬКО текст внутри кавычек.

Исходник: берёт оригинальные файлы из AcesData, применяет переводы из
*.out.json, пишет результат в mod-папку. НЕ трогает оригиналы.
"""
import os, json, glob, hashlib

GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"
BACKUP = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces_backup_txt"
OUT = os.path.expanduser("~/fallenaces-rus")
MOD = os.path.join(OUT, "mod")

def make_id(file, line_no):
    return hashlib.md5(f"{file}:{line_no}".encode()).hexdigest()[:12]

def load_translations():
    trans = {}
    for path in glob.glob(os.path.join(OUT, "packs", "*.out.json")):
        d = json.load(open(path, encoding="utf-8"))
        for k, v in d.items():
            if v:
                trans[k] = v
    return trans

def main():
    recs = json.load(open(os.path.join(OUT, "subtitle_strings.json"), encoding="utf-8"))
    trans = load_translations()
    print(f"Загружено переводов: {len(trans)} из {len(recs)} строк")

    for r in recs:
        r["id"] = make_id(r["file"], r["line_no"])

    by_file = {}
    for r in recs:
        by_file.setdefault(r["file"], []).append(r)

    mod_sub = os.path.join(MOD, "Subtitles")
    os.makedirs(mod_sub, exist_ok=True)

    changed = 0
    translated = 0
    for file, entries in by_file.items():
        if not file.startswith("AcesData/Subtitles"):
            continue
        rel = file[len("AcesData/Subtitles/"):]
        # Читаем ОРИГИНАЛ из бэкап-папки (чистые английские файлы), чтобы мод
        # не зависел от состояния AcesData (которая могла быть изменена пилотом).
        src = os.path.join(BACKUP, file)
        if not os.path.exists(src):
            src = os.path.join(GAME, file)
        if not os.path.exists(src):
            continue
        with open(src, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
        file_changed = False
        for e in entries:
            if e["id"] in trans:
                ru = trans[e["id"]]
                idx = e["line_no"] - 1
                if idx < len(lines):
                    old = lines[idx]
                    new = e["prefix"] + '"' + ru + '"' + e["suffix"]
                    if new != old:
                        lines[idx] = new
                        translated += 1
                        file_changed = True
        if file_changed:
            dst = os.path.join(mod_sub, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            changed += 1

    print(f"\nФайлов в мод-папке: {changed}")
    print(f"Строк переведено: {translated}")
    print(f"Мод-папка: {MOD}/Subtitles")

if __name__ == "__main__":
    main()
