# ENOLYTICS — Plan de profundización de las 7 inteligencias

> Propuesta de desarrollo, inteligencia por inteligencia: lo que pide la **memoria** y que aún
> falta, más **mejoras propias** que refuerzan el proyecto. Fecha: 2026-07-13.
> Complementa a [auditoria_coherencia.md](auditoria_coherencia.md).

**Leyenda de esfuerzo:** 🟢 bajo (horas) · 🟡 medio (días) · 🔴 alto (requiere decisión/recursos)
**Origen del dato:** 🟢 oficial · 🔵 reseñas/web · 🟡 estimado

---

## 🔑 Cuatro mejoras transversales (mi propuesta principal)

Antes de ir inteligencia por inteligencia, estas cuatro son las que **más valor añaden al
conjunto**, y tres de ellas están *prometidas en la memoria* pero no hechas.

### 1. Motor de recomendaciones accionables ⭐ 🟡
La memoria promete, textualmente, que ENOLYTICS *"no solo recopila datos, sino que los
transforma en **recomendaciones accionables**"*. **Hoy el dashboard muestra datos; no recomienda.**

Propuesta: reglas que generen recomendaciones automáticas por bodega y para el destino:
> *"«Organización y reserva» está 0,4 puntos por debajo de la media del Marco **y empeorando**
> (DIPCA: pierde terreno). Cuadrante IPA: «Concéntrese aquí». → **Prioridad de actuación alta.**"*

Es traducir el IPA/IPCA/DIPCA a lenguaje de gestión. **Es el diferencial que vende la memoria.**

### 2. Índice de Competitividad Enoturística (ICE) ⭐ 🟡
La memoria habla de *"índices de competitividad que comparan destinos"*. Propuesta: índice
compuesto (reputación + madurez digital + sostenibilidad + accesibilidad + oferta), calculable
**por bodega** y **por destino**. Es, además, una **salida académica publicable**.

### 3. Etiquetado del origen de cada indicador 🟢
Marcar cada dato como 🟢 oficial · 🔵 reseñas/web · 🟡 estimado. Barato y eleva mucho el **rigor
científico** (imprescindible para publicar y para justificar ante FEDER).

### 4. Análisis de estacionalidad ⭐ 🟢
El proyecto está alineado con la prioridad **FEDER P4A: "reducir la estacionalidad"**, pero **no
medimos estacionalidad**. Ya tenemos los datos (fechas de 10.972 reseñas + Google Trends semanal):
índice de estacionalidad del Marco vs. rutas competidoras, y meses valle a atacar.

---

## 💶 1. Inteligencia Económica

*Hoy:* gasto TPV de Cádiz (Dataestur) — **provincial, no enoturístico**.

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Impacto económico del Marco** = visitantes × gasto medio del enoturista | ACEVIN (425.652 visitantes; 504,4 €/estancia) | 🟢 | 🟡 estimado |
| **Cuota del Marco** sobre el enoturismo nacional (425.652 / 3.036.878 ≈ **14%**) | ACEVIN | 🟢 | 🟢 |
| **Empleo turístico** en Cádiz (afiliación a la SS) | Dataestur / INE | 🟡 | 🟢 |
| **Facturación y empleo por bodega** | SABI (biblioteca UCA) o BORME | 🔴 | 🟢 |

> 💡 *Mejora propia:* estimar el **efecto multiplicador** (impacto directo vs. inducido en
> restauración, alojamiento y comercio), que la memoria menciona pero no cuantifica.

---

## 📈 2. Inteligencia de Mercado

*Hoy:* Google Trends (interés, comparación, origen por CCAA) + gasto por procedencia + percepción.

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Estacionalidad de la demanda** (ver transversal nº4) | Trends + reseñas | 🟢 | 🔵 |
| **Consultas emergentes** (*rising queries* de Trends) → cubre "tendencias emergentes" | pytrends | 🟢 | 🔵 |
| **Interés internacional** ("sherry tour", "jerez wine tour" por país) | Trends | 🟢 | 🔵 |
| **Gasto medio y pernoctaciones del enoturista** | ACEVIN demanda | 🟢 | 🟢 |
| Escucha de **redes sociales** | API X/Instagram | 🔴 | 🔵 |

---

## 🥊 3. Inteligencia de Competidores

*Hoy:* ✅ visitantes por ruta (ACEVIN 2022-24) + paradoja competitiva. **Faltan 2 indicadores.**

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Comparación de la OFERTA entre rutas** (nº establecimientos por ruta y tipo) | Mismos PDF de ACEVIN (sección de oferta) | 🟢 | 🟢 |
| **Comparación de PRECIOS** de experiencias entre rutas | Civitatis / GetYourGuide | 🟡 | 🔵 |
| **Reputación online de otras rutas** (nota media de sus bodegas en Google) | Outscraper (~coste bajo) | 🟡 | 🔵 |
| **Estrategias diferenciadoras** de otras rutas | Análisis cualitativo de sus webs | 🟡 | 🔵 |

---

## 😊 4. Inteligencia de Clientes

*Hoy:* IPA + DIPA sobre 10.972 reseñas. **Faltan perfil, motivaciones, fidelización, canales y
volumen de visitas** — que la memoria daba por dependientes de cuestionario.

> 🎯 **Hallazgo clave:** el informe **"Análisis de la demanda" de ACEVIN** (628 encuestas, 95%
> confianza) cubre **motivaciones, canales de reserva, gasto, pernoctaciones, edad y
> satisfacción**. ⚠️ **Es nacional, no desglosa por ruta.** Por tanto sirve para dos cosas:
> 1. **Benchmark oficial** contra el que comparar al Marco (p. ej. 63% reserva online en España).
> 2. **Plantilla validada** para nuestro propio cuestionario a enoturistas del Marco.

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Volumen de visitas** al Marco (425.652) | ACEVIN | 🟢 | 🟢 |
| **Perfil, motivaciones y canales** (benchmark nacional) | ACEVIN demanda | 🟢 | 🟢 |
| **IPA por procedencia**: segmentar reseñas por **idioma** (nacional vs. internacional) | Reseñas | 🟡 | 🔵 |
| **Motivaciones desde las propias reseñas** (topic modeling) — sin encuestar | LDA/BERT | 🟡 | 🔵 |
| **Afluencia real** (*popular times* de Google Places) | Google Places | 🟡 | 🟡 |
| **Cuestionario propio** a enoturistas del Marco | Trabajo de campo | 🔴 | 🟢 |

---

## 🏛️ 5. Inteligencia de Negocios

*Hoy:* 167 recursos en 11 categorías, mapa y directorio. Cubre 4 de los 8 indicadores.

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Agenda de eventos enoturísticos** | Web de la Ruta | 🟢 | 🔵 |
| **Nº de empleados en enoturismo** | Dataestur / INE | 🟡 | 🟢 |
| **Tipos de experiencia, idiomas y precios** ofertados por cada bodega | Webs de bodegas | 🟡 | 🔵 |
| Formación del personal · estrategias de innovación | Cuestionario a bodegas | 🔴 | 🟢 |

> 💡 *Mejora propia:* **densidad de oferta por localidad** (¿está todo concentrado en Jerez?) —
> útil para el equilibrio territorial que la memoria persigue.

---

## 🖥️ 6. Inteligencia Tecnológica

*Hoy:* madurez digital /5 (HTTPS, móvil, inglés, reserva, inmersiva).
⚠️ **La ACCESIBILIDAD UNIVERSAL está a cero, y la memoria la detalla con mucho nivel.**

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Índice de accesibilidad digital (WCAG)**: texto alternativo en imágenes, atributo `lang`, etiquetas de formulario, contraste, ARIA | Auditoría web propia | 🟢 | 🔵 |
| **Accesibilidad física**: entrada accesible, aseo adaptado, aparcamiento | Atributos de Google Maps | 🟡 | 🟢 |
| **Audioguías / material accesible** | Webs + Google Maps | 🟡 | 🔵 |
| **Superar el bloqueo anti-bot** (González Byass, Tradición…) con Playwright | — | 🟡 | 🔵 |
| Ampliar la auditoría **a subpáginas**, no solo la home | — | 🟢 | 🔵 |

---

## 🌱 7. Inteligencia en Sostenibilidad

*Hoy:* certificación FEV (4) + índice de sostenibilidad comunicada por 7 ejes.

| Propuesta | Fuente | Esfuerzo | Origen |
|---|---|---|---|
| **Transporte sostenible**: distancia de cada bodega a estación de tren/autobús | OpenStreetMap (gratis; ya tenemos GPS) | 🟢 | 🟢 |
| **Certificación ecológica** verificada bodega a bodega | Webs + CAAE | 🟡 | 🟢 |
| **Consumos estimados** (agua, energía, huella de carbono) por ratios del sector | OIV / ratios sectoriales | 🟡 | 🟡 |
| Economía circular (datos reales, no solo señal web) | Cuestionario a bodegas | 🔴 | 🟢 |

> 💡 *Mejora propia:* la **distancia a transporte público** es el indicador literal de la memoria
> ("uso de medios de transporte sostenibles en el destino") y es **gratis y reproducible** con los
> GPS que ya tenemos.

---

## 🗺️ Orden recomendado

### Fase A — Victorias rápidas, alto impacto, coste cero
1. **Accesibilidad universal** (Tecnológica) — la mayor laguna frente a la memoria.
2. **ACEVIN: demanda + oferta por ruta** — un solo PDF desbloquea indicadores de *Clientes,
   Mercado, Competidores y Económica* a la vez. **Máximo retorno.**
3. **Transporte sostenible** (OSM) — indicador literal, gratis.
4. **Estacionalidad** — alineado con FEDER P4A.

### Fase B — El diferencial de la memoria
5. **Motor de recomendaciones accionables** ⭐
6. **Etiquetado del origen** de cada indicador.
7. **Índice de Competitividad Enoturística (ICE)**.

### Fase C — Técnicas prometidas (NLP)
8. **Modelado de temas (LDA/BERT)** y **sentimiento multilingüe** real.
9. **TripAdvisor** como segunda fuente.
10. **Automatización periódica** (el "tiempo real" de la memoria).

### Fase D — Requieren decisión o recursos
11. **SABI** (económica por bodega) · **Outscraper** (precios y reputación de otras rutas).
12. **Cuestionarios** a bodegas y visitantes (con la plantilla de ACEVIN como base).
13. Decisiones pendientes: los **3.500 € de Azure**, el **acceso restringido**, la errata **SIPA**.

---

## Reparto sugerido (según [protocolo_trabajo.md](protocolo_trabajo.md))

| Persona | Bloque | De este plan le tocaría |
|---|---|---|
| **Antonio** | Económica · Mercado | Impacto económico, cuota, estacionalidad, consultas emergentes |
| **Paula** | Clientes · Competidores | ACEVIN demanda, IPA por idioma, oferta y precios entre rutas |
| **Fernando** | Negocios · Tecnológica · Sostenibilidad | Accesibilidad, transporte sostenible, eventos, experiencias |

Las **4 mejoras transversales** las coordina Antonio como integrador.
