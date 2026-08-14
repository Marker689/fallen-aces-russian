#!/usr/bin/env python3
"""
Fallen Aces — общие вспомогательные функции конвейера.

Содержит единственные реализации make_id / load_translations, чтобы не
допускать расхождения между скриптами. Все функции ведут себя идентично
исходным локальным копиям (см. notes/tooling_hardening.md).

Важно: НЕ меняйте алгоритмы генерации id — по ним ссылаются .out.json-батчи
и injected-файлы. Любое изменение сломает соответствие переводов.
"""
import glob
import hashlib
import json


def make_id(file, line_no):
    """id строки субтитров (12 hex-символов): md5("file:line_no")."""
    return hashlib.md5(f"{file}:{line_no}".encode()).hexdigest()[:12]


def make_id_orig(file, orig):
    """id строки остатка поверхностей (16 hex-символов): md5("file|orig").

    orig — точный фрагмент файла (включая кавычки). Контент-основан: одинаковый
    orig в одном файле даёт одинаковый id и переводится целиком.
    """
    return hashlib.md5(f"{file}|{orig}".encode()).hexdigest()[:16]


def load_translations(glob_pattern):
    """Загрузить все переводы из *.out.json по glob-шаблону.

    Возвращает dict {id: перевод}. Пустые переводы ("" / None) отбрасываются.
    """
    trans = {}
    for path in glob.glob(glob_pattern):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        for k, v in d.items():
            if v:
                trans[k] = v
    return trans
