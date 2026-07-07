# Plan para completar las 7 inteligencias de ENOLYTICS

> Documento de trabajo. Traduce la Tabla 1 de la memoria científico-técnica en un plan
> accionable: qué mide cada inteligencia, de dónde salen los datos, qué tenemos ya y qué
> falta. Última actualización: 2026-07-07.

## Estado global de un vistazo

| # | Inteligencia | Categoría SEGITTUR | Estado | Depende sobre todo de… |
|---|---|---|---|---|
| 1 | Económica | Sostenibilidad | 🔴 Pendiente | Datos oficiales + cuestionarios bodega |
| 2 | Mercado | Demanda | 🟡 Fácil de arrancar | Google Trends, RRSS, analítica web |
| 3 | Competidores | Oferta/Demanda/Sost. | 🟢 Avanzada | Reseñas (hecho) + precios/benchmarking |
| 4 | Clientes | Demanda | 🟢 Avanzada | Reseñas (hecho) + cuestionarios visitantes |
| 5 | Negocios | Oferta/Sostenibilidad | 🟡 Parcial | Catálogo (hecho) + cuestionarios/OGD |
| 6 | Tecnológica | Oferta/Sostenibilidad | 🟡 Parcial | Catálogo/webs + cuestionarios bodega |
| 7 | Sostenibilidad | Sostenibilidad | 🔴 Pendiente | Cuestionarios + datos ambientales |

Leyenda: 🟢 gran parte hecha · 🟡 base disponible, falta completar · 🔴 por empezar.

---

## Detalle por inteligencia

### 1. Inteligencia Económica
- **Qué mide:** impacto económico del enoturismo, contribución al empleo y desarrollo local, rentabilidad del sector.
- **Fuentes:** INE, Dataestur, ACEVIN (gasto medio enoturista, visitantes), cuestionarios a bodegas.
- **Qué tenemos:** nada aún. (La memoria cita gasto medio 201,80 €/día, 382.716 visitantes 2023 en el Marco.)
- **Qué falta:** ingestar indicadores oficiales (automatizable) + preguntar facturación/empleo a bodegas (cuestionario).
- **Esfuerzo:** medio. Parte automatizable (datos públicos), parte requiere cuestionario.

### 2. Inteligencia de Mercado
- **Qué mide:** patrones de búsqueda online, tendencias del turismo del vino, comparación de demanda con otros destinos, predisposición al gasto.
- **Fuentes:** Google Trends, redes sociales, estudios ad-hoc, analítica web.
- **Qué tenemos:** nada aún.
- **Qué falta:** conectar **Google Trends** (búsquedas de "enoturismo Jerez", nombres de bodegas, comparación con Rioja/Ribera…). Es gratis y automatizable con Python (`pytrends`).
- **Esfuerzo:** BAJO — buen "quick win" automatizable sin coste. ⭐

### 3. Inteligencia de Competidores
- **Qué mide:** comparación de la oferta con otros destinos, estrategias diferenciadoras, reputación online, comparación de precios.
- **Fuentes:** reseñas/RRSS, benchmarking de destinos, cuestionarios.
- **Qué tenemos:** ✅ **reputación online** (nota + volumen por bodega) y **benchmarking interno** (IPCA: cada bodega vs. el Marco).
- **Qué falta:** comparar el Marco con **otras rutas** (Rioja, Ribera del Duero, Penedès) y **precios** de experiencias.
- **Esfuerzo:** medio (ampliar el scraping/censo a otras rutas; precios desde Civitatis/GetYourGuide).

### 4. Inteligencia de Clientes
- **Qué mide:** perfil y comportamiento del visitante, motivaciones, satisfacción, fidelización, canales, volumen de visitas.
- **Fuentes:** cuestionarios a visitantes, big data (reseñas), análisis de consumo.
- **Qué tenemos:** ✅ **satisfacción y motivaciones** (análisis de sentimiento + atributos de 11.000 reseñas), volumen relativo por bodega, idioma/procedencia aproximada.
- **Qué falta:** **cuestionario a visitantes** para perfil sociodemográfico, fidelización y canales de reserva.
- **Esfuerzo:** medio (diseño y trabajo de campo del cuestionario).

### 5. Inteligencia de Negocios
- **Qué mide:** nº de bodegas abiertas, museos, enotecas, empresas de servicios, eventos, empleados, formación del personal, innovación.
- **Fuentes:** datos de OGDs y AAPP, cuestionarios a OGDs/bodegas/empresas.
- **Qué tenemos:** ✅ base del **catálogo** (nº bodegas, servicios enoturísticos por bodega, localización).
- **Qué falta:** museos/enotecas/empresas de servicios (ampliar catálogo desde la web de la Ruta — otras categorías), y empleo/formación/innovación (cuestionario).
- **Esfuerzo:** bajo-medio (parte se saca de la misma web de la Ruta que ya scrapeamos).

### 6. Inteligencia Tecnológica
- **Qué mide:** adopción de tecnologías (realidad aumentada, visitas virtuales, reservas digitales) y accesibilidad universal (física y digital).
- **Fuentes:** cuestionarios a bodegas y museos, datos digitales de OGDs.
- **Qué tenemos:** ✅ pistas indirectas del catálogo (web propia, RRSS, reserva online detectable).
- **Qué falta:** auditoría de webs (accesibilidad, reserva online, idiomas) — parcialmente automatizable — + cuestionario para tecnologías inmersivas.
- **Esfuerzo:** medio.

### 7. Inteligencia en Sostenibilidad (la NUEVA de la propuesta)
- **Qué mide:** impacto ambiental (agua, energía, huella de carbono), certificaciones ambientales, economía circular, transporte sostenible.
- **Fuentes:** OMT, Green Deal, EUROSTAT, INE, WSET, OIV, Statista, Euromonitor, encuestas a bodegas y museos.
- **Qué tenemos:** nada aún.
- **Qué falta:** sobre todo **cuestionario de sostenibilidad** a bodegas (certificaciones, consumos, prácticas) + indicadores macro.
- **Esfuerzo:** alto (muy dependiente de trabajo de campo). Es la más novedosa y la que más diferencia el proyecto.

---

## Recomendación de secuencia

**Quick wins automatizables (sin coste, sin trabajo de campo):**
1. **Inteligencia de Mercado** → Google Trends (búsquedas y comparación con otras rutas). ⭐
2. **Completar Negocios** → scrapear del sitio de la Ruta las otras categorías (museos, enotecas, restaurantes, actividades) igual que hicimos con bodegas.
3. **Competidores (ampliación)** → censo de reseñas de otras rutas del vino para comparar el Marco con Rioja/Ribera.

**Requieren diseño de cuestionarios (trabajo de "proyecto", con Paula y las bodegas):**
4. **Clientes** (perfil/fidelización), **Económica** (facturación/empleo), **Tecnológica** e **Sostenibilidad**.
   - Propuesta: un **único cuestionario a bodegas** que cubra a la vez económica + negocios + tecnológica + sostenibilidad, y un **cuestionario a visitantes** para clientes. Cada pregunta se deriva de un indicador de la Tabla 1.

**Idea clave:** las inteligencias que salen de **datos públicos** (mercado, parte de negocios y competidores) las podemos automatizar ya; las que salen de **cuestionarios** conviene diseñarlas bien una sola vez y lanzarlas en la fase piloto (Emilio Hidalgo y Tradición).
