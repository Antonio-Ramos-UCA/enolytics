"""Motor de recomendaciones accionables (el diferencial de ENOLYTICS).

La memoria promete que la plataforma *"no solo recopila datos, sino que los transforma en
**recomendaciones accionables y estratégicas** que permiten una toma de decisiones más ágil,
precisa y personalizada"*. Este módulo es esa traducción: convierte los indicadores de las 7
inteligencias en **qué hacer**, priorizado.

Cada regla:
  · Se dispara **solo si el dato la sostiene** (si falta el dato, no se inventa nada).
  · Declara su **diagnóstico** (la evidencia numérica) y su **acción** (qué hacer).
  · Cita la **fuente**, para que sea auditable.

Dos niveles:
  · `recomendaciones_destino(...)` → para el gestor del Marco.
  · `recomendaciones_bodega(...)`  → para una bodega concreta.

Uso:
    from enolytics.analitica import recomendaciones
    recs = recomendaciones.recomendaciones_destino(acevin=..., ...)
"""
from __future__ import annotations

from dataclasses import dataclass, field

PRIORIDADES = {"alta": 0, "media": 1, "baja": 2}
ICONO_PRIORIDAD = {"alta": "🔴", "media": "🟠", "baja": "🟡"}


@dataclass
class Recomendacion:
    """Una recomendación accionable, con su evidencia."""
    prioridad: str            # alta | media | baja
    inteligencia: str         # cuál de las 7 la origina
    titulo: str               # qué hacer, en una línea
    diagnostico: str          # el dato que la justifica
    accion: str               # cómo llevarla a cabo
    fuente: str = ""          # de dónde sale el dato
    etiquetas: list = field(default_factory=list)


def ordenar(recs: list[Recomendacion]) -> list[Recomendacion]:
    """Ordena por prioridad (alta primero)."""
    return sorted(recs, key=lambda r: PRIORIDADES.get(r.prioridad, 9))


def _menciones(fila) -> int:
    """Nº de reseñas que mencionan el atributo.

    Con la PRCA, la columna `importancia` es el impacto (una fracción), y el recuento vive en
    `menciones`. Con el IPA clásico, `importancia` ES el nº de menciones. Este helper sirve a
    los dos, para que el texto de las recomendaciones nunca muestre "0 menciones".
    """
    m = fila.get("menciones") if hasattr(fila, "get") else None
    if m is not None and m == m:  # no NaN
        return int(m)
    return int(fila["importancia"])


def _por_impacto(fila) -> bool:
    """True si esta fila trae la importancia por impacto (PRCA), no la frecuencia."""
    m = fila.get("menciones") if hasattr(fila, "get") else None
    return m is not None and m == m


# Acción concreta según el atributo. Antes la recomendación del "peor atributo" tenía la acción
# fija en "revisar la reserva y la organización", lo que dejó de tener sentido al añadir
# Gastronomía y al medir la importancia por impacto: el peor atributo ya no es siempre la reserva.
ACCIONES_ATRIBUTO = {
    "Organización y reserva": ("Revisar el proceso de reserva y la organización de la visita de "
                               "punta a punta: confirmaciones, puntualidad, tamaño del grupo y "
                               "tiempos de espera."),
    "Precio y valor": ("Revisar la relación calidad-precio percibida. A menudo el problema no es "
                       "el precio sino que no se comunica bien qué incluye la visita o la cata."),
    "Gastronomía y restauración": ("Revisar la oferta gastronómica (tapeo, maridaje, "
                                   "restaurante): calidad, variedad y encaje con la visita. En el "
                                   "Marco el 'vino + comida' es cada vez más parte de la experiencia."),
    "Vino y cata": ("Revisar la cata en sí: número y variedad de vinos, explicación y ritmo. Es "
                    "el corazón del producto enoturístico."),
    "Personal y trato": ("Reforzar la formación del personal de sala y de los guías: es lo que "
                         "más deleita al visitante cuando va bien."),
    "Instalaciones": ("Revisar el estado, la comodidad y la señalización de las instalaciones "
                      "(salas, patios, accesibilidad, limpieza)."),
    "Visita y experiencia": ("Revisar el guion de la visita: contenido, duración y dinamismo, "
                             "para que se perciba como una experiencia y no como un trámite."),
    "Entorno y viñedo": ("Poner en valor el entorno y el viñedo (paisaje, vistas, paseos entre "
                         "cepas): suele ser un deleitador infrautilizado."),
}


def _accion_atributo(atributo: str, por_defecto: str = "") -> str:
    """Acción recomendada para un atributo concreto (o una genérica si no está mapeado)."""
    return ACCIONES_ATRIBUTO.get(atributo, por_defecto or
                                 "Analizar las reseñas negativas de este atributo para aislar la "
                                 "causa raíz y actuar sobre el proceso, no sobre el síntoma.")


# --------------------------------------------------------------------------- #
# Recomendaciones para el GESTOR DEL DESTINO
# --------------------------------------------------------------------------- #
def recomendaciones_destino(
    acevin=None, acevin_oferta=None, acevin_ingresos=None, acevin_demanda=None,
    trends=None, accesibilidad=None, transporte=None, auditoria=None,
    sostenibilidad=None, resumen_dipa=None, tabla_ipa=None, respuestas=None,
    anotadas=None, aereo_mercados=None, aereo_capacidad=None, cruceros=None,
) -> list[Recomendacion]:
    """Genera las recomendaciones para el conjunto del Marco de Jerez."""
    recs: list[Recomendacion] = []
    FOCO = "Marco de Jerez"

    def _vacio(df):
        return df is None or (hasattr(df, "empty") and df.empty)

    # --- 0. Bodegas que no responden a ninguna reseña (Clientes) ---
    if not _vacio(respuestas) and "% contestadas" in respuestas.columns:
        mudas = respuestas[respuestas["% contestadas"] == 0]
        criticas = int(mudas["Críticas (1-2★)"].sum()) if not mudas.empty else 0
        if len(mudas) >= 3 and criticas >= 50:
            peor = mudas.sort_values("Críticas (1-2★)", ascending=False).iloc[0]
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Clientes",
                titulo="Plan de respuesta a reseñas en las bodegas del Marco",
                diagnostico=(f"**{len(mudas)} de {len(respuestas)} bodegas no responden a "
                             f"ninguna reseña**, acumulando **{criticas} críticas de 1-2★ sin una "
                             f"sola respuesta**. La más expuesta: **{peor['Bodega']}** "
                             f"({int(peor['Críticas (1-2★)'])} críticas mudas)."),
                accion=("Formar a las bodegas en gestión de reputación online: responder es "
                        "**gratis** y lo lee el futuro visitante que está decidiendo. Es la "
                        "mejora de reputación de **menor coste y mayor visibilidad** del destino."),
                fuente="Reseñas de Google"))

    # --- 1. Desequilibrio demanda-oferta (Competidores / Negocios) ---
    if not _vacio(acevin) and not _vacio(acevin_oferta):
        ult = int(acevin["anio"].max())
        rank = acevin[acevin["anio"] == ult].sort_values("visitantes", ascending=False)
        rank = rank.reset_index(drop=True)
        of = acevin_oferta.sort_values("servicios", ascending=False).reset_index(drop=True)
        if FOCO in set(rank["ruta"]) and FOCO in set(of["ruta"]):
            pos_vis = int(rank.index[rank["ruta"] == FOCO][0]) + 1
            pos_of = int(of.index[of["ruta"] == FOCO][0]) + 1
            serv = int(of.loc[of["ruta"] == FOCO, "servicios"].iloc[0])
            lider_of = of.iloc[0]
            if pos_of > pos_vis + 2:
                recs.append(Recomendacion(
                    prioridad="alta", inteligencia="Negocios",
                    titulo="Ampliar y diversificar la oferta enoturística",
                    diagnostico=(f"El Marco es **{pos_vis}º en visitantes** pero solo "
                                 f"**{pos_of}º en oferta** ({serv} servicios, frente a los "
                                 f"{int(lider_of['servicios'])} de {lider_of['ruta']}). "
                                 f"La oferta no acompaña a la demanda."),
                    accion=("Captar nuevos socios para el club de producto (restauración, "
                            "alojamiento, experiencias) y ampliar el catálogo de actividades. "
                            "Alineado con la prioridad FEDER **P4A** (diversificar la oferta)."),
                    fuente=f"ACEVIN {ult}"))

    # --- 2. Brecha de monetización (Económica) ---
    if not _vacio(acevin_ingresos) and not _vacio(acevin):
        ing = acevin_ingresos[acevin_ingresos["ruta"] != "TOTAL Rutas del Vino de España"].copy()
        anio_i = int(acevin_ingresos["anio"].max())
        vis = acevin[acevin["anio"] == anio_i].set_index("ruta")["visitantes"]
        ing["visitantes"] = ing["ruta"].map(vis)
        ing = ing.dropna(subset=["visitantes"])
        if not ing.empty:
            ing["eur_vis"] = ing["ingresos_eur"] / ing["visitantes"]
            foco = ing[ing["ruta"] == FOCO]
            mejor = ing.sort_values("eur_vis", ascending=False).iloc[0]
            if not foco.empty and mejor["ruta"] != FOCO:
                brecha = mejor["eur_vis"] - foco["eur_vis"].iloc[0]
                if brecha > 10:
                    recs.append(Recomendacion(
                        prioridad="alta", inteligencia="Económica",
                        titulo="Elevar el ingreso por visitante",
                        diagnostico=(f"El Marco ingresa **{foco['eur_vis'].iloc[0]:.1f} € por "
                                     f"visitante**, frente a los **{mejor['eur_vis']:.1f} €** de "
                                     f"{mejor['ruta']}: **{brecha:.1f} € menos por cada visita**. "
                                     f"Lidera en volumen, pero monetiza peor."),
                        accion=("Revisar el precio de la visita (hoy por debajo del potencial), "
                                "impulsar la venta en tienda y crear **experiencias premium** "
                                "(catas verticales, maridajes, visitas privadas)."),
                        fuente=f"ACEVIN {anio_i}"))

    # --- 3. Déficit de captación digital (Mercado) ---
    if not _vacio(trends) and not _vacio(acevin):
        tcols = [c for c in trends.columns if c != "fecha"]
        if tcols:
            medias = trends[tcols].mean().sort_values(ascending=False)
            lider = medias.index[0]
            ult = int(acevin["anio"].max())
            rank = (acevin[acevin["anio"] == ult]
                    .sort_values("visitantes", ascending=False).reset_index(drop=True))
            es_lider_visitas = (not rank.empty and rank.iloc[0]["ruta"] == FOCO)
            if es_lider_visitas and "Jerez" not in lider:
                recs.append(Recomendacion(
                    prioridad="alta", inteligencia="Mercado",
                    titulo="Invertir en captación y posicionamiento digital",
                    diagnostico=(f"El Marco es **1º de España en visitantes reales**, pero **no "
                                 f"lidera el interés de búsqueda** en Google: por delante está "
                                 f"*{lider.replace('bodegas ', '')}*. El destino convierte bien, "
                                 f"pero tiene menos visibilidad digital que su competencia."),
                    accion=("Reforzar SEO y contenidos del destino, campañas de búsqueda pagada "
                            "en los mercados emisores y presencia en plataformas de reserva. "
                            "El potencial de crecimiento está en la fase de *descubrimiento*."),
                    fuente="Google Trends + ACEVIN"))

    # --- 3-ter. Cruceristas: mercado cautivo a 40 minutos (Mercado) ---
    if not _vacio(cruceros) and not _vacio(acevin):
        anios_ok = cruceros.groupby("AÑO")["MES"].nunique()
        # Último año COMPLETO de cruceros que además exista en ACEVIN (van desacompasados).
        completos = {int(a) for a in anios_ok[anios_ok >= 12].index}
        comunes = completos & {int(a) for a in acevin["anio"].unique()}
        if comunes:
            anio_c = max(comunes)
            n_cru = int(cruceros[cruceros["AÑO"] == anio_c]["PASAJEROS_CRUCERO"].sum())
            v = acevin[(acevin["anio"] == anio_c) & (acevin["ruta"] == FOCO)]
            if not v.empty and n_cru > int(v["visitantes"].iloc[0]):
                n_bod = int(v["visitantes"].iloc[0])
                recs.append(Recomendacion(
                    prioridad="alta", inteligencia="Mercado",
                    titulo="Capturar al crucerista: un mercado cautivo a 40 minutos",
                    diagnostico=(f"En {anio_c} desembarcaron **{n_cru:,}".replace(",", ".") +
                                 f" cruceristas** en la Bahía de Cádiz, **más que los "
                                 f"{n_bod:,}".replace(",", ".") +
                                 f" visitantes que recibieron TODAS las bodegas del Marco "
                                 f"juntas**. Y su temporada alta es **octubre-noviembre**, "
                                 f"justo cuando el enoturismo cae."),
                    accion=("Diseñar **excursiones de medio día** empaquetadas con las navieras "
                            "y las agencias receptivas del puerto (visita + cata, 4-5 horas). "
                            "Ataca a la vez dos objetivos: **captar demanda nueva** y **reducir "
                            "la estacionalidad** (prioridad FEDER P4A)."),
                    fuente="Dataestur — tráfico portuario + ACEVIN"))

    # --- 3-bis. Demanda aérea sin conectividad directa (Mercado) ---
    if not _vacio(aereo_mercados) and not _vacio(aereo_capacidad):
        mer = aereo_mercados[aereo_mercados["pais"] != "Total"].copy()
        asientos = (aereo_capacidad[aereo_capacidad["PAIS_ORIGEN"] != "Total"]
                    .groupby("PAIS_ORIGEN")["ASIENTOS"].sum())
        mer["asientos"] = mer["pais"].map(asientos).fillna(0)
        sin_vuelo = mer[(mer["asientos"] == 0) & (mer["busquedas"] >= 100_000)]
        if not sin_vuelo.empty:
            total_b = int(sin_vuelo["busquedas"].sum())
            paises = ", ".join(sin_vuelo.sort_values("busquedas", ascending=False)
                               .head(4)["pais"].tolist())
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Mercado",
                titulo="Negociar rutas aéreas directas con los mercados que ya nos buscan",
                diagnostico=(f"**{total_b:,}".replace(",", ".") +
                             f" búsquedas de vuelo a Jerez proceden de países **sin un solo "
                             f"asiento directo**: {paises}. La demanda **ya existe y está "
                             f"medida**; lo que falta es el avión."),
                accion=("Llevar estos datos a la mesa de negociación con aerolíneas y con el "
                        "Patronato de Turismo: no es una hipótesis, es **intención de viaje "
                        "cuantificada**. Es el argumento más fuerte para abrir ruta."),
                fuente="Dataestur — conectividad aérea"))

    # --- 4. Accesibilidad sensorial inexistente (Tecnológica) ---
    if not _vacio(accesibilidad):
        acc = accesibilidad[accesibilidad["web_ok"] == True]  # noqa: E712
        if not acc.empty and "menciona_apoyo_sensorial" in acc.columns:
            n_sen = int(acc["menciona_apoyo_sensorial"].sum())
            if n_sen == 0:
                recs.append(Recomendacion(
                    prioridad="alta", inteligencia="Tecnológica",
                    titulo="Plan de accesibilidad sensorial del destino",
                    diagnostico=(f"**Ninguna** de las {len(acc)} bodegas auditadas menciona "
                                 f"audioguías, braille, lengua de signos ni material accesible "
                                 f"para personas con discapacidad visual o auditiva. Es un "
                                 f"**vacío total** del destino."),
                    accion=("Impulsar un plan conjunto de accesibilidad sensorial (audioguías, "
                            "signoguías, material en braille) y certificarlo. Además de la "
                            "inclusión, es un **factor de diferenciación** frente a otras rutas."),
                    fuente="Auditoría de accesibilidad web"))

        # Zoom bloqueado: barrera grave y de arreglo trivial
        if not acc.empty and "zoom_permitido" in acc.columns:
            sin_zoom = int((~acc["zoom_permitido"].astype(bool)).sum())
            if sin_zoom / len(acc) > 0.2:
                recs.append(Recomendacion(
                    prioridad="media", inteligencia="Tecnológica",
                    titulo="Desbloquear el zoom en las webs de las bodegas",
                    diagnostico=(f"**{sin_zoom} de {len(acc)} webs "
                                 f"({sin_zoom / len(acc) * 100:.0f}%) impiden ampliar la página** "
                                 f"(`user-scalable=no`). Excluye directamente a personas con baja "
                                 f"visión."),
                    accion=("Es un arreglo **de una sola línea de código**. Comunicar a las "
                            "bodegas afectadas: quitar `user-scalable=no` y `maximum-scale=1` "
                            "de la etiqueta *viewport*."),
                    fuente="Auditoría de accesibilidad web"))

    # --- 5. Transporte público infrautilizado (Sostenibilidad) ---
    if not _vacio(transporte) and not _vacio(acevin_demanda):
        coche = acevin_demanda[
            acevin_demanda["indicador"] == "Llegan en vehículo propio o alquilado"]
        n_ok = int(transporte["accesible_transporte_publico"].sum())
        pct_ok = n_ok / len(transporte) * 100
        if not coche.empty and pct_ok >= 75 and coche["valor"].iloc[0] >= 60:
            recs.append(Recomendacion(
                prioridad="media", inteligencia="Sostenibilidad",
                titulo="Promocionar el transporte público que ya existe",
                diagnostico=(f"El **{pct_ok:.0f}% de las bodegas es accesible en transporte "
                             f"público**, pero el **{coche['valor'].iloc[0]:.0f}% de los "
                             f"enoturistas llega en coche**. El problema no es la "
                             f"infraestructura: es la **información y el hábito**."),
                accion=("Publicar cómo llegar en tren/autobús en cada ficha de bodega, crear "
                        "paquetes combinados transporte+visita y señalizar las paradas. "
                        "Reduce la huella sin necesidad de inversión en infraestructura."),
                fuente="OpenStreetMap + ACEVIN"))

    # --- 6. Atributo del destino que empeora (Clientes) ---
    if not _vacio(resumen_dipa):
        col_tend = "Tendencia" if "Tendencia" in resumen_dipa.columns else None
        if col_tend:
            empeora = resumen_dipa[resumen_dipa[col_tend] == "Empeora"]
            for _, r in empeora.iterrows():
                var = r.get("Variación", 0)
                recs.append(Recomendacion(
                    prioridad="alta", inteligencia="Clientes",
                    titulo=f"Frenar el deterioro de «{r['Atributo']}»",
                    diagnostico=(f"El **sentimiento** hacia **{r['Atributo']}** **empeora** con el "
                                 f"tiempo (variación {var:+.2f} puntos entre el primer y el último "
                                 f"periodo). Es un problema estructural, no un mal año."),
                    accion=_accion_atributo(r["Atributo"]),
                    fuente="Análisis DIPA (evolución del sentimiento por atributo)"))

    # --- 7. Atributo con desempeño crítico (Clientes) ---
    # Complementa al IPA: el cuadrante usa el nº de menciones como "importancia", lo que
    # infravalora atributos de los que el visitante solo habla cuando FALLAN (típicamente,
    # la organización y la reserva). Aquí se mira el desempeño en términos absolutos.
    if not _vacio(tabla_ipa) and {"atributo", "desempeno"} <= set(tabla_ipa.columns):
        media = tabla_ipa["desempeno"].mean()
        criticos = tabla_ipa[tabla_ipa["desempeno"] < media - 0.5]
        for _, r in criticos.sort_values("desempeno").iterrows():
            nota = ""
            if _por_impacto(r) and "Concéntrese" in str(r.get("cuadrante", "")):
                nota = (" La importancia por **impacto** (PRCA) lo sitúa en *«Concéntrese aquí»*: "
                        "aunque se mencione poco, **cuando el visitante habla de ello suele ser "
                        "porque ha fallado, y eso arrastra la nota de toda la visita**.")
                if str(r.get("perfil", "")) == "Higiénico":
                    nota += (" Es además un atributo **higiénico**: arreglarlo **evita quejas**, "
                             "pero no esperes que por sí solo suba la nota ni te diferencie.")
            elif "cuadrante" in tabla_ipa.columns and "Baja prioridad" in str(r.get("cuadrante", "")):
                nota = (" ⚠️ El IPA por frecuencia lo sitúa en *«Baja prioridad»* porque se "
                        "menciona poco, pero eso es engañoso: **de la organización y la reserva el "
                        "visitante solo habla cuando falla**. El nº de menciones infravalora su "
                        "importancia real.")
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Clientes",
                titulo=f"Punto débil del destino: «{r['atributo']}»",
                diagnostico=(f"Es de los atributos **peor valorados** del Marco: "
                             f"**{r['desempeno']:.2f}/5**, frente a una media de {media:.2f} en el "
                             f"resto ({_menciones(r)} menciones).{nota}"),
                accion=_accion_atributo(r["atributo"]),
                fuente="Sentimiento por atributo + importancia por impacto (PRCA)"))

    # --- 7-bis. El análisis es sordo al visitante extranjero (Clientes / metodológica) ---
    if not _vacio(anotadas) and "segmento_idioma" in getattr(anotadas, "columns", []):
        INTL = "Internacional (no hispanohablante)"
        intl = anotadas[anotadas["segmento_idioma"] == INTL]
        if len(intl) >= 100:
            ciego = (intl["atributos"].map(len) == 0).mean() * 100
            # El léxico ya es multilingüe; esta regla queda como vigilancia de la cobertura.
            if ciego >= 20:
                recs.append(Recomendacion(
                    prioridad="alta", inteligencia="Clientes",
                    titulo="Ampliar el léxico de atributos a más idiomas",
                    diagnostico=(f"**El {ciego:.0f}% de las {len(intl)} reseñas internacionales "
                                 f"no aporta ningún atributo**: el léxico no cubre bien sus "
                                 f"idiomas. El IPA se estaría construyendo sobre todo con la voz "
                                 f"del visitante hispanohablante."),
                    accion=("Ampliar el léxico de atributos a los idiomas que faltan. "
                            "Mientras la cobertura sea desigual, comparar la importancia entre "
                            "idiomas produce artefactos, no preferencias reales."),
                    fuente="Detección de idioma sobre las reseñas"))

    # --- 7-ter. Palanca de diferenciación: atributo DELEITADOR (Clientes) ---
    # La cara positiva del perfil higiene↔deleite: no solo dónde falla el destino, sino dónde
    # PUEDE destacar. Un deleitador crea satisfacción de verdad; conviene apoyarse en él.
    if not _vacio(tabla_ipa) and "perfil" in getattr(tabla_ipa, "columns", []):
        delei = tabla_ipa[tabla_ipa["perfil"] == "Deleitador"]
        if not delei.empty:
            r = delei.sort_values("desempeno", ascending=False).iloc[0]
            recs.append(Recomendacion(
                prioridad="media", inteligencia="Clientes",
                titulo=f"Palanca de diferenciación: «{r['atributo']}»",
                diagnostico=(f"**{r['atributo']}** es un atributo **deleitador**: cuando va bien "
                             f"**sube de verdad la satisfacción**, no solo evita quejas. Hoy "
                             f"puntúa **{r['desempeno']:.2f}/5**. Es donde el Marco puede destacar "
                             f"frente a otras rutas, más que en los atributos que se dan por supuestos."),
                accion=(_accion_atributo(r["atributo"]) + " Y **comunicarlo en la promoción** del "
                        "destino: es un motivo de visita, no un simple 'está bien'."),
                fuente="Perfil higiene↔deleite (PRCA)"))

    # --- 8. Reserva online insuficiente (Tecnológica) ---
    if not _vacio(auditoria):
        aud = auditoria[auditoria["web_ok"] == True]  # noqa: E712
        if not aud.empty and "reserva_online" in aud.columns:
            pct_res = aud["reserva_online"].mean() * 100
            if pct_res < 80:
                recs.append(Recomendacion(
                    prioridad="media", inteligencia="Tecnológica",
                    titulo="Extender la reserva online a todas las bodegas",
                    diagnostico=(f"Solo el **{pct_res:.0f}%** de las webs auditadas ofrece "
                                 f"reserva online, cuando el **63% de los enoturistas españoles "
                                 f"reserva por internet** (ACEVIN). Se está perdiendo demanda "
                                 f"en el canal donde el visitante decide."),
                    accion=("Acompañar a las bodegas sin reserva online a incorporar un motor "
                            "de reservas (propio o vía plataforma)."),
                    fuente="Auditoría web + ACEVIN"))

    return ordenar(recs)


# --------------------------------------------------------------------------- #
# Recomendaciones para una BODEGA
# --------------------------------------------------------------------------- #
def recomendaciones_bodega(
    nombre: str, ipa=None, ipca=None, dipca=None, fila_auditoria=None,
    fila_accesibilidad=None, fila_sostenibilidad=None, fila_transporte=None,
    rating=None, rating_marco=None, tasa_respuesta=None,
) -> list[Recomendacion]:
    """Genera las recomendaciones para una bodega concreta."""
    recs: list[Recomendacion] = []

    def _vacio(x):
        return x is None or (hasattr(x, "empty") and x.empty)

    # --- 0. Gestión de la reputación: ¿contesta a sus visitantes? ---
    # Es la acción más barata que existe: no cuesta dinero y la lee el futuro visitante.
    if tasa_respuesta:
        pct = tasa_respuesta.get("pct_total", 0)
        n_neg = tasa_respuesta.get("n_negativas", 0)
        if pct == 0 and n_neg >= 5:
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Clientes",
                titulo="Empezar a responder las reseñas (hoy no se responde ninguna)",
                diagnostico=(f"La bodega **no ha respondido a ninguna reseña**, ni siquiera a "
                             f"las **{n_neg} críticas de 1-2 estrellas**. Cada una queda ahí, "
                             f"sin réplica, para el próximo visitante que la lea."),
                accion=("Responder es **gratis** y es lo primero que ve quien duda. Contestar "
                        "las críticas con educación (reconocer, explicar, invitar a volver) "
                        "mejora la percepción incluso de quien no escribió la reseña."),
                fuente="Reseñas de Google"))
        elif pct < 15 and n_neg >= 10:
            recs.append(Recomendacion(
                prioridad="media", inteligencia="Clientes",
                titulo="Aumentar la respuesta a las reseñas",
                diagnostico=(f"Solo se responde al **{pct:.0f}%** de las reseñas, con "
                             f"{n_neg} críticas de 1-2★ acumuladas."),
                accion="Priorizar la respuesta a las críticas: son las que más se leen.",
                fuente="Reseñas de Google"))

    # --- 1. IPA: cuadrante "Concéntrese aquí" (mucha importancia, bajo desempeño) ---
    if not _vacio(ipa) and "cuadrante" in ipa.columns:
        criticos = ipa[ipa["cuadrante"].str.contains("Concéntrese", case=False, na=False)]
        for _, r in criticos.iterrows():
            if _por_impacto(r):
                diag = (f"Es de los atributos que **más mueven la satisfacción** en esta bodega "
                        f"(importancia por impacto, {_menciones(r)} menciones) pero con "
                        f"**desempeño bajo** ({r['desempeno']:.2f}/5). Cuadrante IPA: "
                        f"*Concéntrese aquí*.")
            else:
                diag = (f"Es de los atributos **más mencionados** por los visitantes "
                        f"({_menciones(r)} menciones) pero con **desempeño bajo** "
                        f"({r['desempeno']:.2f}/5). Cuadrante IPA: *Concéntrese aquí*.")
            # Matiz según el perfil: ¿arreglarlo diferencia o solo evita quejas?
            perfil = str(r.get("perfil", ""))
            if perfil == "Higiénico":
                diag += (" Es un atributo **higiénico**: arreglarlo evita quejas, pero no esperes "
                         "que por sí solo te diferencie.")
            elif perfil == "Deleitador":
                diag += (" Y es un atributo **deleitador**: mejorarlo no solo quita quejas, "
                         "**sube de verdad la satisfacción**. Doble motivo para priorizarlo.")
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Clientes",
                titulo=f"Prioridad de mejora: «{r['atributo']}»",
                diagnostico=diag,
                accion=_accion_atributo(r["atributo"]),
                fuente="IPA por impacto (PRCA) sobre las reseñas de la bodega"))

    # --- 1-bis. Palanca de diferenciación de la bodega: atributo DELEITADOR ---
    if not _vacio(ipa) and "perfil" in getattr(ipa, "columns", []):
        delei = ipa[ipa["perfil"] == "Deleitador"]
        if not delei.empty:
            r = delei.sort_values("desempeno", ascending=False).iloc[0]
            recs.append(Recomendacion(
                prioridad="media", inteligencia="Clientes",
                titulo=f"Dónde puede destacar: «{r['atributo']}»",
                diagnostico=(f"**{r['atributo']}** es un **deleitador** para los visitantes de "
                             f"esta bodega (crea satisfacción de verdad) y hoy puntúa "
                             f"**{r['desempeno']:.2f}/5**. Es su palanca para diferenciarse."),
                accion=(_accion_atributo(r["atributo"]) + " Y usarlo como gancho en la web y en "
                        "la comunicación de la bodega."),
                fuente="Perfil higiene↔deleite (PRCA)"))

    # --- 2. IPCA: por detrás del Marco en un atributo importante ---
    # (cuadrante 1 = "Actuar: por detrás del Marco")
    if not _vacio(ipca) and "cuadrante" in ipca.columns:
        detras = ipca[ipca["cuadrante"].str.contains("por detrás", case=False, na=False)]
        for _, p in detras.iterrows():
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Competidores",
                titulo=f"Recortar distancia con el Marco en «{p['atributo']}»",
                diagnostico=(f"En **{p['atributo']}** la bodega puntúa "
                             f"**{p['Esta bodega']:.2f}** frente a **{p['Media del Marco']:.2f}** "
                             f"de la media del Marco (brecha **{p['brecha']:+.2f}**), y es un "
                             f"atributo importante para los visitantes."),
                accion=("Observar cómo lo resuelven las bodegas mejor valoradas del Marco en "
                        "este atributo concreto y adaptar el proceso."),
                fuente="Análisis IPCA (competitivo)"))

    # --- 3. DIPCA: la brecha competitiva se amplía ---
    if not _vacio(dipca) and "tendencia" in dipca.columns:
        pierde = dipca[dipca["tendencia"].str.contains("Pierde", case=False, na=False)]
        for _, p in pierde.iterrows():
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Competidores",
                titulo=f"Alerta: se pierde terreno en «{p['atributo']}»",
                diagnostico=(f"La brecha frente al Marco en **{p['atributo']}** **se está "
                             f"ampliando**: pasó de {p['brecha_inicial']:+.2f} a "
                             f"{p['brecha_final']:+.2f}. No es un bache puntual, va a peor."),
                accion="Actuar ya: cuanto más se amplíe la brecha, más costará cerrarla.",
                fuente="Análisis DIPCA (competitivo dinámico)"))

    # --- 4. Reputación por debajo de la media del Marco ---
    if rating is not None and rating_marco is not None and rating < rating_marco - 0.15:
        recs.append(Recomendacion(
            prioridad="media", inteligencia="Competidores",
            titulo="Reputación por debajo de la media del Marco",
            diagnostico=(f"Nota media **{rating:.2f}** frente a **{rating_marco:.2f}** del "
                         f"conjunto del Marco."),
            accion=("Responder a las reseñas negativas e invitar a los visitantes satisfechos "
                    "a valorar. La nota en Google condiciona la elección del enoturista."),
            fuente="Censo de reseñas de Google"))

    # --- 5. Madurez digital (auditoría web) ---
    if fila_auditoria is not None and bool(fila_auditoria.get("web_ok")):
        if not fila_auditoria.get("reserva_online"):
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Tecnológica",
                titulo="Habilitar la reserva online",
                diagnostico=("La web no ofrece reserva online, y el **63% de los enoturistas "
                             "españoles reserva por internet** (ACEVIN)."),
                accion="Incorporar un motor de reservas propio o vía plataforma.",
                fuente="Auditoría web + ACEVIN"))
        if not fila_auditoria.get("ingles"):
            recs.append(Recomendacion(
                prioridad="media", inteligencia="Tecnológica",
                titulo="Publicar la web en inglés",
                diagnostico=("No se detecta versión en inglés, pese a que una parte relevante de "
                             "las reseñas del Marco no está escrita en español."),
                accion="Traducir al menos la información de visitas, horarios y reservas.",
                fuente="Auditoría web"))

    # --- 6. Accesibilidad ---
    if fila_accesibilidad is not None and bool(fila_accesibilidad.get("web_ok")):
        if not fila_accesibilidad.get("zoom_permitido"):
            recs.append(Recomendacion(
                prioridad="alta", inteligencia="Tecnológica",
                titulo="Desbloquear el zoom de la web (barrera de accesibilidad)",
                diagnostico=("La web **impide ampliar la página** (`user-scalable=no`), lo que "
                             "excluye a personas con baja visión."),
                accion=("Arreglo de **una línea**: quitar `user-scalable=no` / `maximum-scale=1` "
                        "de la etiqueta *viewport*."),
                fuente="Auditoría de accesibilidad (WCAG)"))
        if not fila_accesibilidad.get("imagenes_con_alt"):
            recs.append(Recomendacion(
                prioridad="media", inteligencia="Tecnológica",
                titulo="Añadir texto alternativo a las imágenes",
                diagnostico=("Más del 20% de las imágenes no tiene texto alternativo (`alt`): un "
                             "lector de pantalla no puede describirlas."),
                accion="Describir cada imagen relevante en su atributo `alt`.",
                fuente="Auditoría de accesibilidad (WCAG)"))
        if not fila_accesibilidad.get("menciona_apoyo_sensorial"):
            recs.append(Recomendacion(
                prioridad="baja", inteligencia="Tecnológica",
                titulo="Oportunidad: ofrecer y comunicar apoyo sensorial",
                diagnostico=("La web no menciona audioguías, braille ni lengua de signos. "
                             "**Ninguna bodega del Marco lo hace**: quien dé el paso será la "
                             "primera."),
                accion="Incorporar audioguía o signoguía en la visita y comunicarlo en la web.",
                fuente="Auditoría de accesibilidad"))

    # --- 7. Sostenibilidad ---
    if fila_sostenibilidad is not None:
        if not bool(fila_sostenibilidad.get("certificado_swfcp")):
            recs.append(Recomendacion(
                prioridad="baja", inteligencia="Sostenibilidad",
                titulo="Valorar la certificación climática de la FEV",
                diagnostico=("La bodega no figura en el sello *Sustainable Wineries for Climate "
                             "Protection*, que sí tienen otras bodegas del Marco."),
                accion="Estudiar la adhesión al sello: es un distintivo reconocido y comunicable.",
                fuente="Listado oficial FEV"))

    # --- 8. Transporte ---
    if fila_transporte is not None and not fila_transporte.get("accesible_transporte_publico", True):
        recs.append(Recomendacion(
            prioridad="media", inteligencia="Sostenibilidad",
            titulo="Facilitar la llegada sin coche",
            diagnostico=(f"La bodega **no es alcanzable a pie** desde el transporte público "
                         f"(parada de autobús más cercana a "
                         f"{fila_transporte.get('dist_bus_km', '?')} km)."),
            accion=("Ofrecer traslado desde el centro urbano o acuerdos con empresas de "
                    "transporte; e indicarlo con claridad en la web."),
            fuente="OpenStreetMap"))

    return ordenar(recs)
