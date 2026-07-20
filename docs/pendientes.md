# ENOLYTICS — Tareas pendientes (backlog)

> Lista viva de todo lo que queda por hacer, para no perder el hilo entre sesiones.
> Marca con [x] lo completado. Última actualización: 2026-07-17 (modelo Kano + PRCA).

## Datos y fuentes
- [ ] **SABI** — confirmar acceso de la UCA (biblioteca) para facturación/empleo por bodega (inteligencia económica y de negocios). Alternativa: Registro Mercantil/BORME.
- [x] 🐛 **BUG DEL CLIENTE DATAESTUR CORREGIDO** — algunos endpoints (`PUERTOS_DL`, `AFILIACION_TURISMO_DL`) **devuelven un fichero Excel, no CSV**. El cliente solo leía CSV y fallaba con "No se pudo decodificar". Ahora detecta el formato por la firma del contenido (`PK` = cabecera zip de xlsx) y el content-type. **Esto desbloquea el empleo turístico (`AFILIACION_TURISMO_DL`), que llevaba semanas atascado y es un indicador de la Tabla 1 a cero.**
- [x] ⭐ **CRUCEROS — puerto de la Bahía de Cádiz** (`enolytics/ingesta/cruceros.py`, idea de Antonio). **HALLAZGO ENORME: 696.151 cruceristas en 2024, MÁS que los 425.652 visitantes de TODAS las bodegas del Marco juntas.** 6º puerto de España. Atracan a **40 min de Jerez** y hacen excursión de día (ACEVIN: ~30% de enoturistas no pernocta). **Y su pico es octubre-noviembre, justo cuando el enoturismo cae** → en **noviembre**: cruceros al 85% de su máximo, enoturismo al 54%. **Es la prioridad FEDER P4A (desestacionalizar) servida en bandeja.** Recomendación de prioridad alta: excursiones de medio día empaquetadas con navieras y receptivos.
- [ ] **Más conjuntos de Dataestur** — empleo turístico (¡ya se puede leer!), empresas turísticas (DIRCE), procedencia de extranjeros (FRONTUR/EGATUR/TURISMO_RECEPTOR), precios (IPC), museos.
- [x] **Google Trends** (pytrends) — interés de búsqueda "bodegas Jerez" vs Rioja/Ribera/Rías Baixas (últimos 5 años) + origen por CCAA. En `datos/procesado/google_trends/`. Hallazgo: Jerez 2º de 4 (media 37; líder Rioja 56), tendencia −15% (2 años vs 2 años). Módulo `enolytics/ingesta/google_trends.py`.
- [x] **Ampliar scraping de la Ruta** — 167 recursos en 11 categorías (bodegas 41, restaurantes 27, recursos culturales 27, naturales 20, actividades 19, alojamientos 14, museos 7, turismo accesible 6, enotecas 3, caterings 2, agencias 1). En `datos/procesado/oferta_enoturistica.csv`. Falta: agenda de eventos + enriquecer fichas (GPS) de no-bodegas.
- [ ] **TripAdvisor** — segunda fuente de reseñas (más visitante internacional), vía Outscraper.
- [ ] Otras plataformas de reseñas: **Civitatis, GetYourGuide** (precios de experiencias, canales de reserva), **Vivino**.
- [x] **ACEVIN — visitantes por ruta del vino** (`enolytics/ingesta/acevin.py`): descarga los informes oficiales del Observatorio RVE (PDF) y extrae visitantes por ruta 2022-2024 → `datos/procesado/acevin/visitantes_rutas.csv`. **Hallazgo: el Marco de Jerez es 1º de España en 2024 (425.652, +11,2%), adelantando a Rioja Alta (−18,6%).**
- [ ] **Censo de reseñas de otras rutas** (Rioja, Ribera) para comparar *reputación online entre destinos* (requiere Outscraper).
- [x] **Oferta y precios comparados entre rutas** — ACEVIN: `oferta_rutas.csv` (37 rutas), `ingresos_rutas.csv` (parcial). **Hallazgos: el Marco es 1º en visitantes pero 7º en oferta (111 servicios vs 334 de Ribera), e ingresa 40,4 €/visitante frente a 70,0 € de Rioja Alta.** Falta: precios de experiencias (Civitatis/GetYourGuide).
- [ ] **Estrategias diferenciadoras** de otras rutas (análisis cualitativo) — indicador de la Tabla 1 aún sin cubrir.
- [x] **Certificaciones de sostenibilidad** — FEV SWfCP cruzado (4: Barbadillo, González Byass, Lustau, Osborne) + **auditoría web de sostenibilidad** por 7 ejes (`enolytics/ingesta/sostenibilidad.py`): 10 bodegas comunican ecológico; Miguel Domecq 7/7. En `datos/procesado/sostenibilidad.csv`. Nota: el buscador público de **CAAE** solo expone su lista internacional (Perú/México), no el registro español; por la solera, los vinos de Jerez tradicionales no certifican "vino ecológico". Falta (opcional): indicadores de consumo (estimados) y transporte sostenible.
- [ ] **Atributos de Google Maps** (accesibilidad, reserva online) vía servicio "Google Maps" de Outscraper (inteligencia tecnológica).
- [ ] **Afluencia con Google Places** — estimar la afluencia/ocupación de cada bodega a partir de los *"popular times"* (horas punta, ocupación por franja/día y "live busyness") de Google Maps/Places. Proxy de visitantes sin sensores: perfiles de estacionalidad y horarios de mayor demanda por bodega y para el destino (inteligencia de clientes/negocios). Vías: Outscraper (campo popular_times) o librería `populartimes`. Ojo: no es un dato oficial de la API estándar de Places; validar cobertura y términos de uso.
- [ ] **Desplazamientos y procedencia del enoturista** (⚠️ *distinto* de la afluencia y del transporte sostenible: aquí se trata de **de dónde viene** y **cómo se mueve** el visitante). Tres vías complementarias:
  - **Dataestur / INE — estudios de movilidad** (basados en telefonía móvil): flujos de viajeros entre provincias/CCAA hacia Cádiz. Fuente oficial.
  - **Procedencia inferida de las reseñas**: detectar el **idioma** de cada reseña (1/3 no están en español) → segmentar nacional vs. internacional, y cruzarlo con el IPA (indicador ya previsto: *IPA/IPCA por procedencia*).
  - **Google Trends por región/país** (ya lo tenemos parcialmente: de dónde se busca "bodegas Jerez" → Andalucía, Ceuta, Extremadura…). Ampliar a interés internacional ("sherry tour").
  - Cubre indicadores de la Tabla 1: *perfil y comportamiento de los visitantes* (Clientes) y *procedencia* (Mercado).
- [x] ✅ ⭐ **CONECTIVIDAD AÉREA (Dataestur)** — `enolytics/ingesta/conectividad_aerea.py`. **EL PRIMER INDICADOR PREDICTIVO DE ENOLYTICS.**
  - **Jerez de la Frontera es ciudad destino propia** en Dataestur (no hace falta aproximar con Sevilla).
  - 4 conjuntos en `datos/procesado/conectividad_aerea/`: búsquedas y reservas **por fecha de inicio de viaje** (miran al futuro), capacidad (asientos programados) y tráfico real. **Datos hasta agosto de 2026** (por delante de hoy). Vienen **por país emisor**, con **antelación de compra** y **estancia media prevista**.
  - 🚨 **HALLAZGO EXCEPCIONAL: 2.631.321 búsquedas de vuelo a Jerez proceden de países SIN UN SOLO ASIENTO DIRECTO** (Italia 634k, EE.UU. 621k, Francia 591k, Países Bajos 422k). Solo **9 países** tienen vuelo directo. **La demanda existe y está medida; lo que falta es el avión.** Es el argumento más fuerte para negociar rutas con aerolíneas y el Patronato.
  - Otros datos: Alemania es el 2º mercado emisor (5,1M búsquedas) y planifica con ~167 días de antelación → **dice cuándo lanzar cada campaña**. EE.UU. es el que mejor convierte (5,87%) y el de estancia más larga.
  - Falta (opcional): estacionalidad mensual y cruce con los meses valle del enoturismo.

- [ ] ⭐ **BLOG DE DATAESTUR — mina de fuentes** (https://www.dataestur.es/blog/). Revisadas las páginas 1-4 y **cruzados los artículos con nuestras lagunas** en **[docs/fuentes_blog_dataestur.md](fuentes_blog_dataestur.md)**. Lo que tapa (todo son indicadores de la Tabla 1 hoy a CERO):
  - **Empleo turístico** (empresas + empleo, DIRCE) → Económica y Negocios.
  - **Rentabilidad** (hostelería: beneficios, ventas, trabajadores) → alternativa **gratuita a SABI**.
  - **Redes sociales** (qué interesa de España en RRSS) → Mercado (la memoria las cita y no las tenemos).
  - **Impacto de un gran evento en los desplazamientos** → desplazamientos + eventos enoturísticos (¡la Vendimia!).
  - **Índice de sentimiento oficial de SEGITTUR** → **benchmark para validar nuestro análisis de sentimiento** (hoy derivado de las estrellas, no de un modelo NLP). Muy útil para el paper.
  - **Calendario de publicación 2026** → imprescindible para la **automatización periódica** ("tiempo real").
  - [ ] Falta revisar las **páginas 5-9** del blog.
- [ ] **Consejo Regulador de Jerez** — memorias anuales (producción, ventas, exportación).

## Calidad del análisis (NLP)
- [x] ⭐ **IDIOMA DE LAS RESEÑAS → procedencia** (`enolytics/nlp/idioma.py`, langdetect con semilla fija para que sea reproducible). Columnas `idioma` y `segmento_idioma` en `resenas.csv`.
  - **Resultado:** 62,3% de reseñas con idioma detectable. **Hispanohablante 5.090 (46,4%) · Internacional 1.750 (15,9%) · Sin determinar 4.132 (37,7%)**. Top idiomas: inglés (905), alemán (290), italiano (180), francés (91). El internacional puntúa **4,46★ frente a 4,58★** del hispanohablante.
  - 🚨 **SESGO MEDIDO (hallazgo clave):** el léxico de atributos está **solo en español**, así que **el 35,8% de las reseñas internacionales no aporta ningún atributo**, frente al 5,1% de las hispanohablantes. **El IPA actual se construye casi solo con la voz del visitante hispanohablante.**
  - ⚠️ **Por eso NO se muestra un IPA comparado por idioma:** la "importancia" del segmento internacional sería un **artefacto del léxico**, no una preferencia real. Requiere primero el léxico multilingüe.
  - **Cautelas declaradas en el dashboard:** idioma ≠ nacionalidad (un mexicano escribe en español y es internacional); 1/3 de reseñas no tienen texto.

- [x] ✅ **LÉXICO MULTILINGÜE** (ES/EN/DE/IT/FR) en `enolytics/nlp/analisis.py`. **Reseñas internacionales sin analizar: 35,8% → 11,4%** (analizables: 64% → 88,6%), sin regresión en las hispanohablantes (5,1%).
  - 🐛 **BUG CORREGIDO de paso:** la clave suelta **"tiempo"** contaminaba «Organización y reserva» (disparaba 118 reseñas españolas, la mayoría sin relación: *"nada de las típicas turistadas"*, ¡reseñas de logística de camiones!). En español es polisémica (el clima, la duración). Sustituida por la locución "tiempo de espera".
  - ⚠️ **CAMBIA UN NÚMERO PUBLICADO:** «Organización y reserva» pasa de **3,66★ a 4,00★** en el destino (al quitar el ruido y sumar el internacional). **Sigue siendo el peor atributo**, pero el dato anterior estaba inflado por ruido. Revisar cualquier borrador que citara 3,66.
  - 🎯 **HALLAZGO nuevo (ya defendible):** el visitante **internacional menciona la reserva 4,6× más** (11,5% vs 2,5%) pero **la puntúa mejor** (4,29★ vs **3,56★** del hispanohablante). El problema de organización lo sufre sobre todo **el visitante nacional**.
  - Cautela declarada en el dashboard: las palabras clave de cada idioma capturan matices distintos (el inglés *booking* es descriptivo; el español *espera*/*cola* ya arrastra queja).
- [x] ✅⭐ **HECHO (17/07) — SENTIMIENTO POR ATRIBUTO CON BERT** (`enolytics/nlp/sentimiento.py`).
  Modelo `nlptown/bert-base-multilingual-uncased-sentiment`: entrenado sobre RESEÑAS en EN/NL/DE/
  FR/ES/IT (incluye el **neerlandés**, que ni está en el léxico) y devuelve **5 clases con
  probabilidades** — justo lo que piden las ec. 2-3 de Zhang. Va **frase a frase**: 7.277 reseñas
  → **14.041 frases** → **16.499 filas reseña-atributo**, en ~3 min con MPS.
  - 🎯 **LA PRUEBA DE QUE FUNCIONA:** con estrellas, la desviación DENTRO de una reseña era
    **0,000 siempre** (todos los atributos recibían la misma nota). Ahora es **0,280**, y en el
    **21%** de las reseñas dos atributos difieren en más de 1 punto. Ejemplo real (reseña de 4★):
    *"Estupenda bodega, visita guiada espectacular. Mi gran decepción fue…"* → **Visita 4,67 ·
    Instalaciones 3,22 · Precio 1,26**. Antes los tres eran 4,0.
  - **No es circular:** correlación sentimiento-del-atributo vs estrellas-de-la-reseña = **0,677**
    (fuerte pero no copia). A nivel de reseña completa es 0,837, que sólo valida el modelo.
  - Arquitectura: se ejecuta EN LOCAL y deja CSV; el dashboard sólo lee. `torch` NO entra en
    `requirements.txt` (Streamlit Cloud tiene ~1 GB de RAM).

- [x] ✅⭐ **HECHO (17/07) — PRCA: IMPORTANCIA POR IMPACTO** (`enolytics/analitica/prca.py`).
  Ecuaciones de Zhang et al. (2021). Precalcula a `datos/procesado/prca_kano.csv` (destino + 16
  bodegas con muestra suficiente); `statsmodels` tampoco entra en producción.
  - 🚨 **ARREGLA EL CONSEJO INVERTIDO, que era el objetivo:** «Precio» (771 men.) y
    «Organización» (331) —los dos PEORES atributos— pasan de ***"Baja prioridad"*** a
    **"CONCÉNTRESE AQUÍ"** (16,9% y 16,1% de importancia). El dashboard dejará de decir "lo que
    peor haces, no lo toques".
  - 💡 **HALLAZGO NUEVO:** «Vino y cata» es lo MÁS mencionado (4.232) pero sólo el **11,1%** de
    importancia → **"Posible exceso"**. Se habla del vino sin parar y no mueve la nota, porque
    siempre es bueno. Es esfuerzo mal repartido.
  - Modelo sano: **R² = 0,55**, F significativa, 465 obs/variable.
  - 🐛 **Bug cazado al vuelo:** sin mínimo de menciones, Barbadillo daba «Entorno y viñedo» con
    **52,6% de importancia sobre 6 menciones** (coeficiente inestable que, al normalizar, se
    comía el reparto). Añadido `MIN_MENCIONES_ATRIBUTO = 8`. Efecto secundario bueno: al haber
    menos variables, **16 bodegas** aguantan la PRCA en vez de 12.

- [x] ✅⭐ **RESUELTO (18/07) — KANO REENFOCADO COMO ESPECTRO HIGIENE↔DELEITE.** La clasificación
  ABSOLUTA de Kano no es rescatable con estos datos (efecto techo, ver abajo), pero **el orden
  relativo de λ sí es robusto**: correlaciona **0,79 (Spearman)** entre OLS y regresión ordinal,
  dos estimadores muy distintos. Se muestra el **espectro relativo** en vez de las 3 cajas.
  - **`prca.py`**: nuevo `_lambda_ordinal()` (respaldo, sólo si n≥400) + `perfil`
    (Higiénico/Mixto/Deleitador) y `perfil_pos` (0-1) por atributo, relativo a su ámbito.
  - **Dashboard**: `figura_perfil()` — espectro horizontal, tamaño = importancia. Con leyenda
    honesta del efecto techo. NO se muestran las etiquetas absolutas de Kano.
  - **Recomendaciones**: si un atributo urgente es *higiénico*, avisa de que arreglarlo evita
    quejas pero no diferencia.
  - **Resultado destino:** Precio = Higiénico (sólo evita dolor); Entorno = Deleitador (crea
    satisfacción); resto Mixto. Cruzado con impacto: Precio y Organización son urgentes PERO con
    techo de recompensa; Personal y Entorno son las palancas de diferenciación.

- [x] 📌 **EFECTO TECHO — documentado (era la decisión pendiente).** Los 7 atributos dan "Básico".
  No es un hallazgo, es aritmética: con **78,7% de cincos**, la nota de referencia ya es 4,61/5,
  así que hablar bien de un atributo sube **+0,23** y hablar mal hunde **−2,56** — **11× de
  asimetría mecánica**. β_penalty >> β_reward para CUALQUIER atributo → λ siempre muy negativo
  (−0,39 a −0,96). **λ absoluto NO es interpretable; su orden relativo quizá sí.**
  - ⚡ **Es la objeción (1) de Bi et al. (2019) CONFIRMADA con nuestros datos**: la nota es una J,
    no una Gaussiana. Zhang y Han nunca la comprobaron (Yelp está más repartido que Google Maps).
  - **Vías:** (a) **regresión ordinal** (ordered logit: modela la satisfacción latente y trata el
    techo como umbral — es el arreglo estándar para variables dependientes acotadas); (b) usar
    sólo el orden relativo de λ; (c) aceptar el resultado negativo y no publicar Kano.
  - 📄 Para el futuro paper esto es material: **nadie ha documentado que el método de Zhang/Han
    se rompe en corpus con techo**, que es el caso normal en enoturismo.

- [x] ✅ **SOLO MÉTODO BUENO (18/07, decisión de Antonio).** Se elimina el respaldo por frecuencia:
  el IPA/perfil/IPCA/DIPCA de una bodega **solo se muestran si tiene muestra para la PRCA** (16
  bodegas); las **24 sin muestra reciben un mensaje honesto** ("N reseñas con atributo; el método
  por impacto necesita ~140; con menos daría un resultado engañoso, se omite") y conservan
  reputación y reseñas. Motivo medido: las 24 tienen **mediana de 26 reseñas** (la mayor, 80),
  ninguna cerca del umbral → el método clásico sobre esas muestras era ruido con pinta de gráfico.
  Función `ipa_desde_anotadas` (clásico) eliminada del dashboard; las recomendaciones tampoco se
  alimentan de atributos si no hay PRCA.
  - [x] ✅ **DEUDA SALDADA (18/07): IPCA y DIPCA migrados al SENTIMIENTO.** `ipca_desde_sentimiento`
    y `dipca_desde_sentimiento`: comparan el **sentimiento** hacia cada atributo (no estrellas) de
    la bodega contra el **RESTO** del Marco (excluyéndola — antes se comparaba contra el todo, que
    la incluía; para González Byass eso era el 14%). Banda de indiferencia recalibrada para la
    escala del sentimiento: **0,07** (percentil 25 de las brechas reales). Resultado más nítido:
    la brecha de «Organización» en Barbadillo pasa de −0,53 (estrellas) a **−0,66** y cae en
    *«Actuar: por detrás del Marco»*. El sentimiento por (reseña, atributo) se une con la fecha
    (de `resenas.csv`) para poder partir el DIPCA por periodos.
  - [x] ✅ **Panel hispanohablante vs internacional migrado** al sentimiento (la columna «Nota»
    era por estrellas). Hallazgo coherente: el internacional puntúa «Organización» **+0,46** mejor
    que el hispanohablante (ya lo veíamos: la menciona más pero la sufre menos). «Menciona %» sigue
    siendo frecuencia de mención (descriptivo, correcto).
  - [x] ✅ **DIPA migrado al sentimiento (18/07): COHERENCIA AL 100%.** `evolucion_sentimiento()`
    (mismas columnas que `evolucion_atributos` pero con sentimiento) alimenta el DIPA del destino
    y el de bodega. **Ya NINGÚN rendimiento por atributo usa estrellas.**
  - 📋 **Auditoría de coherencia FINAL (18/07):** verificado en código que las únicas estrellas que
    quedan son legítimas — **notas GLOBALES** (satisfacción general de bodega/segmento) y
    **recuentos de mención** (frecuencia). Todo el rendimiento POR ATRIBUTO (IPA, DIPA, IPCA,
    DIPCA, panel de idiomas) usa el sentimiento BERT. Importancia = impacto (PRCA) en todo.

- [x] ✅⭐ **HECHO (18/07) — PRCA ENCHUFADA AL DASHBOARD Y A LAS RECOMENDACIONES.**
  - `ipa_desde_prca(ambito)` lee `prca_kano.csv`; el destino y las 16 bodegas con muestra usan la
    importancia por impacto. Las 24 bodegas sin muestra caen al IPA clásico (con aviso en pantalla).
  - `figura_ipa(tabla, metodo=)` rotula bien cada eje ("impacto en la satisfacción" vs "nº menciones").
  - **El consejo invertido ya NO llega al usuario:** «Precio» y «Organización» aparecen en
    *«Concéntrese aquí»* en el gráfico del destino. Verificado en el dashboard (HTTP 200, sin errores).
  - Recomendaciones: `_menciones()` y `_por_impacto()` evitan el "0 menciones" que habría salido al
    ser la importancia una fracción; el texto explica que es impacto, no frecuencia.
  - ⚠️ La columna **Kano** se calcula pero **NO se muestra** aún (todo "Básico" por efecto techo).

- [ ] ~~PRIORIDAD 1 — SENTIMIENTO POR ATRIBUTO~~ (hecho arriba). Queda: validar contra el índice
  de sentimiento oficial de SEGITTUR. Validar contra el índice de sentimiento oficial de SEGITTUR.
  Instalar `transformers`. **NO es una mejora opcional: es el CIMIENTO del núcleo científico.**
  Motivo (auditoría del 17/07, a raíz de la preocupación de Antonio sobre cómo medimos):

  🚨 **EL DESEMPEÑO NO MIDE EL ATRIBUTO, MIDE LA VISITA ENTERA.** `tabla_importancia_desempeno()`
  define *desempeño = nota media (estrellas) de las reseñas que mencionan el atributo*. Pero las
  estrellas son de la experiencia **completa**, no del atributo. Si alguien escribe *"it is
  expensive but a special place"* y pone 5★, registramos **desempeño del Precio = 5,0**.
  - **PRUEBAS EN NUESTROS DATOS:** (1) de las **96 reseñas que se quejan explícitamente del
    precio, el 44% tiene 4-5 estrellas** — y a todas les asignamos su nota global como desempeño
    del precio; (2) **todos los atributos se apiñan entre 4,00 y 4,71** alrededor de la nota
    global (4,573), desviación típica **0,288**. Esa compresión es la huella del sesgo: no
    medimos 7 atributos distintos, medimos 7 veces casi la misma nota global.
  - **QUÉ IMPLICA PARA LO PUBLICADO:** «Organización y reserva = 4,00★» **no significa "qué tal
    funciona la organización"**, sino *"la satisfacción global media de quienes la mencionaron"*.
    El **orden probablemente aguante** (quejarse arrastra la nota global), pero **el número no
    mide lo que decimos que mide**. Es lo que tumbaría el artículo en revisión.
  - ✅ **VERIFICADO QUE NO HAY ERROR NUMÉRICO ADEMÁS:** el DIPA solo usa desempeño, y el IPCA
    compara la importancia solo *dentro* de la misma bodega (umbral = media de sus propios
    atributos). No se comparan recuentos en bruto entre corpus de distinto tamaño.
  - 🎯 **UN SOLO ARREGLO RESUELVE TODO:** con sentimiento por atributo → *desempeño = sentimiento
    hacia ESE atributo* (arregla lo anterior) + *importancia = regresión penalty–reward* (arregla
    la crítica de la frecuencia) + **Kano** de regalo. Ver "MODELO KANO + PRCA" en Modelos
    analíticos. **Sin esto, Kano es imposible** (la PRCA sería circular: explicaría la nota con
    la propia nota).

- [x] 🐛 **BUG DE POLISEMIA CORREGIDO: "cara"** (17/07, hermano del bug de "tiempo"). La clave
  suelta `'cara'` estaba en el léxico de Precio: en español es "costosa" pero también **el
  rostro** (*"se les ilumina la cara"*, *"las explicaciones como la cara han sido magníficas"*) y
  el modismo **"de cara al público/cliente"**. Disparaba **11 falsos positivos de 29** reseñas.
  Sustituida por locuciones ("muy cara", "un poco cara", "algo cara", "cara para"…), que además
  **rescatan el portugués** ("mais cara", "embora cara"). Se pierde 1 acierto ("se hace corta o
  cara"), asumible. `'caro'` en masculino no es ambigua y se mantiene.
  - **Impacto medido: PEQUEÑO.** Precio pasa de 783 menciones / 4,074★ a **771 / 4,088★**
    (+0,014). **No cambia ningún ranking** (Precio sigue 2º peor; Organización sigue la peor).
    A diferencia del bug de "tiempo" (3,66 → 4,00), este era ruido menor. No hay que revisar
    borradores.
  - 💡 Curiosidad detectada: *"con su **cara** de vino"* y *"con **cara** de 4 vinos"* son
    **erratas de "cata"** → el léxico de "Vino y cata" pierde esas menciones. Menor.

- [ ] **Ampliar el léxico a PORTUGUÉS y NEERLANDÉS** (detectado el 17/07 al arreglar "cara").
  Recuento real de idiomas en el corpus: es 5.090 · en 905 · de 290 · it 180 · **fr 91** ·
  **nl 63** · **pt 60** · ca 39 · ru 30 · pl 15. **El neerlandés (63) y el portugués (60) tienen
  ya el mismo orden de magnitud que el francés (91), que sí está en el léxico.** Son ~123 reseñas
  hoy analizadas a medias. El catalán (39) probablemente cae en parte por parecido con el español.
- [~] **Modelado de temas (LDA)** — descubrir atributos automáticamente, más allá del léxico fijo.
  - [x] ✅ **LDA exploratorio hecho (18/07)** sobre las 4.882 reseñas en español (sklearn). Confirmó
    que los 7 atributos existentes mapean bien los temas, pero **destapó un hueco: la gastronomía**
    emergía como tema propio en el **11%** de las reseñas y no estaba cubierta. También asomaron
    "tienda/compra" (3,8%) y "arte/colección" (1,8%), menores. Método: como Zhang et al. (2021),
    LDA propone + criterio humano depura (híbrido supervisado, no automático puro).
  - [x] ✅ **Añadido «Gastronomía y restauración» como 8.º atributo** (léxico multilingüe validado,
    751 reseñas / 11%; descartada "menu" por polisémica). Pipeline regenerado (sentimiento + PRCA).
    **Hallazgo:** 747 menciones en el destino (más que Precio), desempeño **3,88** (3.º peor),
    perfil **higiénico**. Diferencia bien las bodegas (Fundador deleitador 4,23; González Byass 3,29).
  - [ ] Falta (opcional): LDA sobre el inglés/otros idiomas por si emergen temas distintos; y el
    flujo Zhang completo (rederivar TODOS los atributos desde LDA), que es rehacer el cimiento.
- [ ] Validar/afinar el léxico de atributos con criterio experto (Paula / bodegas).

## Modelos analíticos
- [x] 🐛 **TRES ARREGLOS DE PRODUCTO** (17/07, a petición de Antonio: "estoy pensando en mejorar
  ENOLYTICS, no en hacer un paper"). Los tres a nivel de BODEGA; el destino no cambia.
  1. 🚨 **CRASH EN VIVO CORREGIDO:** `tabla_importancia_desempeno()` **petaba con KeyError** si
     ninguna reseña tenía atributos: `pd.DataFrame([])` no tiene columnas y `.sort_values
     ("importancia")` reventaba. **Lo disparaba `Viñedos Bodega El Piraña`** (1 reseña, sin
     texto): seleccionarla en la vista "Bodega individual" **tumbaba el dashboard**.
     `ipa_desde_anotadas()` no lo cazaba porque comprobaba `an.empty` y la bodega SÍ tenía
     reseñas. Ahora devuelve tabla vacía con columnas.
  2. **MÍNIMO DE MUESTRA** (`nlp.MIN_MENCIONES = 8`): un atributo con menos de 8 reseñas no
     tiene media publicable. Lo disparó Barbadillo: *"Entorno y viñedo" = **5,000★ con 6
     reseñas*** (una sola de 3★ lo habría dejado en 4,71). El criterio ya existía disperso e
     inconsistente (`evolucion_atributos` filtraba a 8, el DIPCA a 10, esta función a NADA);
     ahora está unificado en la función base. **Medido:** con 8 se caen 73 de 235 filas
     bodega-atributo y 9 de 41 bodegas quedan con <3 atributos; con 30 se caerían 148 y 23
     bodegas quedarían vacías (inviable). **El destino no se toca** (su atributo menor tiene 208).
     **No se descarta en silencio:** `aviso_omitidos()` dice en pantalla qué se omitió y por qué.
  3. **BANDA DE INDIFERENCIA EN EL IPCA** (`ipa.BANDA_INDIFERENCIA = 0.10`): antes
     `ventaja = brecha >= 0` convertía el ruido en diagnóstico. En Barbadillo: *"Vino y cata"
     con brecha **−0,004** → "Actuar: por detrás del Marco"* y *"Instalaciones" con **+0,001**
     → "Fortaleza competitiva"* — **etiquetas opuestas para diferencias inexistentes**. Nuevo
     cuadrante 5 = **"En línea con el Marco"**. El valor sale de la distribución real de las 162
     brechas bodega-atributo (percentil 25 = 0,093; mediana = 0,202): ±0,10 declara "sin
     diferencia" el 26,5% de los casos, justo el cuartil donde vive el ruido.
  - **Resultado en Barbadillo:** de 4 "fortalezas competitivas" (3 de ellas ruido) a **1
    fortaleza real** (Personal, +0,116), **1 debilidad real** (Organización, −0,532) y el resto
    en línea. Verificado: las 41 bodegas procesan sin fallos y el dashboard arranca limpio.
  - ⚠️ **LO QUE ESTO NO ARREGLA:** «Organización y reserva» sigue saliendo como *"Debilidad
    **menor**"* pese a tener la mayor brecha (−0,532), porque con 18 menciones cae en "baja
    importancia". **El consejo invertido solo lo arregla la importancia por PRCA.**

- [x] IPA (destino + por bodega)
- [x] IPCA (competitivo, por bodega vs. Marco)
- [x] DIPA (evolución temporal del destino)
- [x] DIPCA (evolución de la brecha competitiva por bodega)
- [x] **Perfil Kano (higiene↔deleite) TAMBIÉN por bodega** (18/07). El dato ya se calculaba para
  las 16 bodegas con muestra; ahora `figura_perfil()` se pinta también en la vista de bodega
  individual (antes solo en el destino). Barbadillo, p.ej., tiene «Visita» como deleitador e
  «Instalaciones/Precio» como higiénicos — perfil propio, distinto del destino.
- [x] ✅ **DIPA por bodega HECHO (18/07)** con mínimo de muestra. `dipa_bodega(an_bod,
  min_menciones=8)`: nota media anual de los atributos de la bodega, solo los presentes en ≥2
  años con ≥8 reseñas cada año. **Da DIPA útil en 18 de 40 bodegas** (las de más historia; entra
  Barbadillo, González Byass, Tradición…). Leyenda que lo enmarca como *señal de tendencia sobre
  pocas reseñas, no veredicto*. Reutiliza `evolucion_atributos` + `resumen_dipa` del destino.
  - ⚠️ Como el DIPA del destino, se basa en la **nota media (estrellas)**, no en el sentimiento
    por atributo. Coherente entre niveles; mejorarlo a sentimiento es tarea futura.
- [ ] IPA/IPCA por **atributo cruzado con procedencia** (nacional vs internacional).
- [ ] ⭐ **MODELO KANO + PRCA** (a propuesta de Antonio, 17/07). Fuente: **Han, W., Zhang, C.,
  Zhang, Y.C., Raab, C. y Chen, Z. (2026), "How do robots reshape restaurant service attributes?
  – Evidence from online reviews", *IJCHM*, DOI 10.1108/IJCHM-01-2026-0071** →
  `BIBLIOGRAFIA/ijchm-01-2026-0071en.pdf`. Su pipeline **es el nuestro** (reseñas → NLP →
  atributos → sentimiento → IPA), pero con dos mejoras que nos convienen:
  - 🚨 **ARREGLA NUESTRO TALÓN DE AQUILES — la "importancia".** Hoy usamos
    *importancia = nº de menciones*, que es discutible (que se hable mucho del vino no prueba
    que el vino determine la satisfacción). **Es la crítica más probable de un revisor JCR.**
    Ellos la derivan de una **regresión penalty–reward (PRCA, Brandt 1987)**: cuánto sube la
    nota global cuando el sentimiento hacia el atributo es alto (β_reward) y cuánto baja cuando
    es bajo (β_penalty). Importancia_i = √(β_penalty² + β_reward²) normalizada sobre el
    sumatorio. **Se puede calcular YA con lo que tenemos** (sentimiento por atributo + nota de
    la reseña); no exige datos nuevos.
  - 🎁 **AÑADE EL MODELO KANO** (lo que el IPA solo no dice: no solo *dónde* actuar, sino *qué
    retorno esperar*). De la misma regresión sale λ = (|β_reward| − |β_penalty|) /
    (|β_reward| + |β_penalty|), con λ ∈ [−1, 1]. Umbrales del paper (Pratt et al., 2020):
    **λ > 0,20 = entusiasmo** (deleita si está, no penaliza si falta) · **λ ∈ [−0,20, 0,20] =
    desempeño** (lineal) · **λ < −0,20 = básico** (se da por supuesto; si falla, cabrea; si va
    bien, no suma).
  - 💡 **Por qué importa para Jerez:** si «Organización y reserva» (nuestro peor atributo, 4,00★)
    resultara **básico**, arreglarlo **no subiría la nota** — solo está restando. Cambia la
    recomendación de gestión que damos a las bodegas.
  - ⚠️ **Requisito previo:** ellos miden sentimiento con **RNTN** (Socher et al., 2013) y
    justifican explícitamente por qué es superior a los métodos léxicos. Nosotros lo derivamos
    de las estrellas → **va de la mano de la tarea "Sentimiento con modelo NLP real"**. Ojo: la
    PRCA regresa el sentimiento del atributo contra la nota de la reseña; si el sentimiento SALE
    de la nota, la regresión es circular. **Hay que resolver el sentimiento real ANTES o a la vez.**
  - 🚀 **HUECO DE LITERATURA CON NUESTRO NOMBRE:** en sus limitaciones (pág. 15) piden
    literalmente *"cross-cultural comparisons should be encouraged"*. Ellos son **monolingües,
    un país, una sola cadena**. Nosotros tenemos **corpus multilingüe (ES/EN/DE/IT/FR)** con
    segmentación hispanohablante vs. internacional. **Kano comparado por segmento cultural es
    publicable y ellos no pueden hacerlo.** Enlaza con la tarea de IPA/IPCA por procedencia.
  - Otras ideas suyas aprovechables: **anclar el análisis temporal a un EVENTO** (ellos: antes/
    después de los robots; nosotros podríamos: antes/después de la pandemia, de una reforma,
    de la llegada de cruceros) → daría sentido causal a nuestro DIPA, que hoy es solo evolución.

## Las 7 inteligencias (estado)
- [x] **Clientes** — reseñas (satisfacción, atributos) + índices Dataestur + **perfil del enoturista (ACEVIN, 16 indicadores)** y **volumen de visitas**. ⚠️ El perfil de ACEVIN es NACIONAL (no por ruta): sirve de benchmark y de plantilla de cuestionario.
- [x] **Competidores** — reputación + IPCA. Falta: precios y otras rutas.
- [~] **Económica** — gasto Dataestur (hecho). Falta: por bodega (SABI).
- [x] **Mercado** — gasto/percepción Dataestur + **Google Trends** (interés de búsqueda comparativo vs rutas competidoras + origen por CCAA). Falta (opcional): procedencia internacional (FRONTUR).
- [~] **Negocios** — catálogo de bodegas. Falta: museos/enotecas/eventos + empleo.
- [x] **Tecnológica** — madurez digital (`auditoria_web.csv`: HTTPS, móvil, inglés, reserva, inmersiva → /5) + **accesibilidad universal** (`accesibilidad.csv`: índice WCAG /8 + señales de accesibilidad física/sensorial). 29/42 auditadas. **Hallazgo: 0 de 29 bodegas mencionan apoyo sensorial (audioguías, braille, signos); solo 4 mencionan accesibilidad física.** Falta: accesibilidad física REAL vía Google Maps; contraste/teclado (exige renderizar).
- [x] **Sostenibilidad** — certificación FEV (4) + índice de sostenibilidad comunicada (7 ejes) + **transporte sostenible** (`transporte_sostenible.csv`, OpenStreetMap): 88% de las bodegas accesibles en transporte público. Falta (opcional): consumos estimados (agua/energía/huella).

## Dashboard y producto
- [x] ✅ **Versiones fijadas en `requirements.txt`** (18/07): `streamlit==1.52.2` (antes `>=1.30`,
  abierto). Motivo: `use_container_width` (usado 25 veces) está deprecado y Streamlit Cloud podía
  romper el dashboard al actualizar solo. Ahora el despliegue es reproducible.
  - [ ] Deuda menor: cuando se suba la versión de Streamlit, migrar `use_container_width=True` →
    `width="stretch"` (25 sitios) y quitar el pin exacto.
- [x] ⭐ **REESTRUCTURACIÓN DE LA VISUALIZACIÓN** (a propuesta de Antonio: "abruma tanta información"). El dashboard había crecido a **25 gráficos, 46 métricas, 12 tablas y 20 avisos** en una sola vista. Aplicado el **mantra de Shneiderman** ("primero la panorámica; el detalle, a demanda") y la **regla de los 5 segundos**. Tres niveles:
  1. **🏠 Resumen ejecutivo** (portada): 4 KPIs + **semáforo de las 7 inteligencias** + las **3 recomendaciones más urgentes**. De 67 métricas a **11**.
  2. **🧭 Las 7 inteligencias**: las 7 pestañas de siempre, pero cada una abre con lo esencial y **lo secundario va plegado** (rankings, tablas, gráficos de apoyo).
  3. **🏭 Bodega individual**: sin cambios.
  - 💡 **El semáforo NO se pinta a mano: lo calcula el motor de recomendaciones** (🔴 2+ acciones urgentes · 🟠 1 · 🟡 mejoras · 🟢 sin avisos). Se actualiza solo al cambiar los datos.
- [x] **Ficha de reputación estilo Booking/Amazon** por bodega (`enolytics/analitica/reputacion.py`, idea de Antonio): distribución de estrellas, "lo que dicen los visitantes", aspectos con signo (↗ ~ ↘) y nº de menciones, reseñas representativas y **tasa de respuesta del propietario**. El resumen es **determinista** (se compone de los datos agregados), no lo genera una IA → reproducible y auditable, a diferencia del de Amazon. **Hallazgo: 11 de 33 bodegas no responden a NINGUNA reseña; González Byass acumula 209 críticas sin contestar.**
- [x] **Motor de recomendaciones accionables** (`enolytics/analitica/recomendaciones.py`) — el diferencial que promete la memoria. Reglas que cruzan las 7 inteligencias y generan recomendaciones priorizadas, cada una con su diagnóstico (dato que la justifica) y su fuente. Dos niveles: destino (8 recomendaciones, 5 de prioridad alta) y bodega individual.
- [x] ✅ **Motor de recomendaciones puesto al día (18/07)** para explotar los datos nuevos (PRCA,
  perfil, sentimiento, Gastronomía):
  - 🐛 **Bug arreglado:** la acción del "peor atributo del destino" estaba **hardcodeada a
    'revisar la reserva y la organización'** — sin sentido si el peor era Gastronomía o Precio.
    Ahora `ACCIONES_ATRIBUTO` da una acción **específica por atributo** (verificado: en Hidalgo –
    La Gitana, con Gastronomía crítica, aconseja sobre la oferta gastronómica, no la reserva).
  - ➕ **Palanca de diferenciación** (nueva regla, destino y bodega): surface del atributo
    **deleitador** — dónde se PUEDE destacar, no solo dónde se falla. La cara positiva del perfil.
  - La regla 1 de bodega ahora usa el **perfil** (higiénico → "no diferencia"; deleitador →
    "doble motivo") y acción específica. Fuentes actualizadas (sentimiento/PRCA, no estrellas).
- [x] ✅ **Jerga de siglas fuera de los títulos (18/07, mejora UX).** Los títulos de sección
  hablaban en siglas (*"Análisis avanzado (IPA · perfil · DIPA · IPCA · DIPCA)"*, *"Análisis
  competitivo (IPCA)"*), que el bodeguero no entiende. Ahora son **preguntas en lenguaje llano**
  con la sigla como apunte secundario en cursiva: *"Fortalezas y debilidades según los visitantes"*,
  *"¿Cómo va frente al resto del Marco? (IPCA)"*, *"¿Gana o pierde terreno frente al Marco? (DIPCA)"*,
  *"¿Mejora o empeora con el tiempo? (DIPA)"*. En destino y en bodega.
- [x] ✅ **Recomendaciones de bodega CONSOLIDADAS por atributo (18/07, mejora UX).** Antes IPA,
  IPCA y DIPCA generaban cada uno su tarjeta, así que un mismo atributo débil aparecía **hasta 3
  veces** (peor nota + por detrás del Marco + empeorando). Ahora se tejen en **una sola tarjeta**
  por atributo que combina las señales: *"Precio: mueve mucho la satisfacción, 3,66/5, higiénico;
  va por detrás del Marco (3,66 vs 3,79); y pierde terreno (de +0,07 a −0,34)"*. Barbadillo pasa
  de 7 tarjetas de atributo repetidas a **4 limpias**, sin repetir ninguno. La palanca deleitadora
  ya no repite un atributo que salga como problema.
- [x] **Reorganizar en pestañas** por inteligencia (Gestor: Visión general · Clientes y experiencia · Económica y mercado. Bodega: Ficha · Reseñas y análisis). Añadir más pestañas al sumar inteligencias.
- [x] **Etiquetado del origen de cada indicador** (🟢 oficial · 🔵 observado · 🟡 estimado) con leyenda en el dashboard. 13 etiquetas en las 7 inteligencias. `config.ORIGENES_DATO` + helper `fuente()`.
- [x] **Enlace permanente** — PUBLICADO en **https://enolytics-feder-uca.streamlit.app** (Streamlit Community Cloud, repo público `Antonio-Ramos-UCA/enolytics`). Redespliega solo al hacer `git push`. Falta (opcional): restringir vista por correo desde Settings → Sharing.
- [ ] **Automatización incremental** de reseñas (API Outscraper + programación) — la parte "periódica" de la memoria.

## Pendientes menores de datos
- [x] **Superar el bloqueo anti-bot** (`enolytics/ingesta/navegador.py`, Playwright): las webs con verificación de edad se leen abriendo un Chromium real. **29 → 38 webs auditadas** en las 3 auditorías (madurez, accesibilidad, sostenibilidad); 15 rescatadas. **Bodegas Tradición (piloto) recuperada: 5/5 madurez, 7/8 accesibilidad.** Siguen sin web accesible: Emilio Hidalgo (piloto), Yuste, Caydsa, El Piraña.
- [ ] Resolver identidad de **AC Wines** en Google (excluida del corpus).
- [ ] Completar datos de ficha de **Bodegas Emilio Hidalgo** (piloto).

## Cuestionarios (fase piloto, con Paula y bodegas)
- [ ] Diseñar **cuestionario a bodegas** (económica + negocios + tecnológica + sostenibilidad) — solo para lo NO obtenible de fuentes públicas.
- [ ] Diseñar **cuestionario a enoturistas** (perfil, fidelización, canales) — validación de proxies.

## Salidas académicas (memoria)
- [ ] Redactar hallazgos para publicación JCR (el problema de "organización/reserva" que empeora es un buen ángulo).
- [ ] **Ángulo cross-cultural con Kano** (ver "MODELO KANO + PRCA" en Modelos analíticos): Han
  et al. (2026, IJCHM) piden expresamente comparaciones interculturales y no pueden hacerlas
  (corpus monolingüe). Nuestro corpus multilingüe sí. Candidato fuerte a paper.
- [ ] **Revista objetivo:** IJCHM (Emerald, Q1) acepta exactamente este método (reseñas + Kano +
  IPA). Ver el paper de `BIBLIOGRAFIA/` como plantilla de estructura y de nivel exigido.
- [ ] Definir TFM/TFG asociados.
