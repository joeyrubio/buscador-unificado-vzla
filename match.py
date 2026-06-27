"""Motor de cruce desaparecidos <-> hospitales.

Estrategia, en orden:
  1) CÉDULA  -> coincidencia casi exacta (alta confianza). Es el identificador
     único venezolano; si coincide, es la misma persona.
  2) NOMBRE + EDAD -> coincidencia difusa y CONSERVADORA (posible). Solo si el
     nombre es >=90% similar y la edad no contradice.

Somos conservadores a propósito: un falso positivo aquí es cruel (decirle a una
familia que su persona está en un hospital cuando no lo está). Por eso lo difuso
se marca como "posible, revisar", no como certeza.
"""
from dataclasses import dataclass
from difflib import SequenceMatcher

from schema import norm_name, name_tokens


@dataclass
class Match:
    desaparecido: object
    hospital: object
    score: float
    nivel: str        # "alta" | "posible"
    motivo: str


def _age_ok(a, b):
    try:
        return abs(int(a) - int(b)) <= 2
    except (ValueError, TypeError):
        return True   # si falta la edad, no descartamos


def _name_sim(a, b):
    na, nb = norm_name(a), norm_name(b)
    if not na or not nb:
        return 0.0
    seq = SequenceMatcher(None, na, nb).ratio()
    ta, tb = name_tokens(a), name_tokens(b)
    jacc = len(ta & tb) / len(ta | tb) if (ta or tb) else 0.0
    return max(seq, jacc)


def cross_match(desaparecidos, hospitales, name_threshold=0.90):
    by_cedula = {}
    for h in hospitales:
        if h.cedula:
            by_cedula.setdefault(h.cedula, []).append(h)

    matches = []
    for d in desaparecidos:
        # 1) cédula: casi exacto
        if d.cedula and d.cedula in by_cedula:
            for h in by_cedula[d.cedula]:
                matches.append(Match(d, h, 1.0, "alta", f"cédula {d.cedula} coincide"))
            continue
        # 2) nombre + edad: difuso y conservador
        for h in hospitales:
            sim = _name_sim(d.nombre, h.nombre)
            if sim >= name_threshold and _age_ok(d.edad, h.edad):
                motivo = f"nombre {int(sim * 100)}% similar"
                if d.edad and h.edad:
                    motivo += f", edad {d.edad}/{h.edad}"
                matches.append(Match(d, h, round(sim, 3), "posible", motivo))
    return matches
