"""Conectores de lectura por tipo de fuente.

REGLA DE ORO: estos conectores solo LEEN. Nunca escriben, nunca modifican,
nunca agregan registros a la base de nadie. Leen lo que la plataforma ya
publica y lo traducen al esquema común (schema.Person).
"""
import urllib.request
import urllib.parse
import json
import csv
import io
import os

from schema import Person, norm_cedula, norm_genero


def _http_get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _apply_map(row, mapping):
    """Traduce las columnas de la fuente a los campos del esquema común."""
    return {dst: (row.get(src, "") if src else "") for dst, src in mapping.items()}


def _rows_to_people(rows, cfg):
    mapping = cfg["map"]
    people = []
    for row in rows:
        m = _apply_map(row, mapping)
        people.append(Person(
            source=cfg["id"],
            category=cfg["category"],
            nombre=str(m.get("nombre", "")).strip(),
            cedula=norm_cedula(m.get("cedula", "")),
            edad=str(m.get("edad", "")).strip(),
            genero=norm_genero(m.get("genero", "")),
            ubicacion=str(m.get("ubicacion", "")).strip(),
            estatus=str(m.get("estatus", "")).strip(),
            fecha=str(m.get("fecha", "")).strip(),
            link=cfg.get("link", ""),
            raw=row,
        ))
    return people


def from_supabase(cfg):
    """Lee una tabla de Supabase por la API REST pública (la misma que usa su web)."""
    base = cfg["url"].rstrip("/")
    table = urllib.parse.quote(cfg["table"])
    key = cfg["anon_key"]
    url = f"{base}/rest/v1/{table}?select=*"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows = json.loads(_http_get(url, headers))
    return _rows_to_people(rows, cfg)


def from_gsheet(cfg):
    """Lee una Google Sheet pública como CSV (gviz)."""
    sid = cfg["sheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv"
    if cfg.get("sheet_name"):
        url += "&sheet=" + urllib.parse.quote(cfg["sheet_name"])
    rows = list(csv.DictReader(io.StringIO(_http_get(url))))
    return _rows_to_people(rows, cfg)


def from_csv(cfg):
    """Lee un CSV o JSON local (data de muestra o exports manuales que nos pasen)."""
    path = cfg["path"]
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
    else:
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    return _rows_to_people(rows, cfg)


def _rest_extract(data, cfg):
    """Saca la lista de registros de una respuesta JSON y descarta los ocultos.

    - list_path: ruta a la lista si viene anidada (ej. "data.items").
    - skip_if: descarta registros que igualen estos campos (ej. {"oculto": true}),
      para respetar lo que la plataforma marcó como NO público.
    """
    if cfg.get("list_path"):
        for key in cfg["list_path"].split("."):
            data = data.get(key, []) if isinstance(data, dict) else []
    if isinstance(data, dict):
        data = data.get("data") or data.get("results") or data.get("personas") or []
    skip = cfg.get("skip_if", {})
    return [r for r in data
            if not any(str(r.get(k)).lower() == str(v).lower() for k, v in skip.items())]


def from_rest(cfg):
    """Lee un API REST JSON público (GET). Genérico y reutilizable entre sitios."""
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    headers.update(cfg.get("headers", {}))
    data = json.loads(_http_get(cfg["url"], headers))
    return _rows_to_people(_rest_extract(data, cfg), cfg)


LOADERS = {"supabase": from_supabase, "gsheet": from_gsheet, "csv": from_csv, "rest": from_rest}


def load_source(cfg):
    return LOADERS[cfg["type"]](cfg)
