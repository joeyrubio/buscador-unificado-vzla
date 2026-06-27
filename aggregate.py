"""Capa de unificación.

Junta a todas las personas de todas las fuentes en un índice único:
  - Deduplica (una persona que aparece en varias plataformas = un solo registro
    con varias "apariciones").
  - Adjunta la ALERTA de cruce desaparecido <-> hospital.
  - Exporta una versión para el buscador.

PRIVACIDAD: por defecto el índice NO incluye cédula (`include_cedula=False`).
La búsqueda por cédula (`include_cedula=True`) la incluye SOLO para permitir el
match exacto; en un despliegue público con data real eso debe hacerse en un
endpoint del servidor, no en un archivo estático (una cédula es de baja entropía
y un hash sería reversible). Nunca se publican teléfonos.
"""
from schema import norm_name
from match import cross_match


def _identity(p):
    """Clave de identidad para deduplicar. Cédula manda; si no hay, nombre+edad."""
    if p.cedula:
        return ("c", p.cedula)
    return ("n", norm_name(p.nombre), str(p.edad).strip())


def _aparicion(p):
    return {
        "fuente": p.source,
        "categoria": p.category,
        "ubicacion": p.ubicacion,
        "estatus": p.estatus,
        "fecha": p.fecha,
        "link": p.link,
    }


def build_unified(people, include_cedula=False):
    groups = {}
    for p in people:
        groups.setdefault(_identity(p), []).append(p)

    unified = []
    rec_by_key = {}
    for key, members in groups.items():
        nombre = max((m.nombre for m in members), key=len, default="")
        edad = next((m.edad for m in members if m.edad), "")
        genero = next((m.genero for m in members if m.genero), "")
        cats = {m.category for m in members}
        rec = {
            "nombre": nombre,
            "edad": edad,
            "genero": genero,
            "apariciones": [_aparicion(m) for m in members],
            "alerta": None,
        }
        if include_cedula:
            ced = next((m.cedula for m in members if m.cedula), "")
            if ced:
                rec["cedula"] = ced
        # ALERTA ALTA: la misma persona (misma cédula/identidad) está reportada
        # como desaparecida Y aparece en un hospital.
        if "desaparecido" in cats and "hospital" in cats:
            hosp = next(m for m in members if m.category == "hospital")
            rec["alerta"] = {
                "nivel": "alta",
                "texto": f"Reportada desaparecida y APARECE en hospital: "
                         f"{hosp.ubicacion or '—'} ({hosp.estatus or 's/d'})",
            }
        unified.append(rec)
        rec_by_key[key] = rec

    # ALERTA POSIBLE: cruce difuso por nombre+edad para los que NO traían cédula
    # (no se autoagruparon arriba).
    des = [p for p in people if p.category == "desaparecido" and not p.cedula]
    hos = [p for p in people if p.category == "hospital"]
    for m in cross_match(des, hos):
        rec = rec_by_key.get(_identity(m.desaparecido))
        if rec and not rec["alerta"]:
            rec["alerta"] = {
                "nivel": "posible",
                "texto": f"POSIBLE coincidencia en hospital: "
                         f"{m.hospital.ubicacion or '—'} ({m.hospital.estatus or 's/d'}) — {m.motivo}",
            }
    return unified
