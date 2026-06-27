"""Capa de unificación.

Junta a todas las personas de todas las fuentes en un índice único:
  - Deduplica (una persona que aparece en varias plataformas = un solo registro
    con varias "apariciones").
  - Calcula UN estatus/alerta de cabecera por persona, con esta prioridad:
      1. localizado_confirmado : 2+ plataformas la marcan ubicada -> ubicada al 100%.
      2. alta                  : reportada desaparecida Y aparece en hospital (cédula).
      3. localizado            : UNA plataforma la marca ubicada -> "Ubicada según X (verifica)".
      4. posible               : coincidencia difusa (nombre+edad) con un hospital.
      5. fallecido             : reportada como fallecida en una fuente (verifica).
      (sin alerta = sigue buscada)
  - Exporta una versión para el buscador. Por defecto SIN cédula ni teléfonos.

Somos SOLO LECTURA: no marcamos nada en la web de nadie. Pero mostramos la verdad
más fresca cruzando todas las fuentes, y siempre enlazamos para verificar.
"""
from schema import norm_name, norm_estatus
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
        "estatus_norm": norm_estatus(p.estatus),
        "fecha": p.fecha,
        "link": p.link,
    }


def _alerta(rec, cross_alta, cross_pos):
    """Aplica la prioridad de estatus de cabecera (ver docstring del módulo)."""
    aps = rec["apariciones"]
    locs = [a for a in aps if a["estatus_norm"] == "LOCALIZADO"]
    fuentes_loc = {a["fuente"] for a in locs}
    falls = [a for a in aps if a["estatus_norm"] == "FALLECIDO"]

    if len(fuentes_loc) >= 2:
        return {"nivel": "localizado_confirmado",
                "texto": f"✅ Ubicada — confirmada por {len(fuentes_loc)} plataformas"}
    if cross_alta:
        return cross_alta
    if len(fuentes_loc) == 1:
        a = locs[0]
        return {"nivel": "localizado",
                "texto": f"Ubicada según {a['fuente']} — verifica",
                "link": a["link"]}
    if cross_pos:
        return cross_pos
    if falls:
        a = falls[0]
        return {"nivel": "fallecido",
                "texto": f"Reportada como fallecida en {a['fuente']} — verifica",
                "link": a["link"]}
    return None


def build_unified(people, include_cedula=False):
    groups = {}
    for p in people:
        groups.setdefault(_identity(p), []).append(p)

    recs = []           # [(key, rec, members)]
    cross_alta = {}     # key -> alerta dict (cruce por cédula: desaparecido+hospital)
    for key, members in groups.items():
        rec = {
            "nombre": max((m.nombre for m in members), key=len, default=""),
            "edad": next((m.edad for m in members if m.edad), ""),
            "genero": next((m.genero for m in members if m.genero), ""),
            "apariciones": [_aparicion(m) for m in members],
            "alerta": None,
        }
        if include_cedula:
            ced = next((m.cedula for m in members if m.cedula), "")
            if ced:
                rec["cedula"] = ced
        cats = {m.category for m in members}
        if "desaparecido" in cats and "hospital" in cats:
            hosp = next(m for m in members if m.category == "hospital")
            cross_alta[key] = {
                "nivel": "alta",
                "texto": f"Reportada desaparecida y APARECE en hospital: "
                         f"{hosp.ubicacion or '—'} ({hosp.estatus or 's/d'})",
                "link": hosp.link,
            }
        recs.append((key, rec, members))

    # Cruce difuso (nombre+edad) para los desaparecidos SIN cédula.
    cross_pos = {}
    des = [p for p in people if p.category == "desaparecido" and not p.cedula]
    hos = [p for p in people if p.category == "hospital"]
    for m in cross_match(des, hos):
        cross_pos.setdefault(_identity(m.desaparecido), {
            "nivel": "posible",
            "texto": f"POSIBLE coincidencia en hospital: "
                     f"{m.hospital.ubicacion or '—'} ({m.hospital.estatus or 's/d'}) — {m.motivo}",
            "link": m.hospital.link,
        })

    out = []
    for key, rec, members in recs:
        rec["alerta"] = _alerta(rec, cross_alta.get(key), cross_pos.get(key))
        out.append(rec)
    return out
