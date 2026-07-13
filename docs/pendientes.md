# ENOLYTICS — Tareas pendientes (backlog)

> Lista viva de todo lo que queda por hacer, para no perder el hilo entre sesiones.
> Marca con [x] lo completado. Última actualización: 2026-07-13.

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
- [ ] **Consejo Regulador de Jerez** — memorias anuales (producción, ventas, exportación).

## Calidad del análisis (NLP)
- [ ] ⭐ **IDIOMA DE LAS RESEÑAS → procedencia del visitante** (interesa especialmente a Antonio; **la más barata: los datos ya los tenemos**).
  - **Qué:** detectar el idioma de cada una de las 10.972 reseñas (`langdetect`/`langid`, o el campo de idioma si Outscraper lo trae) → nueva columna `idioma` en `resenas.csv` y segmento **nacional (ES) vs. internacional**.
  - **Para qué:** (1) **IPA/IPCA por procedencia** — ¿valora lo mismo el enoturista internacional que el nacional? (2) medir el **peso real del visitante internacional** por bodega; (3) detectar bodegas con vocación exportadora vs. locales.
  - **Por qué importa:** hoy el léxico de atributos es **solo español**, así que ~1/3 de las reseñas se analizan mal o no se analizan → el IPA actual está **sesgado hacia el visitante nacional**. Esto lo arregla y a la vez abre un eje de análisis nuevo.
  - **Ojo:** el idioma de la reseña es un *proxy* de la procedencia, no la procedencia real (un español puede escribir en inglés). Etiquetar como 🟡 estimado.
- [ ] **Sentimiento/atributos multilingües** — ~1/3 de reseñas no son en español; instalar `transformers` (BERT multilingüe) o ampliar el léxico a EN/DE/IT/FR. (Va de la mano de la tarea anterior.)
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
