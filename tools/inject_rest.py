#!/usr/bin/env python3
"""
Fallen Aces — инжектор перевода остатка поверхностей (записки/главы/предметы/советы).
Работает на уровне ФАЙЛА: заменяет точное совпадение orig на перевод. Собирает
результат в mod-папку, сохраняя структуру AcesData.

Замена выполняется ОДНИМ проходом по оригинальному тексту: все вхождения каждого
orig заменяются (id контент-основан — одинаковый orig в одном файле переводится
целиком), а уже вставленные переводы не пере-матчатся последующими orig.
"""
import os, re, json

from _paths import OUT, MOD, resolve_source
from _common import load_translations

def main():
    recs = json.load(open(os.path.join(OUT, "rest_strings.json"), encoding="utf-8"))
    trans = load_translations(os.path.join(OUT, "packs_rest", "*.out.json"))
    print(f"Загружено переводов остатка: {len(trans)} из {len(recs)}")

    # Группируем по файлу
    by_file = {}
    for r in recs:
        by_file.setdefault(r["file"], []).append(r)

    changed = 0
    applied = 0
    errors = []
    leftovers = []
    for file, entries in by_file.items():
        src = resolve_source(file)
        if not src:
            errors.append(f"MISSING SOURCE {file}")
            continue
        with open(src, "r", encoding="utf-8") as f:
            txt = f.read()

        # Карта orig -> новый фрагмент (prefix + перевод + suffix).
        # Одинаковый orig даёт одинаковый id и должен переводиться целиком.
        mapping = {}
        for e in entries:
            if e["id"] not in trans:
                continue
            ru = trans[e["id"]]
            if ru == e["content"]:
                continue
            orig = e["orig"]
            if orig not in txt:
                errors.append(f"ORIG NOT FOUND: {file} :: {orig[:60]!r}")
            else:
                mapping[orig] = e["prefix"] + ru + e["suffix"]

        if not mapping:
            continue

        # Один проход: самый длинный orig матчится первым (защита от перекрытий),
        # заменяем ВСЕ вхождения, переводы не пере-матчатся (работаем по оригиналу).
        pattern = re.compile(
            "|".join(re.escape(o) for o in sorted(mapping, key=len, reverse=True))
        )
        def repl(m):
            return mapping[m.group(0)]

        new_txt = pattern.sub(repl, txt)
        applied += len(pattern.findall(txt))
        file_changed = new_txt != txt

        # Контроль остатков: если ожидаемый orig всё ещё присутствует — предупреждение.
        for orig in mapping:
            if orig in new_txt:
                leftovers.append(f"LEFTOVER: {file} :: {orig[:60]!r}")

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
    if leftovers:
        print(f"Предупреждений (непереведённые остатки): {len(leftovers)}")
        for e in leftovers[:15]:
            print("  ", e)

if __name__ == "__main__":
    main()
