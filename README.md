# 🇻🇪 Buscador Unificado de Personas — Terremoto Venezuela 2026

Reúne en un solo buscador la información de las +100 plataformas que surgieron
tras el terremoto, para que una familia no tenga que revisar 17 sitios para
encontrar a alguien. Si una persona reportada como **desaparecida** aparece en
una **lista de hospital**, lo detecta y lo avisa.

**Python puro, sin dependencias.** Los conectores solo **leen**; nunca escriben
en la base de nadie. Siempre se enlaza de vuelta a la fuente original.

## Correr

```bash
python3 test_match.py        # pruebas del cruce
python3 test_aggregate.py    # pruebas de la unificación

# Demo con data de muestra (sin red):
python3 run.py --sample --export web/data.json --with-cedula
cd web && python3 -m http.server 8777     # abrir http://localhost:8777
```

Busca en el buscador por **nombre, cédula, género y rango de edad**. Prueba
`maria` o `carmen` para ver las alertas rojas de coincidencia con hospital.

## Cómo funciona

| Archivo | Rol |
|---|---|
| `schema.py` | Formato común (`Person`) + normalización de cédula, nombre, género, edad |
| `connectors.py` | Lectores **Supabase / Google Sheet / CSV** (solo lectura) |
| `match.py` | Cruce: **cédula** = alta; **nombre+edad** = posible (conservador) |
| `aggregate.py` | Unifica apariciones, genera alertas, exporta índice |
| `run.py` | Orquesta todo |
| `web/` | Buscador web estático (nombre · cédula · género · edad) |

## Conectar una fuente real

1. `cp sources.example.json sources.json`  (sources.json está gitignored)
2. Completa `anon_key`, `table` y ajusta `map` a las columnas reales.
3. Quita `"disabled": true`.
4. `python3 run.py --export web/data.json`

## Privacidad (innegociable)

- El índice público (`--export` sin `--with-cedula`) **no** incluye cédula.
- **Nunca** se publican teléfonos ni datos sensibles.
- `--with-cedula` es solo para demo/local: una cédula es de baja entropía, así
  que en **producción** la búsqueda por cédula debe ser un endpoint del servidor,
  no un archivo estático. `web/data.json` está gitignored para no commitear data real.
- El cruce es **conservador**: lo difuso se marca "posible", nunca como certeza.
  Un falso positivo aquí le da falsas esperanzas a una familia.

## Formato común mínimo

`nombre · cedula · edad · genero · ubicacion · estatus · fecha · link`
