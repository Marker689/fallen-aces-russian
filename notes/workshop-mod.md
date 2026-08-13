# Упаковка русификатора как мода Steam Workshop

Источник: официальный гайд «AceEd and Steam Workshop Guide» (id=3486794926,
автор El Oshcuro — разработчик, обновлён 1-2 июня 2025) и гайд «Fallen Aces
SDK and Workshop Documentation» (Metadata Rosenberg).

## Как устроен моддинг Fallen Aces

- Игра поддерживает **официальные моды** через **Aces Mod Manager** (в игре:
  `Tools\Mod Manager\Aces Mod Manager.exe`) и **Steam Workshop**.
- Mod Manager интегрирован со SteamUGC (WorkshopID, TryGetWorkshopMod, SteamAPI).
- Логика загрузки модов в игровом движке (FallAces.CSharp.dll): ищет папку `Mods/`,
  строки `modlist.txt`, `Workshop episodes`, `AcesData/Subtitles`, `Episodes`.
- Для загрузки мода на Workshop используется **Lead Pipe.exe** —
  `Steam\steamapps\common\Fallen Aces\Tools\Lead Pipe\Lead Pipe.exe`
  (официальный Workshop Uploader, также есть как вариант запуска игры).

## КРИТИЧНО: структура мода = структура AcesData

> «Once you have created a mod, you need to mimic the game's file structure to
> successfully upload it.»

Мод — это **папка, повторяющая внутреннюю структуру `AcesData`**. Пример из
официального гайда:

```
TestMod/
  Audio/Music/newsong.ogg
  Episodes/MyNewMap/(все данные уровня)
  Texture Packages/newtextures.bin
```

Дополнительно (из раздела про спрайты): мод может содержать
`Mod Folder/Texture Packages` и `Mod Folder/Sprites` — игра подхватывает их.

## Структура мода-русификатора

Для перевода нарратива мод должен содержать переведённые файлы в тех же
относительных путях, что и в `AcesData`:

```
RU_Localization/
  Subtiles/                        <- AcesData/Subtitles
    Blake/...txt
    Mike/...txt
    ... (все папки персонажей)
  Episodes/                        <- AcesData/Episodes
    Heart of Glass/ChapterN/Scripts/...txt
    Heart of Glass/ChapterN/Notes/...txt
    .../chapterInfo.txt
  (опционально) misc.txt, npcs.txt и др. корневые .txt
```

## Правила и ограничения

1. **Имена файлов менять нельзя.** `SpeakDialogue("...")` в скриптах ссылается
   на субтитры по имени файла (`EP1 CH1 - Shakedown_0`, `Level 1 - About To Blow`).
   Переводим ТОЛЬКО содержимое внутри кавычек, файл оставляем с тем же именем.
2. **Кодировка — UTF-8 без BOM.** Именно так пишутся оригинальные файлы.
3. **Формат строк сохранять байт-в-байт** (тайминги `T`, блоки `I N {}`,
   скобки `{ }`, теги `<color=#...>`, точки с запятой).
4. **Число строк в файле не менять** — нельзя добавлять/удалять строки.
5. Субтитры бывают в разных форматах: `{ T 0.5 } "text"`, `T 0 "text"` (внутри
   `I N {}` блоков), просто `"text"`, а также `text = "..."` (записки) и
   `SpeakDialogue(arg, "text")` (скрипты). Экстрактор/инжектор учитывают это.

## Процесс публикации (по гайду)

1. Собрать папку мода с правильной структурой (см. выше).
2. Запустить **Lead Pipe.exe**.
3. Кнопка **Mod Directory** → указать папку мода.
4. Ввести **название мода** (заголовок в Workshop).
5. Добавить **preview image** (макс 1 МБ).
6. Написать **описание**.
7. **Сохранить мод** (обязательно!) — НЕ класть `.acesmod` в папку загрузки,
   держать отдельно (например на рабочем столе).
8. Нажать **Upload**.

После успешной загрузки мод появится в Steam Workshop.

## Вывод для конвейера

Конвейер перевода должен выдавать не просто изменённые файлы в AcesData, а
**отдельную папку-мод** с той же внутренней структурой. Для этого:
- инжектор пишет переведённые файлы в `~/fallenaces-rus/mod/Subtitles/...`,
  `~/fallenaces-rus/mod/Episodes/...` и т.д. (сохраняя относительные пути);
- затем папка `mod/` загружается через Lead Pipe.
- (необязательно) одновременно можно копировать в реальную AcesData для
  локальной проверки, но основной носитель — мод.
