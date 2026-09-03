# Preguntas y observaciones pendientes — revisión de la plataforma

> Enviado por **Paula (IP)** el **03/09/2026**. Original de diseño en
> [`04_preguntas_y_observaciones.html`](04_preguntas_y_observaciones.html).
> **La numeración de aquí es la del documento**, para poder decir «la 4» y entendernos.

> **✅ ESTADO: las diez, aplicadas el 03/09/2026.** Ver la sesión del 03/09 en
> [`../CONTEXTO.md`](../CONTEXTO.md) para el detalle de cómo se resolvió cada una.

Diez puntos salidos de usar el cuadro de mando: **2 errores** (4 y 5) y **8 observaciones**
(cosas que funcionan pero que en pantalla se leen mal).

| # | Qué | Tipo | Dónde | Estado |
|---|-----|------|-------|--------|
| 1 | Las recomendaciones del destino salen dos veces (14 ≠ 12) | Observación | Resumen ejecutivo + 7 inteligencias | ✅ |
| 2 | «Categoría SEGITTUR: Sostenibilidad» en la pestaña Económica parece una errata | Observación | 7 inteligencias → Económica | ✅ |
| 3 | «Cómo leer los datos» sale tres veces | Observación | 7 inteligencias + Guía §1 y §5 | ✅ |
| 4 | **Bodega individual revienta si el filtro de localidad se queda vacío** | 🐞 Error · urgente | Bodega individual | ✅ |
| 5 | Una bodega con dos localidades se cuenta como localidad nueva | 🐞 Error | Filtro de localidad (barra lateral) | ✅ |
| 6 | La tarjeta «Media nacional» compara al revés | Observación | Económica | ✅ |
| 7 | «Diferencia por visitante» enseña el objetivo, no la diferencia | Observación | Simulador → Monetización | ✅ |
| 8 | La leyenda de varios gráficos imprime «undefined» | Observación | Kamensky, Kano, co-ocurrencias | ✅ |
| 9 | Un apunte interno («Idea de Paula, Pieza 3») se ha colado en pantalla | Observación | Simulador, al pie | ✅ |
| 10 | Los umbrales del motor de recomendaciones no están documentados | Observación | Guía y metodología | ✅ |

---

## 1. Las recomendaciones del destino salen dos veces

**Qué pasa.** La lista de recomendaciones accionables aparece en el **Resumen ejecutivo**
(«14 recomendaciones · 10 de prioridad alta») y otra vez en **Las 7 inteligencias**
(«las 12 recomendaciones accionables del destino»). Ya se han **desincronizado: 14 ≠ 12**.

**Propuesta.** Dejar la lista priorizada **solo en el Resumen ejecutivo** —es para lo que
sirve esa vista— y que en Las 7 inteligencias cada recomendación aparezca **dentro de la
pestaña de su propia inteligencia**, junto al dato que la justifica. Todas declaran ya la
suya («· Clientes», «· Negocios», «· Económica»), así que el reparto está hecho.

Con eso no se repite, no puede volver a descuadrarse, y se ven juntas evidencia y acción.

## 2. «Categoría SEGITTUR: Sostenibilidad» en la pestaña Económica

**Qué pasa.** **El dato es correcto** y viene bien traído de `config.py` (es lo que dice la
Tabla 1 de la memoria). Pero en lenguaje corriente «sostenibilidad» significa *ambiental*, y
verlo encabezando la pestaña *Económica* hace pensar que se ha cruzado algo. La respuesta
está dentro del desplegable (los tres indicadores son económicos y sociales, ninguno
ambiental), pero **hay que abrirlo**.

**Propuesta.** No tocar el dato: añadir una **aclaración de una línea** donde sale la
categoría — *«En SEGITTUR, la sostenibilidad incluye el pilar económico y social, no solo el
ambiental»*.

## 3. «Cómo leer los datos» sale tres veces

**Qué pasa.** El bloque de la leyenda de procedencia es la misma función `leyenda_origenes()`
pintada en dos sitios, y la guía vuelve sobre lo mismo en una tercera sección:

- «Cómo leer los datos: el origen de cada indicador» → Guía §1
- «Cómo leer los datos: origen de cada indicador» → 7 inteligencias
- «De dónde salen los datos» → Guía §5

**Propuesta.** Separar **recordatorio** de **explicación**:

- **En las vistas con datos:** una línea siempre visible con los tres puntos y su etiqueta
  (🟢 oficial · 🔵 observado · 🟠 estimación). Nada más.
- **En la guía:** **fundir §1 y §5 en una sola sección**, usando los tres colores como
  encabezados y colgando las fuentes de cada uno:
  - **Dato oficial** — ACEVIN · Dataestur/SEGITTUR · FEV · Ruta del Vino y Brandy
  - **Dato observado** — Reseñas de Google · Google Trends · auditoría web propia + OpenStreetMap
  - **Estimación / proxy** — *sin fuentes*: es un cálculo nuestro a partir de lo anterior.

Que el ámbar **no tenga fuentes** se ve muy bien así: no es un origen, es un cálculo nuestro.
Ahora mismo eso queda escondido.

## 4. 🐞 «Bodega individual» revienta si el filtro de localidad se queda vacío — URGENTE

**Qué pasa.** Si en la barra lateral se desmarcan todas las localidades, la vista **Bodega
individual** cae con un `IndexError`:

```
File "app.py", line 2362, in <module>
    b = df_f[df_f["nombre"] == nombre].iloc[0]
IndexError: single positional indexer is out-of-bounds
```

**El fondo del asunto no es de código sino de recorrido.** El filtro vive en la barra
lateral, o sea **fuera** de la vista, pero decide lo que esa vista puede enseñar. Quien entra
en «Bodega individual» sin haber tocado el filtro no tiene manera de saber que hay un filtro
puesto en otro sitio: solo ve un desplegable vacío y un error rojo. Y ese es justo el orden
natural de quien abre la aplicación por primera vez.

**Cómo arreglarlo**, de lo más urgente a lo más de fondo:

1. **Que nunca aparezca un traceback.**
   ```python
   if df_f.empty:
       st.info("No hay bodegas con el filtro actual. "
               "Amplía la selección de localidades en la barra lateral.")
       st.stop()
   ```
   Conviene mirar si hay **más `.iloc[0]` sobre tablas filtradas** con el mismo riesgo.
2. **Que vacío signifique «todas»**, que es lo que cualquiera espera de un filtro:
   ```python
   df_f = df if not sel_local else df[df["localidad"].isin(sel_local)]
   ```
3. **Que el filtro se vea desde la vista**: una línea encima del selector con el filtro
   activo y la manera de quitarlo («Filtrando por: **Jerez de la Frontera** · Quitar filtro»).

**Mientras tanto:** volver a marcar las localidades en la barra lateral.

## 5. 🐞 Una bodega con dos localidades se cuenta como localidad nueva

**Qué pasa.** En el filtro de localidad hay tres opciones que se solapan. Es **una sola
bodega**, `Viña La Torre`, que en `datos/catalogo/bodegas_enriquecido.csv` tiene el campo
`localidad` guardado como el texto compuesto «El Puerto de Santa María / Jerez de la
Frontera». Como el filtro agrupa por el valor literal, ese texto se vuelve una categoría más.

**Consecuencia:** si filtras por «Jerez», Viña La Torre no sale. Ni filtrando por «El Puerto».
Y Jerez figura con **21 en vez de 22**.

**Propuesta.** Que la localidad admita más de un valor:

```python
loc = df["localidad"].str.split(r"\s*/\s*")
df_f = df[loc.apply(lambda ls: any(l in sel_local for l in ls))]
```

Y que el desplegable se construya sobre los valores ya separados
(`sorted(set(loc.explode().dropna()))`), para que salgan las **7 reales** y desaparezca la
opción compuesta. En la ficha se sigue viendo el texto completo, que es información buena.
Conviene revisar de paso **si hay otros campos con varios valores en una sola celda**.

## 6. La tarjeta «Media nacional» compara al revés

**Qué pasa.** El Marco ingresa **40,4 €**/visitante y la media nacional es **37,0 €**: el
Marco está **3,4 € por encima**. Pero la flecha verde y el «+3,4 €» están puestos en la
tarjeta *de la media*, y dicen «vs Marco», que leído literalmente significa que la media
supera al Marco. Es justo al contrario.

**Propuesta.** Colgar la comparación **de la tarjeta a la que se juzga**: «Ingreso por
visitante · 40,4 € · ↑ +3,4 € vs media nacional», y dejar «Media nacional · 37,0 €» limpia.

**Comprobado con los datos del prototipo:** `acevin/ingresos_rutas.csv` da 17,2 M€ para el
Marco y `visitantes_rutas.csv` 425.652 visitantes → 40,4 €; el total de las rutas son
112,3 M€ sobre el total de visitantes de ACEVIN → 37,0 €. **Los números están bien; lo que
está del revés es el rótulo.**

**Y una cosa más.** Con el arreglo la pantalla dirá dos cosas que parecen contradictorias y no
lo son: el Marco está **por encima de la media nacional** (37,0 €) y **muy por debajo del
líder** (Rioja Alta, 70,0 €). Si cabe, la línea de la brecha podría decir: *«por encima de la
media de las rutas españolas, y a 29,6 € del líder»*.

## 7. «Diferencia por visitante» enseña el objetivo, no la diferencia

**Qué pasa.** En **Simulador → Monetización**, con el mando en 50,40 €, la tarjeta central
dice «Diferencia por visitante» y enseña **50,4 €**. Ese es el ingreso por visitante
*objetivo*, no la diferencia. La diferencia son los 10,0 € de la flechita. **Mismo patrón que
la 6: el rótulo describe la flechita, no el número grande.**

**Propuesta.** Llamarla **«Ingreso por visitante objetivo»** y dejar el «↑ +10,0 €» como
delta. Y ya que van dos, **repasar de una vez todas las tarjetas que llevan delta**.

## 8. La leyenda de varios gráficos imprime «undefined»

**Qué pasa.** En tres gráficos sale la palabra `undefined` donde debería ir el título de la
leyenda:

| Gráfico | Dónde | Título que debería llevar |
|---|---|---|
| Mapa de Kamensky | Bodega individual → Competidores | **Tipo de competidor** |
| Perfil de los atributos (¿higiénico o deleitador?) | Clientes | **Atributo** |
| ¿De qué habla junto el visitante? (co-word) | Clientes | **Aspecto** |

Y donde no haga falta título, **pasar un valor vacío de verdad** en lugar de una variable sin
definir.

Es cosmético, pero **se ve mucho**: el mapa de Kamensky es de las pantallas de la demo.

## 9. Un apunte interno se ha colado en la pantalla del simulador

**Qué pasa.** Al pie del Simulador, la línea que explica los modelos termina con
«**Idea de Paula (propuesta de mejora, Pieza 3).**» — «Pieza 3» y «propuesta de mejora» son
documentos de trabajo nuestros; quien usa la plataforma no los ha visto nunca.

**Propuesta.** Dejar la línea de los modelos (dice que las palancas no se inventan nada, que
es justo lo que uno se pregunta al ver un simulador) y **borrar la atribución**. De paso,
mirar si hay más apuntes que citen documentos internos o quién propuso qué.

## 10. Los umbrales del motor de recomendaciones no están documentados

**De dónde sale esto.** Una recomendación aparece cuando un dato cruza un listón. La pregunta
obvia es **de dónde sale ese listón**, y la respuesta es distinta según el umbral.

**Los del análisis ya están justificados** —y muy bien— en los comentarios del código, pero
**no están en la guía**: banda de indiferencia del IPCA en estrellas (0,10★), la del
sentimiento (**0,07**, percentil 25 de 94 pares), el mínimo de **8 menciones** (con 6 salía un
5,00 que una sola reseña de 3★ dejaba en 4,71), los 10 casos por variable de la regresión, el
λ de Kano (**±0,20**, Pratt et al. 2020) y los 20 caracteres para detectar idioma.

**Los del motor de recomendaciones, no.** El **15 %** de respuesta, las **5 y 10** críticas,
las 3 bodegas mudas con 50 críticas, los **10 €** de brecha, el 20 % de webs sin zoom, el
80 % de reserva online, el 75/60 % del transporte. Ninguno tiene una razón escrita.

**Propuesta.** Una **sección nueva en la Guía y metodología, en dos bloques**: primero los
umbrales con base metodológica (con su justificación), y debajo **los que son criterio del
equipo**, dichos como tales. **No hace falta cambiar ningún umbral: basta con decir cuál es
cada cosa.**

**Por qué importa.** Son decisiones legítimas —alguien tiene que poner el listón—, pero la
plataforma no dice que sean decisiones del equipo. *Un motor de recomendaciones con los
umbrales declarados es defendible y publicable; uno cuyos umbrales no se sabe de dónde salen,
no.*
