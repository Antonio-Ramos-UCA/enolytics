# ENOLYTICS — Tareas pendientes (backlog)

> Lista viva de todo lo que queda por hacer, para no perder el hilo entre sesiones.
> Marca con [x] lo completado. Última actualización: 2026-07-07.

## Datos y fuentes
- [ ] **SABI** — confirmar acceso de la UCA (biblioteca) para facturación/empleo por bodega (inteligencia económica y de negocios). Alternativa: Registro Mercantil/BORME.
- [ ] **Más conjuntos de Dataestur** — empleo turístico, empresas turísticas (DIRCE), procedencia de extranjeros (FRONTUR/EGATUR/TURISMO_RECEPTOR), precios (IPC), museos.
  - [ ] Revisar el endpoint `AFILIACION_TURISMO_DL` (falló al decodificar; formato distinto).
- [ ] **Google Trends** (pytrends) — interés de búsqueda del enoturismo de Jerez y comparación con Rioja/Ribera (inteligencia de mercado).
- [x] **Ampliar scraping de la Ruta** — 167 recursos en 11 categorías (bodegas 41, restaurantes 27, recursos culturales 27, naturales 20, actividades 19, alojamientos 14, museos 7, turismo accesible 6, enotecas 3, caterings 2, agencias 1). En `datos/procesado/oferta_enoturistica.csv`. Falta: agenda de eventos + enriquecer fichas (GPS) de no-bodegas.
- [ ] **TripAdvisor** — segunda fuente de reseñas (más visitante internacional), vía Outscraper.
- [ ] Otras plataformas de reseñas: **Civitatis, GetYourGuide** (precios de experiencias, canales de reserva), **Vivino**.
- [ ] **Censo de reseñas de otras rutas** (Rioja, Ribera) para benchmarking competitivo real.
- [~] **Certificaciones de sostenibilidad** — FEV SWfCP cruzado (4 bodegas certificadas: Barbadillo, González Byass, Lustau, Osborne) en `datos/procesado/sostenibilidad.csv`. Falta: **CAAE ecológico**, indicadores de consumo (estimados) y transporte sostenible.
- [ ] **Atributos de Google Maps** (accesibilidad, reserva online) vía servicio "Google Maps" de Outscraper (inteligencia tecnológica).
- [ ] **Consejo Regulador de Jerez** — memorias anuales (producción, ventas, exportación).

## Calidad del análisis (NLP)
- [ ] **Sentimiento/atributos multilingües** — ~1/3 de reseñas no son en español; instalar `transformers` (BERT multilingüe) o ampliar el léxico a EN/DE/IT/FR.
- [ ] **Modelado de temas (LDA)** — descubrir atributos automáticamente, más allá del léxico fijo.
- [ ] Validar/afinar el léxico de atributos con criterio experto (Paula / bodegas).

## Modelos analíticos
- [x] IPA (destino + por bodega)
- [x] IPCA (competitivo, por bodega vs. Marco)
- [x] DIPA (evolución temporal del destino)
- [x] DIPCA (evolución de la brecha competitiva por bodega)
- [ ] IPA/IPCA por **atributo cruzado con procedencia** (nacional vs internacional).

## Las 7 inteligencias (estado)
- [x] **Clientes** — reseñas (satisfacción, atributos) + índices Dataestur. Falta: perfil/fidelización (cuestionario o ACEVIN).
- [x] **Competidores** — reputación + IPCA. Falta: precios y otras rutas.
- [~] **Económica** — gasto Dataestur (hecho). Falta: por bodega (SABI).
- [~] **Mercado** — gasto/percepción Dataestur. Falta: Google Trends, procedencia.
- [~] **Negocios** — catálogo de bodegas. Falta: museos/enotecas/eventos + empleo.
- [x] **Tecnológica** — auditoría automática de webs (`datos/procesado/auditoria_web.csv`): HTTPS, móvil, inglés, reserva online, inmersiva → índice madurez /5. 29/42 auditadas (13 bloquean bot/sin web). Falta: accesibilidad física de Google Maps; afinar sobre subpáginas.
- [ ] **Sostenibilidad** — certificaciones (FEV/CAAE) + transporte + consumos (estimados).

## Dashboard y producto
- [x] **Reorganizar en pestañas** por inteligencia (Gestor: Visión general · Clientes y experiencia · Económica y mercado. Bodega: Ficha · Reseñas y análisis). Añadir más pestañas al sumar inteligencias.
- [ ] Etiquetar cada indicador por origen (🟢 oficial · 🔵 reseñas · 🟡 estimado) para rigor.
- [x] **Enlace permanente** — PUBLICADO en **https://enolytics-feder-uca.streamlit.app** (Streamlit Community Cloud, repo público `Antonio-Ramos-UCA/enolytics`). Redespliega solo al hacer `git push`. Falta (opcional): restringir vista por correo desde Settings → Sharing.
- [ ] **Automatización incremental** de reseñas (API Outscraper + programación) — la parte "periódica" de la memoria.

## Pendientes menores de datos
- [ ] Resolver identidad de **AC Wines** en Google (excluida del corpus).
- [ ] Completar datos de ficha de **Bodegas Emilio Hidalgo** (piloto).

## Cuestionarios (fase piloto, con Paula y bodegas)
- [ ] Diseñar **cuestionario a bodegas** (económica + negocios + tecnológica + sostenibilidad) — solo para lo NO obtenible de fuentes públicas.
- [ ] Diseñar **cuestionario a enoturistas** (perfil, fidelización, canales) — validación de proxies.

## Salidas académicas (memoria)
- [ ] Redactar hallazgos para publicación JCR (el problema de "organización/reserva" que empeora es un buen ángulo).
- [ ] Definir TFM/TFG asociados.
