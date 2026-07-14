# ENOLYTICS — Tareas pendientes (backlog)

> Lista viva de todo lo que queda por hacer, para no perder el hilo entre sesiones.
> Marca con [x] lo completado. Última actualización: 2026-07-14.

## Datos y fuentes
- [ ] **SABI** — confirmar acceso de la UCA (biblioteca) para facturación/empleo por bodega (inteligencia económica y de negocios). Alternativa: Registro Mercantil/BORME.
- [ ] **Más conjuntos de Dataestur** — empleo turístico, empresas turísticas (DIRCE), procedencia de extranjeros (FRONTUR/EGATUR/TURISMO_RECEPTOR), precios (IPC), museos.
  - [ ] Revisar el endpoint `AFILIACION_TURISMO_DL` (falló al decodificar; formato distinto).
- [x] **Google Trends** (pytrends) — interés de búsqueda "bodegas Jerez" vs Rioja/Ribera/Rías Baixas (últimos 5 años) + origen por CCAA. En `datos/procesado/google_trends/`. Hallazgo: Jerez 2º de 4 (media 37; líder Rioja 56), tendencia −15% (2 años vs 2 años). Módulo `enolytics/ingesta/google_trends.py`.
- [x] **Ampliar scraping de la Ruta** — 167 recursos en 11 categorías (bodegas 41, restaurantes 27, recursos culturales 27, naturales 20, actividades 19, alojamientos 14, museos 7, turismo accesible 6, enotecas 3, caterings 2, agencias 1). En `datos/procesado/oferta_enoturistica.csv`. Falta: agenda de eventos + enriquecer fichas (GPS) de no-bodegas.
- [ ] **TripAdvisor** — segunda fuente de reseñas (más visitante internacional), vía Outscraper.
- [ ] Otras plataformas de reseñas: **Civitatis, GetYourGuide** (precios de experiencias, canales de reserva), **Vivino**.
- [x] **ACEVIN — visitantes por ruta del vino** (`enolytics/ingesta/acevin.py`): descarga los informes oficiales del Observatorio RVE (PDF) y extrae visitantes por ruta 2022-2024 → `datos/procesado/acevin/visitantes_rutas.csv`. **Hallazgo: el Marco de Jerez es 1º de España en 2024 (425.652, +11,2%), adelantando a Rioja Alta (−18,6%).**
- [ ] **Censo de reseñas de otras rutas** (Rioja, Ribera) para comparar *reputación online entre destinos* (requiere Outscraper).
- [x] **Oferta y precios comparados entre rutas** — ACEVIN: `oferta_rutas.csv` (37 rutas), `ingresos_rutas.csv` (parcial). **Hallazgos: el Marco es 1º en visitantes pero 7º en oferta (111 servicios vs 334 de Ribera), e ingresa 40,4 €/visitante frente a 70,0 € de Rioja Alta.** Falta: precios de experiencias (Civitatis/GetYourGuide).
- [ ] **Estrategias diferenciadoras** de otras rutas (análisis cualitativo) — indicador de la Tabla 1 aún sin cubrir.
- [x] **Certificaciones de sostenibilidad** — FEV SWfCP cruzado (4: Barbadillo, González Byass, Lustau, Osborne) + **auditoría web de sostenibilidad** por 7 ejes (`enolytics/ingesta/sostenibilidad.py`): 10 bodegas comunican ecológico; Miguel Domecq 7/7. En `datos/procesado/sostenibilidad.csv`. Nota: el buscador público de **CAAE** solo expone su lista internacional (Perú/México), no el registro español; por la solera, los vinos de Jerez tradicionales no certifican "vino ecológico". Falta (opcional): indicadores de consumo (estimados) y transporte sostenible.
- [ ] **Atributos de Google Maps** (accesibilidad, reserva online) vía servicio "Google Maps" de Outscraper (inteligencia tecnológica).
- [ ] **Afluencia con Google Places** — estimar la afluencia/ocupación de cada bodega a partir de los *"popular times"* (horas punta, ocupación por franja/día y "live busyness") de Google Maps/Places. Proxy de visitantes sin sensores: perfiles de estacionalidad y horarios de mayor demanda por bodega y para el destino (inteligencia de clientes/negocios). Vías: Outscraper (campo popular_times) o librería `populartimes`. Ojo: no es un dato oficial de la API estándar de Places; validar cobertura y términos de uso.
- [ ] **Desplazamientos y procedencia del enoturista** (⚠️ *distinto* de la afluencia y del transporte sostenible: aquí se trata de **de dónde viene** y **cómo se mueve** el visitante). Tres vías complementarias:
  - **Dataestur / INE — estudios de movilidad** (basados en telefonía móvil): flujos de viajeros entre provincias/CCAA hacia Cádiz. Fuente oficial.
  - **Procedencia inferida de las reseñas**: detectar el **idioma** de cada reseña (1/3 no están en español) → segmentar nacional vs. internacional, y cruzarlo con el IPA (indicador ya previsto: *IPA/IPCA por procedencia*).
  - **Google Trends por región/país** (ya lo tenemos parcialmente: de dónde se busca "bodegas Jerez" → Andalucía, Ceuta, Extremadura…). Ampliar a interés internacional ("sherry tour").
  - Cubre indicadores de la Tabla 1: *perfil y comportamiento de los visitantes* (Clientes) y *procedencia* (Mercado).
- [ ] ⭐ **CONECTIVIDAD AÉREA (Dataestur) — el único dato PREDICTIVO que hemos encontrado.**
  Fuente: https://www.dataestur.es/blog/como-usar-datos-conectividad-aerea-pasajeros-destinos/
  - **Qué ofrece:** 4 indicadores, y **tres de ellos miran al FUTURO (hasta 3 meses de proyección)**:
    1. **Búsquedas online de vuelos** (proyección 3 meses) → intención de viaje *antes* de que ocurra.
    2. **Reservas confirmadas** (proyección 3 meses) → demanda ya comprometida.
    3. **Oferta de asientos programada** (3 meses) → capacidad de llegada.
    4. Tráfico de pasajeros estimado (mes anterior).
  - **Por qué es importante:** la memoria promete *"modelos de integración de datos **en tiempo real** que permitan mejorar la **capacidad predictiva**"* y *"**simulaciones y proyecciones** de escenarios turísticos"*. **Hoy TODOS nuestros datos miran al pasado.** Esta es la primera fuente que permitiría cumplir esa promesa.
  - **Encaja con el Marco:** Jerez **tiene aeropuerto propio** (aparece en nuestros datos de OSM). Habría que ver si está entre los 23 destinos con informe mensual, y si no, usar el de Sevilla/Cádiz como aproximación.
  - **Indicadores que propone construir:** tasa de conversión búsqueda→reserva, **antelación de compra por mercado emisor**, duración media de estancia, ocupación estimada.
  - **Alimenta:** **Mercado** (demanda futura, mercados prioritarios, demanda potencial sin cobertura aérea), **Clientes** (procedencia real del internacional) y **estacionalidad** (FEDER P4A).
  - **Acceso:** API de Dataestur (ya tenemos cliente en `enolytics/ingesta/dataestur.py`) + cuadro de mando en `/transporte/informacion-transporte-aereo-pasajeros/`. También vía SIT de SEGITTUR (previa solicitud).
  - **Tarea:** leer el blog entero, localizar los conjuntos concretos en la API y evaluar la cobertura para Jerez.
- [ ] ⭐ **BLOG DE DATAESTUR — mina de fuentes** (https://www.dataestur.es/blog/). Revisadas las páginas 1-4 y **cruzados los artículos con nuestras lagunas** en **[docs/fuentes_blog_dataestur.md](fuentes_blog_dataestur.md)**. Lo que tapa (todo son indicadores de la Tabla 1 hoy a CERO):
  - **Empleo turístico** (empresas + empleo, DIRCE) → Económica y Negocios.
  - **Rentabilidad** (hostelería: beneficios, ventas, trabajadores) → alternativa **gratuita a SABI**.
  - **Redes sociales** (qué interesa de España en RRSS) → Mercado (la memoria las cita y no las tenemos).
  - **Impacto de un gran evento en los desplazamientos** → desplazamientos + eventos enoturísticos (¡la Vendimia!).
  - **Índice de sentimiento oficial de SEGITTUR** → **benchmark para validar nuestro análisis de sentimiento** (hoy derivado de las estrellas, no de un modelo NLP). Muy útil para el paper.
  - **Calendario de publicación 2026** → imprescindible para la **automatización periódica** ("tiempo real").
  - [ ] Falta revisar las **páginas 5-9** del blog.
- [ ] **Consejo Regulador de Jerez** — memorias anuales (producción, ventas, exportación).

## Calidad del análisis (NLP)
- [x] ⭐ **IDIOMA DE LAS RESEÑAS → procedencia** (`enolytics/nlp/idioma.py`, langdetect con semilla fija para que sea reproducible). Columnas `idioma` y `segmento_idioma` en `resenas.csv`.
  - **Resultado:** 62,3% de reseñas con idioma detectable. **Hispanohablante 5.090 (46,4%) · Internacional 1.750 (15,9%) · Sin determinar 4.132 (37,7%)**. Top idiomas: inglés (905), alemán (290), italiano (180), francés (91). El internacional puntúa **4,46★ frente a 4,58★** del hispanohablante.
  - 🚨 **SESGO MEDIDO (hallazgo clave):** el léxico de atributos está **solo en español**, así que **el 35,8% de las reseñas internacionales no aporta ningún atributo**, frente al 5,1% de las hispanohablantes. **El IPA actual se construye casi solo con la voz del visitante hispanohablante.**
  - ⚠️ **Por eso NO se muestra un IPA comparado por idioma:** la "importancia" del segmento internacional sería un **artefacto del léxico**, no una preferencia real. Requiere primero el léxico multilingüe.
  - **Cautelas declaradas en el dashboard:** idioma ≠ nacionalidad (un mexicano escribe en español y es internacional); 1/3 de reseñas no tienen texto.

- [x] ✅ **LÉXICO MULTILINGÜE** (ES/EN/DE/IT/FR) en `enolytics/nlp/analisis.py`. **Reseñas internacionales sin analizar: 35,8% → 11,4%** (analizables: 64% → 88,6%), sin regresión en las hispanohablantes (5,1%).
  - 🐛 **BUG CORREGIDO de paso:** la clave suelta **"tiempo"** contaminaba «Organización y reserva» (disparaba 118 reseñas españolas, la mayoría sin relación: *"nada de las típicas turistadas"*, ¡reseñas de logística de camiones!). En español es polisémica (el clima, la duración). Sustituida por la locución "tiempo de espera".
  - ⚠️ **CAMBIA UN NÚMERO PUBLICADO:** «Organización y reserva» pasa de **3,66★ a 4,00★** en el destino (al quitar el ruido y sumar el internacional). **Sigue siendo el peor atributo**, pero el dato anterior estaba inflado por ruido. Revisar cualquier borrador que citara 3,66.
  - 🎯 **HALLAZGO nuevo (ya defendible):** el visitante **internacional menciona la reserva 4,6× más** (11,5% vs 2,5%) pero **la puntúa mejor** (4,29★ vs **3,56★** del hispanohablante). El problema de organización lo sufre sobre todo **el visitante nacional**.
  - Cautela declarada en el dashboard: las palabras clave de cada idioma capturan matices distintos (el inglés *booking* es descriptivo; el español *espera*/*cola* ya arrastra queja).
- [ ] **Sentimiento con modelo NLP real** (hoy se deriva de las estrellas) — BERT multilingüe. Validar contra el índice de sentimiento oficial de SEGITTUR. instalar `transformers` (BERT multilingüe) o ampliar el léxico a EN/DE/IT/FR. (Va de la mano de la tarea anterior.)
- [ ] **Modelado de temas (LDA)** — descubrir atributos automáticamente, más allá del léxico fijo.
- [ ] Validar/afinar el léxico de atributos con criterio experto (Paula / bodegas).

## Modelos analíticos
- [x] IPA (destino + por bodega)
- [x] IPCA (competitivo, por bodega vs. Marco)
- [x] DIPA (evolución temporal del destino)
- [x] DIPCA (evolución de la brecha competitiva por bodega)
- [ ] IPA/IPCA por **atributo cruzado con procedencia** (nacional vs internacional).

## Las 7 inteligencias (estado)
- [x] **Clientes** — reseñas (satisfacción, atributos) + índices Dataestur + **perfil del enoturista (ACEVIN, 16 indicadores)** y **volumen de visitas**. ⚠️ El perfil de ACEVIN es NACIONAL (no por ruta): sirve de benchmark y de plantilla de cuestionario.
- [x] **Competidores** — reputación + IPCA. Falta: precios y otras rutas.
- [~] **Económica** — gasto Dataestur (hecho). Falta: por bodega (SABI).
- [x] **Mercado** — gasto/percepción Dataestur + **Google Trends** (interés de búsqueda comparativo vs rutas competidoras + origen por CCAA). Falta (opcional): procedencia internacional (FRONTUR).
- [~] **Negocios** — catálogo de bodegas. Falta: museos/enotecas/eventos + empleo.
- [x] **Tecnológica** — madurez digital (`auditoria_web.csv`: HTTPS, móvil, inglés, reserva, inmersiva → /5) + **accesibilidad universal** (`accesibilidad.csv`: índice WCAG /8 + señales de accesibilidad física/sensorial). 29/42 auditadas. **Hallazgo: 0 de 29 bodegas mencionan apoyo sensorial (audioguías, braille, signos); solo 4 mencionan accesibilidad física.** Falta: accesibilidad física REAL vía Google Maps; contraste/teclado (exige renderizar).
- [x] **Sostenibilidad** — certificación FEV (4) + índice de sostenibilidad comunicada (7 ejes) + **transporte sostenible** (`transporte_sostenible.csv`, OpenStreetMap): 88% de las bodegas accesibles en transporte público. Falta (opcional): consumos estimados (agua/energía/huella).

## Dashboard y producto
- [x] **Ficha de reputación estilo Booking/Amazon** por bodega (`enolytics/analitica/reputacion.py`, idea de Antonio): distribución de estrellas, "lo que dicen los visitantes", aspectos con signo (↗ ~ ↘) y nº de menciones, reseñas representativas y **tasa de respuesta del propietario**. El resumen es **determinista** (se compone de los datos agregados), no lo genera una IA → reproducible y auditable, a diferencia del de Amazon. **Hallazgo: 11 de 33 bodegas no responden a NINGUNA reseña; González Byass acumula 209 críticas sin contestar.**
- [x] **Motor de recomendaciones accionables** (`enolytics/analitica/recomendaciones.py`) — el diferencial que promete la memoria. Reglas que cruzan las 7 inteligencias y generan recomendaciones priorizadas, cada una con su diagnóstico (dato que la justifica) y su fuente. Dos niveles: destino (8 recomendaciones, 5 de prioridad alta) y bodega individual.
- [x] **Reorganizar en pestañas** por inteligencia (Gestor: Visión general · Clientes y experiencia · Económica y mercado. Bodega: Ficha · Reseñas y análisis). Añadir más pestañas al sumar inteligencias.
- [x] **Etiquetado del origen de cada indicador** (🟢 oficial · 🔵 observado · 🟡 estimado) con leyenda en el dashboard. 13 etiquetas en las 7 inteligencias. `config.ORIGENES_DATO` + helper `fuente()`.
- [x] **Enlace permanente** — PUBLICADO en **https://enolytics-feder-uca.streamlit.app** (Streamlit Community Cloud, repo público `Antonio-Ramos-UCA/enolytics`). Redespliega solo al hacer `git push`. Falta (opcional): restringir vista por correo desde Settings → Sharing.
- [ ] **Automatización incremental** de reseñas (API Outscraper + programación) — la parte "periódica" de la memoria.

## Pendientes menores de datos
- [x] **Superar el bloqueo anti-bot** (`enolytics/ingesta/navegador.py`, Playwright): las webs con verificación de edad se leen abriendo un Chromium real. **29 → 38 webs auditadas** en las 3 auditorías (madurez, accesibilidad, sostenibilidad); 15 rescatadas. **Bodegas Tradición (piloto) recuperada: 5/5 madurez, 7/8 accesibilidad.** Siguen sin web accesible: Emilio Hidalgo (piloto), Yuste, Caydsa, El Piraña.
- [ ] Resolver identidad de **AC Wines** en Google (excluida del corpus).
- [ ] Completar datos de ficha de **Bodegas Emilio Hidalgo** (piloto).

## Cuestionarios (fase piloto, con Paula y bodegas)
- [ ] Diseñar **cuestionario a bodegas** (económica + negocios + tecnológica + sostenibilidad) — solo para lo NO obtenible de fuentes públicas.
- [ ] Diseñar **cuestionario a enoturistas** (perfil, fidelización, canales) — validación de proxies.

## Salidas académicas (memoria)
- [ ] Redactar hallazgos para publicación JCR (el problema de "organización/reserva" que empeora es un buen ángulo).
- [ ] Definir TFM/TFG asociados.
