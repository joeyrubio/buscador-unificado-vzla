"""Esquema común mínimo + normalización.

Una sola definición de "persona" a la que se normaliza la data de TODAS las
plataformas. Si todos hablamos este mismo idioma, cruzar es trivial.
"""
from dataclasses import dataclass, field
import unicodedata
import re

CATEGORIES = {"desaparecido", "hospital", "localizado"}


@dataclass
class Person:
    source: str                       # id de la plataforma de origen
    category: str                     # desaparecido | hospital | localizado
    nombre: str = ""
    cedula: str = ""                  # normalizada (solo dígitos, sin ceros a la izquierda)
    edad: str = ""
    genero: str = ""                  # "M" | "F" | "" (normalizado)
    ubicacion: str = ""               # centro de salud / última ubicación conocida
    estatus: str = ""                 # ingresado | fallecido | localizado | sin localizar...
    fecha: str = ""
    link: str = ""                    # enlace de vuelta a la plataforma de origen
    raw: dict = field(default_factory=dict)


def norm_cedula(value) -> str:
    """'V-12.345.678' -> '12345678'. Quita todo lo que no sea dígito y ceros a la izquierda."""
    if value is None:
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.lstrip("0")


def norm_name(value) -> str:
    """Minúsculas, sin acentos, sin signos, espacios colapsados. Para comparar nombres."""
    if not value:
        return ""
    s = unicodedata.normalize("NFKD", str(value))
    s = "".join(c for c in s if not unicodedata.combining(c))   # quita acentos
    s = re.sub(r"[^a-z\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def norm_genero(value) -> str:
    """Normaliza variantes a 'M' / 'F' / ''. Acepta masculino, hombre, varón, etc."""
    s = norm_name(value)
    if s in {"m", "masculino", "hombre", "varon", "male", "h"}:
        return "M"
    if s in {"f", "femenino", "mujer", "female"}:
        return "F"
    return ""


def norm_estatus(value) -> str:
    """Mapea el estatus libre de cada plataforma a un set común.

    Devuelve: LOCALIZADO | BUSCADO | HOSPITAL | FALLECIDO | "" (desconocido).
    El orden importa: 'no localizado' / 'sin localizar' = BUSCADO, no LOCALIZADO.
    """
    s = norm_name(value)
    if not s:
        return ""
    if any(w in s for w in ("fallecid", "muert", "occis", "sin vida", "deceso")):
        return "FALLECIDO"
    if any(w in s for w in ("desaparec", "buscad", "sin localiz", "no localiz",
                            "perdid", "extraviad", "se busca")):
        return "BUSCADO"
    if any(w in s for w in ("ubicad", "localizad", "encontrad", "a salvo",
                            "rescatad", "aparecio", "hallad", "reunid")) \
            or s in ("vivo", "viva", "sano", "sana"):
        return "LOCALIZADO"
    if any(w in s for w in ("ingresad", "hospitalizad", "internad", "en hospital",
                            "estable", "critic", "herid", "atendid")):
        return "HOSPITAL"
    return ""


def name_tokens(value) -> set:
    return set(norm_name(value).split())


def edad_int(value):
    """Devuelve la edad como int, o None si no es parseable."""
    try:
        return int(re.sub(r"\D", "", str(value)))
    except (ValueError, TypeError):
        return None
