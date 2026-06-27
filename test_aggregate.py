"""Pruebas de la capa de unificación.

Correr:  python3 test_aggregate.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import Person, norm_cedula      # noqa: E402
from aggregate import build_unified         # noqa: E402


def P(cat, nombre, cedula="", edad="", **kw):
    return Person(source=kw.pop("source", "t"), category=cat, nombre=nombre,
                  cedula=norm_cedula(cedula), edad=edad, **kw)


def test_misma_cedula_se_unifica_en_un_registro():
    people = [
        P("desaparecido", "Maria F Gonzalez", "12345678", 34, source="desap"),
        P("hospital", "M. Gonzalez", "12345678", 34, source="hospital-demo", ubicacion="HUC", estatus="ingresado"),
    ]
    u = build_unified(people)
    assert len(u) == 1
    assert len(u[0]["apariciones"]) == 2


def test_genera_alerta_alta_desaparecido_en_hospital():
    people = [
        P("desaparecido", "Carmen Diaz", "9111222", 61, source="desap"),
        P("hospital", "Carmen Diaz", "9111222", 61, source="hospital-demo", ubicacion="Luciani", estatus="estable"),
    ]
    u = build_unified(people)
    assert u[0]["alerta"]["nivel"] == "alta"


def test_export_publico_no_incluye_cedula():
    people = [P("hospital", "Juan Perez", "11222333", 40, source="hospital-demo")]
    u = build_unified(people)                       # por defecto: público, sin cédula
    assert "11222333" not in str(u)


def test_export_con_cedula_la_incluye_para_busqueda():
    people = [P("hospital", "Juan Perez", "11222333", 40, source="hospital-demo")]
    u = build_unified(people, include_cedula=True)  # modo búsqueda exacta
    assert u[0].get("cedula") == "11222333"


def test_personas_distintas_no_se_mezclan():
    people = [
        P("desaparecido", "Ana Lopez", "1", 20, source="desap"),
        P("hospital", "Pedro Gomez", "2", 50, source="hospital-demo"),
    ]
    u = build_unified(people)
    assert len(u) == 2
    assert all(r["alerta"] is None for r in u)


def test_una_fuente_ubicado_dice_segun():
    people = [P("desaparecido", "Ana Lopez", "1", 30, estatus="ubicado", source="plataA", link="http://a")]
    u = build_unified(people)
    assert u[0]["alerta"]["nivel"] == "localizado"
    assert "plataA" in u[0]["alerta"]["texto"] and u[0]["alerta"]["link"] == "http://a"


def test_dos_fuentes_ubicado_confirma_al_cien():
    people = [
        P("desaparecido", "Ana Lopez", "1", 30, estatus="ubicada", source="plataA"),
        P("desaparecido", "Ana Lopez", "1", 30, estatus="encontrada", source="plataB"),
    ]
    u = build_unified(people)
    assert u[0]["alerta"]["nivel"] == "localizado_confirmado"


def test_no_localizado_no_es_ubicado():
    # 'sin localizar' / 'no localizado' = sigue buscada, NO ubicada
    people = [P("desaparecido", "Ana Lopez", "1", 30, estatus="sin localizar", source="plataA")]
    u = build_unified(people)
    assert u[0]["alerta"] is None


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
