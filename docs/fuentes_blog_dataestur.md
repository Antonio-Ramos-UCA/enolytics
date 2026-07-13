# Blog de Dataestur — artículos útiles para ENOLYTICS

> Índice: https://www.dataestur.es/blog/ (9 páginas)
> Revisado el 2026-07-13 (páginas 1-4). **Quedan las páginas 5-9 por revisar.**
> Cada artículo está cruzado con la **laguna concreta** que taparía, según
> [auditoria_coherencia.md](auditoria_coherencia.md).

---

## 🔴 PRIORIDAD ALTA — tapan indicadores de la Tabla 1 que hoy están a CERO

### 1. Empresas turísticas (y su empleo): cuántas hay, cómo son y dónde están
https://www.dataestur.es/blog/empresas-turismo-empleo/
- **Tapa:** *"Contribución del enoturismo al empleo"* (Económica) y *"Nº de empleados en
  enoturismo"* (Negocios). **Ambos indicadores de la Tabla 1 están hoy sin cubrir.**
- Datos de empresas turísticas (DIRCE) y su empleo, por territorio.

### 2. Datos para analizar la hostelería y la restauración: beneficios, ventas y trabajadores
https://www.dataestur.es/blog/hosteleria-beneficios-rendimiento-ventas-empleo/
- **Tapa:** *"Rentabilidad del sector enoturístico"* (Económica) — hoy a cero. Es la alternativa
  **pública y gratuita** a SABI, que sigue pendiente de confirmar acceso.

### 3. Qué interesa de España a los turistas según las redes sociales
https://www.dataestur.es/blog/visitas-tematicas-populares-turismo-spain/
- **Tapa:** *"Patrones de búsquedas online **y redes sociales**"* (Mercado). Hoy solo tenemos
  Google Trends; **las RRSS están sin cubrir** y la memoria las cita expresamente.

### 4. Caso práctico: impacto de un gran evento en los desplazamientos a un destino
https://www.dataestur.es/blog/caso-practico-impacto-evento-desplazamientos-destino/
- **Doblemente útil:** (a) metodología de **desplazamientos** (lo que pidió Antonio) y
  (b) *"Nº de eventos enoturísticos organizados"* (Negocios), hoy a cero.
- Permitiría medir el impacto de la **Vendimia**, las **Fiestas de la Vendimia** o cualquier
  gran evento del Marco sobre la llegada de visitantes.

### 5. Conectividad aérea de los destinos *(ya apuntado como tarea propia)*
https://www.dataestur.es/blog/como-usar-datos-conectividad-aerea-pasajeros-destinos/
- **La única fuente PREDICTIVA** encontrada (búsquedas, reservas y asientos a 3 meses vista).
  La memoria promete *"capacidad predictiva"* y *"proyecciones de escenarios"*, y **hoy todos
  nuestros datos miran al pasado**.

---

## 🟠 PRIORIDAD MEDIA — mejoran o validan lo que ya hacemos

### 6. ⭐ Caso de uso experimental: índice de sentimiento sobre la opinión de los viajeros
https://www.dataestur.es/blog/caso-de-uso-experimental-generacion-de-un-indice-de-sentimiento/
- **Muy relevante para la publicación JCR.** Es un **índice de sentimiento oficial** hecho por
  SEGITTUR. Nosotros construimos el nuestro a partir de reseñas.
- **Usos:** (a) **benchmark metodológico** — comparar nuestro índice con el oficial;
  (b) validar (o cuestionar) nuestro proxy actual, que deriva el sentimiento de **las estrellas**
  y no de un modelo NLP.

### 7. Cómo monitorizar las búsquedas de los destinos turísticos en Internet
https://www.dataestur.es/blog/como-monitorizar-busqueda-destinos-turismo-internet/
- Mejora nuestro módulo `google_trends.py` con la metodología oficial.

### 8. Radiografía del turismo en España en verano (flujos turísticos)
https://www.dataestur.es/blog/radiografia-flujos-turisticos-espana-verano/
- **Desplazamientos**: flujos de viajeros hacia los destinos.

### 9. Datos para conocer la satisfacción del turista con el destino
https://www.dataestur.es/blog/datos-satisfaccion-turista-interaccion-redes-sociales/
### 10. Datos para conocer la satisfacción hotelera del turista en una provincia
https://www.dataestur.es/blog/datos-satisfaccion-hotelera-turista-provincia/
- Complementan **Clientes** (ya usamos los índices de percepción de Cádiz, pero hay más).

### 11. El gasto de viajeros en destino según los pagos con tarjeta (TPV)
https://www.dataestur.es/blog/gasto-turistico-destino-segun-pagos-tarjeta-tpv/
- **Ya usamos este dato**, pero el nuestro es **provincial** (Cádiz) y no aísla el gasto
  enoturístico — una debilidad que el propio dashboard confiesa (🟡 estimado). **Leerlo para ver
  si se puede afinar** (¿por municipio? ¿por sector?).

---

## 🟡 UTILIDAD OPERATIVA

### 12. Cómo usar la API de Dataestur para hacer seguimiento de datos turísticos
https://www.dataestur.es/blog/pasos-como-usar-api-dataestur/
- Mejora nuestro cliente `enolytics/ingesta/dataestur.py` (y quizá resuelva el endpoint
  `AFILIACION_TURISMO_DL`, que falló al decodificar).

### 13. Calendario de publicación de datos turísticos para 2026
https://www.dataestur.es/blog/calendario-de-publicacion-de-datos-turisticos-para-2026/
- **Clave para la automatización periódica** (el *"tiempo real"* de la memoria): saber **cuándo**
  se publica cada dato permite programar las descargas.

---

## Pendiente
- [ ] **Revisar las páginas 5 a 9** del blog (solo se han revisado la 1-4).
