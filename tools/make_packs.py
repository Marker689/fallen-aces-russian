#!/usr/bin/env python3
"""
Fallen Aces — подготовка пакетов для субагентов-переводчиков.
Делит subtitle_strings.json на батчи (по персонажам или по числу строк)
и создаёт для каждого батча входной JSON вида:
    [{"id": "...", "text": "...", "context": "персонаж / файл"}]
"""
import os, json, collections, sys

from _paths import OUT
from _common import make_id

PACKS_DIR = os.path.join(OUT, "packs")
os.makedirs(PACKS_DIR, exist_ok=True)

def build_batches(mode="by_char", max_per=200):
    recs = json.load(open(os.path.join(OUT, "subtitle_strings.json")))
    # назначаем id
    for r in recs:
        r["id"] = make_id(r["file"], r["line_no"])
        # контекст = персонаж
        parts = r["file"].split(os.sep)
        char = parts[2].replace(".txt", "") if len(parts) > 3 else parts[2].replace(".txt", "")
        r["char"] = char

    batches = []
    if mode == "by_char":
        by_char = collections.defaultdict(list)
        for r in recs:
            by_char[r["char"]].append(r)
        # объединяем мелких
        for char, lst in sorted(by_char.items(), key=lambda x: -len(x[1])):
            if len(lst) < 50:
                # merge into last batch if small
                if batches and len(batches[-1]) + len(lst) <= max_per:
                    batches[-1].extend(lst)
                    batches[-1].sort(key=lambda x: x["id"])
                    continue
            batches.append(lst)
    else:
        batches = [recs[i:i+max_per] for i in range(0, len(recs), max_per)]

    print(f"Создано батчей: {len(batches)}")
    manifest = []
    for idx, batch in enumerate(batches):
        batch_name = f"batch_{idx:02d}"
        pack = []
        for r in batch:
            pack.append({"id": r["id"], "text": r["text"], "context": f"{r['char']} | {os.path.basename(r['file'])}"})
        # пишем входной и пустой выходной
        in_path = os.path.join(PACKS_DIR, f"{batch_name}.in.json")
        out_path = os.path.join(PACKS_DIR, f"{batch_name}.out.json")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(pack, f, ensure_ascii=False, indent=1)
        if not os.path.exists(out_path):
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({r["id"]: "" for r in pack}, f, ensure_ascii=False, indent=1)
        manifest.append({"batch": batch_name, "count": len(batch),
                         "in": in_path, "out": out_path,
                         "chars": sorted(set(r["char"] for r in batch))})
        print(f"  {batch_name}: {len(batch)} строк | chars={sorted(set(r['char'] for r in batch))}")

    with open(os.path.join(OUT, "pack_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"\nManifest: {os.path.join(OUT, 'pack_manifest.json')}")

if __name__ == "__main__":
    build_batches(sys.argv[1] if len(sys.argv) > 1 else "by_char")
