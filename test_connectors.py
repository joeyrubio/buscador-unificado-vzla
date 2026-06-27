"""Pruebas del conector REST genérico (sin red).

Correr:  python3 test_connectors.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connectors import _rest_extract, _rows_to_people   # noqa: E402


CFG = {
    "id": "demo", "category": "desaparecido", "link": "https://x",
    "skip_if": {"oculto": True},
    "map": {"nombre": "nombre", "edad": "edad", "ubicacion": "zona", "estatus": "estado"},
}


def test_extrae_lista_simple():
    data = [{"nombre": "Ana", "oculto": False}, {"nombre": "Beto", "oculto": False}]
    assert len(_rest_extract(data, CFG)) == 2


def test_descarta_ocultos():
    data = [{"nombre": "Ana", "oculto": False}, {"nombre": "Secreto", "oculto": True}]
    rows = _rest_extract(data, CFG)
    assert len(rows) == 1 and rows[0]["nombre"] == "Ana"


def test_lista_anidada():
    cfg = dict(CFG, list_path="data.items")
    data = {"data": {"items": [{"nombre": "Ana", "oculto": False}]}}
    assert len(_rest_extract(data, cfg)) == 1


def test_mapeo_a_persona():
    data = [{"nombre": "Ana Pérez", "edad": 30, "zona": "Catia", "estado": "desaparecido", "oculto": False}]
    people = _rows_to_people(_rest_extract(data, CFG), CFG)
    p = people[0]
    assert p.nombre == "Ana Pérez" and p.ubicacion == "Catia" and p.category == "desaparecido"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
            ok += 1
        except AssertionError:
            print(f"FAIL  {fn.__name__}")
    print(f"\n{ok}/{len(fns)} pruebas OK")
    sys.exit(0 if ok == len(fns) else 1)
