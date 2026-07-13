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

## ═══ SESIÓN 2026-07-13 ═══

### 0. Auditoría de coherencia MEMORIA ↔ PROTOTIPO (documento clave)
- **`docs/auditoria_coherencia.md`**: contraste indicador a indicador de lo comprometido en la
  memoria firmada frente a lo que hace el prototipo. **Leerlo antes de seguir.**
- Veredicto: el núcleo diferencial está hecho (7 inteligencias + IPA/IPCA/DIPA/DIPCA + minería
  de reseñas), pero hay **3 desviaciones conscientes**, **1 desajuste conceptual** y lagunas.
- **Decisiones pendientes de Antonio y Paula (¡importante!):**
  - Memoria dice **Power BI** → usamos **Streamlit**. Hay que **justificarlo por escrito** ante FEDER.
  - Memoria compromete **Azure** con **3.500 € presupuestados** → usamos CSV + Streamlit gratis.
    **Ese dinero está SIN EJECUTAR.** Decidir qué se hace.
  - Memoria dice *"acceso protegido, solo personas autorizadas"* → el dashboard es **público**.
    Contradice literalmente la memoria. Reversible en 2 min.
  - Errata en la memoria (p. 4): menciona **"SIPA"** una sola vez. Decidir si entra o es errata.
  - **Cuestionarios**: son hito de la Fase 1 y muchos indicadores solo se cubren así.
- **`docs/plan_profundizacion.md`**: plan por inteligencia (lo que falta + mejoras propias),
  con reparto sugerido entre Antonio, Paula y Fernando.
- **`docs/protocolo_trabajo.md`**: cómo trabajar los 3 en paralelo (ramas, PR, integración
  semanal). Reparto: **Antonio** = Económica+Mercado · **Paula** = Clientes+Competidores ·
  **Fernando** = Negocios+Tecnológica+Sostenibilidad. (Alfredo no participa.)
  ⚠️ **Tras integrar, hacer Reboot** en Streamlit: cachea los módulos importados y da
  `AttributeError` si tocas algo fuera de `app.py`.

### 1. Competidores REORIENTADO + ACEVIN (corrige el desajuste conceptual)
- La memoria define "competidores" como **otros destinos**, no bodegas del propio Marco.
  Pestaña reescrita: el Marco frente a las demás rutas del vino.
- **`enolytics/ingesta/acevin.py`** — Observatorio Turístico de las Rutas del Vino (PDF oficiales,
  extracción por regex). 4 salidas en `datos/procesado/acevin/`:
  `visitantes_rutas.csv` (2022-24) · `oferta_rutas.csv` (37 rutas) ·
  `ingresos_rutas.csv` (parcial) · `perfil_demanda.csv` (16 indicadores, **NACIONAL**).
- **HALLAZGOS (los genera el dashboard solo, con guardas que impiden afirmar sin dato):**
  1. **El Marco es la ruta nº1 de España en 2024**: 425.652 visitantes (+11,2%), adelantando a
     Rioja Alta (389.399 → 316.922, **−18,6%**).
  2. **Desequilibrio demanda-oferta**: 1º en visitantes pero **7º en oferta** (111 servicios
     frente a los 334 de Ribera del Duero).
  3. **Brecha de monetización**: ingresa **40,4 €/visitante** vs **70,0 €** de Rioja Alta
     (media nacional 37,0 €). Lidera en volumen, monetiza mal.
  4. **Paradoja competitiva**: 1º en visitas reales, pero **no lidera el interés de búsqueda**.
- ⚠️ El informe de demanda de ACEVIN es **nacional, no por ruta**: sirve de *benchmark* y de
  **plantilla validada de cuestionario** (628 encuestas, 95% confianza).

### 2. Objetivos de la memoria + categorías SEGITTUR en cada pestaña
- `config.OBJETIVOS_INTELIGENCIAS`: objetivo literal (memoria p.5), categoría SEGITTUR e
  indicadores previstos (Tabla 1) de las 7. Helper `cabecera_inteligencia()`.

### 3. Etiquetado del ORIGEN de cada indicador (rigor)
- `config.ORIGENES_DATO` + helpers `fuente()` / `leyenda_origenes()`. 13 etiquetas:
  🟢 oficial · 🔵 observado · 🟡 estimado. Obliga a confesar las limitaciones (el gasto es
  **provincial**, no enoturístico; la "importancia" del IPA **se infiere**, no se pregunta;
  la sostenibilidad web mide **comunicación**, no desempeño).

### 4. Accesibilidad universal (mayor laguna de la memoria, estaba a CERO)
- **`enolytics/ingesta/accesibilidad.py`**: 8 comprobaciones WCAG sobre el HTML →
  **índice de accesibilidad digital /8** (que la memoria pide literalmente) + señales de
  accesibilidad física/sensorial. `datos/procesado/accesibilidad.csv`.
- **HALLAZGO: 0 de 38 bodegas mencionan apoyo sensorial** (audioguías, braille, signos).
  Solo 4 mencionan accesibilidad física. Media digital 6,4/8; **un tercio bloquea el zoom**
  (`user-scalable=no`) → barrera grave y de **arreglo trivial**.

### 5. Transporte sostenible (OpenStreetMap)
- **`enolytics/ingesta/transporte.py`**: distancia de cada bodega a estación/parada (Overpass).
  ⚠️ Overpass devuelve **406 con User-Agent de navegador**: exige identificarse.
- **HALLAZGO (contrario a lo esperado): el 88% de las bodegas SÍ es accesible en transporte
  público** (34 a pie), pero el 76% de los enoturistas llega en coche (ACEVIN).
  → *"La infraestructura existe, pero no se usa"*: el cuello de botella es **información y
  hábito**, no inversión.

### 6. ⭐ MOTOR DE RECOMENDACIONES ACCIONABLES (el diferencial de la memoria)
- **`enolytics/analitica/recomendaciones.py`**. La memoria promete que ENOLYTICS *"no solo
  recopila datos, sino que los transforma en recomendaciones accionables"*. Ya lo hace.
- Reglas que cruzan las 7 inteligencias; cada una **solo se dispara si el dato la sostiene** y
  declara su **diagnóstico** (evidencia numérica) y su **fuente**.
- **Destino: 8 recomendaciones (5 de prioridad alta)**, sobre las pestañas.
  **Bodega: nueva pestaña 🎯** en la vista individual.
- **HALLAZGO METODOLÓGICO (muy publicable):** el **IPA clásico se equivoca** con
  «Organización y reserva»: lo clasifica como *«Baja prioridad»* porque se menciona poco (233
  menciones), pero **el visitante solo habla de la reserva cuando falla** → el nº de menciones
  **infravalora sistemáticamente** los atributos que solo afloran al fracasar. Y es **el peor
  valorado del Marco: 3,66/5 frente a una media de 4,4**. Se añadió una regla de *desempeño
  crítico absoluto* que sí lo captura. **Es una crítica fundada al IPA sobre reseñas.**

### 7. Playwright: rescate de las webs que bloquean robots
- **`enolytics/ingesta/navegador.py`**: lector en 2 pasos. `requests` (rápido) y, si topa con un
  muro (verificación de edad, JavaScript, texto mínimo), abre **Chromium real**, acepta el aviso
  y lee la página renderizada. Los 3 auditores lo usan y **registran el método en el CSV**.
- **29 → 38 webs auditadas** (15 rescatadas). **Bodegas Tradición (piloto) pasa de 0 a 5/5 en
  madurez digital y 7/8 en accesibilidad.** González Byass 8/8 accesibilidad.
- ⚠️ **Emilio Hidalgo (la otra piloto) sigue sin datos: NO es un bloqueo, su web no responde.**
  Hará falta **Fernando** (es de Emilio Hidalgo y está en el equipo).
- Corregido: `auditoria_web.py` no tenía bloque `__main__` y no hacía nada al ejecutarse.

### ⚠️ RIESGO ABIERTO: las 2 bodegas piloto son las peor cubiertas
La memoria fija el piloto (Fase 3) en **Emilio Hidalgo y Tradición**. Tradición ya está
resuelta con Playwright; **Emilio Hidalgo sigue sin web accesible y sin GPS**. Recoger sus
datos con Fernando (FMH) y Águeda (ACM), que están en el equipo de trabajo.

### PRÓXIMOS PASOS sugeridos (ver `docs/plan_profundizacion.md`)
1. **Índice de Competitividad Enoturística (ICE)** — la memoria menciona *"índices de
   competitividad que comparan destinos"*. Salida académica.
2. **Estacionalidad** — alineado con FEDER **P4A** ("reducir la estacionalidad") y **no se mide**.
   Datos ya disponibles (fechas de 10.972 reseñas + Trends semanal).
3. **NLP prometido**: modelado de temas (LDA/BERT) y **sentimiento con modelo real** (hoy se
   deriva de las estrellas) + multilingüe (1/3 de reseñas no están en español).
4. **Accesibilidad física real** (Google Maps) y **precios entre rutas** (Civitatis/GetYourGuide).
5. **Redactar los hallazgos** para JCR (hay material de sobra: la crítica al IPA, la paradoja
   competitiva, la brecha de monetización, el vacío de accesibilidad sensorial).
6. ⭐ **AFLUENCIA + DESPLAZAMIENTOS** (pedido expreso de Antonio, 13/07). **Son dos cosas
   distintas y no hay que confundirlas** (ni con el transporte sostenible, que ya está hecho):
   - **(a) AFLUENCIA — Google Places.** *Cuánta gente hay* en cada bodega: curvas de ocupación
     por hora y día de la semana (*"popular times"*), estacionalidad y detección de saturación.
     Proxy de visitantes **sin sensores**. Vías: Outscraper (campo `popular_times`) o la
     librería `populartimes`. ⚠️ No es un dato de la API oficial de Places: validar cobertura y
     términos de uso. → Alimenta **Clientes** y **Negocios**, y da la **estacionalidad** que
     exige FEDER P4A. Encaja con el hallazgo "1º en visitantes, 7º en oferta" (¿saturación?).
   - **(b) DESPLAZAMIENTOS Y PROCEDENCIA.** *De dónde viene* y *cómo se mueve* el visitante:
     · **Dataestur / INE — estudios de movilidad** (telefonía móvil): flujos entre provincias.
     · **Idioma de las reseñas** → nacional vs. internacional, y cruzarlo con el IPA
       (indicador ya previsto: *IPA/IPCA por procedencia*).
     · **Google Trends por región/país** (ya tenemos el origen por CCAA; ampliar a internacional).
     → Alimenta **Clientes** (perfil) y **Mercado** (procedencia).
   - **(c) ⭐ IDIOMA DE LAS RESEÑAS → procedencia.** *La más barata de las tres: los datos ya los
     tenemos.* Detectar el idioma de las 10.972 reseñas (`langdetect`) → columna `idioma` y
     segmento **nacional vs. internacional**. Permite el **IPA/IPCA por procedencia** (¿valora
     lo mismo el turista internacional que el nacional?) y mide el peso del visitante extranjero
     por bodega. **Además corrige un sesgo actual**: el léxico de atributos es solo español, así
     que ~1/3 de las reseñas se analizan mal → **el IPA de hoy está sesgado hacia el nacional**.
     ⚠️ El idioma es un *proxy* de la procedencia, no la procedencia real → etiquetar 🟡 estimado.
   - Recordatorio de lo que **NO** es: el módulo `transporte.py` (OpenStreetMap) mide si *se
     puede llegar* sin coche, no cuánta gente hay ni de dónde viene.
   - **Estado: las tres (a, b, c) quedan PENDIENTES por decisión de Antonio (13/07).**

---

### Inteligencia de Sostenibilidad: auditoría web (2026-07-09)
- Módulo `enolytics/ingesta/sostenibilidad.py`: `auditar_bodega(url)` / `auditar_todas()`.
  Consolida catálogo + FEV (leído del CSV previo) + **auditoría web por 7 ejes**
  (ecológico, clima, energía, agua, residuos, biodiversidad, general). Sigue home + hasta
  2 subpáginas de sostenibilidad (enlaces con "sosteni/compromiso/medioambiente/ecolog...").
- `datos/procesado/sostenibilidad.csv` reescrito con columnas nuevas: `eje_*`,
  `menciona_ecologico`, `web_ok`, `indice_sostenibilidad` (0-7), además de FEV.
- **Resultado:** 42 bodegas · FEV 4 · **10 comunican ecológico** · destacada **Miguel Domecq
  (Entrechuelos) 7/7**. ~12 con web:0 (bloquean bot o sin web accesible → falsos negativos,
  ej. González Byass, Tradición). Es un proxy de *comunicación*, no certificación.
- **CAAE descartado como fuente automática:** su buscador (certificados.caae.es, Angular →
  API AWS `wz7mdd1v1k.execute-api.eu-west-3.amazonaws.com/caae/caae-listado-operadores`,
  auth Basic pública en el bundle + cabeceras Origin/Referer) solo devuelve 792 operadores
  **internacionales** (Perú 567, España 115...), no el registro andaluz. Por criaderas/solera,
  los vinos de Jerez tradicionales no pueden certificar "vino ecológico".
- Dashboard (📈 pestaña 🌱 Sostenibilidad): métricas FEV + ecológico + índice medio;
  barras de adopción por eje; ranking top-10; distintivos en ficha de bodega (FEV + ecológico).
  Loader `cargar_sostenibilidad` sin cambios (lee el CSV). Verificado con AppTest (sin excepciones).

### Inteligencia de Mercado: Google Trends (2026-07-09)
- Módulo `enolytics/ingesta/google_trends.py` (pytrends, en requirements-dev). Descarga:
  `interes_temporal.csv` (interés semanal 5 años, remuestreado a mes en el dashboard) e
  `interes_regiones.csv` (interés por CCAA del término foco). En `datos/procesado/google_trends/`.
- Términos comparativos en `config.TERMINOS_TRENDS`: **"bodegas Jerez"** vs Rioja / Ribera del
  Duero / Rías Baixas (proxy de intención de visita; "enoturismo X" salía casi a 0 por bajo volumen).
- **Hallazgo:** Jerez **2º de 4** en interés de búsqueda (media 37; líder Rioja 56; Ribera 16;
  Rías Baixas ~0). Tendencia **−15%** (primeros 2 años vs últimos 2). Demanda concentrada en
  Andalucía (100), Ceuta, Extremadura, La Rioja.
- Dashboard (pestaña 📈 Mercado): 3 métricas (posición, interés medio, tendencia) + evolución
  suavizada (media móvil 6 meses) + barras de origen por CCAA. Loaders `cargar_trends_temporal/regiones`.
- Notas técnicas: pytrends con urllib3>=2 falla si se le pasan `retries` (arg `method_whitelist`
  eliminado) → cliente sin reintentos internos; Google limita con 429, se resuelve con backoff
  propio (20s, 40s...). Verificado con `streamlit.testing` (AppTest): app sin excepciones, 7 pestañas.

### Despliegue permanente ✅ PUBLICADO (2026-07-09)
- **El dashboard está EN LÍNEA 24/7:** 👉 **https://enolytics-feder-uca.streamlit.app**
  (Streamlit Community Cloud, gratis). El equipo lo ve con el Mac apagado.
- **Repositorio GitHub:** `Antonio-Ramos-UCA/enolytics` → https://github.com/Antonio-Ramos-UCA/enolytics
  **PÚBLICO** (se decidió hacerlo público para evitar la fricción del OAuth de repos privados
  en Streamlit; no hay secretos: `.env`/corpus xlsx están en `.gitignore`, las reseñas son
  públicas de Google). Cuenta usada: `Antonio-Ramos-UCA`.
- **Requisitos:** `requirements.txt` ligero (streamlit, pandas, plotly) para el deploy; el
  completo está en `requirements-dev.txt`. Fichero principal: `enolytics/dashboard/app.py`,
  rama `main`.
- **CÓMO ACTUALIZAR la app publicada:** basta con `git push` a `main` → Streamlit Cloud
  **redespliega solo** en 1-2 min. (Push con token: ver nota abajo.)
  - Push seguro sin guardar el token en `.git/config`:
    `git push "https://x-access-token:TOKEN@github.com/Antonio-Ramos-UCA/enolytics.git" main:main`
    (config `http.postBuffer 524288000` ya puesta para el repo de 6 MB).
- **Token GitHub (PAT classic, scope `repo`):** lo crea el usuario en
  github.com/settings/tokens. Es como una contraseña; se puede revocar ahí al terminar.
- Pendiente opcional: restringir QUIÉN ve la app (por correo) desde el panel de Streamlit
  (Settings → Sharing) si se quiere privacidad de visualización.

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
