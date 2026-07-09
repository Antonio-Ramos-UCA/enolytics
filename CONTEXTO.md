# ENOLYTICS — Contexto del proyecto (documento para retomar)

> **Para qué sirve este archivo:** resume todo lo decidido y hecho hasta ahora para
> poder continuar desde cualquier ordenador (este proyecto está en Dropbox y se
> sincroniza). Si retomas con Claude en otro equipo, pásale este archivo primero.
>
> **Última actualización:** 2026-07-01

---

## 1. Qué es el proyecto

**ENOLYTICS** — plataforma digital de **inteligencia competitiva integrada para la
gestión enoturística del Marco de Jerez**. Proyecto de investigación de la
Universidad de Cádiz (financiación FEDER Andalucía 2021-2027).

- **Entregable:** un cuadro de mando interactivo (dashboard) que transforma datos
  —reseñas online, indicadores económicos/sociales/sostenibilidad— en inteligencia
  procesable.
- **Técnicas:** minería de textos, análisis de sentimiento, modelado de temas
  (LDA/BERT) y análisis importancia-desempeño **IPA / IPCA / DIPA / DIPCA** (el
  diferencial científico frente a Shin & Nicolau 2022 y Wu et al. 2024).
- **Memoria científico-técnica:** en `MEMORIA/` (firmada 14/02/2025). Presupuesto
  total 39.628 €, plazo 24 meses.

### Equipo
- **Antonio Rafael Ramos Rodríguez (ARRR)** — Co-IP, líder técnico *(usuario)*.
- **María Paula Lechuga Sancho (MPLS)** — IP.
- **Alfredo Sánchez-Roselly Navarro (ASR)** — informática/infraestructura.
- **Fernando Martín-Hidalgo (FMH)** — Bodegas Emilio Hidalgo.
- **José Luis Baños Ramírez (JLBR)** — Ruta del Vino y Brandy de Jerez.
- **Águeda Caputto Mateos (ACM)** — Bodegas Tradición.
- Bodegas piloto según memoria: **Emilio Hidalgo** y **Tradición**.

### Las 7 inteligencias competitivas (modelo del proyecto)
económica · mercado · competidores · clientes · negocios · tecnológica ·
**sostenibilidad** (esta última es la aportación novedosa). Se mapean a 3 categorías
SEGITTUR: Oferta / Demanda / Sostenibilidad. Alineado con norma UNE 178502.

---

## 2. Decisiones tomadas (importantes)

| Tema | Decisión | Nota |
|------|----------|------|
| **Plataforma** | **Python + Streamlit** (NO Power BI) | ⚠️ Se desvía de la memoria firmada, que decía Power BI + Azure. Desviación consciente: reproducibilidad (RODIN, publicaciones JCR), sin licencias, todo el pipeline en un lenguaje. Justificable ante el organismo si hace falta. |
| **Alcance 1er entregable** | **Marco de Jerez completo** (todas las bodegas, 7 inteligencias) | Construcción por capas: arquitectura para el total, pero funcional desde pocas bodegas. |
| **Audiencia** | **Ambos con vistas por rol**: bodega individual + gestor de destino/OGD | Ya reflejado en el dashboard. |
| **Reseñas** | **Enfoque híbrido** (decidido 2026-07-01) | Scraper propio para fuentes estables (catálogo, webs, RRSS); **API de terceros (Outscraper) para reseñas de Google/TripAdvisor**. Cubierto por los 4.000 € del presupuesto. Interfaz agnóstica (se puede cambiar a SerpAPI/Apify). **Acción pendiente del usuario: crear cuenta Outscraper y aportar OUTSCRAPER_API_KEY.** |
| **Idioma del código** | Módulos y variables **en español** | Coherente con el dominio. |

---

## 3. Estado de las fuentes de datos

1. **Reseñas online:** NO descargadas aún. **Prueba de viabilidad hecha (2026-07-01):**
   con `requests` no se accede (Google exige JavaScript; TripAdvisor devuelve 403);
   Playwright (navegador real) funciona pero es frágil y confunde bodegas. Decisión:
   **API de terceros (Outscraper)** para las reseñas. Falta que el usuario cree la
   cuenta y aporte la API key (variable de entorno `OUTSCRAPER_API_KEY`).
2. **Cuestionarios (a bodegas/visitantes/OGDs):** NO diseñados. No bloquean el
   arranque; se diseñarán derivándolos de los indicadores de la Tabla 1 de la memoria.
3. **Catálogo de bodegas:** ✅ HECHO — 41 bodegas de la Ruta del Vino y Brandy de
   Jerez (ver sección 4).

---

## 4. Lo que YA está hecho

### Catálogo de bodegas (✅ completo)
- **41 bodegas** inscritas en la Ruta del Vino y Brandy de Jerez, extraídas de
  <https://rutadelvinojerez.es/empresas-y-servicios/categoria/bodegas/>.
- Ficheros en `datos/catalogo/`:
  - `catalogo_bodegas_rutadelvinojerez.csv` — listado base.
  - `bodegas_enriquecido.csv` / `bodegas_enriquecido.json` — **catálogo completo**.
- **Campos por bodega:** nombre, localidad, dirección, teléfono, email, web,
  gps_lat, gps_lon, rrss (perfiles oficiales), servicios enoturísticos, url_ficha,
  descripción completa.
- **Cobertura (/41):** dirección 41, teléfono 41, GPS 41, servicios 41, web 40
  (falta El Piraña), RRSS 37, email 13 (la mayoría de fichas no lo publican).
- **Distribución:** Jerez 20, Sanlúcar 10, Trebujena 3, El Puerto 3, Chiclana 2,
  Lebrija 1, Rota 1, mixta 1.
- ⚠️ **Ojo:** **Bodegas Tradición SÍ está**; **Bodegas Emilio Hidalgo NO aparece**
  (no está inscrita en la Ruta) pese a ser bodega piloto → habrá que añadirla a mano.
- **Nota técnica:** la web randomiza el orden de las tarjetas y su paginación
  `/page/N/` no es estable → el scraper hace varias pasadas acumulando hasta
  estabilizar (41 tras ~4 pasadas).

### Estructura del proyecto (✅ montada y verificada)
Ver sección 5. Todo compila e importa correctamente.

---

## 5. Estructura del código

```
PROTOTIPO ENOLYTICS/
├── CONTEXTO.md              ← este archivo
├── README.md
├── requirements.txt
├── .gitignore
├── enolytics/               # paquete principal
│   ├── config.py            # rutas, constantes, las 7 inteligencias, fuentes
│   ├── ingesta/
│   │   ├── ruta_jerez.py    # scraper del catálogo (funciones reutilizables)
│   │   └── resenas.py       # interfaz común descargar_resenas() + dataclass Resena (STUB)
│   ├── etl/                 # (stub, pendiente)
│   ├── nlp/                 # (stub, pendiente)
│   ├── analitica/
│   │   └── ipa.py           # IPA funcional; IPCA/DIPA/DIPCA stubs
│   └── dashboard/
│       └── app.py           # Streamlit funcional (mapa + fichas + vistas por rol)
├── datos/
│   ├── catalogo/            # CSV + JSON del catálogo (versionable)
│   ├── crudo/resenas/       # reseñas descargadas (NO versionado)
│   └── procesado/           # datasets derivados
├── scripts/
│   └── actualizar_catalogo.py
├── tests/
└── MEMORIA/                 # memoria científico-técnica (PDF)
```

Funciones clave de `enolytics/ingesta/ruta_jerez.py`:
`descargar_catalogo()`, `enriquecer_bodegas()`, `guardar_catalogo()`,
`actualizar_catalogo_completo()`, `cargar_catalogo()`.

---

## 6. Cómo poner en marcha (en un ordenador nuevo)

```bash
cd "PROTOTIPO ENOLYTICS"

# 1. Instalar dependencias
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium     # solo cuando toque el scraper de reseñas

# 2. (opcional) regenerar el catálogo de bodegas
python3 scripts/actualizar_catalogo.py

# 3. Lanzar el dashboard
python3 -m streamlit run enolytics/dashboard/app.py
```

**Entorno de referencia:** Python 3.10. Ya instalados en el equipo original:
streamlit, pandas, sklearn, plotly, matplotlib, requests, bs4.
**Faltan por instalar:** playwright, transformers (están en requirements.txt).

---

## 7. Próximos pasos (por orden sugerido)

1. **Localizar las bodegas en Google Maps / TripAdvisor** — usando GPS + nombre,
   encontrar la ficha de cada bodega en esas plataformas (paso previo a las reseñas).
2. **Implementar el scraper de reseñas** — decidir antes: scraper propio (Playwright)
   vs API de terceros. Implementar los backends de `enolytics/ingesta/resenas.py`.
3. **NLP** — análisis de sentimiento (BERT español) y modelado de temas (LDA) sobre
   las reseñas → extraer atributos con medidas de importancia y desempeño.
4. **Completar IPCA / DIPA / DIPCA** en `enolytics/analitica/ipa.py`.
5. **Integrar todo en el dashboard** (pestañas de reseñas, sentimiento, cuadrantes IPA).
6. **En paralelo (no bloquea):** diseñar cuestionarios a partir de la Tabla 1 de la
   memoria; incorporar indicadores oficiales (INE, Dataestur, ACEVIN, Google Trends).

### Despliegue permanente (EN CURSO — retomar aquí) (2026-07-07)
- Objetivo: que el equipo vea el dashboard **con el Mac apagado** → publicar en
  **Streamlit Community Cloud** (gratis), **privado/restringido al equipo**.
- **Hecho:** `requirements.txt` ligero (streamlit, pandas, plotly) para el deploy; el
  completo está en `requirements-dev.txt`. **Repo git inicializado** en la carpeta del
  proyecto, rama `main`, primer commit hecho (~36 archivos, 6 MB; corpus xlsx excluido por
  .gitignore). `credential.helper=osxkeychain` configurado.
- **BLOQUEADO en la autenticación de GitHub:** la credencial guardada (usuario
  `antoniorramosenolytics`, token `ghp_...`) está **CADUCADA (401 Bad credentials)**, y el
  login web estaba **temporalmente bloqueado** ("varios intentos fallidos"). El usuario
  tiene además otra cuenta posible: `Antonio-Ramos-UCA`.
- **PRÓXIMO al retomar:** el usuario entra en GitHub (cuando se levante el bloqueo), crea un
  **Personal Access Token classic** (scope `repo`, github.com/settings/tokens) y lo pasa →
  con él: crear repo privado `enolytics` (API o web), `git remote add origin` + `git push -u
  origin main`, luego conectar Streamlit Cloud (share.streamlit.io → New app → repo, rama
  main, fichero `enolytics/dashboard/app.py`) y restringir vista a correos del equipo.
- Alternativa si falla el PAT: **GitHub Desktop** (OAuth in-app) → Add Local Repository →
  Publish (privado).
- Mientras tanto el enlace temporal Cloudflare sigue sirviendo (con el Mac encendido).

### Dashboard: 7 pestañas = 7 inteligencias (2026-07-07)
- Vista Gestor reorganizada: cabecera de métricas + **7 pestañas, una por inteligencia**
  (💶 Económica · 📈 Mercado · 🥊 Competidores · 😊 Clientes · 🏛️ Negocios · 🖥️ Tecnológica ·
  🌱 Sostenibilidad), en el orden de la memoria. Cada una indica fuente y pendientes.
- Reparto: Económica=gasto Dataestur; Mercado=procedencia gasto + percepción; Competidores=
  censo/reputación; Clientes=IPA+DIPA; Negocios=oferta 167 + mapa + directorio;
  Tecnológica=auditoría web; Sostenibilidad=certificaciones. (IPCA/DIPCA por bodega siguen
  en la vista Bodega individual.)

### Inteligencia Tecnológica: auditoría web (2026-07-07)
- Módulo `enolytics/ingesta/auditoria_web.py`: `auditar_bodega(url)`, `auditar_todas()`.
  Detecta HTTPS, viewport móvil, inglés (hreflang), reserva online (keywords/plataformas),
  tecnología inmersiva (360/virtual) → índice `madurez_digital` /5.
- `datos/procesado/auditoria_web.csv`: 29/42 webs auditadas (madurez media 3,5/5; móvil 100%,
  HTTPS 83%, reserva 66%, inglés 52%, inmersiva 52%). **13 no auditables** (sin web o bloqueo
  anti-bot/verificación de edad — falsos negativos, ej. González Byass, Tradición). Se excluyen.
- Dashboard: nueva pestaña Gestor **🖥️ Tecnológica** (métricas + adopción + ranking + aviso).
- **LAS 7 INTELIGENCIAS ya están representadas en el dashboard** (con datos públicos, sin encuestas).

### Inteligencia en Sostenibilidad: certificaciones (2026-07-07)
- Cruzado el catálogo con el listado oficial FEV **Sustainable Wineries for Climate
  Protection** (134 bodegas en España). Matching estricto (todas las palabras distintivas
  del sello en el nombre de la bodega, para evitar falsos positivos tipo Barón≠Barón de Ley).
- **4 bodegas del Marco certificadas:** Barbadillo, González Byass, Lustau, Osborne (10%).
  En `datos/procesado/sostenibilidad.csv`.
- Dashboard: nueva pestaña Gestor **🌱 Sostenibilidad** (nº/% + listado) y distintivo verde
  en la Ficha de bodega. Loader `cargar_sostenibilidad()`.
- Pendiente: CAAE ecológico, consumos (estimados por sector), transporte sostenible.

### Inteligencia de Negocios: oferta enoturística (2026-07-07)
- Scraper generalizado: `ruta_jerez.descargar_catalogo(categoria)` +
  `descargar_oferta_completa()` recorren las 11 categorías de la Ruta. Config:
  `CATEGORIAS_RUTA`, `RUTA_JEREZ_CATEGORIA_BASE`.
- **167 recursos** en `datos/procesado/oferta_enoturistica.csv` (bodegas 41, restaurantes 27,
  recursos culturales 27, naturales 20, actividades 19, alojamientos 14, museos 7,
  turismo accesible 6, enotecas 3, caterings 2, agencias 1).
- Integrado en dashboard (Gestor → Visión general): sección "Oferta enoturística" con
  total, nº categorías y barras por categoría. Loader `cargar_oferta()`.

### Dashboard reorganizado en pestañas (2026-07-07)
- Vista **Gestor**: 3 pestañas (📊 Visión general · 😊 Clientes y experiencia · 💶 Económica
  y mercado). Vista **Bodega**: 2 pestañas (🏭 Ficha · 😊 Reseñas y análisis). Estructura
  lista para añadir pestañas por inteligencia.
- **Backlog completo del proyecto en `docs/pendientes.md`** (fuentes, NLP, 7 inteligencias,
  dashboard, cuestionarios, salidas académicas). Consultarlo al retomar.

### Integración de Dataestur (API oficial) (2026-07-07)
- **API de Dataestur (SEGITTUR) es ABIERTA (sin clave)** y gratuita. Base:
  `https://www.dataestur.es/API-SEGITTUR-v2`. 124 conjuntos oficiales (INE, AEAT, SS,
  Banco de España, SEPE). Spec: `.../mini-mandrake/apidata/openapi.json`. Devuelve CSV
  (sep `;`, decimal `,`, encoding cp1252). Filtro por año/mes y territorio (client-side).
- Módulo **`enolytics/ingesta/dataestur.py`**: `consultar(endpoint, provincia, desde_anio,
  hasta_anio)` → DataFrame; `guardar()`. Catálogo `CONJUNTOS_RELEVANTES`.
- Datos ya descargados en `datos/procesado/dataestur/`:
  - Gasto con tarjeta en **Cádiz** (2024-26, mensual, por origen). Ej.: 342,8 M€ total
    nacional 2024, 91,2 M€ internacional.
  - **Satisfacción/percepción del visitante en Andalucía** (índices: percepción global
    81, productos 66, seguridad 96, clima 96).
- Endpoints útiles: GASTO_TPV_*, IND_SATISFACCION_PERCEPCION_DL, DIRCE_EMPRESAS_TURISMO_DL,
  FRONTUR_DL, EGATUR_DL, TURISMO_RECEPTOR_PROV_PAIS_DL, IPC_CCAA_DL, MUSEO_DL.
  (AFILIACION_TURISMO_DL falló al decodificar — revisar formato.)
- **Integrado en el dashboard (vista Gestor):** sección "💶 Inteligencia Económica y de
  Mercado — Cádiz" con gasto turístico (métricas + evolución mensual + por procedencia) e
  índices de percepción del visitante. Loaders `cargar_gasto_cadiz()`,
  `cargar_satisfaccion_cadiz()` en app.py.
- **Próximo:** más conjuntos Dataestur (empleo, empresas turísticas DIRCE, procedencia
  FRONTUR/EGATUR); confirmar acceso a SABI; organizar el dashboard en pestañas por
  inteligencia. Ver `docs/fuentes_publicas.md` y `docs/plan_7_inteligencias.md`.

### Compartir el dashboard (2026-07-07)
- El dashboard se comparte con el equipo mediante **túnel temporal de Cloudflare**
  (`cloudflared`, binario en el scratchpad de la sesión, sin cuenta). Enlace de esta
  sesión: https://ceiling-corps-provide-batteries.trycloudflare.com
- **TEMPORAL:** solo funciona mientras el Mac esté encendido y corran a la vez el
  dashboard (`streamlit run ...`, puerto 8501) y el túnel. Al reiniciar cambia la URL.
- Para un enlace **permanente** (sin depender del equipo del usuario): pendiente
  publicar en **Streamlit Community Cloud** (gratis, requiere GitHub; se puede
  restringir a los correos del equipo). Ojo al desplegar: crear un `requirements.txt`
  ligero (streamlit, pandas, plotly, openpyxl) — NO subir torch/transformers/playwright.
- Cómo relanzar el túnel: tener el dashboard vivo y ejecutar
  `cloudflared tunnel --url http://localhost:8501` (el binario está en el scratchpad;
  si se borró, se descarga de github.com/cloudflare/cloudflared/releases).

### DIPCA — familia de modelos completa (2026-07-07)
- `enolytics/analitica/ipa.py`: `calcular_dipca(brecha_inicial, brecha_final)` →
  evolución de la brecha competitiva (Gana/Pierde terreno/Estable). **Los 4 modelos
  IPA/IPCA/DIPA/DIPCA de la memoria están implementados y en el dashboard.**
- Dashboard (vista Bodega): sección DIPCA (tabla brecha antes/después + tendencia),
  solo para bodegas con ≥60 reseñas datadas; parte por la mediana de fecha. Helper
  `dipca_bodega()` en app.py.
- Ejemplo: Tío Pepe pierde terreno vs el Marco con el tiempo (brecha Organización
  −0,55 → −1,25), aunque gana en Personal.
- Siguientes mejoras posibles (no imprescindibles): BERT multilingüe, LDA, TripAdvisor,
  otras inteligencias/cuestionarios, automatización incremental por API.

### DIPA temporal (2026-07-07)
- `enolytics/nlp/analisis.py`: `evolucion_atributos(an, freq='Y', min_menciones)` →
  desempeño/menciones por año y atributo (2016-2026). `enolytics/analitica/ipa.py`:
  `calcular_dipa(perf_ini, perf_fin)` → variación + tendencia (Mejora/Estable/Empeora).
- Dashboard (vista Gestor): sección "Evolución temporal (DIPA)" con gráfico de líneas
  por atributo + tabla de tendencias. Helpers `cargar_evolucion()`, `resumen_dipa()`.
- **Hallazgo:** "Organización y reserva" EMPEORA (3,87→3,55 de 2018-20 a 2024-26);
  el resto estable o mejora. Refuerza que la logística de la visita es el problema.
- **Los 4 modelos IPA/IPCA/DIPA de la memoria ya funcionan.** Falta DIPCA (dinámico+
  competitivo) y mejoras NLP (BERT multilingüe, LDA).

### IPCA competitivo por bodega (2026-07-07)
- `enolytics/analitica/ipa.py`: implementado **`calcular_ipca()`** (Albayrak 2015):
  compara desempeño de una bodega vs. media del resto del Marco; brecha + 4 cuadrantes
  (Actuar/Fortaleza/Ventaja menor/Debilidad menor). `PuntoIPCA`, `clasificar_cuadrante_ipca`.
- Dashboard (vista Bodega): sección IPCA con gráfico (importancia vs brecha) y tabla
  (bodega vs media Marco). Helpers `ipca_desde_anotadas()`, `figura_ipca()` en app.py.
- Ejemplos reales: Tradición casi todo +brecha (fortalezas); González Byass/Tío Pepe
  todo −brecha (por detrás del Marco). Modelos IPA que faltan: DIPA/DIPCA (temporal).

### IPA por bodega (2026-07-07)
- Dashboard (vista Bodega) ahora muestra, por bodega: reseñas con texto, gráfico de
  sentimiento, **su propio gráfico de cuadrantes IPA**, y desplegable de reseñas con
  atributos detectados. Helpers en `app.py`: `cargar_resenas_anotadas()` (cache),
  `ipa_desde_anotadas()`, `figura_ipa()`. Guard: IPA por bodega solo si ≥3 atributos.
- Contrastes reales: Tradición 4,78-5,00 (boutique) vs González Byass/Tío Pepe 3,8-3,97
  (volumen alto, notas más bajas). Finca La Pintora solo 6 reseñas → avisa de muestra escasa.

### CORPUS COMPLETO descargado y analizado (2026-07-07)
- **10.972 reseñas** reales de Google (41 bodegas, 7.258 con texto), 2011→2026. En
  `datos/crudo/resenas/corpus_google_completo.xlsx`; normalizado a `datos/procesado/resenas.csv`.
- Coste real de la descarga: ~36 $ (dentro del saldo de 40 $).
- **NLP+IPA sobre el corpus:** 90,2 % sentimiento positivo. Importancia/desempeño:
  Visita 4,61 · Instalaciones 4,57 · Vino 4,58 · Personal 4,67 · Precio 4,03 ·
  **Organización/reserva 3,66 (punto débil claro)** · Entorno 4,74.
- **Insight clave:** la logística de la visita (reservas, esperas) es el talón de
  Aquiles del Marco; coherente con Meneses et al. citado en la memoria.
- Dashboard actualizado con el corpus real (censo + cuadrantes IPA en vivo).
- Pendiente de afinar: léxico ES vs reseñas multilingües → BERT multilingüe mejorará.

### Limpieza previa al corpus completo (2026-07-07)
- **Emilio Hidalgo añadida al catálogo** (bodega piloto que faltaba; ahora 42 bodegas).
  Identidad Google confirmada ("Emilio Hidalgo", nota 4,7). Datos de ficha por completar.
- **AC Wines excluida** de la descarga automática: sin listado propio claro en Google
  (se confundía con Barón / "Alucinante wine"). Marcada en catálogo con `nota_datos`. Revisar a mano.
- **Descarga del corpus por place_id** (más fiable que por nombre): fichero
  `datos/crudo/resenas/consultas_corpus_completo.txt` = 40 place_ids + Emilio Hidalgo por
  nombre. Mapa `datos/procesado/mapa_placeid_bodega.csv` (place_id → bodega) para reconstruir.
- Normalizador ETL actualizado: mapea la bodega por place_id (si la consulta fue un
  place_id) o por texto. Estimación corpus: ~10.900 reseñas ≈ 33 $.
- **LANZADO (2026-07-07):** cargados 40 $ y confirmada la descarga del corpus completo
  en Outscraper (41 consultas, ~12.300 reseñas estimadas, ~36 $, tarda 2-10 h). Corre en
  segundo plano; el resultado quedará en la pestaña "Tareas" (disponible 30 días).
- **PRÓXIMO al retomar:** el usuario descarga el XLSX del corpus desde Tareas → yo lo
  normalizo (`etl.procesar_y_guardar`) → reejecuto NLP+IPA sobre las ~12k reseñas →
  actualizo dashboard + añado IPA por bodega. Tras ello: rellenar place_id de Emilio
  Hidalgo en el mapa, y resolver AC Wines a mano.

### NLP + IPA end-to-end (prueba de concepto) (2026-07-07)
- **Módulo NLP** `enolytics/nlp/analisis.py`: sentimiento por estrellas + extracción de
  atributos por léxico (aspect-based). 7 atributos: Vino y cata, Personal y trato,
  Visita y experiencia, Instalaciones, Precio y valor, Entorno y viñedo, Organización.
  `anotar_resenas()`, `tabla_importancia_desempeno()` (importancia=nº menciones,
  desempeño=nota media).
- **Pipeline completo funcionando**: reseñas → atributos → importancia/desempeño →
  `ipa.calcular_ipa()` → cuadrantes. Integrado en el dashboard (vista Gestor) con
  **gráfico de cuadrantes IPA** (plotly scatter con líneas de umbral).
- Resultado POC (154 reseñas con texto): fortalezas = Vino/Visita/Instalaciones
  (nota 4,6-4,75); señales de mejora = Precio y Organización (nota 4,0). Válido como
  demostración del método, NO como conclusión (muestra pequeña, sesgo positivo, léxico ES).
- Con corpus completo + BERT multilingüe se afinará; la forma del pipeline es la misma.

### Pipeline de reseñas + dashboard integrado (2026-07-07)
- **Normalizador ETL** `enolytics/etl/resenas.py`: convierte el export de Outscraper
  en dataset limpio (`datos/procesado/resenas.csv`, 197 reseñas de muestra) + censo
  (`datos/procesado/censo_google.csv`). Vincula cada reseña con la bodega del catálogo
  por la consulta. Funciones: `procesar_y_guardar()`, `cargar_resenas()`, `cargar_censo()`.
- **Dashboard ampliado** (`enolytics/dashboard/app.py`): vista Gestor con métrica de
  reseñas totales, mapa, censo (gráficos nº reseñas y nota) y tabla; vista Bodega con
  nota/total/muestra y listado de reseñas con estrellas y texto. Validado con el usuario.
- Reseñas son **multilingües** (ES, EN, DE, IT…) → el NLP necesitará modelo multilingüe.
- Decisión del usuario: **seguir gratis con la muestra**, avanzar en NLP/dashboard como
  prueba de concepto; bajar el corpus completo (~35 $) más adelante.
- **Próximo paso:** montar NLP (sentimiento + temas/atributos) sobre la muestra con
  sklearn (ya instalado, sin coste), como base de los futuros IPA. transformers/torch
  aún NO instalados (para BERT cuando toque el corpus completo).

### Censo de reseñas de Google hecho (2026-07-07)
- Vía **panel web de Outscraper (plan gratuito, 0 €)**, servicio "Google Maps Reviews",
  límite 5 reseñas/bodega. Las 41 bodegas resueltas.
- **11.084 reseñas** totales en Google, nota media ponderada **4,56**. Censo en
  `datos/procesado/censo_google.csv`. Muestra en `datos/crudo/resenas/censo_google_41bodegas.xlsx`.
- Export de Outscraper trae 32 columnas (nombre, place_id, rating, reviews total,
  y por reseña: texto, autor, puntuación, fecha, respuesta del propietario, likes…).
- **Hallazgo clave:** descargar TODAS las reseñas de Google costaría ≈ **33 $**
  (Google Maps Reviews a ~$3/1000). Trivial frente a los 4.000 €. → merece la pena
  bajar el corpus completo, no solo muestras.
- **A corregir:** (1) "Bodegas AC Wines & Spirits" se confundió con Bodegas Barón
  (mismo place_id) → afinar su consulta; (2) Viñedos El Piraña tiene 0 reseñas.
- Método de consulta que funciona: texto "Nombre, Localidad, España", uno por línea
  (fichero `datos/crudo/resenas/consultas_41_bodegas.txt`). Subir CSV es premium 👑.
- Nota: la **API** de Outscraper exige saldo (mín. 10 $); el **panel web** es gratis
  hasta 500 registros. Para el corpus completo habrá que añadir crédito.

### Dónde nos quedamos (2026-07-01, fin de sesión)
- **Cuenta de Outscraper creada** (plan gratuito, sin tarjeta, saldo $0.00).
- **Pendiente:** al ir a "API & integraciones" para generar el token, aparece el
  aviso *"Activar acceso a API — Añade créditos a tu cuenta para usar la API"*. Falta
  comprobar si el token se genera sin meter saldo (haciendo clic en el recuadro
  "Haga clic para generar token de API").
- **Plan A:** si el token funciona sin pagar → pasar `OUTSCRAPER_API_KEY` y montar la
  descarga por API.
- **Plan B (si la API exige saldo):** usar el **panel web gratis** (Servicios →
  Google Maps Reviews) con los 500 registros gratis, ejecutar las 41 bodegas,
  **descargar CSV/Excel** y cargarlo en el pipeline (mismo resultado, 0 €).
- Retomar por aquí en la próxima sesión.

### Decisiones abiertas pendientes
- ¿Alcance = solo las 41 bodegas de la Ruta, o ampliar a todo el universo de bodegas
  del Marco (Consejo Regulador, Google Maps)?
- Scraper de reseñas: ¿propio o API de terceros?
- ¿Añadir Bodegas Emilio Hidalgo (piloto) al catálogo manualmente?
