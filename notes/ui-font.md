# Кириллический шрифт для UI — XUnity.AutoTranslator (проверено по исходникам)

> **Важно:** сначала проверь, а нужен ли вообще отдельный шрифт. Запусти игру с
> уже установленным словарём (см. `notes/ui-localization.md`). Если русский текст
> в UI отображается **нормальными буквами** — отдельный шрифт НЕ нужен, и этот
> документ можно игнорировать. Если вместо букв **квадратики/пустота** — читай ниже.

## Ключевой факт (проверено по исходникам XUnity.AutoTranslator)

**XUnity.AutoTranslator НЕ конвертирует `.ttf` в TMP Font Asset автоматически**
и **не** подхватывает шрифты из папки `Translation/{Lang}/Fonts/` (такого
механизма в коде нет). `.ttf` используется только как **исходник внутри Unity
редактора**, чтобы создать SDF-шрифт и упаковать его в **asset bundle**. В
рантайме плагин умеет загружать шрифт только тремя способами (приоритетно):
1. **Файл asset bundle** в корне игры (имя без расширения, без пути);
2. Шрифт, **установленный в ОС** (по имени) — **только TMP 3.2.0+**;
3. Ресурс через `Resources.Load`.

**Критично для этой игры:** у неё TextMeshPro **1.4.0**, поэтому способ №2
(шрифт из ОС) **не работает** (`TMP_FontAsset.CreateFontAsset(string,string,int)`
появился только в TMP 3.2.0). Остаются способ №1 (asset bundle) и №3
(`Resources.Load`). Шрифты игры лежат внутри `data.unity3d`, так что
`Resources.Load` их почти наверняка не найдёт → остаётся **способ №1: собрать
свой asset bundle в Unity-редакторе** (один раз), а в моде распространять только
получившийся файл bundle.

## Почему субтитры с кириллицей работают, а UI — нет

В TMP каждый текстовый компонент (`TMP_Text`) ссылается на **свой** `TMP_FontAsset`.
Шрифты субтитров (`LiberationSans`, `aline_font`) содержат кириллицу, поэтому
субтитры и рендерят её. UI использует **другой** шрифт без кириллицы → в UI
квадратики. Автоперенос глифов из шрифта субтитров в UI плагин **не делает** —
он применяет только **твой** настроенный шрифт.

## Процедура (выполняется ОДИН раз в Unity-редакторе; юзеру играть не нужно)

1. **Unity 6000** (версия должна совпадать с версией игры — иначе пустой текст).
2. Импортировать TextMeshPro; положить `.ttf` с кириллицей в `Assets/`
   (лицензируемый для распространения: Noto Sans / DejaVu Sans / PT Sans — OFL).
3. **Window → TextMeshPro → Font Asset Creator**:
   - Source Font = твой `.ttf`;
   - Character Set = **Unicode Range (Hex)**;
   - **Обязательно** диапазон кириллицы: `0400-04FF` (плюс базовые
     `0020-007E,00A0-00FF,2000-206F` для латиницы/знаков/пунктуации);
   - Padding 3–5, Packing Method Fast, Atlas Resolution 8192×8192.
4. Сгенерировать Font Atlas → получится SDF-шрифт.
5. Создать скрипт `Editor/TextAssetBundleBuilder.cs`, назначить шрифт на
   asset bundle с именем, например `fallenaces_cyr_ru`, собрать через
   `BuildPipeline.BuildAssetBundles`.
6. Итог — **один файл** `fallenaces_cyr_ru` (без расширения). Его и распространяем.

## Установка в моде

1. Положить файл `fallenaces_cyr_ru` в **корень игры** (без расширения).
2. В `BepInEx/config/AutoTranslatorConfig.ini`:
   ```ini
   [TextFrameworks]
   EnableTextMeshPro=True
   [Behaviour]
   FallbackFontTextMeshPro=fallenaces_cyr_ru
   ```
   Рекомендуется **Fallback** (шрифт подставляется как запасной только для
   отсутствующих глифов, основной шрифт UI не ломается). Если fallback не
   срабатывает на TMP 1.4.0 — заменить на `OverrideFontTextMeshPro=fallenaces_cyr_ru`
   (принудительно ставит шрифт на все TMP-компоненты).
3. Перезагрузить словарь/перезапустить игру.

## Единственный непроверенный момент

Плагин проверяет `TMP_Settings_Properties.FallbackFontAssets`; в TMP 1.4.0 это
свойство существует, но **точно ли сработает** путь fallback на этой версии —
нужно проверить в игре. Если не сработает — использовать Override.

## Источники
- Вики: TextMeshPro Font Asset Creation & Packaging Guide (issue #840)
- FontHelper.cs, AutoTranslationPlugin.cs (LoadFallbackFont), Settings.cs
- Требование TMP 3.2.0+ для шрифта из ОС: issue #854
- Пример реального значения: `FallbackFontTextMeshPro=arialuni_sdf_u2019`
  (TinyRogues-zh-CN/build_patch.ps1)
