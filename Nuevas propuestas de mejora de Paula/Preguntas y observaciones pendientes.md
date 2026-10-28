# Preguntas y observaciones pendientes

Dieciséis cosas que han salido usando el cuadro de mando de ENOLYTICS y que **siguen pendientes**. Lo que ya está arreglado se ha movido a «Observaciones ya resueltas», para que esta lista sea solo lo que queda por hacer.

**Una es un error**: el PDF de la guía sale con el texto cortado. Las otras quince son observaciones: cosas que funcionan pero que en pantalla se leen mal, o que se leen bien pero dicen algo que los datos no sostienen.

| Nº | Asunto | Dónde |
| --- | --- | --- |
| 1 | «Diferencia por visitante» enseña el objetivo, no la diferencia | Simulador → Monetización |
| 2 | La leyenda de varios gráficos imprime «undefined» | Bodega individual · Clientes |
| 3 | Un apunte interno se ha colado en pantalla | Simulador, al pie |
| 4 | La plataforma cita documentos que el bodeguero no ha visto | Guía · Las 7 inteligencias · Recomendaciones |
| 5 | La ficha de ACEVIN repite la muestra dos líneas seguidas | Las 7 inteligencias → Clientes |
| 6 | «Ampliar la oferta» se apoya en una comparación que no la sostiene | Resumen ejecutivo → ¿Qué hacer primero? |
| 7 | 🐞 El PDF de la guía sale con el texto cortado por la derecha | Guía y metodología → descargar PDF |
| 8 | Las marcas de negrita se ven como asteriscos en ese mismo PDF | Guía y metodología → descargar PDF |
| 9 | La guía explica al bodeguero para qué le sirve el documento al proyecto | Guía y metodología, entradilla |
| 10 | Falta un umbral por documentar: el mínimo de 5 menciones | Guía y metodología → sección 5 |
| 11 | «Competidores directos» sin ninguno directo, y el mapa anuncia 4 tipos y enseña 2 | Bodega individual → Competidores |
| 12 | El aviso amarillo del simulador es el mismo en las cuatro pestañas | Simulador, arriba |
| 13 | «Pensado para entregar a la bodega», dicho a la propia bodega | Bodega individual → Recomendaciones |
| 14 | «Recursos (lo que ofreces)» define el constructo por cómo se mide | Bodega individual → Competidores |
| 15 | Hay dos «medias del Marco» distintas y las dos se llaman igual | Resumen ejecutivo · Informe de bodega |
| 16 | El globo del mapa de competidores enseña un campo interno | Bodega individual → Competidores |

---

## 1. «Diferencia por visitante» enseña el objetivo, no la diferencia

**Qué pasa.** En *Simulador «¿y si…?» → Monetización*, con el mando puesto en 50,40 €, las tres tarjetas de resultado dicen:

| Ingresos proyectados | Diferencia por visitante | Variación |
|---|---|---|
| 21,5 M€  ↑ 4,3 M€ | **50,4 €**  ↑ 10,0 € | 24,7 % |

El número grande de la tarjeta central, **50,4 €, es el ingreso por visitante objetivo** —el valor al que acabas de llevar el mando—, no la diferencia. La diferencia son los 10,0 € de la flechita.

Es **el mismo patrón que la tarjeta «Media nacional»**, ya corregida: el rótulo describía el delta y no el número que encabeza la tarjeta.

**Qué proponemos.** Llamarla **«Ingreso por visitante objetivo»** y dejar el «↑ +10,0 €» como delta, que es lo que ya hace. Es lo más útil de las dos opciones: el objetivo es lo que el usuario acaba de elegir con el mando, y el delta responde solo a «¿cuánto he subido?».

Y ya que van dos, **merece la pena repasar de una vez todas las tarjetas que llevan delta**, a ver si en alguna más el rótulo describe la flechita en lugar del número.

---

## 2. La leyenda de varios gráficos imprime «undefined»

**Qué pasa.** En tres gráficos distintos sale la palabra `undefined` donde debería ir el título de la leyenda:

| Dónde | Qué se lee |
|---|---|
| Bodega individual → Competidores → «Mapa del terreno competitivo (Kamensky)» | `undefined` delante de «Marginal» y «Potencial» |
| Las 7 inteligencias → Clientes → «Perfil de los atributos: ¿higiénico o deleitador?» | `undefined` encima del gráfico |
| Las 7 inteligencias → Clientes → «¿De qué habla junto el visitante? (co-word)» | `undefined` debajo de los filtros |

**Por qué, aparentemente.** Es el mismo caso en los tres: son gráficos con leyenda de categorías a los que se les pasa un título que no existe, y la librería lo pinta como el texto literal en lugar de omitirlo.

**Qué proponemos.** Ponerle título o quitarlo, según el gráfico. Los naturales serían **«Tipo de competidor»** en el mapa de Kamensky, **«Atributo»** en el perfil higiénico/deleitador y **«Aspecto»** en el de co-ocurrencias. Y donde no haga falta título, pasar un valor vacío de verdad en vez de una variable sin definir.

Es cosmético, pero **se ve mucho**: el mapa de Kamensky es de las pantallas que se enseñan en la demo, y un «undefined» en pantalla resta bastante.

---

## 3. Un apunte interno se ha colado en la pantalla del simulador

**Qué pasa.** Al pie del *Simulador «¿y si…?»*, debajo de las palancas, se lee:

> Las palancas usan modelos ya presentes en la plataforma (ingreso/visitante de ACEVIN, cruceros de Dataestur, reseñas de Google, mapa IPA por impacto/PRCA). **Idea de Paula (propuesta de mejora, Pieza 3).**

**La primera parte está bien y conviene que se quede**: dice que las palancas no se inventan nada, que reutilizan los modelos que ya hay en la plataforma. Eso es justo lo que alguien se pregunta al ver un simulador.

**Lo que sobra es la segunda.** «Idea de Paula (propuesta de mejora, Pieza 3)» es una nota interna: un crédito entre nosotros y una referencia a un documento de trabajo que quien usa la plataforma no ha visto nunca. En una pantalla pública no dice nada y despista.

**Qué proponemos.** Dejar la línea de los modelos y borrar la atribución. Y de paso, mirar si hay más apuntes de este tipo en otras vistas: los que citan documentos internos («Pieza 3», «propuesta de mejora») o quién propuso qué.

---

## 4. La plataforma cita documentos que el bodeguero no ha visto

**De dónde sale esto.** En varias pantallas se nombran documentos internos del proyecto —la memoria científico-técnica y el programa FEDER— como si el usuario los conociera. Quien abre la plataforma es un bodeguero o un gestor del destino, y para él son papeles que no ha leído nunca. Es el mismo patrón que la observación 3, así que conviene arreglarlos de una pasada.

**Van por tres familias.**

**a) La cabecera de la guía.** Va aparte, en la **observación 9**: ahí pedimos quitar la frase entera —«Sirve al bodeguero para entenderlo y al proyecto como documentación metodológica (anexo para FEDER)»— y no solo el paréntesis.

**b) Las citas a la memoria.** Son cinco sitios visibles. Ojo: **lo que sobra es la cita, no el contenido**. Que cada inteligencia declare su objetivo y sus indicadores previstos está muy bien y hay que conservarlo; lo que no aporta es de qué documento salen.

| Dónde | Dice ahora | Podría decir |
|---|---|---|
| `app.py:832` · en **las siete pestañas** | «🎯 **Objetivo (Memoria Científico-Técnica):** …» | «🎯 **Qué mide esta inteligencia:** …» |
| `app.py:833` · en **las siete pestañas** | «Categoría SEGITTUR: … · Indicadores previstos **(Tabla 1 de la memoria)**» | «… · Indicadores previstos» |
| `app.py:1452` · Competidores | «⚠️ Pendiente **(Tabla 1 de la memoria)**: comparación de precios…» | «⚠️ Todavía no disponible: comparación de precios…» |
| `app.py:1468` · Clientes, ayuda de la métrica | «Cubre el indicador «Volumen de visitas…» **de la memoria**.» | quitar la coletilla |
| `app.py:1481` · Clientes, perfil ACEVIN | «Cubre los indicadores de perfil, motivaciones y canales **de la memoria**.» | quitar la frase entera |

Las dos primeras están en la misma función, así que **un solo arreglo corrige las siete pestañas**.

**c) Las menciones a FEDER dentro de las recomendaciones — esto, para decidir.** Hay cuatro: dos avisos en `app.py` (cruceros y oferta) y dos recomendaciones en `recomendaciones.py` (diversificar la oferta y reducir la estacionalidad). Todas dicen «prioridad **FEDER P4A**». A un bodeguero eso no le dice nada: es el código de una línea del programa, y la recomendación se entiende igual —y mejor— diciendo solo qué persigue. **Pero esta es vuestra decisión**, porque puede interesar que la herramienta enseñe su alineación con el programa. Si se quedan, convendría explicar qué es P4A la primera vez que sale.

**Lo que NO hay que tocar.** Los comentarios y *docstrings* del código que citan la memoria (en `ipa.py`, `recomendaciones.py`, `reputacion.py`, `nlp/`, las tres de `ingesta/`) están muy bien donde están: sirven para saber qué indicador cubre cada módulo y no los ve nadie desde la web. Y «Federación Española del Vino» / «FEV», en la pestaña de sostenibilidad, no tienen nada que ver con FEDER.

**Cómo lo hemos mirado.** La cabecera de la guía, sobre la plataforma en vivo. Lo demás, sobre el código del prototipo de julio: **conviene confirmarlo**, porque la guía ha cambiado desde entonces y puede que esto también.

---

## 5. La ficha de ACEVIN repite la muestra dos líneas seguidas

**Qué pasa.** En *Las 7 inteligencias → Clientes*, en el bloque «Perfil del enoturista», el tamaño de la muestra y el nivel de confianza salen **dos veces, una debajo de la otra**:

| Línea | Dice |
|---|---|
| La de la fuente (`app.py:1476`) | ACEVIN — Análisis de la demanda turística **(628 encuestas, 95% de confianza, ±3,9%)** |
| El aviso de debajo (`app.py:1478`) | ⚠️ Dato nacional, no específico del Marco: ACEVIN no desglosa por ruta **(628 encuestas, 95% confianza)**. Sirve como referencia… |

**Qué pedimos.** Quitarlo del **aviso de abajo** y dejarlo solo en la línea de la fuente, que además es la más completa: es la única que trae el margen de error (±3,9 %). El aviso queda mejor centrado en lo suyo, que es la advertencia de que el dato es nacional.

**Ojo, es la misma línea que la observación 4.** Ese mismo aviso termina con «Cubre los indicadores de perfil, motivaciones y canales **de la memoria**», que también sobra. Los dos arreglos son una sola edición:

> ⚠️ **Dato nacional**, no específico del Marco: ACEVIN no desglosa por ruta. Sirve como **referencia** para comparar y como plantilla validada para un cuestionario propio.

**Es el mismo patrón que las dos primeras que ya arreglaste** —las recomendaciones duplicadas y la leyenda repetida—: algo que se cuenta dos veces en sitios distintos y que hay que mantener por duplicado.

---

## 6. La recomendación «ampliar la oferta» se apoya en una comparación que no la sostiene

**Qué pasa.** En *Resumen ejecutivo → ¿Qué hacer primero?*, la recomendación **«Ampliar y diversificar la oferta enoturística · Negocios»** justifica así su diagnóstico:

> El Marco es 1º en visitantes pero solo 7º en oferta (111 servicios, frente a los 334 de Ribera del Duero). **La oferta no acompaña a la demanda.**

Los dos números son correctos. Lo que no se sostiene es la conclusión, y se ve comparando con la ruta que **monetiza** mejor en vez de con la que más servicios tiene. Con los propios CSV de la plataforma (`acevin/visitantes_rutas.csv`, `ingresos_rutas.csv` y `oferta_rutas.csv`, año 2024):

| Ruta | Servicios | Visitantes | Ingresos | Ingreso por visita |
|---|---|---|---|---|
| Rioja Alta | **112** | 316.922 | 22,2 M€ | **70,0 €** |
| Penedès | 250 | 369.170 | 19,2 M€ | 52,0 € |
| Marco de Jerez | **111** | 425.652 | 17,2 M€ | **40,4 €** |

**Rioja Alta tiene 112 servicios y el Marco 111** —uno más, prácticamente la misma oferta— y allí cada visita deja 30 € más. Y **Penedès, con más del doble de oferta que Rioja Alta, ingresa 18 € menos por visita**. Si la oferta alrededor explicara la monetización, el orden sería el contrario.

**Qué proponemos.** Dos cosas, y ninguna es quitar la recomendación:

1. **Cambiar el diagnóstico por la comparación que sí discrimina:** «con una oferta equivalente a la de Rioja Alta (111 frente a 112 servicios), el Marco ingresa 40,4 € por visita frente a 70,0 €. La diferencia no está en la oferta de alrededor, sino dentro de la visita». Eso además enlaza con la recomendación «Elevar el ingreso por visitante», que ya está en la misma lista y apunta al precio de la visita, la tienda y las experiencias premium.
2. **Mantener la acción, pero con su motivo propio.** Diversificar la oferta sigue teniendo sentido por otras razones —estancia media, pernoctaciones, desestacionalización—, y con esos indicadores debería justificarse. Lo que no procede es presentarla como la causa de la brecha de ingreso por visita.

**Por qué corre cierta prisa.** Esta recomendación se lee en la primera pantalla de la herramienta, y **dice lo contrario que la presentación del proyecto**, donde el argumento de partida es justamente que la oferta no explica la brecha.

**Un límite de la comprobación:** de **Ribera del Duero no hay ingresos de 2024** en los archivos, así que no sabemos cuánto ingresa por visita; y solo tres rutas tienen los tres datos a la vez. No es una demostración estadística, pero basta para ver que la oferta no ordena la monetización.

---

## 7. 🐞 ERROR — el PDF de la guía sale con el texto cortado por la derecha

**Qué pasa.** En *Guía y metodología*, al descargar la guía en PDF (`ENOLYTICS_guia_de_uso.pdf`), **muchas líneas pierden sus últimas palabras**. No es el visor: está en el archivo. Medido sobre el PDF generado el 9/09/2026:

| | |
|---|---|
| Tamaño de página | A4, 595,3 × 841,9 pt (210 × 297 mm) |
| El texto empieza en | x = 31,2 pt (**11 mm** de margen izquierdo) |
| El texto termina en | x = 599,6 pt → **1,5 mm POR FUERA del papel** |
| Anchura a la que se parten las líneas | 568,4 pt (**200,5 mm**) |
| Anchura que cabe con esos márgenes | 532,9 pt (**188 mm**) |
| Sobra | **35,5 pt ≈ 12,5 mm** |

**Cuántas líneas afecta.** 23 en total: 13 en la página 1 y 10 en la página 2. La página 3 se salva solo porque sus líneas son más cortas y no llegan al tope.

Ejemplos de lo que se pierde:

- «Con 6, «Entorno y viñedo» de Barbadillo salía 5,00 y una sola rese…» → se corta *reseña de 3★*
- «Sale de la distribución real de las 162 brechas bodega-atributo del Marco (percentil 25…» → se corta el valor
- «Umbral de Kano … Tomado de Pratt et al. (2020), el mismo que usan Han et…» → se corta *al.*
- «…y acumula 5 o más críticas de 1…» → se corta *-2★*

**No es un problema de indentación.** Todas las líneas afectadas empiezan en el mismo x=31,2 que las que sí caben; lo que falla es la anchura de salto de línea, que es mayor que el área imprimible.

**Qué proponemos.** Que la anchura con la que se compone el texto sea **ancho de página − margen izquierdo − margen derecho**, en vez de la que se está usando ahora. Con 11 mm a cada lado son 188 mm. Y de paso subir los márgenes a 15-20 mm, que 11 mm es muy justo para un documento que se va a imprimir.

**Cómo comprobar que queda arreglado:** abrir el PDF y verificar que ninguna línea pasa del borde; o, en Python, `fitz.open(pdf)` y comprobar que ningún `line["bbox"][2]` supera `page.rect.width` menos el margen.

---

## 8. Las marcas de negrita se ven como asteriscos en el PDF de la guía

**Qué pasa.** En la misma exportación, en el apartado de umbrales, se lee literalmente:

> 0 % · 5 críticas — Se recomienda empezar a responder reseñas si la bodega no ha contestado `**ninguna**` y acumula 5 o más críticas de 1-2★.

Los dos pares de asteriscos salen impresos en vez de poner la palabra en negrita. Aparecen **dos veces** en el documento.

**Y pasa también en el informe de bodega**, que es otro PDF distinto. En *Bodega individual → Recomendaciones → Descargar informe*, la primera recomendación dice:

> Responder es `**gratis**` y es lo primero que ve quien duda.

O sea que no es cosa de una cadena suelta de la guía: **son al menos dos generadores de PDF con el mismo problema**. Y el informe de bodega es el documento que se entrega a la bodega, así que ahí se ve más.

**Qué proponemos.** O convertir el marcado a negrita al generar los PDF, o quitar los asteriscos del texto de origen si esas cadenas no pasan por un conversor de Markdown. Conviene **revisar de una vez todas las cadenas de los dos documentos**, porque si dos llevan marcado sin convertir es probable que haya más.

---

## 9. La guía le explica al bodeguero para qué le sirve el documento al proyecto

**Qué pasa.** En la entradilla de *Guía y metodología* se lee:

> …de dónde sale cada indicador. **Sirve al bodeguero para entenderlo y al proyecto como documentación metodológica (anexo para FEDER).**

**Qué pedimos.** Quitar esa frase entera. Lo que hace es contarle al usuario que la pantalla que está leyendo cumple además un trámite nuestro, y eso no le aporta nada: al bodeguero le da igual que el documento valga de anexo, y al que no sea del proyecto le suena a que está leyendo papeleo ajeno. La guía se explica sola diciendo qué es cada apartado y de dónde sale cada dato, que es justamente lo que dice la frase anterior.

**Es el mismo patrón que la observación 4**, la de las citas a documentos que el bodeguero no ha visto: lenguaje interno del proyecto que se ha colado en la parte que ve el usuario. Merece la pena **repasar de una pasada toda la guía** buscando menciones a la memoria, a FEDER, a anexos y a entregables.

**Nota:** esta frase **no está en el prototipo de julio** que tenemos en el zip, así que es posterior; hay que buscarla en la versión viva.

---

## 10. Falta un umbral por documentar en la guía

**Qué pasa.** La sección **«5 · Los umbrales: de dónde sale cada listón»** documenta doce de los trece listones que usa la plataforma. El que falta es el **mínimo de 5 menciones para que un aspecto aparezca en la ficha de una bodega**.

Está en el código como `MIN_MENCIONES = 5` (`reputacion.py`, línea 36) y filtra la función `aspectos()`, que es la que decide qué aspectos se enseñan.

**Ojo, no es el mismo que el de 8, que sí está documentado.** Son dos listones distintos y conviene que la guía los distinga:

| Umbral | Qué decide |
|---|---|
| **5 menciones** (`MIN_MENCIONES`) | Si el aspecto **se enseña** en la ficha de la bodega |
| **8 menciones** (ya en la guía) | Si se **publica la nota** de ese atributo |

**Qué pedimos.** Añadir el de 5 al grupo que le corresponda —si tiene base metodológica, con su razón; si es criterio del equipo, dicho como tal, que también vale— y dejar claro en qué se diferencia del de 8. Con eso la lista queda completa.

---

## 11. El bloque se titula «competidores directos» y ninguno lo es

**Qué pasa.** En *Bodega individual → Competidores*, el bloque se encabeza **«TUS COMPETIDORES DIRECTOS»**. Debajo, en González Byass, los cinco que salen están etiquetados así:

| | Bodega | Etiqueta |
|---|---|---|
| 1 | Bodegas Lustau | **Marginal** · recursos parecidos, pero apunta a otro cliente |
| 2 | Bodegas Dios Baco | **Potencial** · hoy distinto en cliente y recursos: vigílalo |
| 3 | Bodegas Barbadillo | **Potencial** |
| 4 | Bodegas Osborne | **Potencial** |
| 5 | Bodega, Viña y Casa Rural Santa Petronila | **Potencial** |

**Ninguno es «Directo».** La leyenda del mapa de Kamensky que va justo debajo lo confirma: solo tiene dos entradas, Marginal y Potencial. O sea que el titular promete una cosa y el contenido dice exactamente la contraria.

**Por qué importa.** Quien lea solo el encabezado se lleva que esas cinco son sus competidoras directas, que es justo lo que la plataforma está negando. Y quien lea las etiquetas se queda sin entender por qué el bloque se llama así. Nos pasó a nosotros preparando la charla: escribimos «esta bodega no tiene ni un competidor directo» leyendo las etiquetas, mientras el titular decía lo otro.

**Qué proponemos.** Titular el bloque por lo que de verdad enseña —**«Tu grupo competitivo»** o **«Tus competidores más cercanos»**— y reservar la palabra «directo» para las que la plataforma categorice como tales. Si el orden de la lista es por cercanía, decirlo en la línea de debajo: ya explica el método, puede explicar también el criterio de orden.

**⚠️ Y está en dos sitios, no en uno.** El **informe de bodega en PDF** repite el mismo encabezado y la misma lista, con las mismas etiquetas Marginal/Potencial. Ahí, además, va debajo la leyenda de los cuatro tipos de Kamensky, que ayuda; pero el titular sigue diciendo «directos». Los dos textos hay que cambiarlos a la vez.

**Y el título no falla siempre: falla a veces, que es peor.** El encabezado es fijo, pero lo que aparece debajo cambia de una bodega a otra:

| Bodega | Qué sale debajo del título | ¿Encaja el título? |
|---|---|---|
| **González Byass – Tío Pepe** | Lustau (Marginal) y cuatro Potenciales. **Ninguno directo** | **No.** El título anuncia «directos» y la propia herramienta dice que no hay ninguno |
| **Otra bodega que hemos abierto** | Bodegas Tradición sale como **Core · mismo cliente y recursos parecidos: tu rival más directo** | **Sí.** Ahí sí hay un competidor directo |

**Y ese es justamente el problema: quien lo lee no puede saber en cuál de los dos casos está.** Si abre una bodega y lee «tus competidores directos», da por hecho que esos cinco lo son. En González Byass eso es falso, y para darse cuenta hay que fijarse en las etiquetas pequeñas de cada línea y saber qué significa «Marginal».

Dicho en corto: **un título que no cambia no puede describir bien un contenido que sí cambia.** Por eso conviene titularlo con algo que sea verdad siempre y dejar que la etiqueta de cada bodega diga si es directa o no.

**El mapa de debajo tiene el mismo problema, en versión gráfica.** Su pie promete que «las líneas separan **los cuatro tipos**», pero la leyenda enseña solo los que tienen alguien dentro: en González Byass, dos; en otras bodegas, tres. Quien lo mire cuenta dos donde le han anunciado cuatro.

**Qué proponemos para el mapa.** Que la leyenda muestre **siempre los cuatro tipos**, con los vacíos en gris o con un «(0)» al lado. Así el pie deja de contradecirse y, de paso, **se ve el resultado**: que una bodega no tenga ningún rival directo es información, y ahora mismo se pierde en silencio.

---

## 12. El aviso amarillo del simulador es el mismo en las cuatro pestañas

**Qué pasa.** En *Simulador «¿y si…?»*, el aviso amarillo de arriba no cambia al cambiar de pestaña:

> ⚠️ **Esto proyecta un escenario, no predice el futuro.** Cada palanca aplica una regla **lineal y sencilla** («si el ingreso por visitante sube a X, y todo lo demás sigue igual, los ingresos serían Y»). Sirve para **ordenar prioridades y dimensionar una decisión**, no como una previsión. Los supuestos de cada palanca se explican debajo de su resultado.

**El ejemplo del paréntesis es de Monetización**, así que en las otras tres se está leyendo el ejemplo de una palanca que no se está usando.

**Y en una de ellas el aviso se contradice con la propia pantalla.** En *Respuesta a críticos*, el recuadro azul de debajo dice que la palanca es «un **objetivo de gestión**, no una predicción de estrellas» y que «**no afirmamos** que suba la nota media». Pero el aviso de arriba dice que aplica «una regla lineal» que proyecta un resultado. Son dos mensajes distintos sobre la misma palanca, y a diez centímetros uno del otro.

De hecho esa palanca **no aplica ningún modelo**: es aritmética exacta —a las 56 críticas contestadas le suma las que marques y lo divide entre 646—. Llamarla «regla lineal» la hace parecer un modelo cuando es un recuento.

**Qué proponemos, de lo más barato a lo mejor:**

1. **Lo mínimo:** quitar el paréntesis del ejemplo. El aviso se queda cierto para las cuatro, y la frase que ya lleva —«los supuestos de cada palanca se explican debajo de su resultado»— es verdad y basta.
2. **Lo bueno:** que el ejemplo cambie con la pestaña. Uno por palanca:

| Pestaña | Ejemplo |
|---|---|
| Monetización | «si el ingreso por visitante sube a X, y todo lo demás sigue igual, los ingresos serían Y» |
| Cruceros | «si captáramos el X % de los cruceristas, serían Y visitantes más» |
| Respuesta a críticos | «si se contestaran X críticas, la tasa de respuesta pasaría a Y %» — **y aquí sin llamarlo regla lineal**, porque es una cuenta exacta |
| Calidad percibida | «si el sentimiento hacia un aspecto pasara a X, se recolocaría aquí en el mapa» |

La primera frase —«esto proyecta un escenario, no predice el futuro»— vale para las cuatro y conviene que se quede fija.

---

## 13. «Pensado para entregar a la bodega», dicho a la propia bodega

**Qué pasa.** En *Bodega individual → Recomendaciones*, el bloque del informe descargable dice:

> **INFORME DE LA BODEGA**
> Un PDF de una página con la reputación, los competidores directos, las fortalezas/debilidades y qué hacer. **Pensado para entregar a la bodega.**

**La primera frase está bien y se queda**: dice qué trae el PDF, que es lo que uno quiere saber antes de descargarlo. **Lo que sobra es la segunda.** Quien está leyendo esa pantalla **es la bodega**, o alguien que trabaja para ella. Decirle «pensado para entregar a la bodega» le habla de sí mismo en tercera persona y deja ver que la frase se escribió pensando en nosotros —en para qué nos sirve a nosotros el informe—, no en quien lo va a usar.

**Qué proponemos.** Borrarla. Si se quiere decir algo del formato, que sea útil para quien descarga: *«Una página, lista para imprimir»*.

**Es el tercero de la misma familia** —con las observaciones 3 y 9—: texto escrito desde dentro del proyecto que ha acabado en la parte que ve el usuario. Los tres son de una línea y se arreglan en una sola pasada; **merece la pena repasar de una vez todas las cadenas visibles** buscando este patrón, en vez de ir cazándolas de una en una.

**Y un detalle de coherencia:** esa misma frase dice «los competidores **directos**», que es justo lo que señala la **observación 11**. Si se cambia el título de aquel bloque, conviene cambiar también esta descripción.

---

## 14. «Recursos (lo que ofreces)» define el constructo por cómo se mide

**Qué pasa.** En *Bodega individual → Competidores*, la línea que explica el método dice:

> Las bodegas más parecidas a la tuya por **mercado** (a qué cliente sirves) y por **recursos** (**lo que ofreces**). No es todo el Marco, sino **tu grupo**.

La glosa de *mercado* está bien. La de **recursos, no**: en el marco de Chen, los recursos son **lo que la empresa posee**, no lo que pone a la venta.

**Lo que dice nuestro propio paper de ACEDE** (`Main_document_ACEDE.docx`), citando a Chen (1996: 106-107):

> *Resource Similarity*: «the degree to which the **strategic resources** of two firms are comparable».

Y a lo largo del texto lo subraya: «RS refers to **resource endowments possessed by firms**»; «Resources… are **owned by organizations** and deployed across multiple products and markets»; las variables de RS «reflect the **capabilities, resources, and strategic endowment** that characterize each producer». Incluso descarta expresamente derivarlas del sentimiento del consumidor «because RS aims to capture **genuine organizational resources** rather than subjective perceptions».

**De dónde viene la confusión, que es entendible.** Las variables con las que se mide RS sí se construyen a partir de lo que la bodega saca al mercado: número de vinos, amplitud de cartera, diversidad de estilos, posicionamiento y dispersión de precio. Pero eso es **el proxy, no el constructo**, y el propio paper lo declara como limitación:

> «the eight RS variables employed capture observable resources **through wineries' commercial outputs**, but equally determinant strategic dimensions such as distribution capability, financial resources, **intangible brand assets**, or the historical heritage of the soleras **escape the available variables**»

Es decir: los recursos incluyen los **intangibles** —marca, patrimonio, soleras centenarias, capacidad de distribución—, y lo medible es solo la parte que asoma en el mercado. La pantalla está describiendo la medida como si fuera la definición, y con eso pierde el sentido del concepto.

**Qué proponemos.** Cambiar la glosa por **«recursos (con los que cuentas para competir)»**, o simplemente «recursos con los que cuentas». Y si se quiere ser transparente con el proxy, que eso vaya en la **guía**, no en la línea de la pantalla: *«los recursos se aproximan con lo observable desde fuera —tamaño y variedad de la cartera, posicionamiento de precio—; los intangibles, como la marca o el patrimonio, no entran en el cálculo»*. Esa frase, además, es de las que dan confianza.

**⚠️ La frase está en dos sitios.** El **informe de bodega en PDF** repite la misma línea palabra por palabra. Hay que cambiar las dos.

**Y lo que de verdad se está midiendo lo dice el pie del propio mapa:**

> 🟡 Estimación / proxy · Rasgos de la bodega: **servicios, certificación y madurez digital (recursos)**; perfil de sentimiento por atributo, nota, ubicación e idioma (mercado).

**De las tres cosas que forman «recursos», dos no son «lo que ofreces»**: la certificación FEV y la madurez digital son capacidades que la bodega tiene, no cosas que pone a la venta. Solo «servicios» encaja con la glosa actual. O sea que la línea de arriba no describe ni el concepto ni la medida: describe un tercio de la medida.

**Qué proponemos, ahora que sabemos las variables.** Que la glosa diga el concepto —**«recursos (con los que cuentas para competir)»**— y que la guía explique la medida en una línea: *«los recursos se aproximan con tres rasgos observables de la bodega: los servicios que ofrece, su certificación y su madurez digital. Los intangibles —marca, patrimonio, capacidad de distribución— no entran en el cálculo»*. Esa segunda frase, además, es de las que dan confianza.

**No confundirlas con los ocho aspectos de la visita** (visita, vino y cata, instalaciones, personal y trato, precio, gastronomía, organización y reserva, entorno): esos salen del texto de las reseñas y alimentan la reputación, el IPA y el Kano. Los rasgos de recursos son características de la bodega como empresa y solo alimentan el eje «recursos» del mapa de competidores. Son dos listas distintas que se prestan a confusión —nos pasó a nosotros—, así que **conviene que la guía las distinga explícitamente**.

**Nota sobre el paper.** El artículo de ACEDE mide *Resource Similarity* con ocho variables del catálogo de Vivino (número de vinos, amplitud de cartera, diversidad de estilos, posicionamiento y dispersión de precio…). La plataforma usa otras tres, porque Vivino todavía no está integrado. **No es un problema** —son dos operacionalizaciones del mismo constructo—, pero conviene que la guía diga cuál usa la herramienta, para que nadie busque en la plataforma las variables del artículo.

---

## 15. Hay dos «medias del Marco» distintas, y las dos se llaman igual

**Qué pasa.** La valoración media del Marco aparece con dos valores según dónde se mire:

| Dónde | Dice |
|---|---|
| Resumen ejecutivo → tarjeta «Valoración del destino» | **4,56 / 5**, sobre 10.972 reseñas |
| Informe de bodega en PDF → «vs. media del Marco» | **media 4,67** (y de ahí sale el −0,48 de González Byass) |

**Las dos son correctas.** Lo hemos calculado sobre `datos/procesado/resenas.csv`:

| Cómo se calcula | Resultado |
|---|---|
| Media **ponderada por reseña** (las 10.972 juntas) | **4,560** |
| Media **simple de las 41 bodegas** (cada bodega pesa igual) | **4,677** |
| Media simple de las 33 con 30 reseñas o más | 4,631 |

La diferencia es la de siempre: en la media simple, una bodega con 20 reseñas pesa lo mismo que una con 1.689, y las pequeñas puntúan más alto.

**Por qué importa.** Cambia la brecha que se le enseña a la bodega. González Byass tiene un 4,20, así que su distancia con «el Marco» es **−0,36** contra la media ponderada y **−0,48** contra la simple. El informe usa la segunda. No está mal, pero **el bodeguero ve 4,56 en la pantalla y 4,67 en su informe, y nadie le dice que son dos cuentas distintas**.

**Qué proponemos.** Elegir una de las dos para «la media del Marco» y usarla en todas partes; y si hacen falta las dos, **que cada una diga cuál es** —«media de las 41 bodegas» frente a «media de todas las reseñas»— y que la guía lo explique en una línea.

**Es el mismo patrón que ya vimos con las tasas de respuesta:** en una pantalla sale «11 % de reseñas contestadas» (ponderado por reseña) y en otra «13 % de respuesta media del Marco» (media simple de las 33 bodegas). También son las dos correctas, y también están a tres pantallas una de otra. **Merece la pena repasar de una pasada todos los promedios del destino** y decidir el criterio de una vez.

---

## 16. El globo del mapa de competidores enseña un campo interno

**Qué pasa.** Al pasar el ratón por un punto del *Mapa del terreno competitivo (Kamensky)*, el globo dice:

> **Viña La Torre**
> Tipo de competidor=Sustituto
> ◄ mismo cliente · distinto cliente ►=0.11
> ◄ recursos parecidos · recursos distintos ►=0.316
> **icono=**🔄

Hay tres cosas ahí:

1. **`icono=` no debería salir.** Es una columna interna que se usa para dibujar el punto y se ha colado en el globo. Es el mismo caso que los `undefined` de la **observación 2**: campos que llegan al usuario sin querer.
2. **Los nombres de los campos son las etiquetas de los ejes**, con sus flechitas y todo, y en un globo quedan ilegibles: «◄ mismo cliente · distinto cliente ►=0.11» no se entiende.
3. **Los números no dicen su unidad.** Son distancias entre 0 y 1, pero ahí aparecen desnudos.

**Qué proponemos.** Elegir a mano qué se enseña en el globo y con qué nombre. Algo así:

> **Viña La Torre**
> Sustituto · mismo cliente, recursos distintos
> Distancia de mercado: 0,11 · Distancia de recursos: 0,32

Y quitar del globo todas las columnas auxiliares. **Este gráfico es de los que se enseñan en la demo**, y el globo salta con solo pasar el ratón por encima.

---
