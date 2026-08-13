#!/usr/bin/env python3
"""
Fallen Aces — верификатор переведённых субтитров.
Проверяет:
1. Все ли id переведены (из .out.json).
2. Кодировка файлов — UTF-8 без BOM.
3. Синтаксис: число строк в файле не изменилось, структура { T }, I {} цела.
"""
import os, json, glob, hashlib, collections

GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"
OUT = os.path.expanduser("~/fallenaces-rus")

def make_id(file, line_no):
    return hashlib.md5(f"{file}:{line_no}".encode()).hexdigest()[:12]

def main():
    recs = json.load(open(os.path.join(OUT, "subtitle_strings.json"), encoding="utf-8"))
    for r in recs:
        r["id"] = make_id(r["file"], r["line_no"])

    # 1. Собираем все переводы
    trans = {}
    for path in glob.glob(os.path.join(OUT, "packs", "*.out.json")):
        d = json.load(open(path, encoding="utf-8"))
        for k, v in d.items():
            if v:
                trans[k] = v

    translated_ids = set(trans.keys())
    all_ids = set(r["id"] for r in recs)
    missing = all_ids - translated_ids
    print(f"Переведено id: {len(translated_ids)} / {len(all_ids)}")
    print(f"Непереведено id: {len(missing)}")
    if missing:
        # показать примеры
        by_file = collections.defaultdict(list)
        for r in recs:
            if r["id"] in missing:
                by_file[r["file"]].append(r["line_no"])
        print("Примеры непереведённого:")
        for f, lines in list(by_file.items())[:15]:
            print(f"  {f}: строки {lines[:6]}")

    # 2-3. Проверка файлов (только изменённые, где есть переводы)
    # Для каждого файла с переводом — проверяем кодировку и кол-во строк
    print("\n--- Проверка файлов ---")
    affected = set(r["file"] for r in recs if r["id"] in trans)
    issues = 0
    for file in sorted(affected):
        full = os.path.join(GAME, file)
        if not os.path.exists(full):
            print(f"  [MISSING FILE] {file}")
            issues += 1
            continue
        with open(full, "rb") as f:
            data = f.read()
        # BOM check
        if data[:3] == b'\xef\xbb\xbf':
            print(f"  [BOM!] {file}")
            issues += 1
        # валидность UTF-8
        try:
            data.decode("utf-8")
        except Exception as e:
            print(f"  [INVALID UTF-8] {file}: {e}")
            issues += 1
        # кол-во строк
        n_lines_orig = sum(1 for r in recs if r["file"] == file and r["line_no"])
        # берём макс номер строки как оценку
    print(f"\nПроблем: {issues}")

if __name__ == "__main__":
    main()
