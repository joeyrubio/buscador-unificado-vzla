# 🇻🇪 Buscador Unificado de Personas — Terremoto Venezuela 2026

Reúne en un solo buscador la información de las +100 plataformas que surgieron
tras el terremoto, para que una familia no tenga que revisar 17 sitios para
encontrar a alguien. Si una persona reportada como **desaparecida** aparece en
una **lista de hospital**, lo detecta y lo avisa.

**Python puro, sin dependencias.** Los conectores solo **leen**; nunca escriben
en la base de nadie. Siempre se enlaza de vuelta a la fuente original.

## 🤝 ¿Tu plataforma quiere integrarse? (léeme)

Gracias por ayudar. La idea es que una familia **no tenga que revisar 17 sitios**
para buscar a una persona. Tú **no cambias nada** de tu plataforma ni nos
entregas tu base: solo nos das **lectura** de lo que ya publicas, y nosotros lo
unimos enlazando siempre de vuelta a ti.

**Qué necesitamos, según tu plataforma:**

| Si usas… | Qué nos das | Esfuerzo |
|---|---|---|
| **Supabase** | La URL del proyecto + una **anon key de solo lectura** + el nombre de la tabla. (Y de paso revisa tu RLS — te ayudamos.) | ~2 min |
| **Google Sheets** | El link de la hoja en "cualquiera con el link puede ver". | ~1 min |
| **API propio / web con backend** | El endpoint **GET** que devuelve la lista (ej. `/api/personas`). Marca con un campo los registros que NO son públicos; lo respetamos. | bajo |
| **Otra cosa / sin API** | Escríbenos: un export CSV/JSON manual o lo resolvemos contigo. | — |

**Campos que nos sirven** (mientras más, mejor; solo el nombre es imprescindible):
`nombre · cédula · edad · género · última ubicación · estatus · fecha`

> La **cédula** es oro: convierte el cruce con hospitales de "adivinanza por
> nombre" a coincidencia exacta.

**Cómo marcas "ubicado":** dinos qué palabra usas cuando aparece alguien
(ubicado, localizado, a salvo…). Así propagamos la buena noticia: si **una**
plataforma la marca ubicada, mostramos *"Ubicada según tu plataforma (verifica)"*;
si **dos o más** coinciden, la damos por **ubicada al 100%**.

**Nuestros compromisos contigo:**
- **Solo lectura.** Nunca escribimos, modificamos ni borramos nada tuyo.
- Enlazamos **de vuelta a tu plataforma**, con crédito, en cada resultado.
- **No publicamos** cédulas ni teléfonos en el buscador.
- Respetamos lo que marques como **oculto/privado**.
- Eliminación o corrección **a pedido**, al instante.

**Para sumarte:** mándanos los datos de arriba o abre un PR agregando tu entrada
en [`sources.example.json`](sources.example.json) con tu `map` de columnas.
Dudas: **[tu nombre / contacto]**.

## 🔄 Frescura de los datos

El buscador re-lee el estatus **en vivo** de cada fuente en cada corrida, así que
mantenerlo al día es solo cuestión de re-ingerir seguido. El plan es un
**GitHub Action** que ejecute la ingesta cada ~5 min y redepliegue.
**Aún no está activado**: lo encenderemos cuando haya varias plataformas
integradas (antes no aporta).

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
| `connectors.py` | Lectores **Supabase / Google Sheet / CSV / REST** (solo lectura) |
| `match.py` | Cruce: **cédula** = alta; **nombre+edad** = posible (conservador) |
| `aggregate.py` | Unifica apariciones, genera alertas, exporta índice |
| `run.py` | Orquesta todo |
| `web/` | Buscador web estático (nombre · cédula · género · edad) |

## Fuentes reales conectadas

- **desaparecidosvenezuela.com** (`rest`) — API público `/api/personas`, ~20
  desaparecidos. Se respeta el campo `oculto` (no se ingiere lo que la
  plataforma marcó como no público).
- **siviv** (`supabase`, hospitales) — en espera del acceso de lectura.

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

El **estatus** de cada plataforma (texto libre) se normaliza a un set común:
`LOCALIZADO · BUSCADO · HOSPITAL · FALLECIDO`. Regla de "ubicado": 1 fuente →
*"Ubicada según X (verifica)"*; 2+ fuentes coincidentes → **ubicada al 100%**.
