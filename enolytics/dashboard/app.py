"""Cuadro de mando ENOLYTICS (Streamlit) — versión inicial.

Ya operativo con el catálogo de bodegas: mapa, tabla y ficha de detalle, con las
dos vistas por rol previstas (Bodega / Gestor de destino). Los módulos de reseñas,
NLP e IPA se irán integrando aquí a medida que se desarrollen.

Ejecutar desde la raíz del proyecto:
    python3 -m streamlit run enolytics/dashboard/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Permite ejecutar con `streamlit run` resolviendo el paquete enolytics
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import plotly.express as px  # noqa: E402

from enolytics import config  # noqa: E402
from enolytics.etl import resenas as etl_resenas  # noqa: E402
from enolytics.nlp import analisis as nlp  # noqa: E402
from enolytics.analitica import ipa as modelo_ipa  # noqa: E402


st.set_page_config(page_title="ENOLYTICS — Marco de Jerez", page_icon="🍷", layout="wide")


@st.cache_data
def cargar_bodegas() -> pd.DataFrame:
    if not config.CATALOGO_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(config.CATALOGO_CSV)
    for col in ("gps_lat", "gps_lon"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def cargar_resenas() -> pd.DataFrame:
    return etl_resenas.cargar_resenas()


@st.cache_data
def cargar_censo() -> pd.DataFrame:
    return etl_resenas.cargar_censo()


@st.cache_data
def cargar_resenas_anotadas() -> pd.DataFrame:
    """Reseñas con sentimiento y atributos detectados (se calcula una vez)."""
    r = etl_resenas.cargar_resenas()
    return nlp.anotar_resenas(r) if not r.empty else pd.DataFrame()


def ipa_desde_anotadas(an: pd.DataFrame) -> pd.DataFrame:
    """De un conjunto de reseñas anotadas -> tabla IPA (importancia, desempeño, cuadrante)."""
    if an.empty:
        return pd.DataFrame()
    tab = nlp.tabla_importancia_desempeno(an)
    if tab.empty:
        return pd.DataFrame()
    puntos = modelo_ipa.calcular_ipa(tab.to_dict("records"))
    return pd.DataFrame([{
        "atributo": p.atributo, "importancia": p.importancia,
        "desempeno": p.desempeno, "cuadrante": p.etiqueta,
    } for p in puntos])


def ipca_desde_anotadas(focal_an: pd.DataFrame, comp_an: pd.DataFrame) -> pd.DataFrame:
    """IPCA de una bodega (focal) frente a la competencia (resto del Marco)."""
    if focal_an.empty or comp_an.empty:
        return pd.DataFrame()
    focal = nlp.tabla_importancia_desempeno(focal_an)
    comp = nlp.tabla_importancia_desempeno(comp_an)
    if focal.empty or comp.empty:
        return pd.DataFrame()
    comp_perf = dict(zip(comp["atributo"], comp["desempeno"]))
    puntos = modelo_ipa.calcular_ipca(focal.to_dict("records"), comp_perf)
    return pd.DataFrame([{
        "atributo": p.atributo, "importancia": p.importancia,
        "Esta bodega": p.desempeno_focal, "Media del Marco": p.desempeno_competencia,
        "brecha": p.brecha, "cuadrante": p.etiqueta,
    } for p in puntos])


def dipca_bodega(an_bod: pd.DataFrame, comp_an: pd.DataFrame,
                 min_resenas: int = 60, min_menciones: int = 10) -> pd.DataFrame:
    """DIPCA de una bodega: evolución de su brecha vs. el Marco entre dos periodos."""
    f = an_bod[an_bod["fecha"].notna()].copy()
    if len(f) < min_resenas:
        return pd.DataFrame()
    f["fecha"] = pd.to_datetime(f["fecha"]).dt.tz_localize(None)
    c = comp_an[comp_an["fecha"].notna()].copy()
    c["fecha"] = pd.to_datetime(c["fecha"]).dt.tz_localize(None)
    corte = f["fecha"].median()

    def _brechas(focal, comp):
        tf = nlp.tabla_importancia_desempeno(focal)
        tc = nlp.tabla_importancia_desempeno(comp)
        cf = dict(zip(tc["atributo"], tc["desempeno"]))
        tf = tf[tf["importancia"] >= min_menciones]
        return {r["atributo"]: round(r["desempeno"] - cf[r["atributo"]], 3)
                for _, r in tf.iterrows() if r["atributo"] in cf}

    bi = _brechas(f[f["fecha"] <= corte], c[c["fecha"] <= corte])
    bf = _brechas(f[f["fecha"] > corte], c[c["fecha"] > corte])
    filas = modelo_ipa.calcular_dipca(bi, bf)
    if not filas:
        return pd.DataFrame()
    df_out = pd.DataFrame(filas)
    df_out.attrs["corte"] = corte.date().isoformat()
    return df_out


def figura_ipca(tabla: pd.DataFrame):
    """Gráfico IPCA: importancia (x) vs brecha frente al Marco (y)."""
    umbral_imp = tabla["importancia"].mean()
    fig = px.scatter(
        tabla, x="importancia", y="brecha", text="atributo",
        color="cuadrante", size="importancia", size_max=40,
        labels={"importancia": "Importancia (nº menciones)",
                "brecha": "Brecha vs Marco (+ mejor / − peor)"},
    )
    fig.add_hline(y=0, line_color="gray")
    fig.add_vline(x=umbral_imp, line_dash="dash", line_color="gray")
    fig.update_traces(textposition="top center")
    fig.update_layout(height=480, legend_title_text="Situación")
    return fig


def figura_ipa(tabla: pd.DataFrame):
    """Construye el gráfico de cuadrantes IPA (scatter con líneas de umbral)."""
    umbral_imp = tabla["importancia"].mean()
    umbral_des = tabla["desempeno"].mean()
    fig = px.scatter(
        tabla, x="importancia", y="desempeno", text="atributo",
        color="cuadrante", size="importancia", size_max=40,
        labels={"importancia": "Importancia (nº menciones)",
                "desempeno": "Desempeño (nota media)"},
    )
    fig.add_hline(y=umbral_des, line_dash="dash", line_color="gray")
    fig.add_vline(x=umbral_imp, line_dash="dash", line_color="gray")
    fig.update_traces(textposition="top center")
    fig.update_layout(height=480, legend_title_text="Cuadrante")
    return fig


@st.cache_data
def cargar_oferta() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "oferta_enoturistica.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_sostenibilidad() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "sostenibilidad.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_auditoria() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "auditoria_web.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_trends_temporal() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "google_trends" / "interes_temporal.csv"
    if not ruta.exists():
        return pd.DataFrame()
    df = pd.read_csv(ruta, parse_dates=["fecha"])
    return df


@st.cache_data
def cargar_trends_regiones() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "google_trends" / "interes_regiones.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_acevin() -> pd.DataFrame:
    """Visitantes por ruta del vino y año (ACEVIN, fuente oficial)."""
    ruta = config.DATOS_PROCESADO / "acevin" / "visitantes_rutas.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_gasto_cadiz() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "dataestur" / "GASTO_TPV_DESTINO_PROV_MES_HISTORICO_DL.csv"
    if not ruta.exists():
        return pd.DataFrame()
    df = pd.read_csv(ruta)
    df["fecha"] = pd.to_datetime(df["ANYOMES"].astype(str), format="%Y%m", errors="coerce")
    return df


@st.cache_data
def cargar_satisfaccion_cadiz() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "dataestur" / "IND_SATISFACCION_PERCEPCION_DL_Andalucia.csv"
    if not ruta.exists():
        return pd.DataFrame()
    df = pd.read_csv(ruta)
    return df[df["PROVINCIA"].astype(str).str.strip() == "Cádiz"].copy()


@st.cache_data
def cargar_evolucion() -> pd.DataFrame:
    an = cargar_resenas_anotadas()
    if an.empty:
        return pd.DataFrame()
    return nlp.evolucion_atributos(an, freq="Y", min_menciones=15)


def cabecera_inteligencia(clave: str) -> None:
    """Muestra el objetivo de la inteligencia según la memoria + su categoría SEGITTUR."""
    info = config.OBJETIVOS_INTELIGENCIAS.get(clave)
    if not info:
        return
    st.info(f"🎯 **Objetivo (Memoria Científico-Técnica):** {info['objetivo']}")
    with st.expander(f"Categoría SEGITTUR: **{info['segittur']}** · Indicadores previstos "
                     f"(Tabla 1 de la memoria)"):
        for ind in info["indicadores"]:
            st.markdown(f"- {ind}")


def resumen_dipa(ev: pd.DataFrame, anios: int = 3) -> pd.DataFrame:
    """Compara el desempeño de los primeros vs. los últimos `anios` con datos (DIPA)."""
    if ev.empty:
        return pd.DataFrame()
    years = sorted(ev["periodo"].dt.year.unique())
    if len(years) < 2 * anios:
        anios = max(1, len(years) // 2)
    ini_years, fin_years = years[:anios], years[-anios:]

    def _perf(yy):
        sub = ev[ev["periodo"].dt.year.isin(yy)]
        return (sub.groupby("atributo")
                .apply(lambda g: (g["desempeno"] * g["menciones"]).sum() / g["menciones"].sum(),
                       include_groups=False).to_dict())

    puntos = modelo_ipa.calcular_dipa(_perf(ini_years), _perf(fin_years))
    etq_ini = f"{ini_years[0]}-{ini_years[-1]}"
    etq_fin = f"{fin_years[0]}-{fin_years[-1]}"
    return pd.DataFrame([{
        "Atributo": p["atributo"], etq_ini: p["desempeno_inicial"],
        etq_fin: p["desempeno_final"], "Variación": p["variacion"],
        "Tendencia": p["tendencia"],
    } for p in puntos])


df = cargar_bodegas()
resenas = cargar_resenas()
censo = cargar_censo()
anotadas = cargar_resenas_anotadas()
tabla_ipa = ipa_desde_anotadas(anotadas)
evolucion = cargar_evolucion()
oferta = cargar_oferta()
sostenibilidad = cargar_sostenibilidad()
auditoria = cargar_auditoria()
gasto_cadiz = cargar_gasto_cadiz()
satisf_cadiz = cargar_satisfaccion_cadiz()
trends_temporal = cargar_trends_temporal()
trends_regiones = cargar_trends_regiones()
acevin = cargar_acevin()

st.title("🍷 ENOLYTICS — Inteligencia enoturística del Marco de Jerez")

if df.empty:
    st.warning(
        "No hay catálogo de bodegas todavía. Genera el catálogo con:\n\n"
        "`python3 scripts/actualizar_catalogo.py`"
    )
    st.stop()

# --- Barra lateral: rol y filtros ---
with st.sidebar:
    st.header("Configuración")
    rol = st.radio("Vista", ["Gestor de destino", "Bodega individual"])
    localidades = sorted(df["localidad"].dropna().unique())
    sel_local = st.multiselect("Localidad", localidades, default=localidades)

df_f = df[df["localidad"].isin(sel_local)]

# --------------------------------------------------------------------------- #
# Vista GESTOR: panorámica del destino
# --------------------------------------------------------------------------- #
if rol == "Gestor de destino":
    # Cabecera de indicadores (siempre visible sobre las pestañas)
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Bodegas", len(df_f))
    h2.metric("Recursos enoturísticos", len(oferta) if not oferta.empty else "—")
    if not acevin.empty:
        _ult = int(acevin["anio"].max())
        _vis = acevin[(acevin["anio"] == _ult) & (acevin["ruta"] == "Marco de Jerez")]["visitantes"]
        if not _vis.empty:
            h3.metric(f"Visitantes {_ult}", f"{int(_vis.iloc[0]):,}".replace(",", "."),
                      help="Visitas a bodegas y museos del Marco (ACEVIN).")
    elif not censo.empty:
        h3.metric("Reseñas en Google", f"{int(censo['total_resenas'].fillna(0).sum()):,}")
    if not sostenibilidad.empty:
        h4.metric("Bodegas sostenibles", int(sostenibilidad["certificado_swfcp"].sum()))

    st.caption("Una pestaña por cada una de las **7 inteligencias competitivas** del modelo ENOLYTICS.")
    tab_eco, tab_mer, tab_comp, tab_cli, tab_neg, tab_tec, tab_sos = st.tabs(
        ["💶 Económica", "📈 Mercado", "🥊 Competidores", "😊 Clientes",
         "🏛️ Negocios", "🖥️ Tecnológica", "🌱 Sostenibilidad"])

    # Precálculo del gasto anual (Dataestur), reutilizado en Económica y Mercado
    gasto_anio = pd.DataFrame()
    anio_ref = None
    if not gasto_cadiz.empty:
        _pa = gasto_cadiz.groupby("AÑO")["MES"].nunique()
        _comp = _pa[_pa >= 12].index
        anio_ref = int(_comp.max()) if len(_comp) else int(gasto_cadiz["AÑO"].max())
        gasto_anio = gasto_cadiz[gasto_cadiz["AÑO"] == anio_ref]

    # ----- 1. Inteligencia Económica -----
    with tab_eco:
        cabecera_inteligencia("economica")
        st.caption("Impacto económico del enoturismo. Fuente oficial: Dataestur (SEGITTUR), "
                   "provincia de Cádiz. Pendiente: facturación y empleo por bodega (SABI).")
        if gasto_anio.empty:
            st.info("Sin datos de gasto todavía.")
        else:
            nac = gasto_anio[gasto_anio["TIPO_ORIGEN"] == "Total Nacional"]["GASTO"].sum()
            intl = gasto_anio[gasto_anio["TIPO_ORIGEN"] == "Internacional"]["GASTO"].sum()
            m1, m2, m3 = st.columns(3)
            m1.metric(f"Gasto turístico total {anio_ref}", f"{(nac + intl) / 1e6:,.0f} M€")
            m2.metric("Gasto internacional", f"{intl / 1e6:,.0f} M€",
                      f"{intl / (nac + intl) * 100:.0f}% del total")
            m3.metric("Gasto nacional", f"{nac / 1e6:,.0f} M€")
            st.caption("Evolución mensual del gasto con tarjeta (€)")
            serie = gasto_cadiz[gasto_cadiz["TIPO_ORIGEN"].isin(["Total Nacional", "Internacional"])]
            pivot = serie.pivot_table(index="fecha", columns="TIPO_ORIGEN", values="GASTO", aggfunc="sum")
            st.line_chart(pivot)

    # ----- 2. Inteligencia de Mercado -----
    with tab_mer:
        cabecera_inteligencia("mercado")
        st.caption("Demanda y percepción del destino. Fuentes: Google Trends (interés de "
                   "búsqueda) y Dataestur (gasto y percepción). Comparación con las rutas "
                   "del vino competidoras.")
        if gasto_anio.empty and satisf_cadiz.empty and trends_temporal.empty:
            st.info("Sin datos de mercado todavía.")

        # --- Interés de búsqueda (Google Trends) ---
        if not trends_temporal.empty:
            termcols = [c for c in trends_temporal.columns if c != "fecha"]
            foco = next((c for c in termcols if "Jerez" in c), termcols[0])
            # Google devuelve datos semanales en 5 años: remuestreamos a meses.
            mensual = (trends_temporal.set_index("fecha")[termcols]
                       .resample("MS").mean())
            medias = mensual.mean().sort_values(ascending=False)
            rank = list(medias.index).index(foco) + 1

            # Tendencia del foco: media de los primeros vs. los últimos 24 meses (2 años)
            serie_foco = mensual[foco].dropna()
            n = min(24, len(serie_foco) // 2)
            ini, fin = serie_foco.head(n).mean(), serie_foco.tail(n).mean()
            var = (fin - ini) / ini * 100 if ini else 0.0

            st.markdown("**Interés de búsqueda en Google (últimos 5 años, escala 0-100 comparativa)**")
            c1, c2, c3 = st.columns(3)
            etq_foco = foco.replace("bodegas ", "").strip()
            c1.metric(f"Posición de {etq_foco}", f"{rank}º de {len(termcols)}",
                      help="Ranking por interés medio de búsqueda frente a las rutas competidoras.")
            c2.metric(f"Interés medio de {etq_foco}", f"{medias[foco]:.0f}",
                      f"líder: {medias.index[0].replace('bodegas ', '')} ({medias.iloc[0]:.0f})")
            c3.metric("Tendencia de la demanda", f"{var:+.0f}%",
                      help="Variación del interés entre los primeros y los últimos 2 años.")

            # Evolución suavizada (media móvil de 6 meses) para ver la tendencia sin ruido
            suave = mensual.rolling(6, min_periods=2).mean()
            suave.columns = [c.replace("bodegas ", "") for c in suave.columns]
            st.caption("Evolución del interés (media móvil de 6 meses)")
            st.line_chart(suave)

            if not trends_regiones.empty:
                top = trends_regiones.head(8).set_index("comunidad")["interes"]
                st.caption(f"Origen de la demanda: comunidades que más buscan «{foco}» (0-100)")
                st.bar_chart(top)
            st.divider()

        if not gasto_anio.empty:
            st.markdown(f"**Gasto por procedencia del turista ({anio_ref})**")
            comp = (gasto_anio[gasto_anio["TIPO_ORIGEN"].isin(["Internacional", "Interregional", "Regional"])]
                    .groupby("TIPO_ORIGEN")["GASTO"].sum() / 1e6)
            st.bar_chart(comp)
        if not satisf_cadiz.empty:
            idx_cols = [c for c in satisf_cadiz.columns if c.startswith("IN")]
            medias_p = satisf_cadiz[idx_cols].apply(pd.to_numeric, errors="coerce").mean()
            st.markdown("**Índices de percepción del visitante en Cádiz (media, sobre 100)**")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Percepción global", f"{medias_p.get('INIDICE_PERCEPCION_TURISTICA_GLOBAL', float('nan')):.0f}")
            s2.metric("Satisf. productos", f"{medias_p.get('INDICE_SATISFACCION_PRODUCTOS_TURISTICOS', float('nan')):.0f}")
            s3.metric("Seguridad", f"{medias_p.get('INDICE_PERCEPCION_SEGURIDAD', float('nan')):.0f}")
            s4.metric("Clima", f"{medias_p.get('INDICE_PERCEPCION_CLIMATICA', float('nan')):.0f}")

    # ----- 3. Inteligencia de Competidores -----
    with tab_comp:
        cabecera_inteligencia("competidores")
        st.caption("El Marco de Jerez **frente a otras rutas del vino de España**. "
                   "Fuente oficial: Observatorio Turístico de Rutas del Vino de España (ACEVIN).")

        # --- A. Posición del Marco entre las rutas del vino (ACEVIN) ---
        if acevin.empty:
            st.info("Sin datos de ACEVIN todavía.")
        else:
            FOCO = "Marco de Jerez"
            ult = int(acevin["anio"].max())
            prev = int(acevin[acevin["anio"] < ult]["anio"].max()) if (acevin["anio"] < ult).any() else None

            rank_ult = (acevin[acevin["anio"] == ult]
                        .sort_values("visitantes", ascending=False)
                        .reset_index(drop=True))
            pos = int(rank_ult.index[rank_ult["ruta"] == FOCO][0]) + 1 if FOCO in set(rank_ult["ruta"]) else None
            vis_ult = int(rank_ult.loc[rank_ult["ruta"] == FOCO, "visitantes"].iloc[0]) if pos else 0

            c1, c2, c3 = st.columns(3)
            c1.metric(f"Posición del Marco ({ult})", f"{pos}º de {len(rank_ult)}",
                      help="Ranking por nº de visitantes a bodegas y museos (ACEVIN).")
            c2.metric(f"Visitantes {ult}", f"{vis_ult:,}".replace(",", "."))
            if prev:
                vis_prev = acevin[(acevin["anio"] == prev) & (acevin["ruta"] == FOCO)]["visitantes"]
                if not vis_prev.empty and int(vis_prev.iloc[0]):
                    var = (vis_ult - int(vis_prev.iloc[0])) / int(vis_prev.iloc[0]) * 100
                    c3.metric(f"Crecimiento vs {prev}", f"{var:+.1f}%")

            st.markdown(f"**Visitantes por ruta del vino ({ult})**")
            st.bar_chart(rank_ult.set_index("ruta")["visitantes"])

            st.markdown("**Evolución de visitantes por ruta**")
            piv = acevin.pivot_table(index="anio", columns="ruta", values="visitantes")
            st.line_chart(piv)

            # Tabla-ranking con crecimiento interanual
            if prev:
                tab = rank_ult.merge(
                    acevin[acevin["anio"] == prev][["ruta", "visitantes"]],
                    on="ruta", how="left", suffixes=("", "_prev"))
                tab["Crecimiento"] = ((tab["visitantes"] - tab["visitantes_prev"])
                                      / tab["visitantes_prev"] * 100).round(1)
                tab.insert(0, "Pos.", range(1, len(tab) + 1))
                st.dataframe(
                    tab[["Pos.", "ruta", "visitantes", "visitantes_prev", "Crecimiento"]].rename(
                        columns={"ruta": "Ruta del vino", "visitantes": f"Visitantes {ult}",
                                 "visitantes_prev": f"Visitantes {prev}", "Crecimiento": "Crec. %"}),
                    use_container_width=True, hide_index=True,
                )

            # --- B. Demanda real vs. interés digital (el contraste estratégico) ---
            if not trends_temporal.empty:
                st.divider()
                st.markdown("**Demanda real (visitas) vs. interés digital (búsquedas)**")
                tcols = [c for c in trends_temporal.columns if c != "fecha"]
                medias_t = trends_temporal[tcols].mean().sort_values(ascending=False)
                lider_t = medias_t.index[0].replace("bodegas ", "")
                if pos == 1 and "Jerez" not in lider_t:
                    vis_fmt = f"{vis_ult:,}".replace(",", ".")
                    st.warning(
                        f"⚠️ **Paradoja competitiva:** el Marco de Jerez es **1º de España en "
                        f"visitantes reales** ({vis_fmt} en {ult}), pero **no lidera el interés "
                        f"de búsqueda** en Google (lo lidera *{lider_t}*). Hay margen de mejora "
                        f"en captación y posicionamiento digital."
                    )
                st.caption(
                    "Matiz: ACEVIN cuenta Rioja Alta y Rioja Alavesa como **rutas separadas**. "
                    "Sumadas, la Rioja supera al Marco en visitantes, lo que ayuda a explicar su "
                    "mayor volumen de búsquedas. El Marco es líder **como ruta individual**."
                )

        # --- C. Posicionamiento dentro del Marco (benchmarking interno) ---
        st.divider()
        with st.expander("Posicionamiento dentro del Marco (reputación por bodega)"):
            if censo.empty:
                st.info("Sin datos de reseñas todavía.")
            else:
                st.caption("Reputación online de cada bodega del Marco. El análisis competitivo "
                           "IPCA por bodega está en la vista 'Bodega individual'.")
                cen = censo.dropna(subset=["total_resenas"]).sort_values("total_resenas", ascending=False)
                cola, colb = st.columns(2)
                with cola:
                    st.caption("Nº de reseñas por bodega (Top 15)")
                    st.bar_chart(cen.head(15).set_index("bodega")["total_resenas"])
                with colb:
                    st.caption("Nota media por bodega (Top 15 por reseñas)")
                    st.bar_chart(cen.head(15).set_index("bodega")["rating"])
                st.dataframe(
                    cen[["bodega", "nombre_google", "rating", "total_resenas"]].rename(
                        columns={"bodega": "Bodega", "nombre_google": "Nombre en Google",
                                 "rating": "Nota", "total_resenas": "Reseñas"}),
                    use_container_width=True, hide_index=True,
                )

        st.caption("⚠️ Pendiente (Tabla 1 de la memoria): **comparación de precios** de servicios "
                   "enoturísticos y **estrategias diferenciadoras** de otras rutas.")

    # ----- 4. Inteligencia de Clientes -----
    with tab_cli:
        cabecera_inteligencia("clientes")
        st.caption("Satisfacción, motivaciones y atributos valorados por el visitante "
                   "(análisis de 10.972 reseñas de Google).")
        if tabla_ipa.empty and evolucion.empty:
            st.info("Sin datos de reseñas todavía.")
        if not tabla_ipa.empty:
            st.subheader("Análisis Importancia-Desempeño (IPA) del destino")
            st.caption("Importancia = nº de menciones · desempeño = nota media.")
            st.plotly_chart(figura_ipa(tabla_ipa), use_container_width=True)
            st.dataframe(
                tabla_ipa.rename(columns={"atributo": "Atributo", "importancia": "Importancia",
                                          "desempeno": "Desempeño", "cuadrante": "Cuadrante IPA"}),
                use_container_width=True, hide_index=True,
            )
        if not evolucion.empty:
            st.subheader("Evolución temporal (DIPA)")
            st.caption("Desempeño medio de cada atributo por año. Revela si la satisfacción mejora o empeora.")
            fig_dipa = px.line(
                evolucion, x="periodo", y="desempeno", color="atributo", markers=True,
                labels={"periodo": "Año", "desempeno": "Desempeño (nota media)", "atributo": "Atributo"},
            )
            fig_dipa.update_layout(height=460, legend_title_text="Atributo")
            st.plotly_chart(fig_dipa, use_container_width=True)
            tabla_dipa = resumen_dipa(evolucion)
            if not tabla_dipa.empty:
                st.caption("Cambio del primer al último periodo con datos:")
                st.dataframe(tabla_dipa, use_container_width=True, hide_index=True)

    # ----- 5. Inteligencia de Negocios -----
    with tab_neg:
        cabecera_inteligencia("negocios")
        st.caption("Infraestructura y oferta enoturística del destino (club de producto de la Ruta).")
        if not oferta.empty:
            oc1, oc2 = st.columns([1, 2])
            with oc1:
                st.metric("Recursos enoturísticos", len(oferta))
                st.metric("Categorías", oferta["categoria"].nunique())
            with oc2:
                conteo = oferta["categoria"].value_counts()
                conteo.index = [c.replace("-", " ").capitalize() for c in conteo.index]
                st.bar_chart(conteo)

        st.subheader("Mapa de bodegas")
        mapa = df_f.dropna(subset=["gps_lat", "gps_lon"]).rename(
            columns={"gps_lat": "lat", "gps_lon": "lon"}
        )
        if not mapa.empty:
            st.map(mapa[["lat", "lon"]], size=40)

        st.subheader("Directorio de bodegas")
        st.dataframe(
            df_f[["nombre", "localidad", "telefono", "web", "url_ficha"]],
            use_container_width=True, hide_index=True,
        )

    # ----- 6. Inteligencia Tecnológica -----
    with tab_tec:
        cabecera_inteligencia("tecnologica")
        if auditoria.empty:
            st.info("Sin auditoría web todavía.")
        else:
            aud_ok = auditoria[auditoria["web_ok"] == True]  # noqa: E712
            n_no = len(auditoria) - len(aud_ok)
            st.caption("Madurez digital de las webs de las bodegas (proxy automático de la "
                       "home): HTTPS, adaptación móvil, inglés, reserva online, tecnología inmersiva.")
            t1, t2, t3 = st.columns(3)
            t1.metric("Webs auditadas", len(aud_ok))
            t2.metric("Madurez digital media", f"{aud_ok['madurez_digital'].mean():.1f}/5")
            t3.metric("Con reserva online", f"{aud_ok['reserva_online'].mean() * 100:.0f}%")

            st.markdown("**Adopción de funcionalidades (entre las webs auditadas):**")
            feats = {"HTTPS": "https", "Adaptación móvil": "movil", "Versión en inglés": "ingles",
                     "Reserva online": "reserva_online", "Tecnología inmersiva (360/virtual)": "inmersiva"}
            adopcion = pd.Series({k: aud_ok[v].mean() * 100 for k, v in feats.items()})
            st.bar_chart(adopcion)

            st.markdown("**Ranking de madurez digital:**")
            st.dataframe(
                aud_ok.sort_values("madurez_digital", ascending=False)[
                    ["bodega", "localidad", "madurez_digital", "reserva_online", "ingles", "inmersiva"]
                ].rename(columns={"bodega": "Bodega", "localidad": "Localidad",
                                  "madurez_digital": "Madurez /5", "reserva_online": "Reserva",
                                  "ingles": "Inglés", "inmersiva": "Inmersiva"}),
                use_container_width=True, hide_index=True,
            )
            if n_no:
                st.caption(f"⚠️ {n_no} bodegas no auditables automáticamente (sin web, verificación "
                           "de edad o protección anti-bot — frecuente en las webs más avanzadas). "
                           "No se muestran para no falsear el índice.")

    # ----- 7. Inteligencia en Sostenibilidad -----
    with tab_sos:
        cabecera_inteligencia("sostenibilidad")
        if sostenibilidad.empty:
            st.info("Sin datos de sostenibilidad todavía.")
        else:
            st.caption("Compromiso ambiental de las bodegas. Fuentes: certificación climática "
                       "**FEV** (Sustainable Wineries for Climate Protection) y auditoría de las "
                       "webs (señales de sostenibilidad comunicada por ejes temáticos).")
            cert = sostenibilidad[sostenibilidad["certificado_swfcp"] == True]  # noqa: E712
            n_bod = len(sostenibilidad)

            tiene_indice = "indice_sostenibilidad" in sostenibilidad.columns
            tiene_eco = "menciona_ecologico" in sostenibilidad.columns

            s1, s2, s3 = st.columns(3)
            s1.metric("Certificadas FEV (clima)", len(cert),
                      f"{len(cert) / n_bod * 100:.0f}% del Marco")
            if tiene_eco:
                n_eco = int(sostenibilidad["menciona_ecologico"].sum())
                s2.metric("Comunican producción ecológica", n_eco,
                          f"{n_eco / n_bod * 100:.0f}% de las webs")
            if tiene_indice:
                s3.metric("Índice medio de sostenibilidad",
                          f"{sostenibilidad['indice_sostenibilidad'].mean():.1f}/7",
                          help="Nº medio de ejes de sostenibilidad con presencia en la web.")

            st.markdown("**🌱 Bodegas con certificación climática FEV:**")
            for _, r in cert.iterrows():
                st.markdown(f"- **{r['bodega']}** · {r['localidad']}")

            # Adopción por eje temático (qué % de bodegas comunica cada aspecto)
            ejes_cols = [c for c in sostenibilidad.columns if c.startswith("eje_")]
            if ejes_cols:
                st.markdown("**Sostenibilidad comunicada por eje (% de bodegas)**")
                adop = (sostenibilidad[ejes_cols].sum() / n_bod * 100).round(0)
                adop.index = [c.replace("eje_", "").capitalize() for c in adop.index]
                st.bar_chart(adop.sort_values(ascending=False))

            # Ranking por índice de sostenibilidad comunicada
            if tiene_indice:
                st.markdown("**Bodegas líderes en sostenibilidad comunicada**")
                top = (sostenibilidad[sostenibilidad["indice_sostenibilidad"] > 0]
                       .sort_values("indice_sostenibilidad", ascending=False)
                       .head(10)[["bodega", "localidad", "indice_sostenibilidad"]]
                       .rename(columns={"bodega": "Bodega", "localidad": "Localidad",
                                        "indice_sostenibilidad": "Índice /7"}))
                st.dataframe(top, hide_index=True, use_container_width=True)

            st.caption("⚠️ La auditoría web es un *proxy de comunicación*, no una certificación. "
                       "Algunas bodegas (p. ej. González Byass, Tradición) bloquean el robot y "
                       "salen sin señal (falso negativo). Nota del Marco: por el sistema de "
                       "criaderas y solera, los vinos tradicionales no pueden certificarse como "
                       "«vino ecológico»; la señal ecológica se refiere a viñedo/vinos tranquilos.")

# --------------------------------------------------------------------------- #
# Vista BODEGA: ficha individual en detalle
# --------------------------------------------------------------------------- #
else:
    nombre = st.selectbox("Selecciona una bodega", df_f["nombre"].sort_values())
    b = df_f[df_f["nombre"] == nombre].iloc[0]
    an_bod = anotadas[anotadas["bodega"] == nombre] if not anotadas.empty else pd.DataFrame()

    tab_ficha, tab_res = st.tabs(["🏭 Ficha", "😊 Reseñas y análisis"])

    # ----- Pestaña: Ficha -----
    with tab_ficha:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.subheader(b["nombre"])
            st.caption(f"📍 {b.get('localidad', '')} · {b.get('direccion', '')}")
            if not sostenibilidad.empty:
                fila_sos = sostenibilidad[sostenibilidad["bodega"] == nombre]
                if not fila_sos.empty:
                    fs = fila_sos.iloc[0]
                    if bool(fs.get("certificado_swfcp")):
                        st.success("🌱 Certificada Sustainable Wineries for Climate Protection (FEV)")
                    if "menciona_ecologico" in fila_sos.columns and bool(fs.get("menciona_ecologico")):
                        st.info("🍃 Comunica producción/viñedo ecológico en su web")
            if isinstance(b.get("descripcion"), str) and b["descripcion"]:
                st.write(b["descripcion"])
            servicios = [s for s in str(b.get("servicios", "")).split(" | ") if s]
            if servicios:
                st.markdown("**Servicios enoturísticos:**")
                for s in servicios:
                    st.markdown(f"- {s}")
        with col_b:
            st.markdown("**Contacto**")
            if b.get("telefono"):
                st.markdown(f"☎️ {b['telefono']}")
            if isinstance(b.get("email"), str) and b["email"]:
                st.markdown(f"✉️ {b['email']}")
            if isinstance(b.get("web"), str) and b["web"]:
                st.markdown(f"🌐 [{b['web']}]({b['web']})")
            rrss = [r for r in str(b.get("rrss", "")).split(" | ") if r]
            if rrss:
                st.markdown("**Redes sociales:**")
                for r in rrss:
                    st.markdown(f"- [{r}]({r})")
            if pd.notna(b.get("gps_lat")):
                st.map(pd.DataFrame({"lat": [b["gps_lat"]], "lon": [b["gps_lon"]]}), size=60)

    # ----- Pestaña: Reseñas y análisis -----
    with tab_res:
        fila_censo = censo[censo["bodega"] == nombre] if not censo.empty else pd.DataFrame()

        if not fila_censo.empty:
            f = fila_censo.iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Nota media", f"{f['rating']:.1f} ⭐" if pd.notna(f["rating"]) else "—")
            m2.metric("Reseñas totales", f"{int(f['total_resenas']):,}" if pd.notna(f["total_resenas"]) else "0")
            con_texto_n = int((an_bod["texto"].astype(str).str.len() > 5).sum()) if not an_bod.empty else 0
            m3.metric("Reseñas con texto", con_texto_n)

        if not an_bod.empty:
            # Sentimiento y cuadrantes IPA de ESTA bodega
            col1, col2 = st.columns([1, 2])
            with col1:
                st.caption("Sentimiento (por estrellas)")
                st.bar_chart(an_bod["sentimiento"].value_counts())
            with col2:
                tabla_ipa_bod = ipa_desde_anotadas(an_bod)
                if len(tabla_ipa_bod) >= 3:
                    st.caption("Importancia-Desempeño (IPA) de esta bodega")
                    st.plotly_chart(figura_ipa(tabla_ipa_bod), use_container_width=True)
                else:
                    st.caption("Pocas reseñas con atributos para un IPA fiable de esta bodega.")

            # IPCA: esta bodega frente al resto del Marco
            comp_an = anotadas[anotadas["bodega"] != nombre]
            tabla_ipca = ipca_desde_anotadas(an_bod, comp_an)
            if len(tabla_ipca) >= 3:
                st.markdown("**Análisis competitivo (IPCA): esta bodega vs. el Marco de Jerez**")
                st.caption("Brecha positiva = la bodega supera la media del Marco en ese atributo; "
                           "negativa = va por detrás.")
                cg, ct = st.columns([2, 1])
                with cg:
                    st.plotly_chart(figura_ipca(tabla_ipca), use_container_width=True)
                with ct:
                    st.dataframe(
                        tabla_ipca[["atributo", "Esta bodega", "Media del Marco", "brecha"]]
                        .rename(columns={"atributo": "Atributo", "brecha": "Brecha"})
                        .sort_values("Brecha"),
                        use_container_width=True, hide_index=True,
                    )

            # DIPCA: evolución de la brecha competitiva en el tiempo
            tabla_dipca = dipca_bodega(an_bod, comp_an)
            if not tabla_dipca.empty:
                corte = tabla_dipca.attrs.get("corte", "")
                st.markdown("**Evolución competitiva (DIPCA): ¿gana o pierde terreno con el tiempo?**")
                st.caption(f"Compara la brecha vs. el Marco antes y después de {corte}. "
                           "Cambio positivo = la bodega gana terreno frente a la competencia.")
                st.dataframe(
                    tabla_dipca.rename(columns={
                        "atributo": "Atributo", "brecha_inicial": "Brecha antes",
                        "brecha_final": "Brecha después", "cambio_brecha": "Cambio",
                        "tendencia": "Tendencia"}),
                    use_container_width=True, hide_index=True,
                )

            # Muestra de reseñas con texto (máx. 15)
            with st.expander(f"Ver reseñas con texto ({con_texto_n})"):
                muestra = an_bod[an_bod["texto"].astype(str).str.len() > 5].head(15)
                for _, rv in muestra.iterrows():
                    estrellas = "⭐" * int(rv["puntuacion"]) if pd.notna(rv["puntuacion"]) else ""
                    texto = str(rv["texto"]).replace("<br>", " ")
                    atrs = ", ".join(rv["atributos"]) if rv["atributos"] else ""
                    with st.container(border=True):
                        st.markdown(f"**{rv['autor']}** · {estrellas}"
                                    + (f" · _{atrs}_" if atrs else ""))
                        st.write(texto)
        else:
            st.caption("No hay reseñas descargadas para esta bodega.")

st.caption("ENOLYTICS · Universidad de Cádiz · datos: Ruta del Vino y Brandy de Jerez")
