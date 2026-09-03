# Propuestas de mejora — ENOLYTICS

Mockups y documentos de propuesta enviados por el equipo. Se guardan aquí los
**originales** (además del resumen accionable, que está en [`../docs/pendientes.md`](../docs/pendientes.md),
sección "⭐ PROPUESTAS DE PAULA").

## Propuesta de Paula (IP) — 21/07/2026

Tres piezas para convertir el dashboard en producto, con ejemplos de diseño definitivo.
Abrir los `.html` en cualquier navegador (son autónomos).

| Fichero | Qué es |
|---|---|
| [`01_propuesta_paula.html`](01_propuesta_paula.html) | La propuesta: 3 piezas (informe, guía, simulador) + datos nuevos + temas de memoria/FEDER |
| [`02_ejemplo_informe_bodega.html`](02_ejemplo_informe_bodega.html) | Ejemplo del **informe descargable por bodega** (diseño definitivo; competidores directos de ejemplo) |
| [`03_guia_de_uso.html`](03_guia_de_uso.html) | La **guía de uso / metodología** desarrollada |

**Las 3 piezas, en corto:**
1. **Informe PDF por bodega** — corazón nuevo: competidores DIRECTOS (ACEDE: Market Commonality + Resource Similarity).
2. **Guía de uso / metodología** — doble uso: bodeguero + anexo FEDER.
3. **Simulador "¿qué pasaría si…?"** — proyecciones de escenarios (lineales, honestas).

> Enlaces originales (artefactos de claude.ai, requieren la cuenta de la UCA):
> - Propuesta: `claude.ai/code/artifact/0a971c60-4f2f-4059-a917-8f3c81281745`
> - Ejemplo informe: `claude.ai/code/artifact/4815865f-3643-40e1-aa4b-393c0d036eba`
> - Guía: `claude.ai/code/artifact/4878e3ca-06be-4da9-a351-1172c3a09f3f`
>
> Los `.html` de esta carpeta son copias autónomas (se retiró el envoltorio técnico del visor;
> el diseño y el contenido son los originales de Paula).

---

## Revisión de la plataforma — «Preguntas y observaciones pendientes» — 03/09/2026

Segunda entrega de Paula: **diez puntos salidos de usar el cuadro de mando**. No son piezas
nuevas, son arreglos sobre lo que ya hay. **Dos son errores** (el 4 rompe la vista de bodega
individual) y ocho son observaciones de lectura en pantalla.

| Fichero | Qué es |
|---|---|
| [`04_preguntas_y_observaciones.html`](04_preguntas_y_observaciones.html) | El original, con los pares «Ahora / Propuesta» de cada punto |
| [`04_preguntas_y_observaciones.md`](04_preguntas_y_observaciones.md) | El mismo contenido en texto, para trabajar y citar por número |

**Los diez, en corto** (la numeración es la del documento, para decir «la 4» y entendernos):

1. Las recomendaciones del destino salen dos veces y ya se han descuadrado (14 ≠ 12).
2. «Categoría SEGITTUR: Sostenibilidad» en la pestaña Económica parece una errata (el dato es correcto).
3. «Cómo leer los datos» sale tres veces (leyenda ×2 + guía §1 y §5).
4. 🐞 **URGENTE** — Bodega individual revienta (`IndexError`) si el filtro de localidad se queda vacío.
5. 🐞 Viña La Torre («El Puerto / Jerez») se cuenta como una localidad nueva; Jerez figura con 21 en vez de 22.
6. La tarjeta «Media nacional» cuelga la comparación de la tarjeta equivocada y se lee al revés.
7. «Diferencia por visitante» (Simulador) rotula la flechita, no el número grande.
8. Tres gráficos imprimen `undefined` como título de leyenda (Kamensky, Kano, co-ocurrencias).
9. Se ha colado un apunte interno en el pie del Simulador («Idea de Paula, Pieza 3»).
10. Los umbrales del motor de recomendaciones (15 %, 5 y 10 críticas, 10 €…) no están documentados.

> Enlace original: `claude.ai/code/artifact/2d5966ea-1140-4340-a057-e733fc70a447`
