#!/usr/bin/env python3
"""
Fallen Aces — верификатор переведённого контента.

Проверяет:
1. Полноту перевода: все ли id покрыты в packs/*.out.json.
2. Целостность ФАЙЛОВ в папке-мод (основной режим):
   - кодировка UTF-8 без BOM;
   - валидность UTF-8;
   - число строк совпадает с оригиналом (регрессия формата);
   - структура вне кавычек совпадает с оригиналом (предупреждение).

Режимы:
  --target mod   (по умолчанию) — проверяет собранные файлы в mod/.
  --target game  — проверяет живые файлы игры в AcesData (обратная совместимость).

Проверка числа строк / структуры требует доступа к оригиналу (бэкап или игра).
Если ни игра, ни бэкап недоступны, скрипт НЕ падает: проверяет BOM/UTF-8/полноту,
а для числа строк/структуры выводит понятное предупреждение. Пригоден для CI
без установленной игры.
"""
import os, sys, json, glob, re, argparse, collections

from _paths import GAME, BACKUP, OUT, MOD, resolve_source
from _common import make_id, load_translations

# Удаляет все кавыченные фрагменты (включая многострочные и \\-экранированные),
# оставляя «скелет» файла: ключи, тайминги, скобки, имена полей.
_STRIP_QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"', re.S)


def _skeleton(text):
    return _STRIP_QUOTED.sub('""', text)


def _line_count(text):
    return len(text.split("\n"))


def check_translation_completeness():
    """Полнота перевода по packs/*.out.json (оригинальная проверка)."""
    recs = json.load(open(os.path.join(OUT, "subtitle_strings.json"), encoding="utf-8"))
    for r in recs:
        r["id"] = make_id(r["file"], r["line_no"])
    trans = load_translations(os.path.join(OUT, "packs", "*.out.json"))
    translated_ids = set(trans.keys())
    all_ids = set(r["id"] for r in recs)
    missing = all_ids - translated_ids
    print(f"Переведено id: {len(translated_ids)} / {len(all_ids)}")
    print(f"Непереведено id: {len(missing)}")
    if missing:
        by_file = collections.defaultdict(list)
        for r in recs:
            if r["id"] in missing:
                by_file[r["file"]].append(r["line_no"])
        print("Примеры непереведённого:")
        for f, lines in list(by_file.items())[:15]:
            print(f"  {f}: строки {lines[:6]}")
    return len(missing)


def _check_file(mod_path, source_path, strict_lines):
    """Проверка одного файла mod/. Возвращает (issues, warnings)."""
    issues = 0
    warnings = 0
    try:
        with open(mod_path, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"  [READ ERROR] {mod_path}: {e}")
        return 1, 0

    # Кодировка без BOM
    if data[:3] == b"\xef\xbb\xbf":
        print(f"  [BOM!] {mod_path}")
        issues += 1
    # Валидность UTF-8
    try:
        mod_text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"  [INVALID UTF-8] {mod_path}: {e}")
        issues += 1
        return issues, warnings

    if source_path and os.path.exists(source_path):
        try:
            with open(source_path, encoding="utf-8") as f:
                src_text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"  [SOURCE READ ERROR] {source_path}: {e}")
            return issues, warnings
        # Число строк — критичный инвариант формата
        if strict_lines:
            n_src = _line_count(src_text)
            n_mod = _line_count(mod_text)
            if n_src != n_mod:
                print(f"  [LINE COUNT] {mod_path}: {n_mod} != оригинал {n_src}")
                issues += 1
        # Структура вне кавычек — предупреждение (допустимы слитные переводы в строке)
        if _skeleton(src_text) != _skeleton(mod_text):
            print(f"  [STRUCTURE] {mod_path}: структура вне кавычек отличается от оригинала")
            warnings += 1
    return issues, warnings


def check_mod():
    """Основной режим: проверка собранных файлов в mod/."""
    if not os.path.isdir(MOD):
        print(f"Папка мода не найдена: {MOD}")
        return 1

    txt_files = []
    for root, _, files in os.walk(MOD):
        for fn in files:
            if fn.endswith(".txt"):
                txt_files.append(os.path.join(root, fn))

    source_available = os.path.isdir(GAME) or os.path.isdir(BACKUP)
    print(f"\n--- Проверка файлов мода ({len(txt_files)} .txt) ---")
    if not source_available:
        print("Игра/бэкап недоступны: проверка числа строк и структуры пропущена "
              "(проверяются только BOM/UTF-8 и полнота перевода).")

    issues = 0
    warnings = 0
    skipped_lines = 0
    for p in sorted(txt_files):
        rel = "AcesData/" + os.path.relpath(p, MOD).replace(os.sep, "/")
        src = resolve_source(rel)
        i, w = _check_file(p, src, strict_lines=source_available)
        issues += i
        warnings += w
        if src is None:
            skipped_lines += 1

    print(f"\nПроблем (ошибки): {issues}")
    print(f"Предупреждений (структура): {warnings}")
    if skipped_lines:
        print(f"Файлов без доступа к оригиналу (число строк не проверено): {skipped_lines}")
    return 1 if issues else 0


def check_game():
    """Обратная совместимость: проверка живых файлов игры в AcesData."""
    recs = json.load(open(os.path.join(OUT, "subtitle_strings.json"), encoding="utf-8"))
    for r in recs:
        r["id"] = make_id(r["file"], r["line_no"])
    trans = load_translations(os.path.join(OUT, "packs", "*.out.json"))
    affected = set(r["file"] for r in recs if r["id"] in trans)

    print("\n--- Проверка файлов игры (AcesData) ---")
    if not os.path.isdir(GAME):
        print(f"Папка игры не найдена: {GAME}")
        return 1
    issues = 0
    for file in sorted(affected):
        full = os.path.join(GAME, file)
        if not os.path.exists(full):
            print(f"  [MISSING FILE] {file}")
            issues += 1
            continue
        with open(full, "rb") as f:
            data = f.read()
        if data[:3] == b"\xef\xbb\xbf":
            print(f"  [BOM!] {file}")
            issues += 1
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as e:
            print(f"  [INVALID UTF-8] {file}: {e}")
            issues += 1
    print(f"\nПроблем: {issues}")
    return 1 if issues else 0


def main():
    parser = argparse.ArgumentParser(description="Верификатор перевода Fallen Aces")
    parser.add_argument("--target", choices=["mod", "game"], default="mod",
                        help="что проверять: собранные файлы mod/ (по умолчанию) или живую игру")
    args = parser.parse_args()

    check_translation_completeness()

    if args.target == "mod":
        code = check_mod()
    else:
        code = check_game()
    sys.exit(code)


if __name__ == "__main__":
    main()
