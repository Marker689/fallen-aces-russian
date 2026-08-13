#!/usr/bin/env python3
"""
Fallen Aces — экстрактор строк для перевода.
Извлекает текстовые строки из нарративных файлов, сохраняя связку
файл -> строка, и собирает статистику имён собственных для глоссария.
"""
import os, re, json, sys, collections

GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"
OUT = os.path.expanduser("~/fallenaces-rus")

# --- Регэкспы для разных форматов ---
# Субтитры: T 8.7 "text"
SUB_T_RE = re.compile(r'^(?P<indent>\s*)T\s+(?P<time>[\d.]+)\s+"(?P<text>(?:[^"\\]|\\.)*)"')
# Записки/инфо: text = "..."
TEXT_EQ_RE = re.compile(r'^(?P<indent>\s*)(?P<key>[A-Za-z_]+)\s*=\s*"(?P<text>(?:[^"\\]|\\.)*)"')
# Скрипты: SpeakDialogue(-1, "text")
SPEAK_RE = re.compile(r'SpeakDialogue\(\s*(?P<arg>[^,)]+)\s*,\s*"(?P<text>(?:[^"\\]|\\.)*)"')
# Прочие вызовы с текстом: ShowSubtitle("text"), Say(...) — на будущее
ANY_STR_RE = re.compile(r'"(?P<text>(?:[^"\\]|\\.)*)"')

def extract_lines(path):
    """Возвращает список записей {line_no, kind, prefix, text, suffix}."""
    results = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
    except Exception as e:
        return results
    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        # Субтитры T
        m = SUB_T_RE.match(line)
        if m:
            results.append({"line_no": i, "kind": "subtitle", "indent": m.group("indent"),
                            "time": m.group("time"), "text": m.group("text")})
            continue
        # text = "..."
        m = TEXT_EQ_RE.match(line)
        if m:
            results.append({"line_no": i, "kind": "text_eq", "indent": m.group("indent"),
                            "key": m.group("key"), "text": m.group("text")})
            continue
        # SpeakDialogue
        m = SPEAK_RE.search(line)
        if m:
            results.append({"line_no": i, "kind": "speak", "arg": m.group("arg"),
                            "text": m.group("text"), "prefix": line[:m.start()],
                            "suffix": line[m.end():]})
    return results

def main():
    targets = []
    # Субтитры
    sub_dir = os.path.join(GAME, "AcesData/Subtitles")
    for root, _, files in os.walk(sub_dir):
        for fn in files:
            if fn.endswith(".txt"):
                targets.append(("subtitle", os.path.join(root, fn)))
    # Эпизоды (скрипты, записки, chapterInfo)
    ep_dir = os.path.join(GAME, "AcesData/Episodes")
    for root, _, files in os.walk(ep_dir):
        for fn in files:
            if fn.endswith(".txt"):
                targets.append(("episode", os.path.join(root, fn)))
    # Корневые txt (misc, npcs и т.д.)
    for fn in os.listdir(os.path.join(GAME, "AcesData")):
        if fn.endswith(".txt"):
            targets.append(("root", os.path.join(GAME, "AcesData", fn)))

    all_records = []
    per_kind = collections.Counter()
    # Имена собственные
    names = collections.Counter()
    STOP = set("""You I Well The What No So Hey Alright Yeah Oh This Now It Its We Dont That And
    But Why Maybe He Lets Huh Not Just How She Uh It Heh Theres They One Did Listen Got Boss
    Thanks Look Come When Nice Keep Where Try Still Seems Hmm Damn All Who Sir See Say Pfft
    Hell Do Wonder Take Sorry Some Once Ha Go Fine Would With Them Thank Shit My Might May In
    Heading Guess For Didnt Back Art Whatever Wait Too Think These Sure Stupid Something
    Somebody Should Really Probably Police Okay More Honest Hard Catch Came Bygones Bad After
    Aces Worried Whole Time Thatd Stick Shot Real Pretty Only Old Next Nah Lousy Looking
    Killer Iron Holy Nothin Every Understand Wanna True Tough Right Quiet Point Plain Pay
    Means Head Were Wont Wouldnt Mean Lets Attention Huh Hrmph Jeez Yknow Gonna Kinda Gotta
    Whats Ill Youre Youve Id Idve Does Geez Alrighty Wow Good God Sir Fellow""".split())

    for kind, path in targets:
        rel = os.path.relpath(path, GAME)
        recs = extract_lines(path)
        per_kind[kind] += len(recs)
        for r in recs:
            r["file"] = rel
            all_records.append(r)
            # Сбор имён
            for w in re.findall(r'\b[A-Z][a-z]+(?:\x27s)?\b', r["text"]):
                base = w.replace("'s", "")
                if base in STOP or base.endswith("'s"):
                    base = base.replace("'s", "")
                if base and base not in STOP and len(base) > 1:
                    names[base] += 1

    print(f"Всего записей: {len(all_records)}")
    print(f"По типам: {dict(per_kind)}")

    # Сохраняем строки для перевода
    with open(os.path.join(OUT, "strings.json"), "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=1)
    print(f"strings.json сохранён ({len(all_records)} записей)")

    # Имена собственные
    with open(os.path.join(OUT, "glossary", "candidate_names.txt"), "w", encoding="utf-8") as f:
        for name, cnt in names.most_common():
            f.write(f"{cnt:4d}  {name}\n")
    print("candidate_names.txt сохранён")
    print("\nТОП-60 имён:")
    for name, cnt in names.most_common(60):
        print(f"  {cnt:4d}  {name}")

if __name__ == "__main__":
    main()
