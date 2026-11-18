# Guión de TFG — Grado en Turismo (UCA)

> **Para quién es este documento:** para el estudiante que asuma el TFG y para quien lo tutorice.
> No es el TFG: es el guión de trabajo del que partir, con qué va en cada capítulo, de dónde sale
> cada dato y qué hay que decidir por el camino.
>
> **Marco:** se apoya en el proyecto **ENOLYTICS** (FEDER-UCA-2024-A2-27, Universidad de Cádiz).
> El estudiante **no parte de cero**: hereda el corpus de reseñas y la infraestructura de análisis.
> Eso cambia la naturaleza del trabajo —y obliga a definir bien cuál es su aportación propia, que
> es el punto crítico de este TFG y se trata en la sección 0.3.

---

## 0. Antes de empezar: tres decisiones

### 0.1 El riesgo principal

ENOLYTICS ya calcula todo lo que este TFG va a calcular. Si el trabajo se limita a describir lo
que la plataforma muestra, **no es un TFG, es un manual de usuario**. El tribunal lo detectará.

### 0.2 La solución: una pregunta que ENOLYTICS no responde

La plataforma analiza el destino **en conjunto**. No segmenta el análisis importancia-desempeño
por procedencia del visitante. Y hay indicio de que la procedencia importa: la nota media del
visitante internacional es **4,46** frente a **4,58** del hispanohablante. Una diferencia pequeña
en la nota global puede esconder prioridades de mejora **distintas** por segmento, que es
justamente lo que un IPA revela y una media no.

> **Pregunta de investigación:** ¿coinciden las prioridades de mejora de la experiencia
> enoturística del Marco de Jerez cuando se analizan desde el visitante hispanohablante y desde
> el internacional, o el destino debería atender a dos agendas distintas?

Esa es la aportación del TFG: ENOLYTICS pone los datos y el método; el estudiante pone la
segmentación, el contraste y la lectura para la gestión del destino.

### 0.3 Qué hereda y qué construye

| Hereda de ENOLYTICS | Construye el estudiante |
|---|---|
| Corpus de 10.972 reseñas ya descargadas | La segmentación y el diseño del contraste |
| Léxico de atributos multilingüe | La revisión de literatura |
| Pipeline de sentimiento por atributo (BERT) | La interpretación y discusión |
| Matriz IPA del destino | Las matrices IPA **por segmento** y su comparación |
| — | Las implicaciones para la gestión del destino |

**Debe declararse explícitamente** en Metodología qué parte del instrumental es preexistente.
Ocultarlo sería una falta de integridad académica; declararlo es normal en investigación aplicada
y además refuerza el trabajo (acceso a datos que un TFG no podría generar solo).

---

## 1. Título

**Propuesto:** *Prioridades de mejora de la experiencia enoturística en el Marco de Jerez: un
análisis importancia-desempeño segmentado a partir de reseñas online*

Alternativas según el enfoque final: sustituir «segmentado» por «por mercado de origen», o
precisar «(2011-2026)» si se quiere subrayar la serie temporal.

---

## 2. Resumen y palabras clave *(se redacta al final)*

250 palabras, estructura: contexto → objetivo → método → resultados principales → implicación.
Versión en inglés obligatoria según normativa de la UCA.

**Palabras clave:** enoturismo · Marco de Jerez · análisis importancia-desempeño ·
reseñas online · satisfacción del visitante · segmentación de mercado

---

## 3. Introducción *(≈ 8 % de la extensión)*

### 3.1 Justificación
Tres hechos que sostienen la pertinencia, con su fuente:
- El Marco de Jerez es la **primera ruta de España en visitantes** a bodegas y museos del vino
  (425.652 en 2024, ACEVIN).
- Pero ingresa **40,4 € por visitante**, frente a los ~70 € de Rioja Alta. Lidera en volumen y no
  en valor. *(Cálculo de ENOLYTICS: ingresos ÷ visitantes, ambos de ACEVIN.)*
- La diferencia no está en el tamaño de la oferta —el Marco tiene 111 servicios, percentil 81 de
  las 37 rutas—, lo que desplaza la pregunta **al interior de la experiencia**. Y la experiencia
  es justo lo que las reseñas describen.

### 3.2 Objetivos

**General:** identificar y jerarquizar las prioridades de mejora de la experiencia enoturística
del Marco de Jerez a partir del contenido de las reseñas online, diferenciando por procedencia
del visitante.

**Específicos:**
1. Caracterizar los atributos de la experiencia enoturística que el visitante menciona
   espontáneamente.
2. Estimar la importancia y el desempeño de cada atributo mediante IPA derivado de reseñas.
3. Contrastar las matrices IPA del segmento hispanohablante y del internacional.
4. Clasificar los atributos según su relación asimétrica con la satisfacción (higiénicos /
   deleitadores).
5. Derivar implicaciones para la gestión del destino y de las bodegas.

### 3.3 Estructura del trabajo
Un párrafo por capítulo.

---

## 4. Marco teórico *(≈ 25 %)*

> Organizar por **temas**, no como lista de resúmenes. Cada epígrafe debe terminar señalando qué
> queda sin resolver, de modo que el *gap* no aparezca de golpe al final.

### 4.1 El enoturismo como producto turístico
Concepto y evolución. El enoturismo en España: Rutas del Vino de España (ACEVIN) como marco
institucional. Datos del Observatorio.

### 4.2 El Marco de Jerez como destino
Denominación de origen, sistema de criaderas y solera, las 41 bodegas de la Ruta del Vino y
Brandy. Peculiaridades que condicionan la experiencia (la visita a bodega de Jerez no es la de
Rioja: arquitectura de las catedrales del vino, el papel de la cata).

### 4.3 Calidad percibida, satisfacción y lealtad
Paradigma de la disconfirmación de expectativas. Por qué la satisfacción global no basta para
orientar la gestión: no dice **dónde** actuar.

### 4.4 El análisis importancia-desempeño (IPA)
Origen y lógica de los cuatro cuadrantes. Las dos críticas clásicas: cómo se mide la importancia
(declarada vs. inferida) y el supuesto de **relación simétrica** entre desempeño y satisfacción.

### 4.5 Del cuestionario a la reseña: IPA derivado de contenido generado por el usuario
Es el giro metodológico que sostiene este TFG. **Bi et al. (2019)** demuestran que el IPA puede
construirse sobre reseñas, con tres ventajas: muestras mayores, atributos emergentes en lugar de
impuestos por el cuestionario, y coste marginal nulo. Y tres objeciones, que hay que recoger
porque el TFG se topará con ellas.

### 4.6 Relaciones asimétricas: PRCA y modelo de Kano
Que un atributo falle resta más de lo que suma que funcione bien. **Brandt (1987)** propone el
*penalty–reward contrast analysis*; **Zhang et al. (2021)** lo aplican a la priorización de
mejoras hoteleras desde reseñas; **Han et al. (2026)** lo combinan con umbrales de Kano. Base de
la distinción **higiénico / deleitador** que usa el objetivo específico 4.

### 4.7 Marco normativo: el destino turístico inteligente
SEGITTUR y el modelo DTI; normas **UNE 178501** (sistema de gestión de los DTI) y **UNE 178502**
(indicadores). Encuadra el TFG en algo más que un ejercicio académico: la escucha activa del
visitante es un indicador DTI.

### 4.8 Síntesis y *gap*
La literatura aplica el IPA desde reseñas sobre todo a **hoteles y restaurantes**; el enoturismo
está poco representado, y la segmentación por procedencia dentro del IPA derivado, menos aún.
*(Conviene que el estudiante confirme este vacío con una búsqueda sistemática en Scopus/WoS y lo
documente en anexo: una afirmación de vacío sin búsqueda detrás es una debilidad del trabajo.)*

---

## 5. Metodología *(≈ 20 %)*

### 5.1 Diseño
Estudio **cuantitativo, no experimental, de corte transversal** con componente longitudinal
exploratorio, basado en análisis de contenido asistido por computador sobre datos secundarios.

### 5.2 Ámbito y unidad de análisis
Las **41 bodegas** inscritas en la Ruta del Vino y Brandy de Jerez. Unidad de análisis: **la
reseña**; unidad de observación para el sentimiento: **la frase**, porque una misma reseña puede
elogiar la cata y criticar la reserva.

### 5.3 El corpus
*(Cifras comprobadas sobre `datos/procesado/resenas.csv` el 15/11/2026.)*

| | |
|---|---|
| Reseñas | **10.972** |
| Bodegas | **41** |
| Con texto suficiente para analizar | **7.258** |
| Periodo | 22/07/2011 – 06/07/2026 |
| Hispanohablante | 5.090 |
| Internacional (no hispanohablante) | 1.750 |
| Sin determinar | 4.132 |
| Valoraciones de 5★ | **75,9 %** |
| Reseñas críticas (≤2★) | 646 |
| Con respuesta del propietario | 1.256 (11,4 %) |

Fuente: Google Maps, extraídas con Outscraper en el marco del proyecto ENOLYTICS.

### 5.4 Detección de atributos
Léxico multilingüe (ES/EN/DE/IT/FR) sobre siete atributos: *vino y cata · personal y trato ·
visita y experiencia · instalaciones · precio y valor · entorno y viñedo · organización y
reserva*, más *gastronomía y restauración*. Explicar que es un enfoque **léxico**, no de
modelado de temas (LDA), y por qué: trazabilidad y reproducibilidad frente a tópicos que cambian
en cada ejecución.

### 5.5 Desempeño: sentimiento por atributo
**No usar las estrellas.** Es el punto metodológico más importante del TFG y hay que argumentarlo:
la nota es de la **visita entera**, no del atributo. Una reseña de 5★ que dice *«carísimo pero
merece la pena»* asignaría desempeño 5 al precio, que es falso. Se usa un modelo BERT multilingüe
de sentimiento frase a frase, siguiendo la lógica de Bi et al. (2019) y Zhang et al. (2021).

### 5.6 Importancia: frecuencia frente a impacto
Presentar las dos y justificar la elegida:
- **Frecuencia** (importancia derivada clásica): cuántas reseñas lo mencionan.
- **Impacto** (PRCA): cuánto mueve el sentimiento hacia el atributo la valoración global.

No son intercambiables: *organización y reserva* se menciona poco —solo se habla de ella cuando
falla— pero arrastra la nota. Con frecuencia aparece como «baja prioridad»; con impacto, como
«concéntrese aquí». **Esta discrepancia es un resultado en sí mismo** y merece un epígrafe propio.

### 5.7 Segmentación
Por idioma detectado de la reseña, como ***proxy* de procedencia**. Declarar su limitación sin
rodeos: **idioma ≠ nacionalidad** (un mexicano escribe en español y es turista internacional), y
un 37,7 % del corpus queda «sin determinar» por reseñas demasiado cortas. Justificar por qué aun
así es el mejor *proxy* disponible y qué se pierde.

### 5.8 Contraste entre segmentos
Para cada atributo, comparar menciones y sentimiento entre segmentos. Aplicar pruebas de
diferencia de medias con corrección por comparaciones múltiples (Bonferroni o Benjamini-Hochberg:
son ocho atributos, el riesgo de falso positivo es real) y **reportar tamaño del efecto**, no solo
el *p*-valor: con 5.090 frente a 1.750 observaciones, diferencias triviales saldrán significativas.

### 5.9 Consideraciones éticas y legales
No es un trámite; en un TFG con datos de personas es materia de evaluación.
- **RGPD:** las reseñas incluyen nombre de autor. **Seudonimizar** antes de cualquier análisis y
  no reproducir nombres en el texto. Las citas textuales de reseñas, sin autoría.
- **Condiciones de uso** de la plataforma de origen: declarar la vía de obtención (proveedor
  comercial, no *scraping* propio).
- **Datos secundarios de un proyecto financiado:** declarar el acceso autorizado y agradecer la
  financiación con la cláusula FEDER obligatoria (ver `datos/marca_feder/LEEME.md`).
- **Uso de IA:** declarar herramientas empleadas según la normativa de la UCA.

---

## 6. Resultados *(≈ 25 %)*

> Presentar, no interpretar. La interpretación va en Discusión. Toda tabla y figura, numerada,
> rotulada y citada en el texto.

6.1 **Descripción del corpus** — distribución temporal, por bodega, por puntuación y por segmento.
6.2 **Frecuencia y sentimiento por atributo** — tabla base de todo lo demás.
6.3 **Matriz IPA del destino** — los cuatro cuadrantes, con los umbrales declarados.
6.4 **Frecuencia frente a impacto** — la discrepancia del epígrafe 5.6, con el caso de
   *organización y reserva*.
6.5 **Perfil higiénico / deleitador** — y el aviso del efecto techo (ver 7.3).
6.6 **⭐ Contraste por segmento** — el núcleo del TFG. Dos matrices IPA enfrentadas y la tabla de
   brechas por atributo con su significación y tamaño del efecto.
6.7 **Evolución temporal** — exploratorio. Hay indicio de que *precio y valor* se deteriora
   (3,87 → 3,70 en el análisis de ENOLYTICS); el estudiante debe recalcularlo y decidir si la
   serie aguanta la afirmación.

---

## 7. Discusión *(≈ 15 %)*

7.1 Qué dicen los resultados sobre las prioridades del destino.
7.2 **Si las agendas divergen por segmento**, qué implica para la promoción y para el producto;
    **si convergen**, también es resultado: significa que el destino puede tratar la experiencia
    como una sola y es un hallazgo publicable.
7.3 **Diálogo crítico con la literatura.** Aquí el TFG puede aportar de verdad: en un corpus con
    **75,9 % de valoraciones de 5★** el margen por encima de la media casi no existe, de modo que
    el *deleite* apenas puede observarse y todos los atributos tienden a higiénicos. Es un **efecto
    techo** que Zhang et al. (2021) y Han et al. (2026) no afrontan porque sus corpus de Yelp están
    más repartidos. Señalarlo es contribución, no defecto.
7.4 **Limitaciones**, sin suavizar:
    - Las reseñas **no son una muestra aleatoria**: hay autoselección hacia los extremos y sesgo
      hacia quien usa Google y escribe reseñas.
    - El *proxy* de idioma y el 37,7 % sin determinar.
    - Solo una plataforma: falta TripAdvisor, con más visitante internacional.
    - El corpus se cierra el 06/07/2026.
    - El análisis es del **destino**: la mayoría de bodegas no tiene muestra para un IPA propio.

---

## 8. Conclusiones

Responder a los objetivos específicos **uno por uno y en orden**. Separar:
- **Implicaciones para la gestión** (bodegas y Ruta).
- **Implicaciones teóricas** (el efecto techo; la frecuencia como mala *proxy* de importancia).
- **Futuras líneas** (TripAdvisor; encuesta propia para validar los *proxies*; extensión a otras
  rutas para comparar).

---

## 9. Referencias

### Verificadas *(PDF en `BIBLIOGRAFIA/`, citas comprobadas sobre el documento)*

- Bi, J.-W., Liu, Y., Fan, Z.-P., & Zhang, J. (2019). Wisdom of crowds: Conducting
  importance-performance analysis (IPA) through online reviews. *Tourism Management*, *70*,
  460–478. https://doi.org/10.1016/j.tourman.2018.09.010
- Han, W., Zhang, C., Zhang, Y. C., & Raab, C. (2026). How do robots reshape restaurant service
  attributes? – Evidence from online reviews. *International Journal of Contemporary Hospitality
  Management*. https://doi.org/10.1108/IJCHM-01-2026-0071
- Zhang, C., Xu, Z., Gou, X., & Chen, S. (2021). An online reviews-driven method for the
  prioritization of improvements in hotel services. *Tourism Management*, *87*, 104382.
- Zhou, R., Song, B., Li, G., & Law, R. (2026). A data-driven approach to competitor
  identification and categorization in the hotel industry. *International Journal of Hospitality
  Management*, *133*, 104503.

### Citadas en el proyecto, **pendientes de verificar**

> ⚠️ Aparecen en el código y la documentación de ENOLYTICS pero **no se ha comprobado su ficha
> completa**. El estudiante debe localizarlas en Scopus, Web of Science, Google Scholar o Dialnet
> y verificar autoría, año, volumen y páginas **antes** de citarlas. No copiarlas de aquí.

Martilla & James (1977), origen del IPA · Brandt (1987), PRCA · Kano et al. (1984) ·
Oliver (1980), disconfirmación · Shin & Nicolau (2022) · Wu et al. (2024) ·
Pratt et al. (2020), umbrales de Kano · Ji et al. (2012), *K-prototypes* ·
Callon et al. (1983), índice de equivalencia · Kamensky (2000), categorización de competidores.

### Fuentes institucionales
ACEVIN — Observatorio Turístico de las Rutas del Vino de España · Dataestur/SEGITTUR ·
Consejo Regulador D.O. Jerez-Xérès-Sherry · Ruta del Vino y Brandy del Marco de Jerez ·
UNE 178501 y UNE 178502.

---

## 10. Anexos

A. Léxico de atributos completo. · B. Estrategia de búsqueda bibliográfica (cadenas, bases,
resultados). · C. Tablas de resultados extensas. · D. Declaración de uso de IA. · E. Código o
protocolo de análisis, para reproducibilidad.

---

## 11. Cronograma orientativo (14 semanas)

| Semanas | Tarea | Entregable al tutor |
|---|---|---|
| 1–2 | Delimitar tema y objetivos; búsqueda bibliográfica | Índice + 15 referencias clave |
| 3–5 | Marco teórico | Borrador cap. 4 |
| 6 | Metodología; acceso al corpus | Borrador cap. 5 |
| 7–9 | Análisis | Tablas y figuras |
| 10–11 | Resultados | Borrador cap. 6 |
| 12 | Discusión y conclusiones | Borrador cap. 7–8 |
| 13 | Revisión íntegra, formato, referencias | Borrador completo |
| 14 | Correcciones y defensa | Versión final + presentación |

---

## 12. Otros TFG posibles sobre la misma base

Por si se asignan varios trabajos. Todos parten de ENOLYTICS y no se solapan entre sí.

| Tema | Pregunta | Datos | Dificultad |
|---|---|---|---|
| **Accesibilidad universal en el enoturismo** | ¿Está preparado el Marco para el visitante con discapacidad? | Auditoría WCAG de las 41 webs — **el estudiante puede rehacerla él mismo**. Hallazgo de partida: ninguna bodega menciona audioguías, braille ni lengua de signos | Media. Muy recomendable: tema socialmente relevante y poco explotado |
| **El crucerista como palanca de desestacionalización** | ¿Puede el puerto de Cádiz corregir la estacionalidad del enoturismo de Jerez? | Dataestur (696.151 cruceristas en 2024, frente a 425.652 visitantes a bodegas) + estacionalidad cruzada | Baja-media. Requiere complementar con entrevistas a receptivos |
| **Madurez digital y destino inteligente** | ¿Cumple el Marco los requisitos DTI de SEGITTUR? | Auditoría web + UNE 178501/178502/178510 | Media. Fuerte componente normativo |
| **Gestión de la reputación online** | ¿Responden las bodegas a sus reseñas, y cambia eso la valoración? | 11,4 % de respuesta; 646 críticas ≤2★ | Media-alta. Exige diseño causal cuidadoso: correlación ≠ efecto |
| **Conectividad aérea y demanda no capturada** | ¿Existe demanda hacia Jerez sin vuelo que la sirva? | Dataestur: 3,25 M de búsquedas desde países sin vuelo directo | Media. Más económico que turístico |

---

## 13. Notas para quien tutorice

1. **Vigilar el riesgo de la sección 0.1.** Si a mitad de curso el trabajo se ha convertido en una
   descripción del cuadro de mando, reconducir hacia la pregunta de segmentación.
2. **El corpus no se mueve.** Está cerrado el 06/07/2026, lo que es una ventaja para un TFG:
   resultados estables y reproducibles durante todo el curso.
3. **El estudiante no necesita programar.** Puede trabajar sobre los CSV de `datos/procesado/` con
   Excel, SPSS, Jamovi o R. Si sabe Python, puede usar los módulos del proyecto, pero no es
   requisito y no debería condicionar la elección del tema.
4. **Exigir la verificación de las referencias marcadas** en la sección 9. Es un hábito que el TFG
   debe instalar.
