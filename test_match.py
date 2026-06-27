"""Pruebas del motor de cruce. Lo crítico para no darle falsas esperanzas a una familia.

Correr:  python3 test_match.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import Person, norm_cedula      # noqa: E402
from match import cross_match               # noqa: E402


def P(cat, nombre, cedula="", edad="", **kw):
    return Person(source="t", category=cat, nombre=nombre,
                  cedula=norm_cedula(cedula), edad=edad, **kw)


def test_cedula_normalization_handles_formatting():
    assert norm_cedula("V-12.345.678") == "12345678"
    assert norm_cedula("0012345678") == "12345678"
    assert norm_cedula("12.345.678") == norm_cedula("12345678")


def test_cedula_match_es_alta():
    d = [P("desaparecido", "Maria Gonzalez", "V-12.345.678", 34)]
    h = [P("hospital", "M. Gonzalez", "12345678", 34, ubicacion="HUC", estatus="ingresado")]
    m = cross_match(d, h)
    assert len(m) == 1 and m[0].nivel == "alta"


def test_fuzzy_nombre_edad_es_posible():
    d = [P("desaparecido", "Luis Alberto Rodríguez", edad=27)]
    h = [P("hospital", "Luis Alberto Rodriguez", edad=28, ubicacion="Vargas")]
    m = cross_match(d, h)
    assert len(m) == 1 and m[0].nivel == "posible"


def test_no_falso_positivo_por_nombre_distinto():
    d = [P("desaparecido", "Jose Ramon Perez", "18900111", 52)]
    h = [P("hospital", "Pedro Pablo Marquez", "30222111", 45)]
    assert cross_match(d, h) == []


def test_edad_contradictoria_descarta_fuzzy():
    # mismo nombre pero edades muy distintas y sin cédula -> NO match
    d = [P("desaparecido", "Ana Maria Lopez", edad=20)]
    h = [P("hospital", "Ana Maria Lopez", edad=70)]
    assert cross_match(d, h) == []


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
