"""Orquestador: carga fuentes -> unifica -> cruza -> reporta y/o exporta.

Uso:
  python3 run.py --sample                       # demo con data de muestra (sin red)
  python3 run.py                                # fuentes reales de sources.json
  python3 run.py --sample --export web/data.json               # índice público (sin cédula)
  python3 run.py --sample --export web/data.json --with-cedula  # índice con búsqueda por cédula (solo demo/local)
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connectors import load_source          # noqa: E402
from match import cross_match               # noqa: E402
from aggregate import build_unified         # noqa: E402


def load_all(sources):
    people = []
    for cfg in sources:
        if cfg.get("disabled"):
            print(f"  · {cfg['id']}: en espera (sin acceso todavía)")
            continue
        try:
            p = load_source(cfg)
            print(f"  · {cfg['id']} ({cfg['category']}): {len(p)} registros")
            people += p
        except Exception as e:
            print(f"  · {cfg['id']}: ERROR -> {e}")
    return people


def report(matches):
    if not matches:
        print("\nSin coincidencias por ahora.")
        return
    alta = [m for m in matches if m.nivel == "alta"]
    pos = [m for m in matches if m.nivel == "posible"]
    print(f"\n=== {len(alta)} coincidencia(s) ALTA  +  {len(pos)} POSIBLE(s) ===\n")
    for m in alta + pos:
        d, h = m.desaparecido, m.hospital
        flag = "🔴 ALTA   " if m.nivel == "alta" else "🟡 POSIBLE"
        print(f"{flag} | {d.nombre}  (reportado desaparecido en '{d.source}')")
        print(f"           → APARECE EN HOSPITAL: {h.ubicacion or '—'} | "
              f"estatus: {h.estatus or '—'} | fuente: '{h.source}'")
        print(f"           motivo: {m.motivo}")
        print(f"           enlaces: {d.link}  ↔  {h.link}\n")


def export(people, path, with_cedula=False):
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = build_unified(people, include_cedula=with_cedula)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    alertas = sum(1 for r in data if r["alerta"])
    print(f"\nExportadas {len(data)} personas unificadas ({alertas} con alerta) -> {path}")
    if with_cedula:
        print("⚠️  Este índice incluye cédula para permitir la búsqueda exacta.")
        print("    NO publiques este archivo con data REAL: en producción la búsqueda")
        print("    por cédula debe ser un endpoint del servidor, no un archivo estático.")
    else:
        print("(El índice público NO incluye cédula ni datos sensibles.)")


def main():
    argv = sys.argv
    sample = "--sample" in argv
    here = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(here, "sources.sample.json" if sample else "sources.json")
    with open(cfg_path, encoding="utf-8") as f:
        sources = json.load(f)

    print("Cargando fuentes:")
    people = load_all(sources)
    des = [p for p in people if p.category == "desaparecido"]
    hos = [p for p in people if p.category == "hospital"]
    print(f"\nTotal cargado: {len(des)} desaparecidos · {len(hos)} en hospitales")

    report(cross_match(des, hos))

    if "--export" in argv:
        export(people, argv[argv.index("--export") + 1], with_cedula="--with-cedula" in argv)


if __name__ == "__main__":
    main()
