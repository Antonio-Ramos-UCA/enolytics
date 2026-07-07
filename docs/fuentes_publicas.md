# Fuentes públicas por inteligencia (prototipo sin encuestas)

> Fuentes de datos públicas/automatizables verificadas para poblar las 7 inteligencias
> del prototipo **sin necesidad de encuestar a nadie**. Cada fuente indica cómo se accede
> y su calidad (🟢 dato oficial · 🔵 derivado de reseñas · 🟡 proxy/estimación).
> Última actualización: 2026-07-07.

## Fuentes transversales (sirven a varias inteligencias)

| Fuente | Qué aporta | Acceso |
|---|---|---|
| **Dataestur** (SEGITTUR) — dataestur.es | Turismo España: gasto, PIB turístico, empleo, transporte, alojamiento. Datos de INE, Renfe, Segittur | **API pública** + descarga XLSX por año/CCAA/provincia |
| **ACEVIN – Observatorio Rutas del Vino** — wineroutesofspain.com | Visitantes a bodegas/museos, **perfil del enoturista**, impacto económico. Cifras del Marco de Jerez | Informes anuales PDF (oferta + demanda) |
| **INE** — ine.es | Empleo, demografía de empresas (DIRCE), turismo, encuesta ocupación | Descarga / API INEbase |
| **IECA / BADEA** (Junta de Andalucía) | Estadística regional andaluza (turismo, economía, territorio) | Portal datos abiertos + BADEA |
| **Consejo Regulador Jerez** — sherry.wine (Documentación) | Memorias anuales: producción, existencias, **ventas y exportación** del Marco | Memorias PDF |
| **datos.gob.es** | Catálogo nacional de datos abiertos (buscador) | Portal / API |

---

## 1. Inteligencia Económica
- **Indicadores:** impacto económico, empleo, rentabilidad.
- **Fuentes:**
  - 🟢 **SABI** (Informa) — cuentas anuales de cada bodega: **facturación, nº empleados, resultado**. Acceso por la **biblioteca de la UCA** (vía RedIRIS). Alternativa: Registro Mercantil / BORME (depósito de cuentas).
  - 🟢 **Dataestur / INE** — gasto turístico, empleo turístico, PIB.
  - 🟢 **ACEVIN** — gasto medio del enoturista, impacto económico de la Ruta.
- **Sin encuesta:** ✅ prácticamente completa (SABI cubre lo que se preguntaría a la bodega).

## 2. Inteligencia de Mercado
- **Indicadores:** búsquedas online, tendencias, comparación de demanda, predisposición al gasto.
- **Fuentes:**
  - 🟢 **Google Trends** vía **pytrends** (Python, gratis): interés de "enoturismo Jerez", nombres de bodegas, **Jerez vs Rioja/Ribera**, estacionalidad.
  - 🟢 **ACEVIN** — demanda y comparación entre rutas (Rioja 389k, Jerez 383k, Ribera 369k visitantes 2023).
  - 🟢 **Dataestur** — gasto y flujos turísticos.
- **Sin encuesta:** ✅ completa y automatizable.

## 3. Inteligencia de Competidores
- **Indicadores:** comparación de oferta, reputación online, precios.
- **Fuentes:**
  - 🔵 **Reseñas Google** (hecho) + IPCA (cada bodega vs. Marco).
  - 🟢 **Censo de reseñas de otras rutas** (Rioja, Ribera) — mismo método Outscraper.
  - 🟡 **Precios** de experiencias en **Civitatis / GetYourGuide** (scraping).
- **Sin encuesta:** ✅ completa.

## 4. Inteligencia de Clientes
- **Indicadores:** perfil, motivaciones, satisfacción, fidelización, canales, volumen.
- **Fuentes:**
  - 🔵 **Reseñas** — satisfacción, motivaciones, **idioma → procedencia** del visitante, volumen.
  - 🟢 **ACEVIN – Perfil del enoturista** — informe con perfil sociodemográfico agregado (edad, procedencia, gasto).
  - 🟡 **Canales de reserva** — dónde es reservable cada bodega (web propia / OTA).
- **Sin encuesta:** 🟡 casi completa (perfil agregado por ACEVIN; solo la fidelización individual quedaría estimada).

## 5. Inteligencia de Negocios
- **Indicadores:** nº bodegas/museos/enotecas/empresas/eventos, empleados, formación, innovación.
- **Fuentes:**
  - 🟢 **Web de la Ruta del Vino de Jerez** — museos, enotecas, restaurantes, actividades, **agenda de eventos** (scraping, como bodegas).
  - 🟢 **SABI / INE (DIRCE)** — nº empleados y demografía empresarial.
  - 🟡 **Innovación** — proxy: premios, notas de prensa, contenido web.
- **Sin encuesta:** ✅ casi completa.

## 6. Inteligencia Tecnológica
- **Indicadores:** adopción de tecnologías, accesibilidad universal (física y digital).
- **Fuentes:**
  - 🟢 **Google Maps (atributos)** — accesibilidad física (entrada adaptada, aseos), reserva online. Vía Outscraper (servicio "Google Maps", barato).
  - 🟡 **Auditoría automática de webs** — idiomas, reserva online, mobile-friendly, accesibilidad digital (scripts).
  - 🟡 **Tecnologías inmersivas** (RA/360) — proxy: keywords en la web ("realidad virtual", "visita 360").
- **Sin encuesta:** 🟡 mayormente proxy, pero suficiente para el prototipo.

## 7. Inteligencia en Sostenibilidad
- **Indicadores:** impacto ambiental (agua, energía, huella carbono), certificaciones, economía circular, transporte sostenible.
- **Fuentes:**
  - 🟢 **FEV – Sustainable Wineries for Climate Protection** (fev.es) — **listado oficial de bodegas certificadas** (~148 en España).
  - 🟢 **CAAE** (caae.es) — directorio de **operadores ecológicos** de Andalucía (bodegas ecológicas certificadas).
  - 🟢 **Transporte sostenible** — Google Maps transit / Consorcio de Transportes Bahía de Cádiz (accesibilidad en transporte público a cada bodega).
  - 🟡 **Consumo agua/energía/huella** — NO público por bodega → **estimación por sector** (OIV, informes) escalada por tamaño, claramente etiquetada como estimación.
- **Sin encuesta:** 🟡 parcial (certificaciones y transporte = dato real; consumos = estimación pendiente de validar).

---

## Resumen: ¿se puede el prototipo sin encuestas?

**Sí.** De ~40 indicadores del modelo, la gran mayoría se cubren con fuentes públicas
(dato real o proxy). Solo **2-3 quedan como estimación transparente**: consumo ambiental
por bodega y fidelización individual del cliente. Los cuestionarios de la fase piloto
(Emilio Hidalgo, Tradición) servirían para **validar y afinar** esos proxies, no para
generar el modelo de cero.

**Dependencia a confirmar:** acceso de la UCA a **SABI** (probable vía biblioteca).
Sin SABI, la parte económica por bodega se cubriría con el Registro Mercantil (más manual).
