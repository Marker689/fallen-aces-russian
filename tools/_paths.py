#!/usr/bin/env python3
"""
Fallen Aces — централизованное разрешение путей конвейера.

Все скрипты должны импортировать пути отсюда, а не хардкодить их.
Пути читаются из переменных окружения с безопасными значениями по умолчанию
(текущие WSL-пути), поэтому поведение без окружения не меняется.

Переменные окружения:
    FALLEN_ACES_GAME    — корень установленной игры (Fallen Aces).
    FALLEN_ACES_BACKUP  — папка с оригинальными (англ.) исходниками для инжекта.
    FALLEN_ACES_OUT     — рабочая папка репозитория (по умолчанию ~/fallenaces-rus).
"""
import os

_DEFAULT_GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"
_DEFAULT_BACKUP = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces_backup_txt"
_DEFAULT_OUT = os.path.expanduser("~/fallenaces-rus")

# Корень игры. ВАЖНО: относительные пути в данных всегда вида "AcesData/...".
GAME = os.environ.get("FALLEN_ACES_GAME", _DEFAULT_GAME)
# Папка с чистыми английскими исходниками (для инжекта, чтобы мод не зависел
# от состояния живой AcesData, которая могла быть изменена пилотом).
BACKUP = os.environ.get("FALLEN_ACES_BACKUP", _DEFAULT_BACKUP)
# Рабочая папка репозитория (json-данные, пакеты, мод).
OUT = os.environ.get("FALLEN_ACES_OUT", _DEFAULT_OUT)
# Папка-мод, куда инжекторы собирают переведённые файлы.
MOD = os.path.join(OUT, "mod")


def source_root(subpath="AcesData"):
    """Корень исходных данных для чтения: BACKUP приоритетно, иначе GAME.

    Возвращает путь к папке, содержащей `subpath` (по умолчанию AcesData),
    или None, если ни бэкапа, ни игры нет. Бэкап — это чистые английские
    исходники (источник истины); живая игра может быть уже изменена пилотом.
    """
    for base in (BACKUP, GAME):
        if os.path.isdir(os.path.join(base, subpath)):
            return base
    return None


def resolve_source(file_rel):
    """Найти читаемый исходный файл по относительному пути вида "AcesData/...".

    Сначала смотрит в BACKUP (чистые оригиналы), затем в GAME (живая игра).
    Возвращает абсолютный путь или None, если файла нет ни там, ни там.
    """
    for base in (BACKUP, GAME):
        p = os.path.join(base, file_rel)
        if os.path.exists(p):
            return p
    return None


def mod_path(file_rel):
    """Преобразовать относительный путь "AcesData/Subtitles/X.txt" в путь внутри mod/."""
    if file_rel.startswith("AcesData/"):
        file_rel = file_rel[len("AcesData/"):]
    return os.path.join(MOD, file_rel)


def aces_rel(rel):
    """Нормализовать путь относительно корня игры до вида 'AcesData/...'."""
    rel = rel.replace("\\", "/")
    parts = rel.split("/")
    if "AcesData" in parts:
        return "/".join(parts[parts.index("AcesData"):])
    return rel
