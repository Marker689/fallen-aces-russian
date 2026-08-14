#!/usr/bin/env python3
"""
Fallen Aces — формирование батчей для перевода остатка (rest_strings.json).
Группирует по поверхности, объединяет мелкие, создаёт .in.json/.out.json.
"""
import os, json, collections

from _paths import OUT

PACKS = os.path.join(OUT, "packs_rest")
os.makedirs(PACKS, exist_ok=True)

def main():
    recs = json.load(open(os.path.join(OUT, "rest_strings.json"), encoding="utf-8"))
    by_surface = collections.defaultdict(list)
    for r in recs:
        by_surface[r["surface"]].append(r)

    batches = []
    # Записки — крупный объём, разбиваем по ~80
    notes = by_surface.get("note", [])
    for i in range(0, len(notes), 80):
        batches.append(notes[i:i+80])
    # Мелкие поверхности объединяем в 1-2 батча
    small = []
    for s in ["chapterinfo", "faction", "episode", "item_title", "tip"]:
        small += by_surface.get(s, [])
    for i in range(0, len(small), 120):
        batches.append(small[i:i+120])

    manifest = []
    for idx, batch in enumerate(batches):
        bname = f"rbatch_{idx:02d}"
        pack = []
        for r in batch:
            pack.append({
                "id": r["id"],
                "surface": r["surface"],
                "content": r["content"],
                "file": r["file"],
            })
        in_p = os.path.join(PACKS, f"{bname}.in.json")
        out_p = os.path.join(PACKS, f"{bname}.out.json")
        with open(in_p, "w", encoding="utf-8") as f:
            json.dump(pack, f, ensure_ascii=False, indent=1)
        if not os.path.exists(out_p):
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump({r["id"]: "" for r in pack}, f, ensure_ascii=False, indent=1)
        surfaces = sorted(set(r["surface"] for r in batch))
        manifest.append({"batch": bname, "count": len(batch), "surfaces": surfaces,
                         "in": in_p, "out": out_p})
        print(f"{bname}: {len(batch)} строк | {surfaces}")

    with open(os.path.join(OUT, "pack_manifest_rest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"\nВсего батчей: {len(batches)}")

if __name__ == "__main__":
    main()
