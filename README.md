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

**Para sumarte:** abre un PR agregando tu archivo en `sources.d/` (instrucciones
paso a paso en **Integra tu plataforma**, más abajo), o escríbenos.
Dudas: **Joel Rubio — IG [@joelrubios](https://instagram.com/joelrubios)**.

## 🔄 Frescura de los datos

El buscador re-lee el estatus **en vivo** de cada fuente en cada corrida, así que
mantenerlo al día es solo cuestión de re-ingerir seguido. Hay un GitHub Action
listo en [`.github/workflows/refresco.yml`](.github/workflows/refresco.yml) que
reingiere y redepliega, pero está **desactivado a propósito**: el bloque
`schedule` está comentado. Para encenderlo, descoméntalo cuando haya varias
plataformas integradas (antes no aporta).

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

El lado **hospitales** aún no tiene plataformas integradas: cualquiera puede
sumarse (ver guía de integración).

## Integra tu plataforma (desarrolladores)

Eres programador: no esperas a nadie. Tu plataforma se integra con **un archivo
de config** — no una copia de tu data, solo dice *dónde* leerte y *cómo* se
llaman tus columnas. Lo registras una vez; cuando tu base cambia, nosotros la
releemos en vivo (no editas el archivo por cada actualización).

1. Haz **fork** y clona el repo.
2. Copia la plantilla:
   `cp sources.d/_PLANTILLA.json sources.d/tu-plataforma.json`
3. Llénala según tu `type`:

   **Supabase** (la `anon_key` ya es pública, va en el archivo):
   ```json
   { "id": "tu-plataforma", "type": "supabase", "category": "desaparecido",
     "url": "https://xxxx.supabase.co", "anon_key": "TU_ANON_KEY", "table": "personas",
     "link": "https://tu-plataforma.com/",
     "map": { "nombre": "nombre", "cedula": "cedula", "edad": "edad", "genero": "sexo",
              "ubicacion": "zona", "estatus": "estado", "fecha": "created_at" } }
   ```

   **API REST propio** (un GET que devuelve la lista de personas):
   ```json
   { "id": "tu-plataforma", "type": "rest", "category": "desaparecido",
     "url": "https://tu-plataforma.com/api/personas",
     "link": "https://tu-plataforma.com/", "skip_if": { "oculto": true },
     "map": { "nombre": "nombre", "edad": "edad", "ubicacion": "zona", "estatus": "estado" } }
   ```

   **Google Sheet** (compártela como "cualquiera con el link puede ver"):
   ```json
   { "id": "tu-plataforma", "type": "gsheet", "category": "hospital",
     "sheet_id": "ID_DE_LA_HOJA", "sheet_name": "Hoja1",
     "link": "https://docs.google.com/...",
     "map": { "nombre": "Nombre", "cedula": "Cedula", "ubicacion": "Centro" } }
   ```

   - `category`: `desaparecido`, `hospital` o `localizado`.
   - En `map`, deja en `""` los campos que no tengas (solo `nombre` es imprescindible).
   - `skip_if`: descarta lo que marques como no público (ej. `{"oculto": true}`).
   - Usa en `estatus` la palabra con la que marcas "ubicado" para propagar la buena noticia.

4. Prueba local: `python3 run.py --export web/data.json` — deberías ver tu fuente
   cargada y tus registros en el buscador (`cd web && python3 -m http.server 8777`).
5. Abre un **PR**. Eso es todo.

> Solo pongas credenciales **públicas de solo lectura** (la anon key de Supabase
> ya viaja en tu frontend). Cualquier secreto real va en `sources.json` (local,
> gitignored), nunca en `sources.d/`.

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
