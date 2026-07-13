# ENOLYTICS — Auditoría de coherencia: Memoria ↔ Prototipo

> Contraste entre lo comprometido en la **Memoria Científico-Técnica** (firmada, 14/02/2025)
> y lo que hoy hace el **prototipo** (https://enolytics-feder-uca.streamlit.app).
> Fecha de la auditoría: 2026-07-13.

## Veredicto general

El prototipo **cumple el núcleo diferencial de la memoria** (las 7 inteligencias, los 4 modelos
IPA/IPCA/DIPA/DIPCA y la minería de reseñas), pero tiene **3 desviaciones conscientes** que hay
que justificar ante el financiador, **1 desajuste conceptual** que conviene corregir, y
**lagunas** en indicadores concretos comprometidos en la Tabla 1.

| Bloque | Estado |
|---|---|
| Las 7 inteligencias representadas | ✅ Sí (7 pestañas) |
| Modelos IPA / IPCA / DIPA / DIPCA | ✅ Los 4 implementados |
| Minería de textos sobre reseñas | ✅ 10.972 reseñas de Google |
| Cobertura de indicadores de la Tabla 1 | 🟡 ~40% |
| Stack tecnológico comprometido | ❌ Desviado (ver §2) |

---

## 1. Coherencia indicador a indicador (Tabla 1 de la memoria)

**Leyenda:** ✅ hecho · 🟡 parcial/proxy · ❌ no hecho

### 💶 Inteligencia Económica *(SEGITTUR: Sostenibilidad)*
| Indicador comprometido | Estado | En el prototipo |
|---|---|---|
| Impacto económico del enoturismo | 🟡 | Gasto turístico TPV de Cádiz (Dataestur). Es **provincial, no enoturístico** |
| Contribución al empleo y desarrollo local | ❌ | Nada |
| Rentabilidad del sector enoturístico | ❌ | Nada (SABI pendiente) |

### 📈 Inteligencia de Mercado *(Demanda)*
| Indicador | Estado | En el prototipo |
|---|---|---|
| Patrones de búsquedas online | ✅ | Google Trends (5 años) |
| Comparación de demanda con otros destinos | ✅ | Jerez vs Rioja/Ribera/Rías Baixas |
| Predisposición al gasto | 🟡 | Gasto por procedencia (Dataestur) |
| Tendencias emergentes / RRSS | ❌ | Sin redes sociales |

### 🥊 Inteligencia de Competidores *(Oferta/Demanda/Sostenibilidad)*
| Indicador | Estado | En el prototipo |
|---|---|---|
| Reputación online del destino | 🟡 | Reputación **por bodega dentro del Marco** |
| Comparación de la oferta con otros destinos | ❌ | Nada |
| Comparación de **precios** con otros destinos | ❌ | Nada |
| Estrategias diferenciadoras de otras regiones | ❌ | Nada |

> ⚠️ **Desajuste conceptual — ver §3.**

### 😊 Inteligencia de Clientes *(Demanda)*
| Indicador | Estado | En el prototipo |
|---|---|---|
| Nivel de satisfacción y percepción | ✅ | IPA + DIPA sobre 10.972 reseñas |
| **Volumen de visitas** a bodegas y museos | ❌ | Nada. ACEVIN publica 382.716 visitantes (2023), **citado en la propia memoria** |
| Perfil y comportamiento del visitante | ❌ | Requiere cuestionario o ACEVIN |
| Motivaciones y fidelización | ❌ | Requiere cuestionario |
| Canales de planificación y reserva | ❌ | Nada |

### 🏛️ Inteligencia de Negocios *(Oferta/Sostenibilidad)*
| Indicador | Estado | En el prototipo |
|---|---|---|
| Nº bodegas abiertas al turismo | ✅ | 41 |
| Nº museos y centros de interpretación | ✅ | 7 |
| Nº enotecas y agencias | ✅ | 3 y 1 |
| Nº empresas de servicios enoturísticos | ✅ | 167 recursos, 11 categorías |
| Nº eventos enoturísticos | ❌ | Nada |
| Nº empleados en enoturismo | ❌ | Nada |
| Nivel de formación del personal | ❌ | Requiere cuestionario |
| Estrategias de innovación en bodegas | ❌ | Requiere cuestionario |

### 🖥️ Inteligencia Tecnológica *(Oferta/Sostenibilidad)*
| Indicador | Estado | En el prototipo |
|---|---|---|
| Adopción de tecnologías (RA, visitas virtuales, reserva digital) | ✅ | Auditoría web: reserva online, inmersiva |
| **Accesibilidad universal** (accesibilidad física, audioguías, aseos adaptados) | ❌ | **Nada** — la memoria lo detalla mucho |
| Índice de accesibilidad digital de webs | ❌ | Nada (tenemos HTTPS/móvil/inglés, que no es accesibilidad) |

### 🌱 Inteligencia en Sostenibilidad *(Sostenibilidad)*
| Indicador | Estado | En el prototipo |
|---|---|---|
| Certificaciones ambientales | ✅ | FEV SWfCP (4 bodegas) |
| Prácticas de economía circular | 🟡 | Señal web "residuos" (proxy de comunicación) |
| Impacto ambiental (agua, energía, huella de carbono) | ❌ | Solo señales web, sin magnitudes |
| Transporte sostenible en el destino | ❌ | Nada |

---

## 2. Desviaciones tecnológicas conscientes (⚠️ justificar ante FEDER)

La memoria compromete un stack concreto. El prototipo usa otro. Son decisiones **razonables**,
pero deben **documentarse y justificarse** en los informes, porque hay presupuesto asociado.

| Memoria dice | Prototipo hace | Comentario |
|---|---|---|
| Cuadro de mando en **Power BI** | **Streamlit** (Python) | Decisión tomada: mayor control, reproducibilidad científica, sin licencias. **Justificar.** |
| Infraestructura **Azure** (Data Factory, SQL, Blob, Analysis Services, AD, Key Vault, Monitor) — **3.500 €** presupuestados | Ficheros CSV + Streamlit Community Cloud (gratis) | Suficiente a escala piloto. **Ojo: hay 3.500 € de presupuesto Azure sin ejecutar.** |
| "Acceso protegido mediante **sistema de seguridad y control de permisos**; solo personas autorizadas" | Dashboard **público y abierto** | ⚠️ **Contradice la memoria.** Decidido dejarlo abierto por comodidad. Reversible en 2 min. |
| "Información en **tiempo real**" (repetido varias veces) | Fotos estáticas; sin actualización automática | ❌ Falta la automatización periódica (la memoria pide scraping periódico). |
| "Simulaciones y proyecciones de escenarios turísticos" | No implementado | ❌ Comprometido en la memoria (p. 8). |

---

## 3. Desajuste conceptual: la Inteligencia de Competidores

**La memoria define "competidores" como OTROS DESTINOS enoturísticos** (comparar la oferta, los
precios, la reputación y las estrategias del Marco de Jerez *frente a Rioja, Ribera, etc.*).

**El prototipo, en cambio, compara bodegas DENTRO del Marco** entre sí (ranking de reseñas y notas).
Eso es *benchmarking interno*, no inteligencia de competidores en el sentido de la memoria.

Curiosamente, **la única comparación real entre destinos que tenemos (Google Trends vs Rioja/Ribera)
está en la pestaña de Mercado**, no en la de Competidores.

**Recomendación:** reorientar la pestaña de Competidores hacia **otros destinos** (reseñas y notas
de bodegas de Rioja/Ribera, precios de experiencias, interés de búsqueda), y dejar el ranking
interno del Marco como "posicionamiento dentro del destino".

---

## 4. Lagunas metodológicas (técnicas prometidas)

| Técnica prometida | Estado |
|---|---|
| Minería de textos | ✅ |
| **Análisis de sentimiento** | 🟡 Se deriva de la **puntuación en estrellas**, no de un modelo NLP. La memoria promete análisis de sentimiento (y cita **BERT**). |
| **Modelado de temas (LDA / BERT)** | ❌ **No implementado.** Usamos un léxico fijo de 7 atributos. La memoria lo cita explícitamente. |
| Multilingüe | ❌ ~1/3 de las reseñas no están en español y se analizan con léxico español |
| Fuentes de reseñas: **TripAdvisor**, Google, **RRSS** | 🟡 Solo Google |
| IPA / IPCA / DIPA / DIPCA | ✅ Los cuatro |

> 📌 **Nota:** en la p. 4 la memoria menciona "IPA, **SIPA**, IPCA, DIPA y DIPCA", pero en el resto
> del documento solo aparecen los cuatro. Parece una errata. **Decidir si SIPA entra o no.**

---

## 5. ⚠️ Riesgo operativo: las dos bodegas piloto son las peor cubiertas

La memoria fija el piloto (Fase 3) en **Bodegas Emilio Hidalgo** y **Bodegas Tradición**.
En el prototipo, ambas son precisamente las que **peor cobertura de datos tienen**:

| Bodega piloto | Reseñas | Auditoría web | Sostenibilidad |
|---|---|---|---|
| **Emilio Hidalgo** | 49 (pocas) | ❌ web bloquea el robot | ❌ sin señal (0/7) |
| **Tradición** | 374 | ❌ web bloquea el robot | ❌ sin señal (0/7) |

Sus webs bloquean el robot (verificación de edad / anti-bot), así que las inteligencias
**Tecnológica** y **Sostenibilidad** salen **vacías justo en las dos bodegas del piloto**.

**Recomendación:** para estas dos (y solo estas), recoger los datos **manualmente o con su
colaboración** — son socios del proyecto (FMH y ACM están en el equipo). Es la vía más rápida
y además valida los proxies automáticos.

---

## 6. Recomendaciones priorizadas

### 🔴 Prioridad alta (coherencia con lo comprometido)
1. ~~**Reorientar Competidores** hacia otros destinos (§3).~~ ✅ **HECHO (2026-07-13)** — módulo
   `enolytics/ingesta/acevin.py` + pestaña reescrita: el Marco frente a las demás rutas del vino
   (visitantes ACEVIN 2022-2024). Sigue faltando **precios** y **estrategias diferenciadoras**.
2. **Accesibilidad universal** en Tecnológica — muy detallada en la memoria, hoy ausente. Vía:
   atributos de accesibilidad de Google Maps + auditoría de accesibilidad web.
3. **Volumen de visitas** (Clientes) — ACEVIN publica los datos y la memoria los cita. Complementar
   con la afluencia vía *popular times* de Google Places (ya en el backlog).
4. **Datos de las 2 bodegas piloto** — recogida asistida con FMH y ACM (§5).

### 🟡 Prioridad media (técnicas prometidas)
5. **Modelado de temas (LDA/BERT)** y **sentimiento con modelo NLP** (no solo estrellas), multilingüe.
6. **TripAdvisor** como segunda fuente de reseñas.
7. **Automatización periódica** (el "tiempo real" de la memoria).

### 🟢 Decisiones a tomar en equipo
8. **Justificar por escrito** las desviaciones de stack (Power BI → Streamlit; Azure → CSV/Cloud),
   y decidir qué se hace con los **3.500 € de Azure**.
9. **Decidir si el dashboard debe ser restringido** (la memoria dice acceso controlado).
10. **Cuestionarios** (bodegas y visitantes): la memoria los sitúa como hito de la **Fase 1**.
    Muchos indicadores ❌ solo se pueden cubrir así. Decidir si se diseñan ya.
11. Aclarar la errata **SIPA**.
