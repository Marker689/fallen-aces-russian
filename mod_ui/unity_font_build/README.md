# Сборка кириллического TMP-шрифта для UI (только если понадобится)

Используй это, **только если** при проверке в игре русский текст в UI
отображается квадратиками/пустотой. Если буквы нормальные — этот раздел не нужен.

## Почему так сложно (проверено по исходникам AutoTranslator)
- AutoTranslator **не** конвертирует `.ttf` в TMP Font Asset сам и не читает
  папку `Translation/{Lang}/Fonts/`.
- У игры TextMeshPro **1.4.0**, поэтому запасной путь «шрифт, установленный в ОС»
  (требует TMP 3.2.0+) **не работает**.
- Остаётся один надёжный способ: собрать **asset bundle** в Unity-редакторе
  (один раз) и распространять только файл bundle.

## Что здесь лежит
- `DejaVuSans-Regular.ttf` — кириллический шрифт (лицензия OFL, можно
  распространять). Берём его как источник.
- `Editor/FallenAcesFontBundleBuilder.cs` — скрипт сборки asset bundle в Unity.

## Как собрать (нужен Unity 6000, версия как у игры 6000.3.10)
1. Открой проект в Unity 6000, импортируй TextMeshPro.
2. Положи `DejaVuSans-Regular.ttf` в `Assets/Fonts/`.
3. **Window → TextMeshPro → Font Asset Creator**:
   - Source Font = DejaVuSans-Regular;
   - Character Set = Unicode Range (Hex), диапазон **обязательно** включает
     `0400-04FF` (кириллица) + `0020-007E,00A0-00FF,2000-206F`;
   - Padding 3–5, Packing Method Fast, Atlas Resolution 8192×8192 → Generate.
4. Положи `Editor/FallenAcesFontBundleBuilder.cs` в `Assets/Editor/`.
5. В инспекторе созданного шрифта назначь AssetBundle `fallenaces_cyr_ru`
   (поле AssetBundle → New), и поправь путь к ассету в скрипте (строка
   `assetNames`), если он другой.
6. Меню **FallenAces UI Localization → Build Font Bundle** → получится файл
   `fallenaces_cyr_ru` (без расширения).

## Установка
1. Скопируй файл `fallenaces_cyr_ru` в **корень игры**.
2. В `BepInEx/config/AutoTranslatorConfig.ini`:
   ```ini
   [Behaviour]
   FallbackFontTextMeshPro=fallenaces_cyr_ru
   ```
   Если fallback на TMP 1.4.0 не применится — замени на
   `OverrideFontTextMeshPro=fallenaces_cyr_ru`.
3. Перезапусти игру. См. `notes/ui-font.md` для деталей и источников.
