#!/usr/bin/env python3
"""
Fallen Aces — перевод повторяющихся UI-полей (глаголы, сообщения).
Обрабатывает напрямую корневые .txt в mod-папке (после inject_rest).
Фиксированный словарь — эти значения повторяются и не требуют контекста.
НЕ трогает pickupReaction = "UsefulItem" (технический id).
"""
import os, re

MOD = os.path.expanduser("~/fallenaces-rus/mod")

VERB_MAP = {
    '"Drink"': '"Пить"',
    '"Eat"': '"Съесть"',
    '"Smoke"': '"Курить"',
    '"Take"': '"Взять"',
    '"Use"': '"Использовать"',
    '"Wear"': '"Надеть"',
    '"Pickup"': '"Подобрать"',
}

MSG_MAP = {
    '"That will absorb some damage!"': '"Это поглотит немного урона!"',
    '"You feel like you could punch through concrete!"': '"Такое чувство, что можно пробить бетон голыми руками!"',
    '"You feel like you could run a marathon!"': '"Такое чувство, что можно пробежать марафон!"',
    '"You feel tougher"': '"Ты чувствуешь себя крепче"',
    '"Your Favourite!"': '"Твоё любимое!"',
    '"Your energy is replenishing!"': '"Твоя энергия восстанавливается!"',
}

def main():
    for fn in ["consumables.txt", "props.txt"]:
        p = os.path.join(MOD, fn)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        orig = txt
        # Заменяем ТОЛЬКО в полях useVerb/holdVerb/messageOnConsumption
        for field in ["consumable_useVerb", "consumable_holdVerb", "consumable_messageOnConsumption"]:
            for src, dst in {**VERB_MAP, **MSG_MAP}.items():
                txt = txt.replace(f'{field} = {src}', f'{field} = {dst}')
        if txt != orig:
            with open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            print(f"Обновлён {fn}")

if __name__ == "__main__":
    main()
