"""The ingest pipeline's part-time detection (scripts/ingest/structure.py).

Every imported post used to go in as full_time, so "yarim stavka" jobs were
listed as "To'liq stavka" and the part-time filter could not find them.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts" / "ingest"))
structure = pytest.importorskip("structure")
PART_TIME = structure.PART_TIME


@pytest.mark.parametrize("text", [
    "Ish vaqti: yarim stavka", "Yarim kunlik ish", "ЯРИМ СТАВКА", "Part-time", "part time job",
    "Работа по 4 часа в день", "Гибкий график: 4–6 часов в день", "неполный рабочий день",
    "частичная занятость", "подработка для студентов", "полставки", "kuniga 4 soat",
])
def test_says_part_time(text):
    assert PART_TIME.search(text)


@pytest.mark.parametrize("text", [
    "To'liq stavka", "Erkin grafik", "Свободный график", "2/2 smenali ish", "Ish vaqti 09:00-18:00",
    "yarimta non", "8 часов в день",
])
def test_does_not(text):
    assert not PART_TIME.search(text)
