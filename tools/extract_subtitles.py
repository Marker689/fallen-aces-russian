#!/usr/bin/env python3
"""
Fallen Aces — надёжный экстрактор строк для перевода.
Работает с реальными форматами:
- Субтитры: { T 0.5 } "text" | T 0 "text" (внутри I N {} блоков) | "text"
- Записки/инфо: key = "text"
- Скрипты: SpeakDialogue(arg, "text") и прочие вызовы с "text"

Принцип: для каждой строки с текстом в кавычках сохраняем ВСЁ, что идёт
до открывающей кавычки (prefix) и после закрывающей (suffix), чтобы инжектор
мог переписать строку, заменив только текст внутри кавычек.
"""
import os, re, json, collections

from _paths import OUT, source_root

# Строка целиком в кавычках с префиксом/суффиксом.
# Захватывает: { T 0.5 } "text", T 0 "text", key = "text", SpeakDialogue(a, "text")...
# (?:[^"\\]|\\.)* — любой текст, поддерживающий экранирование \" и \\.
LINE_RE = re.compile(r'^(?P<prefix>.*?)"(?P<text>(?:[^"\\]|\\.)*)"(?P<suffix>.*)$')

def is_probably_nontranslatable(text):
    """Строки, которые почти наверняка не переводятся (ключи/имена файлов/теги)."""
    t = text.strip()
    # Пустые
    if not t:
        return True
    # Технические ключи: name = "value" где value технический (нет букв > 1 слова)
    return False

def extract_lines(path):
    results = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_lines = f.read().split("\n")
    except Exception:
        return results
    for i, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip("\n")
        m = LINE_RE.match(line)
        if not m:
            continue
        prefix, text, suffix = m.group("prefix"), m.group("text"), m.group("suffix")
        # Исключаем строки, где кавычки это часть кода без реального текста,
        # например только { и } без содержимого — но там и кавычек нет, так что ок.
        results.append({
            "line_no": i,
            "prefix": prefix,
            "text": text,
            "suffix": suffix,
            "orig_line": line,
        })
    return results

def main():
    SRC = source_root()
    if SRC is None:
        print("Игра/бэкап недоступны — нечего извлекать.")
        return
    targets = []
    sub_dir = os.path.join(SRC, "AcesData/Subtitles")
    for root, _, files in os.walk(sub_dir):
        for fn in files:
            if fn.endswith(".txt"):
                targets.append(("subtitle", os.path.join(root, fn)))

    all_records = []
    per_kind = collections.Counter()
    for kind, path in targets:
        rel = os.path.relpath(path, SRC)
        recs = extract_lines(path)
        per_kind[kind] += len(recs)
        for r in recs:
            r["file"] = rel
            all_records.append(r)

    print(f"Всего строк с текстом: {len(all_records)}")
    print(f"По типам: {dict(per_kind)}")

    # Проверка: сколько строк содержат реальный текст (не только теги/пустые)
    real = [r for r in all_records if r["text"].strip() and '<color' not in r["text"][:20] or (r['text'].strip())]
    with open(os.path.join(OUT, "subtitle_strings.json"), "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=1)
    print(f"subtitle_strings.json сохранён ({len(all_records)} записей)")

    # Сводка по структуре: показать примеры всех типов префиксов
    prefixes = collections.Counter()
    for r in all_records:
        p = r["prefix"].strip()
        prefixes[p[:40]] += 1
    print("\nТипы префиксов (сгруппировано):")
    for p, c in prefixes.most_common(25):
        print(f"  {c:4d}  [{p}]")

if __name__ == "__main__":
    main()
