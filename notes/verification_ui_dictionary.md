# Verification Report — UI Dictionary (XUnity.AutoTranslator)

**File reviewed:** `mod_ui/Translation/ru/Text/ui_dictionary.txt` (240 lines, 216 entries)
**Source of truth:** `mod_ui/ui_strings_curated.txt` + `glossary/glossary.md`
**Date:** 2026-08-14
**Reviewer role:** Localization QA verifier

---

## 1. Summary

| Category | Verdict | Notes |
|---|---|---|
| 1. Glossary compliance | **FAIL (1 critical)** | One entry contradicts glossary (`головорез` for *Goon* instead of *Громила*); all other glossary terms compliant. |
| 2. Noir tone / register | **PASS (minor notes)** | Mostly fine; a few mob-slang idioms flattened or calqued. |
| 3. Technical correctness | **PASS** | All 216 originals preserved byte-for-byte; rich-text tags, `{0}/{1}`, `${0}`, `\n`, `\t` balanced/kept. |
| 4. Naturalness | **PASS (minor issues)** | Several awkward/unidiomatic phrasings flagged. |
| 5. Consistency | **FAIL (minor)** | Same EN term rendered differently (`Goon`→громила/головорез; *loot* gender mismatch). |

**Overall quality rating: 78 / 100**

Strong technical execution and mostly faithful register, but a hard glossary
violation on line 223, a few off-register mob-slang translations, and several
awkward phrasings keep it from being release-ready. None of the issues break the
file (all entries parse; placeholders/tags survive).

---

## 2. Glossary compliance check (must-follow terms)

Terms in the glossary that appear in this dictionary:

- `Nightwave` → **Найтвейв** (lines 125, 175) — ✅ compliant.
- `Hideout` → **Притон** (lines 112, 117, 187) — ✅ compliant.
- `Goon` → **Громила** (line 171 uses *громила* ✅) — **but line 223 uses `головорез`** ❌.
- `VISE`, `Glassjaw`, `Glasshearts`, `gumshoe` — **not present** in this dictionary (N/A here; verify in Subtitles/Notes surfaces).

**Glossary gaps (no contradiction, but undocumented names):** `Umburgh` (Умбург,
line 170), `Gianni` (Джанни, line 138), `Marek` (Марек, line 183) are not in the
glossary. Transliterations are reasonable, but these should be **added to the
glossary** to prevent drift in other surfaces.

---

## 3. Issues table

Priorities: **[CRIT]** = wrong meaning / contradicts glossary; **[MIN]** = style/consistency.

| Line | English original | Current translation | Issue type | Suggested fix |
|---|---|---|---|---|
| 223 | `Unarmed Goon` | `Безоружный головорез` | **[CRIT]** Glossary — *Goon* is defined as *Громила* (glossary §2), and line 171 already uses *громила*. | `Безоружный громила` |
| 137 | `Whacking wise guys...` | `Заваливаем умников...` | [MIN] Register — mob slang *whack* (убить/замочить) and *wiseguy* (мафиози) flattened to "умник". | `Валим мафиози...` (or keep `умник` only if used consistently for the *Wise Guy Eh?* nickname) |
| 139 | `Making unrefusable offers...` | `Делаем предложения, от которых не отказываются...` | [MIN] Naturalness/register — clumsy; the canonical Godfather phrasing is stronger. | `Делаем предложения, от которых невозможно отказаться...` |
| 169 | `Sleep With The Fishes` | `Спать с рыбами` | [MIN] Register/idiom — awkward calque; Russian idiom is *кормить рыб*. | `Кормить рыб` |
| 53 | `Picked cursed Loot! - ${0}` | `Подобрано проклятое добро! - ${0}` | [MIN] Naturalness + consistency — *добро* is off for "loot"; conflicts with line 52 *добыча* and gender (Подобрана/Подобрано). | `Подобрана проклятая добыча! - ${0}` |
| 65 | `Ammo is full!` | `Патроны заполнены!` | [MIN] Naturalness — "патроны заполнены" is non-idiomatic. | `Боезапас полон!` |
| 31 | `Restricted Area Price` | `Цена закрытой зоны` | [MIN] Naturalness — "цена зоны" reads like a store label. | `Плата за доступ в закрытую зону` |
| 73 | `Can't plant here!` | `Здесь нельзя установить!` | [MIN] Naturalness — verb without object. | `Здесь нельзя разместить!` |
| 98 | `Got permission to enter this faction's turf!` | `Получено разрешение на территорию этой фракции!` | [MIN] Naturalness — "разрешение на территорию" is clipped. | `Получено разрешение войти на территорию этой фракции!` |
| 119 | `Workshop episodes` | `Эпизоды мастерской` | [MIN] Naturalness — "мастерской" is ambiguous/calque. | `Эпизоды из мастерской` |
| 158 | `Custom Difficulties` | `Пользовательские сложности` | [MIN] Register — "пользовательские" is neutral/technical, not player-facing. | `Настраиваемые сложности` |
| 37 | `Player Cant Afford Item` | `Игроку не хватает на предмет` | [MIN] Naturalness — clipped "на предмет". | `Игрок не может позволить себе предмет` |
| 88 | `Open Door Region` | `Открыть зону двери` | [MIN] Naturalness — awkward. | `Открыть область двери` |

---

## 4. Corrected lines (apply directly)

```
223: Name: Unarmed Goon\n\nPhysical State: \n\tIdle\n\tSubstate: Unknown\nBehaviour State: \n\tEngagingPlayer\n\tSubstate: Unknown=Имя: Безоружный громила\n\nФизическое состояние: \n\tБездействие\n\tПодсостояние: Неизвестно\nСостояние поведения: \n\tВступает в бой\n\tПодсостояние: Неизвестно

137: Whacking wise guys...=Валим мафиози...

139: Making unrefusable offers...=Делаем предложения, от которых невозможно отказаться...

169: Sleep With The Fishes=Кормить рыб

53: Picked cursed Loot! - ${0}=Подобрана проклятая добыча! - ${0}

65: Ammo is full!=Боезапас полон!

31: Restricted Area Price=Плата за доступ в закрытую зону

73: Can't plant here!=Здесь нельзя разместить!

98: Got permission to enter this faction's turf!=Получено разрешение войти на территорию этой фракции!

119: Workshop episodes=Эпизоды из мастерской

158: Custom Difficulties=Настраиваемые сложности

37: Player Cant Afford Item=Игрок не может позволить себе предмет

88: Open Door Region=Открыть область двери
```

**Note on line 137 vs line 168 consistency:** If you adopt `Валим мафиози...` for
line 137, be aware line 168 (`Wise Guy Eh?=Умник, а?`) also renders *wise guy* as
*умник*. These are two different strings so a mismatch is not fatal, but decide on
one register for "wise guy" (mob-flavored vs. literal "умник") and apply it in both,
or document the nickname intent of line 168.

---

## 5. Category details

### 3. Technical correctness — PASS
- All 216 originals on the left of `=` match `ui_strings_curated.txt` **byte-for-byte**
  (automated cross-check: 0 mismatches).
- Rich-text tags preserved and balanced: lines 57, 58, 226–234 (`<color=...>`, `<u>`).
  Note lines 81 and 234 deliberately carry an unclosed `<color=red>` / leading `</color>`
  — these match the original and are concatenation fragments; keep as-is.
- Placeholders preserved exactly: `${0}` (lines 47, 52, 53), `{0}`/`{1}` (lines 32, 51, 54,
  55, 76, 226–233). No placeholder was dropped or reordered.
- Escapes `\n` and `\t` preserved: lines 189, 191, 194, 223.
- Layout dot-fields on stats screen (lines 128–131) retain exact dot counts and trailing
  spaces (`$` alignment) — verified.

### 2. Noir tone / register — PASS with minor notes
- Strong, in-tone translations: line 137/168 mob slang, 134–141 loading jokes, 169 mafia
  idiom, 171 "громила/слабак", 172–175 short noir quips.
- Minor flattening: line 137 *whack*/*wiseguy*, line 139 Godfather riff, line 169
  *sleep with the fishes* — all lose some period-mob flavor; corrections above restore it
  without breaking register.

### 4. Naturalness — PASS with minor issues
- Mostly idiomatic. Flagged phrasings (lines 31, 37, 53, 65, 73, 88, 98, 119, 158) are
  readable but not what a native-speaker localizer would ship; fixes provided.

### 5. Consistency — FAIL (minor)
- `Goon` → *громила* (line 171) vs *головорез* (line 223) — fixed by the CRIT item.
- "loot": *добыча* (lines 52, 131) vs *добро* (line 53) with gender mismatch
  (Подобрана/Подобрано) — fixed by line 53 correction.
- "toll" rendered *проезд* consistently (lines 32, 95) — internally consistent, though
  *пошлина/сбор* would be more accurate; not flagged as a defect.

---

## 6. Recommended follow-ups (non-blocking)
1. **Add to glossary** (no translation change needed, prevents future drift):
   `Umburgh → Умбург`, `Gianni → Джанни`, `Marek → Марек`.
2. Decide and document the register for "wise guy" (mob-flavored *мафиози* vs literal
   *умник*) so lines 137 and 168 stay aligned.
3. After applying corrections, re-run the byte-for-byte left-side check and a
   placeholder/tag-balance lint on the whole file before shipping.
