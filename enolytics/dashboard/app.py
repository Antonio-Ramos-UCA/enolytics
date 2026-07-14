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
from enolytics.analitica import recomendaciones as reco  # noqa: E402
from enolytics.analitica import reputacion as rep  # noqa: E402


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
def cargar_accesibilidad() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "accesibilidad.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_transporte() -> pd.DataFrame:
    """Accesibilidad de cada bodega en transporte público (OpenStreetMap)."""
    ruta = config.DATOS_PROCESADO / "transporte_sostenible.csv"
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
def cargar_acevin_oferta() -> pd.DataFrame:
    """Oferta (servicios y entidades) de cada ruta del vino (ACEVIN)."""
    ruta = config.DATOS_PROCESADO / "acevin" / "oferta_rutas.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_acevin_ingresos() -> pd.DataFrame:
    """Ingresos del enoturismo en bodegas y museos por ruta (ACEVIN, cobertura parcial)."""
    ruta = config.DATOS_PROCESADO / "acevin" / "ingresos_rutas.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


@st.cache_data
def cargar_acevin_demanda() -> pd.DataFrame:
    """Perfil del enoturista (ACEVIN). ⚠️ Dato NACIONAL, no desglosado por ruta."""
    ruta = config.DATOS_PROCESADO / "acevin" / "perfil_demanda.csv"
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


def fuente(origen: str, detalle: str) -> None:
    """Etiqueta el origen del dato del bloque: 🟢 oficial · 🔵 observado · 🟡 estimado."""
    emoji, etiqueta, _ = config.ORIGENES_DATO.get(origen, ("", "", ""))
    st.caption(f"{emoji} **{etiqueta}** · {detalle}")


def leyenda_origenes() -> None:
    """Explica los distintivos de origen del dato (rigor metodológico)."""
    with st.expander("ℹ️ Cómo leer los datos: origen de cada indicador"):
        for emoji, etiqueta, desc in config.ORIGENES_DATO.values():
            st.markdown(f"{emoji} **{etiqueta}** — {desc}")
        st.caption("Todo indicador del cuadro de mando lleva su distintivo. Nunca se mezcla "
                   "estadística oficial con estimaciones sin advertirlo.")


@st.cache_data
def tabla_respuestas_marco(res: pd.DataFrame, min_resenas: int = 30) -> pd.DataFrame:
    """Tasa de respuesta a reseñas de cada bodega (solo las que tienen suficientes reseñas)."""
    if res.empty or "respuesta_propietario" not in res.columns:
        return pd.DataFrame()
    filas = []
    for bod, g in res.groupby("bodega"):
        if len(g) < min_resenas:
            continue
        t = rep.tasa_respuesta(g)
        filas.append({"Bodega": bod, "Reseñas": len(g),
                      "% contestadas": t["pct_total"],
                      "Críticas (1-2★)": t["n_negativas"],
                      "% críticas contestadas": t["pct_negativas"]})
    if not filas:
        return pd.DataFrame()
    return pd.DataFrame(filas).sort_values("% contestadas", ascending=False)


def ficha_reputacion(res_bod: pd.DataFrame, an_bod: pd.DataFrame, titulo: str) -> None:
    """Ficha de reputación al estilo Booking/Amazon: estrellas, resumen y aspectos."""
    if res_bod.empty:
        st.info("No hay reseñas para mostrar.")
        return

    st.markdown(f"### {titulo}")
    fuente("observado", "Reseñas de Google. El resumen **no lo genera una IA**: se compone a "
                        "partir de las menciones y notas medias reales, así que es "
                        "reproducible y no puede inventarse nada.")

    col_nota, col_dist = st.columns([1, 2])
    with col_nota:
        st.metric("Valoración global", f"{res_bod['puntuacion'].mean():.2f} / 5",
                  f"{len(res_bod)} reseñas")
    with col_dist:
        dist = rep.distribucion_estrellas(res_bod)
        for _, d in dist.iterrows():
            c1, c2, c3 = st.columns([1, 6, 1])
            c1.caption(f"{int(d['estrellas'])} ★")
            c2.progress(min(d["pct"] / 100, 1.0))
            c3.caption(f"{d['pct']:.0f}%")

    asp = rep.aspectos(an_bod) if not an_bod.empty else pd.DataFrame()

    # "Lo que dicen los visitantes" (resumen determinista a partir de los datos)
    st.markdown("**Lo que dicen los visitantes**")
    st.info(rep.resumen_textual(asp))

    if not asp.empty:
        st.markdown("**Aspectos valorados** · ↗ lo destacan · ~ opiniones variadas · ↘ descontento")
        for _, a in asp.iterrows():
            ca, cb, cc = st.columns([3, 5, 2])
            ca.markdown(f"{a['icono']} **{a['atributo']}** ({int(a['menciones'])})")
            cb.progress(min(a["desempeno"] / 5, 1.0))
            cc.markdown(f"**{a['desempeno']:.2f}**/5")

    # Gestión de la reputación: ¿contesta la bodega a sus visitantes?
    tr = rep.tasa_respuesta(res_bod)
    if tr:
        st.markdown("**Gestión de la reputación**")
        r1, r2 = st.columns(2)
        r1.metric("Reseñas contestadas", f"{tr['pct_total']:.0f}%",
                  f"{tr['n_respondidas']} de {len(res_bod)}")
        if tr.get("pct_negativas") is not None:
            r2.metric("Críticas contestadas", f"{tr['pct_negativas']:.0f}%",
                      f"de {tr['n_negativas']} reseñas de 1-2★")
        if tr["pct_total"] == 0 and tr["n_negativas"] >= 5:
            st.warning(
                f"⚠️ Esta bodega **no ha respondido a ninguna reseña**, ni siquiera a las "
                f"**{tr['n_negativas']} críticas** (1-2★). Responder es la acción de reputación "
                f"**más barata y visible** que existe: no cuesta dinero y el futuro visitante lo lee."
            )

    # Reseñas representativas
    dest = rep.resenas_destacadas(res_bod)
    if not dest["positivas"].empty or not dest["negativas"].empty:
        with st.expander("Reseñas representativas"):
            for etiqueta, clave in [("👍 Lo mejor valorado", "positivas"),
                                    ("👎 Las críticas más leídas", "negativas")]:
                sub = dest[clave]
                if sub.empty:
                    continue
                st.markdown(f"**{etiqueta}**")
                for _, x in sub.iterrows():
                    st.markdown(f"> {'★' * int(x['puntuacion'])} — *{str(x['texto'])[:320]}*")


def pintar_recomendaciones(recs: list, titulo: str, vacio: str) -> None:
    """Muestra las recomendaciones accionables, ordenadas por prioridad."""
    if not recs:
        st.success(f"✅ {vacio}")
        return

    n_alta = sum(1 for r in recs if r.prioridad == "alta")
    st.markdown(f"### {titulo}")
    st.caption(f"{len(recs)} recomendaciones · **{n_alta} de prioridad alta**. "
               "Generadas automáticamente cruzando las 7 inteligencias; cada una declara el dato "
               "que la justifica y su fuente.")

    for r in recs:
        icono = reco.ICONO_PRIORIDAD.get(r.prioridad, "•")
        with st.expander(f"{icono} **{r.titulo}** · _{r.inteligencia}_",
                         expanded=(r.prioridad == "alta")):
            st.markdown(f"**Diagnóstico.** {r.diagnostico}")
            st.markdown(f"**Acción propuesta.** {r.accion}")
            if r.fuente:
                st.caption(f"Fuente: {r.fuente}")


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
accesibilidad = cargar_accesibilidad()
transporte = cargar_transporte()
gasto_cadiz = cargar_gasto_cadiz()
satisf_cadiz = cargar_satisfaccion_cadiz()
trends_temporal = cargar_trends_temporal()
trends_regiones = cargar_trends_regiones()
acevin = cargar_acevin()
acevin_oferta = cargar_acevin_oferta()
acevin_ingresos = cargar_acevin_ingresos()
acevin_demanda = cargar_acevin_demanda()

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

    # ----- Recomendaciones accionables para el destino -----
    tabla_respuestas = tabla_respuestas_marco(resenas)
    recs_destino = reco.recomendaciones_destino(
        acevin=acevin, acevin_oferta=acevin_oferta, acevin_ingresos=acevin_ingresos,
        acevin_demanda=acevin_demanda, trends=trends_temporal,
        accesibilidad=accesibilidad, transporte=transporte, auditoria=auditoria,
        sostenibilidad=sostenibilidad, resumen_dipa=resumen_dipa(evolucion),
        tabla_ipa=tabla_ipa, respuestas=tabla_respuestas,
    )
    with st.container(border=True):
        pintar_recomendaciones(
            recs_destino,
            titulo="🎯 Recomendaciones accionables para el destino",
            vacio="No hay recomendaciones pendientes con los datos actuales.")

    st.caption("Una pestaña por cada una de las **7 inteligencias competitivas** del modelo ENOLYTICS.")
    leyenda_origenes()
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
        st.caption("Impacto económico del enoturismo. Fuentes oficiales: ACEVIN (ingresos del "
                   "enoturismo) y Dataestur (gasto turístico en Cádiz). "
                   "Pendiente: facturación y empleo por bodega (SABI).")

        # --- Rentabilidad: ingresos del enoturismo y monetización por visitante (ACEVIN) ---
        if not acevin_ingresos.empty and not acevin.empty:
            ing = acevin_ingresos[acevin_ingresos["ruta"] != "TOTAL Rutas del Vino de España"]
            total = acevin_ingresos[acevin_ingresos["ruta"] == "TOTAL Rutas del Vino de España"]
            anio_i = int(acevin_ingresos["anio"].max())
            vis_i = (acevin[acevin["anio"] == anio_i].set_index("ruta")["visitantes"])

            mon = ing.copy()
            mon["visitantes"] = mon["ruta"].map(vis_i)
            mon = mon.dropna(subset=["visitantes"])
            mon["eur_por_visitante"] = (mon["ingresos_eur"] / mon["visitantes"]).round(1)

            foco_m = mon[mon["ruta"] == "Marco de Jerez"]
            if not foco_m.empty:
                fuente("oficial", f"ACEVIN, informe de visitas {anio_i}. El «ingreso por "
                                  f"visitante» lo calcula ENOLYTICS (ingresos ÷ visitantes).")
                e1, e2, e3 = st.columns(3)
                e1.metric(f"Ingresos del enoturismo ({anio_i})",
                          f"{foco_m['ingresos_eur'].iloc[0] / 1e6:.1f} M€",
                          help="Ingresos por visitas a bodegas y museos del Marco (ACEVIN). "
                               "No incluye alojamiento ni restauración.")
                e2.metric("Ingreso por visitante", f"{foco_m['eur_por_visitante'].iloc[0]:.1f} €")
                if not total.empty:
                    media_nac = total["ingresos_eur"].iloc[0] / 3_036_878
                    e3.metric("Media nacional", f"{media_nac:.1f} €",
                              f"{foco_m['eur_por_visitante'].iloc[0] - media_nac:+.1f} € vs Marco",
                              help="Ingreso medio por visitante en el conjunto de las Rutas del "
                                   "Vino de España.")

                st.markdown("**Ingreso por visitante frente a las rutas líderes**")
                st.bar_chart(mon.set_index("ruta")["eur_por_visitante"])

                mejor = mon.sort_values("eur_por_visitante", ascending=False).iloc[0]
                if mejor["ruta"] != "Marco de Jerez":
                    brecha = mejor["eur_por_visitante"] - foco_m["eur_por_visitante"].iloc[0]
                    st.warning(
                        f"⚠️ **Brecha de monetización:** el Marco ingresa "
                        f"**{foco_m['eur_por_visitante'].iloc[0]:.1f} € por visitante**, frente a "
                        f"los **{mejor['eur_por_visitante']:.1f} €** de *{mejor['ruta']}* "
                        f"(**{brecha:.1f} € menos por cada visita**). Lidera en volumen, pero "
                        f"convierte menos cada visita en ingreso: margen en precio de la visita, "
                        f"venta en tienda y experiencias premium."
                    )
                st.caption("⚠️ Cobertura parcial: ACEVIN solo publica en texto los ingresos de las "
                           "rutas destacadas; el resto va en un gráfico como imagen.")
                st.divider()
        if gasto_anio.empty:
            st.info("Sin datos de gasto todavía.")
        else:
            fuente("estimado", "Gasto turístico con tarjeta de **toda la provincia de Cádiz** "
                               "(Dataestur/SEGITTUR). Es una **aproximación**: no aísla el gasto "
                               "específicamente enoturístico.")
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
            fuente("observado", "Google Trends sobre el término «bodegas [zona]», usado como "
                                "**proxy de intención de visita**. Escala relativa (0-100), no "
                                "es volumen absoluto de búsquedas.")
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

            fuente("oficial", f"ACEVIN — Observatorio Turístico de las Rutas del Vino de España, "
                              f"informes {int(acevin['anio'].min())}-{ult}.")
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

            # --- A-bis. Comparación de la OFERTA entre rutas (indicador de la Tabla 1) ---
            if not acevin_oferta.empty:
                st.divider()
                st.markdown("**Oferta enoturística por ruta** (servicios y entidades asociadas)")
                fuente("oficial", "ACEVIN (37 rutas). El indicador «visitantes por servicio» lo "
                                  "calcula ENOLYTICS cruzando visitantes ÷ servicios.")
                of = (acevin_oferta.sort_values("servicios", ascending=False)
                      .reset_index(drop=True))
                fila_foco = of[of["ruta"] == FOCO]
                serv_foco = int(fila_foco["servicios"].iloc[0]) if not fila_foco.empty else None
                pos_of = int(fila_foco.index[0]) + 1 if not fila_foco.empty else None

                # Cruce oferta × visitantes → intensidad de uso de la oferta
                cruce = rank_ult.merge(of[["ruta", "servicios"]], on="ruta", how="inner")
                cruce["vis_por_servicio"] = (cruce["visitantes"] / cruce["servicios"]).round(0)
                cruce = cruce.sort_values("vis_por_servicio", ascending=False)

                o1, o2 = st.columns(2)
                if serv_foco:
                    o1.metric("Servicios del Marco", serv_foco,
                              f"{pos_of}º de {len(of)} rutas en oferta")
                if not cruce.empty and FOCO in set(cruce["ruta"]):
                    vps = int(cruce.loc[cruce["ruta"] == FOCO, "vis_por_servicio"].iloc[0])
                    o2.metric("Visitantes por servicio", f"{vps:,}".replace(",", "."),
                              help="Visitantes de la ruta ÷ nº de servicios y entidades. "
                                   "Un valor muy alto indica que la oferta va por detrás "
                                   "de la demanda.")

                st.caption("Top 12 rutas por tamaño de la oferta")
                st.bar_chart(of.head(12).set_index("ruta")["servicios"])

                # Desequilibrio: lidera la demanda pero su oferta está muy por detrás
                if pos and pos_of and pos_of > pos:
                    st.warning(
                        f"⚠️ **Desequilibrio demanda-oferta:** el Marco es **{pos}º en visitantes** "
                        f"pero solo **{pos_of}º en oferta** ({serv_foco} servicios, frente a los "
                        f"{int(of.iloc[0]['servicios'])} de *{of.iloc[0]['ruta']}*). Atrae más "
                        f"gente que nadie con una oferta asociada mucho menor → margen para "
                        f"**ampliar y diversificar la oferta** (prioridad FEDER P4A)."
                    )
                st.caption("Visitantes por servicio (a más alto, más tensionada está la oferta)")
                st.bar_chart(cruce.set_index("ruta")["vis_por_servicio"])

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
                fuente("observado", "Censo de reseñas y notas de Google Maps.")
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
        st.caption("Satisfacción, perfil y atributos valorados por el visitante. Fuentes: "
                   "reseñas de Google (10.972) y Observatorio de la Demanda de ACEVIN.")

        # --- Volumen de visitas al Marco (indicador de la Tabla 1) ---
        if not acevin.empty:
            _u = int(acevin["anio"].max())
            _v = acevin[(acevin["anio"] == _u) & (acevin["ruta"] == "Marco de Jerez")]["visitantes"]
            if not _v.empty:
                st.metric(f"Volumen de visitas a bodegas y museos del Marco ({_u})",
                          f"{int(_v.iloc[0]):,}".replace(",", "."),
                          help="Cubre el indicador «Volumen de visitas a bodegas y Museos del "
                               "Vino» de la memoria.")
                fuente("oficial", "ACEVIN — Observatorio Turístico de las Rutas del Vino.")

        # --- Perfil del enoturista (benchmark NACIONAL de ACEVIN) ---
        if not acevin_demanda.empty:
            with st.expander("👤 Perfil del enoturista — *benchmark nacional* (ACEVIN)",
                             expanded=True):
                fuente("oficial", "ACEVIN — Análisis de la demanda turística (628 encuestas, "
                                  "95% de confianza, ±3,9%).")
                st.caption("⚠️ **Dato nacional**, no específico del Marco: ACEVIN no desglosa por "
                           "ruta (628 encuestas, 95% confianza). Sirve como **referencia** para "
                           "comparar y como plantilla validada para un cuestionario propio. "
                           "Cubre los indicadores de perfil, motivaciones y canales de la memoria.")
                for cat in ["Perfil", "Comportamiento", "Promoción y comercialización",
                            "Impacto económico"]:
                    sub = acevin_demanda[acevin_demanda["categoria"] == cat]
                    if sub.empty:
                        continue
                    st.markdown(f"**{cat}**")
                    cols = st.columns(min(4, len(sub)))
                    for i, (_, r) in enumerate(sub.iterrows()):
                        val = (f"{r['valor']:.0f} %" if r["unidad"] == "%"
                               else f"{r['valor']:g} {r['unidad']}")
                        cols[i % len(cols)].metric(r["indicador"], val)
            st.divider()
        if tabla_ipa.empty and evolucion.empty:
            st.info("Sin datos de reseñas todavía.")
        # ----- Ficha de reputación del Marco (estilo Booking/Amazon) -----
        if not resenas.empty:
            with st.container(border=True):
                ficha_reputacion(resenas, anotadas,
                                 "⭐ Lo que dicen los visitantes del Marco de Jerez")
            st.divider()

        # ----- Gestión de la reputación: quién responde y quién no -----
        if not resenas.empty and "respuesta_propietario" in resenas.columns:
            st.subheader("💬 Gestión de la reputación por bodega")
            fuente("observado", "Respuestas del propietario en Google. **Ni Amazon ni Booking "
                                "muestran esto**, pero responder es la acción de reputación más "
                                "barata y visible que puede tomar una bodega.")
            dfr = tabla_respuestas
            if not dfr.empty:
                mudas = dfr[dfr["% contestadas"] == 0]
                g1, g2, g3 = st.columns(3)
                g1.metric("Respuesta media del Marco", f"{dfr['% contestadas'].mean():.0f}%")
                g2.metric("Bodegas que no responden nada", f"{len(mudas)} de {len(dfr)}",
                          delta_color="inverse")
                if not mudas.empty:
                    g3.metric("Críticas sin contestar",
                              int(mudas["Críticas (1-2★)"].sum()),
                              "en las bodegas mudas", delta_color="inverse")

                if not mudas.empty:
                    peor = mudas.sort_values("Críticas (1-2★)", ascending=False).iloc[0]
                    if peor["Críticas (1-2★)"] >= 20:
                        st.warning(
                            f"⚠️ **{len(mudas)} bodegas no responden a ninguna reseña.** La más "
                            f"expuesta es **{peor['Bodega']}**, con **{int(peor['Críticas (1-2★)'])} "
                            f"críticas de 1-2★ sin una sola respuesta**. Es la mejora de "
                            f"reputación **más barata del destino**: no cuesta dinero, solo tiempo."
                        )
                st.dataframe(dfr, use_container_width=True, hide_index=True)
            st.divider()

        if not tabla_ipa.empty:
            st.subheader("Análisis Importancia-Desempeño (IPA) del destino")
            fuente("estimado", "Calculado sobre 10.972 reseñas de Google. **Importancia** = nº de "
                               "menciones del atributo; **desempeño** = nota media de las reseñas "
                               "que lo mencionan. Son *proxies*: la importancia no se pregunta al "
                               "visitante, se infiere de cuánto habla de cada atributo.")
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
        fuente("observado", "Catálogo extraído de la web oficial de la Ruta del Vino y Brandy "
                            "del Marco de Jerez (11 categorías).")
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
            st.caption("Madurez digital de las webs de las bodegas: HTTPS, adaptación móvil, "
                       "inglés, reserva online, tecnología inmersiva.")
            _nav = int((aud_ok["metodo"] == "navegador").sum()) if "metodo" in aud_ok.columns else 0
            _nota_nav = (f" {_nav} webs con verificación de edad o JavaScript se leyeron abriendo "
                         f"un **navegador real**, para que las bodegas que bloquean robots no "
                         f"salgan penalizadas injustamente." if _nav else "")
            fuente("estimado", "Auditoría automática de la **página de inicio** de cada bodega. "
                               "Es un *proxy*: no ve subpáginas." + _nota_nav)
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

        # ----- Accesibilidad universal (indicador de la Tabla 1 de la memoria) -----
        if not accesibilidad.empty:
            st.divider()
            st.subheader("♿ Accesibilidad universal")
            acc_ok = accesibilidad[accesibilidad["web_ok"] == True]  # noqa: E712
            if acc_ok.empty:
                st.info("Sin webs auditables para accesibilidad.")
            else:
                fuente("observado", "Comprobaciones objetivas sobre el HTML de cada web, basadas "
                                    "en las **WCAG**. No sustituye a una auditoría WCAG completa: "
                                    "el contraste de color y la navegación por teclado exigen "
                                    "renderizar la página.")
                a1, a2, a3 = st.columns(3)
                a1.metric("Accesibilidad digital media",
                          f"{acc_ok['indice_accesibilidad_digital'].mean():.1f}/8")
                a2.metric("Webs sin barreras graves",
                          int((acc_ok["indice_accesibilidad_digital"] >= 7).sum()),
                          f"de {len(acc_ok)} auditadas")
                a3.metric("Declaran el idioma",
                          f"{acc_ok['idioma_declarado'].mean() * 100:.0f}%",
                          help="Sin <html lang>, los lectores de pantalla no saben en qué idioma "
                               "leer la página.")

                st.markdown("**Cumplimiento por criterio (% de webs)**")
                criterios = {
                    "Idioma declarado": "idioma_declarado",
                    "Título de página": "titulo_pagina",
                    "Imágenes con texto alternativo": "imagenes_con_alt",
                    "Zoom permitido": "zoom_permitido",
                    "Encabezado principal (h1)": "encabezado_h1",
                    "Jerarquía de encabezados": "jerarquia_encabezados",
                    "Formularios etiquetados": "formularios_etiquetados",
                    "Estructura semántica": "estructura_semantica",
                }
                cumpl = pd.Series({k: acc_ok[v].mean() * 100
                                   for k, v in criterios.items() if v in acc_ok.columns})
                st.bar_chart(cumpl.sort_values())

                # Accesibilidad física/sensorial: solo lo que comunican (proxy)
                st.markdown("**Accesibilidad física y sensorial comunicada**")
                fuente("estimado", "*Proxy*: detecta si la web **menciona** accesibilidad para "
                                   "movilidad reducida, audioguías, etc. **No confirma** que la "
                                   "bodega sea accesible. El dato real exige Google Maps o "
                                   "preguntar a la bodega.")
                f1, f2 = st.columns(2)
                n_fis = int(acc_ok["menciona_accesibilidad_fisica"].sum())
                n_sen = int(acc_ok["menciona_apoyo_sensorial"].sum())
                f1.metric("Mencionan accesibilidad física", n_fis,
                          f"{n_fis / len(acc_ok) * 100:.0f}% de las webs")
                f2.metric("Mencionan apoyo sensorial", n_sen,
                          f"{n_sen / len(acc_ok) * 100:.0f}% (audioguías, braille…)")

                st.markdown("**Ranking de accesibilidad digital**")
                st.dataframe(
                    acc_ok.sort_values("indice_accesibilidad_digital", ascending=False)[
                        ["bodega", "localidad", "indice_accesibilidad_digital",
                         "menciona_accesibilidad_fisica", "menciona_apoyo_sensorial"]
                    ].rename(columns={
                        "bodega": "Bodega", "localidad": "Localidad",
                        "indice_accesibilidad_digital": "Accesibilidad digital /8",
                        "menciona_accesibilidad_fisica": "Menciona acces. física",
                        "menciona_apoyo_sensorial": "Menciona apoyo sensorial"}),
                    use_container_width=True, hide_index=True,
                )

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

            fuente("oficial", "Certificación **Sustainable Wineries for Climate Protection** "
                              "(Federación Española del Vino).")
            st.markdown("**🌱 Bodegas con certificación climática FEV:**")
            for _, r in cert.iterrows():
                st.markdown(f"- **{r['bodega']}** · {r['localidad']}")

            # Adopción por eje temático (qué % de bodegas comunica cada aspecto)
            ejes_cols = [c for c in sostenibilidad.columns if c.startswith("eje_")]
            if ejes_cols:
                st.markdown("**Sostenibilidad comunicada por eje (% de bodegas)**")
                fuente("estimado", "Auditoría de las webs por palabras clave. Mide lo que la "
                                   "bodega **comunica**, no su desempeño ambiental real ni una "
                                   "certificación.")
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

            # ----- Transporte sostenible (indicador de la Tabla 1 de la memoria) -----
            if not transporte.empty:
                st.divider()
                st.subheader("🚉 Transporte sostenible")
                fuente("observado", "Distancia en línea recta de cada bodega a la estación de tren "
                                    "o parada de autobús más cercana (**OpenStreetMap**). Mide si "
                                    "el visitante *puede* elegir el transporte público.")

                n_tot = len(transporte)
                n_ok = int(transporte["accesible_transporte_publico"].sum())
                a_pie = int((transporte["categoria_transporte"]
                             == "A pie desde el transporte público").sum())
                t1, t2, t3 = st.columns(3)
                t1.metric("Accesibles en transporte público", f"{n_ok}/{n_tot}",
                          f"{n_ok / n_tot * 100:.0f}% del Marco")
                t2.metric("A pie desde una parada", a_pie,
                          f"{a_pie / n_tot * 100:.0f}%")
                t3.metric("Requieren vehículo privado", n_tot - n_ok,
                          f"{(n_tot - n_ok) / n_tot * 100:.0f}%",
                          delta_color="inverse")

                st.markdown("**Bodegas por accesibilidad en transporte público**")
                st.bar_chart(transporte["categoria_transporte"].value_counts())

                # Cruce con ACEVIN: ¿la infraestructura explica el uso del coche?
                if not acevin_demanda.empty:
                    coche = acevin_demanda[
                        acevin_demanda["indicador"] == "Llegan en vehículo propio o alquilado"]
                    pct_ok = n_ok / n_tot * 100
                    if not coche.empty and pct_ok >= 75 and coche["valor"].iloc[0] >= 60:
                        st.info(
                            f"💡 **La infraestructura existe, pero no se usa.** El "
                            f"**{pct_ok:.0f}% de las bodegas del Marco es accesible en transporte "
                            f"público** ({a_pie} de ellas, a pie desde una parada); sin embargo, "
                            f"el **{coche['valor'].iloc[0]:.0f}% de los enoturistas llega en "
                            f"vehículo propio** (ACEVIN). El cuello de botella **no es la "
                            f"conexión, es la información y el hábito** → oportunidad de "
                            f"**promocionar el transporte público existente** (rutas, horarios, "
                            f"paquetes combinados) para reducir la huella del enoturismo."
                        )
                    elif not coche.empty and pct_ok < 60:
                        st.warning(
                            f"⚠️ **El coche es una necesidad, no una elección:** solo el "
                            f"{pct_ok:.0f}% de las bodegas es accesible en transporte público, y "
                            f"el {coche['valor'].iloc[0]:.0f}% de los enoturistas llega en coche."
                        )

                st.dataframe(
                    transporte.sort_values("dist_bus_km")[
                        ["bodega", "localidad", "categoria_transporte",
                         "dist_bus_km", "dist_tren_km", "estacion_tren"]
                    ].rename(columns={
                        "bodega": "Bodega", "localidad": "Localidad",
                        "categoria_transporte": "Accesibilidad",
                        "dist_bus_km": "Bus (km)", "dist_tren_km": "Tren (km)",
                        "estacion_tren": "Estación más cercana"}),
                    use_container_width=True, hide_index=True,
                )
                st.caption("⚠️ Distancias **en línea recta**, no por carretera (la real será algo "
                           "mayor). No se comprueba la frecuencia ni el horario del servicio.")
                st.divider()

            st.caption("⚠️ La auditoría web es un *proxy de comunicación*, no una certificación: "
                       "mide lo que la bodega **dice**, no su desempeño ambiental. Las webs con "
                       "verificación de edad se leen abriendo un **navegador real**, para no "
                       "penalizar a quien bloquea robots. Nota del Marco: por el sistema de "
                       "criaderas y solera, los vinos tradicionales no pueden certificarse como "
                       "«vino ecológico»; la señal ecológica se refiere a viñedo/vinos tranquilos.")

# --------------------------------------------------------------------------- #
# Vista BODEGA: ficha individual en detalle
# --------------------------------------------------------------------------- #
else:
    nombre = st.selectbox("Selecciona una bodega", df_f["nombre"].sort_values())
    b = df_f[df_f["nombre"] == nombre].iloc[0]
    an_bod = anotadas[anotadas["bodega"] == nombre] if not anotadas.empty else pd.DataFrame()

    tab_reco, tab_ficha, tab_res = st.tabs(
        ["🎯 Recomendaciones", "🏭 Ficha", "😊 Reseñas y análisis"])

    # ----- Pestaña: Recomendaciones accionables de esta bodega -----
    with tab_reco:
        def _fila(df, col="bodega"):
            """Fila de esta bodega en un dataset, como dict (o None)."""
            if df is None or df.empty or col not in df.columns:
                return None
            sel = df[df[col] == nombre]
            return sel.iloc[0].to_dict() if not sel.empty else None

        comp_an = anotadas[anotadas["bodega"] != nombre] if not anotadas.empty else pd.DataFrame()
        ipa_bod = ipa_desde_anotadas(an_bod) if not an_bod.empty else pd.DataFrame()
        ipca_bod = (ipca_desde_anotadas(an_bod, comp_an)
                    if not an_bod.empty and not comp_an.empty else pd.DataFrame())
        dipca_bod = (dipca_bodega(an_bod, comp_an)
                     if not an_bod.empty and not comp_an.empty else pd.DataFrame())

        fila_cen = _fila(censo)
        rating_bod = fila_cen.get("rating") if fila_cen else None
        rating_marco = (censo["rating"].mean() if not censo.empty
                        and "rating" in censo.columns else None)

        res_bod_r = resenas[resenas["bodega"] == nombre] if not resenas.empty else pd.DataFrame()
        recs_bod = reco.recomendaciones_bodega(
            nombre,
            ipa=ipa_bod, ipca=ipca_bod, dipca=dipca_bod,
            fila_auditoria=_fila(auditoria),
            fila_accesibilidad=_fila(accesibilidad),
            fila_sostenibilidad=_fila(sostenibilidad),
            fila_transporte=_fila(transporte),
            rating=rating_bod, rating_marco=rating_marco,
            tasa_respuesta=rep.tasa_respuesta(res_bod_r) if not res_bod_r.empty else None,
        )
        pintar_recomendaciones(
            recs_bod,
            titulo=f"🎯 Qué debería priorizar {nombre}",
            vacio="Sin recomendaciones pendientes: esta bodega no presenta puntos críticos "
                  "con los datos disponibles.")

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
        # ----- Ficha de reputación (estilo Booking/Amazon) -----
        res_bod = resenas[resenas["bodega"] == nombre] if not resenas.empty else pd.DataFrame()
        if not res_bod.empty:
            with st.container(border=True):
                ficha_reputacion(res_bod, an_bod, f"⭐ Reputación de {nombre}")
            st.divider()

        st.subheader("Análisis avanzado (IPA · IPCA · DIPCA)")
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
            con_texto_n = int((an_bod["texto"].astype(str).str.len() > 5).sum())
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
