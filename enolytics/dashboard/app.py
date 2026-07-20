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
from enolytics.nlp import idioma as nlp_idioma  # noqa: E402 (solo nombres; no usa langdetect)
from enolytics.analitica import ipa as modelo_ipa  # noqa: E402
from enolytics.analitica import recomendaciones as reco  # noqa: E402
from enolytics.analitica import reputacion as rep  # noqa: E402
from enolytics.dashboard import estilo  # noqa: E402


# --------------------------------------------------------------------------- #
# Gráficos con la identidad de ENOLYTICS (sustituyen a los st.*_chart planos)
# --------------------------------------------------------------------------- #
def barras(datos, titulo: str = "", horizontal: bool = False, color=None,
           alto: int = 300, formato: str | None = None, destacar: str | None = None):
    """Gráfico de barras con el estilo de la casa. `datos`: Series (índice = categoría).

    `destacar`: categoría a resaltar (p. ej. "Marco de Jerez"). El resto queda en un tono
    apagado — patrón *foco + contexto*: el ojo va solo a lo que importa. El color sigue a la
    **entidad**, no a su puesto en el ranking.
    """
    if datos is None or len(datos) == 0:
        return
    d = datos.dropna()
    if d.empty:
        return

    etiquetas = [str(i) for i in d.index]
    if destacar is not None:
        colores = [estilo.SERIES[0] if destacar.lower() in e.lower() else estilo.CONTEXTO
                   for e in etiquetas]
    elif color is not None:
        colores = color
    else:
        colores = estilo.SERIES[0]

    if horizontal:
        orden = d.sort_values()
        etiquetas = [str(i) for i in orden.index]
        if destacar is not None:
            colores = [estilo.SERIES[0] if destacar.lower() in e.lower() else estilo.CONTEXTO
                       for e in etiquetas]
        fig = px.bar(x=orden.values, y=etiquetas, orientation="h")
        plantilla = "<b>%{y}</b><br>%{x:,.0f}<extra></extra>"
    else:
        fig = px.bar(x=etiquetas, y=d.values)
        plantilla = "<b>%{x}</b><br>%{y:,.0f}<extra></extra>"

    fig.update_traces(marker_color=colores, marker_line_width=0, hovertemplate=plantilla)
    # Marcas finas: la barra no debe engordar hasta tocar a su vecina.
    fig.update_layout(title=titulo, bargap=0.45)
    if formato:
        fig.update_traces(texttemplate=formato, textposition="outside",
                          textfont=dict(size=11, color=estilo.INK_SUAVE))
    st.plotly_chart(estilo.figura(fig, alto=alto, leyenda=False), use_container_width=True)


def lineas(datos, titulo: str = "", alto: int = 320):
    """Gráfico de líneas multi-serie. `datos`: DataFrame (índice = eje X, columnas = series)."""
    if datos is None or len(datos) == 0:
        return
    fig = px.line(datos, color_discrete_sequence=estilo.SERIES)
    fig.update_traces(line=dict(width=2), hovertemplate="%{y:,.0f}<extra>%{fullData.name}</extra>")
    fig.update_layout(title=titulo, hovermode="x unified")

    # Si el eje X son años enteros, forzar marcas de año en año: si no, Plotly los trata
    # como números continuos e inventa medios años ("2.022,5"), que no existen.
    idx = getattr(datos, "index", None)
    if idx is not None and pd.api.types.is_integer_dtype(idx):
        fig.update_xaxes(dtick=1, tickformat="d")

    n_series = datos.shape[1] if hasattr(datos, "shape") and len(datos.shape) > 1 else 1
    st.plotly_chart(estilo.figura(fig, alto=alto, leyenda=n_series > 1),
                    use_container_width=True)


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
    """De un conjunto de reseñas anotadas -> tabla IPA (importancia = nº menciones).

    Método CLÁSICO (frecuencia). Se usa como respaldo cuando una bodega no tiene muestra
    suficiente para la PRCA. El método bueno es `ipa_desde_prca`.
    """
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


@st.cache_data
def cargar_prca() -> pd.DataFrame:
    """Importancia por IMPACTO (regresión PRCA) + Kano, precalculada en local.

    Ver enolytics/analitica/prca.py. Columnas: ambito, atributo, importancia, desempeno,
    kano, lambda_kano, beta_penalty, beta_reward, menciones. El dashboard SOLO lee este CSV.
    """
    ruta = config.DATOS_PROCESADO / "prca_kano.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


def ipa_desde_prca(ambito: str) -> pd.DataFrame:
    """Tabla IPA con la importancia REAL (impacto en la satisfacción), no la frecuencia.

    La importancia sale de la regresión PRCA —cuánto mueve la nota global el sentimiento
    hacia el atributo— y el desempeño, del sentimiento por atributo (BERT), no de las
    estrellas de la visita entera. Es lo que corrige el "consejo invertido": «Organización»
    y «Precio», poco mencionados pero de gran impacto, dejan de caer en "Baja prioridad".

    `ambito` = "Marco de Jerez" (destino) o el nombre exacto de una bodega. Devuelve vacío
    si esa bodega no tenía muestra suficiente para una regresión (se usa el IPA clásico).
    """
    prca = cargar_prca()
    if prca.empty:
        return pd.DataFrame()
    sub = prca[prca["ambito"] == ambito]
    if len(sub) < 3:
        return pd.DataFrame()
    registros = [{"atributo": r["atributo"], "importancia": r["importancia"],
                  "desempeno": r["desempeno"]} for _, r in sub.iterrows()]
    puntos = modelo_ipa.calcular_ipa(registros)
    extra = sub.set_index("atributo")
    return pd.DataFrame([{
        "atributo": p.atributo, "importancia": p.importancia,
        "desempeno": p.desempeno, "cuadrante": p.etiqueta,
        "menciones": int(extra.loc[p.atributo, "menciones"]),
        "kano": extra.loc[p.atributo, "kano"],
    } for p in puntos])


def atributos_omitidos(an: pd.DataFrame) -> list[tuple[str, int]]:
    """Atributos descartados por muestra insuficiente, para poder DECIRLO en pantalla.

    Descartar en silencio es lo que hacía que "Entorno y viñedo" apareciera con 5,000★
    calculados sobre 6 reseñas. Se omite, pero se avisa de qué se ha omitido.
    """
    completa = nlp.tabla_importancia_desempeno(an, min_menciones=1)
    if completa.empty:
        return []
    pocos = completa[completa["importancia"] < nlp.MIN_MENCIONES]
    return [(r["atributo"], int(r["importancia"])) for _, r in pocos.iterrows()]


def aviso_omitidos(an: pd.DataFrame) -> None:
    """Pinta el aviso de atributos omitidos por muestra insuficiente."""
    om = atributos_omitidos(an)
    if om:
        detalle = " · ".join(f"{a} ({n})" for a, n in om)
        st.caption(f"⚠️ Omitidos por muestra insuficiente (menos de {nlp.MIN_MENCIONES} "
                   f"reseñas, su media no sería fiable): {detalle}")


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


def figura_ipa(tabla: pd.DataFrame, metodo: str = "prca"):
    """Construye el gráfico de cuadrantes IPA (scatter con líneas de umbral).

    `metodo`: "prca" (importancia = impacto en la satisfacción, desempeño = sentimiento por
    atributo) o "frecuencia" (importancia = nº menciones, desempeño = nota media) para el
    respaldo de bodegas sin muestra suficiente.
    """
    if metodo == "prca":
        lab_imp = "Importancia (impacto en la satisfacción)"
        lab_des = "Desempeño (sentimiento hacia el atributo, 1-5)"
    else:
        lab_imp = "Importancia (nº menciones)"
        lab_des = "Desempeño (nota media, 1-5)"
    umbral_imp = tabla["importancia"].mean()
    umbral_des = tabla["desempeno"].mean()
    fig = px.scatter(
        tabla, x="importancia", y="desempeno", text="atributo",
        color="cuadrante", size="importancia", size_max=40,
        labels={"importancia": lab_imp, "desempeno": lab_des},
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
def cargar_aereo(clave: str) -> pd.DataFrame:
    """Conectividad aérea de Jerez (Dataestur): busquedas, reservas, capacidad, mercados."""
    ruta = config.DATOS_PROCESADO / "conectividad_aerea" / f"{clave}.csv"
    if not ruta.exists():
        return pd.DataFrame()
    df = pd.read_csv(ruta)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


@st.cache_data
def cargar_cruceros() -> pd.DataFrame:
    """Cruceristas del puerto de la Bahía de Cádiz (Dataestur)."""
    ruta = config.DATOS_PROCESADO / "cruceros" / "cruceros_cadiz.csv"
    if not ruta.exists():
        return pd.DataFrame()
    df = pd.read_csv(ruta)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


@st.cache_data
def estacionalidad_resenas(res: pd.DataFrame) -> pd.Series:
    """Reparto de reseñas por mes — *proxy* de la estacionalidad de las visitas."""
    if res.empty or "fecha" not in res.columns:
        return pd.Series(dtype=float)
    f = pd.to_datetime(res["fecha"], errors="coerce", utc=True).dropna()
    if f.empty:
        return pd.Series(dtype=float)
    return f.dt.month.value_counts().sort_index()


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


def panel_idiomas(res: pd.DataFrame, an: pd.DataFrame, ambito: str) -> None:
    """Composición por idioma de las reseñas y sesgo del léxico (solo español)."""
    if res.empty or "segmento_idioma" not in res.columns:
        return

    HISPANO = "Hispanohablante"
    INTL = "Internacional (no hispanohablante)"
    DESC = "Sin determinar"

    st.markdown("**🌍 Idioma de las reseñas** *(proxy de procedencia)*")
    fuente("estimado", "Idioma **inferido** del texto (langdetect). ⚠️ **Idioma ≠ nacionalidad**: "
                       "un mexicano escribe en español y es turista internacional. Además, el "
                       f"**{(res['segmento_idioma'] == DESC).mean() * 100:.0f}%** de las reseñas "
                       "no tiene texto suficiente para determinarlo.")

    det = res[res["segmento_idioma"] != DESC]
    if det.empty:
        st.info("No hay reseñas con texto suficiente para detectar el idioma.")
        return

    n_int = int((det["segmento_idioma"] == INTL).sum())
    i1, i2, i3 = st.columns(3)
    i1.metric("Reseñas en idioma extranjero", f"{n_int / len(det) * 100:.0f}%",
              f"{n_int} de {len(det)} identificadas")
    nota_h = det[det["segmento_idioma"] == HISPANO]["puntuacion"].mean()
    nota_i = det[det["segmento_idioma"] == INTL]["puntuacion"].mean()
    if pd.notna(nota_h):
        i2.metric("Nota · hispanohablante", f"{nota_h:.2f} ★")
    if pd.notna(nota_i):
        i3.metric("Nota · internacional", f"{nota_i:.2f} ★",
                  f"{nota_i - nota_h:+.2f} vs hispanohablante" if pd.notna(nota_h) else None)

    if "idioma" in det.columns:
        top = det["idioma"].value_counts().head(8)
        top.index = [nlp_idioma.nombre_idioma(c) for c in top.index]
        st.caption("Idiomas detectados")
        barras(top)

    # --- ¿Valoran lo mismo el visitante hispanohablante y el internacional? ---
    if not an.empty and "atributos" in an.columns and "segmento_idioma" in an.columns:
        intl_an = an[an["segmento_idioma"] == INTL]
        hisp_an = an[an["segmento_idioma"] == HISPANO]
        if len(intl_an) >= 50 and len(hisp_an) >= 50:
            ciego_i = (intl_an["atributos"].map(len) == 0).mean() * 100

            th = nlp.tabla_importancia_desempeno(hisp_an).set_index("atributo")
            ti = nlp.tabla_importancia_desempeno(intl_an).set_index("atributo")
            filas = []
            for atr in nlp.ATRIBUTOS:
                if atr not in th.index or atr not in ti.index:
                    continue
                filas.append({
                    "Atributo": atr,
                    "Menciona (hispano)": round(th.loc[atr, "importancia"] / len(hisp_an) * 100, 1),
                    "Nota (hispano)": round(th.loc[atr, "desempeno"], 2),
                    "Menciona (internac.)": round(ti.loc[atr, "importancia"] / len(intl_an) * 100, 1),
                    "Nota (internac.)": round(ti.loc[atr, "desempeno"], 2),
                    "Brecha": round(ti.loc[atr, "desempeno"] - th.loc[atr, "desempeno"], 2),
                })
            if filas:
                comp = pd.DataFrame(filas)
                st.markdown("**¿Valoran lo mismo el visitante hispanohablante y el internacional?**")
                st.caption("«Menciona» = % de reseñas de ese segmento que hablan del atributo. "
                           "«Brecha» = nota del internacional menos la del hispanohablante.")
                st.dataframe(comp, use_container_width=True, hide_index=True)

                st.caption(
                    f"⚠️ **Cautela metodológica.** El léxico ya es multilingüe (ES/EN/DE/IT/FR) y "
                    f"solo el **{ciego_i:.0f}%** de las reseñas internacionales queda sin analizar "
                    f"(antes era el 36%), así que la comparación es válida. Aun así, **las palabras "
                    f"clave de cada idioma pueden capturar matices distintos** (p. ej. el inglés "
                    f"*booking* suele ser descriptivo, mientras el español *espera* o *cola* ya "
                    f"arrastran queja). Interpretar las brechas con prudencia."
                )


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


# Estado de una inteligencia según las recomendaciones que genera.
# No se pinta a mano: lo calcula el motor. Si una inteligencia acumula avisos, se enciende sola.
ESTADOS = {
    "critico": ("🔴", "Crítico"),
    "atencion": ("🟠", "Atención"),
    "mejorable": ("🟡", "Mejorable"),
    "ok": ("🟢", "En orden"),
}


def semaforo_inteligencias(recs: list) -> dict:
    """Estado de cada una de las 7 inteligencias, deducido de sus recomendaciones."""
    estado = {}
    for clave, info in config.OBJETIVOS_INTELIGENCIAS.items():
        # El nombre corto que usa el motor ("Económica", "Mercado"...)
        corto = info["titulo"].replace("Inteligencia en ", "").replace("Inteligencia de ", "")
        corto = corto.replace("Inteligencia ", "")
        propias = [r for r in recs if r.inteligencia == corto]
        n_alta = sum(1 for r in propias if r.prioridad == "alta")
        if n_alta >= 2:
            clave_estado = "critico"
        elif n_alta == 1:
            clave_estado = "atencion"
        elif propias:
            clave_estado = "mejorable"
        else:
            clave_estado = "ok"
        estado[clave] = {"titulo": info["titulo"], "corto": corto, "estado": clave_estado,
                         "n_alta": n_alta, "n_total": len(propias)}
    return estado


def pintar_semaforo(estado: dict) -> None:
    """Estado de las 7 inteligencias, de un vistazo.

    El color de estado **nunca va solo**: cada tarjeta lleva icono y texto, para que se lea
    igual sin distinguir colores.
    """
    st.markdown("#### ¿Cómo va el destino?")
    st.caption("Estado de cada inteligencia, deducido de los avisos que genera el motor.")

    orden = ["critico", "atencion", "mejorable", "ok"]
    items = sorted(estado.values(), key=lambda e: orden.index(e["estado"]))

    def _tarjeta(e: dict) -> str:
        color = estilo.ESTADO[e["estado"]]
        icono, etiqueta = ESTADOS[e["estado"]]
        detalle = (f"{e['n_alta']} acción urgente" if e["n_alta"] == 1
                   else f"{e['n_alta']} acciones urgentes" if e["n_alta"] > 1
                   else f"{e['n_total']} mejora(s)" if e["n_total"] else "sin avisos")
        return (
            f'<div style="background:#fff;border:1px solid {estilo.BORDE};'
            f'border-left:4px solid {color};border-radius:11px;padding:.7rem .85rem;'
            f'box-shadow:0 1px 2px rgba(28,27,25,.04);height:100%;">'
            f'<div style="font-size:.72rem;font-weight:700;letter-spacing:.04em;'
            f'text-transform:uppercase;color:{estilo.INK_TENUE};margin-bottom:.3rem;">'
            f'{e["corto"]}</div>'
            f'<div style="font-size:.95rem;font-weight:700;color:{estilo.INK};'
            f'line-height:1.2;">{icono} {etiqueta}</div>'
            f'<div style="font-size:.75rem;color:{estilo.INK_SUAVE};margin-top:.2rem;">'
            f'{detalle}</div></div>'
        )

    # Siempre 4 columnas por fila, aunque la última quede incompleta: así todas las
    # tarjetas tienen el mismo ancho (si no, la fila de 3 se ve desproporcionada).
    for inicio in range(0, len(items), 4):
        fila = items[inicio:inicio + 4]
        cols = st.columns(4)
        for col, e in zip(cols, fila):
            col.markdown(_tarjeta(e), unsafe_allow_html=True)

    st.caption("🔴 2+ acciones urgentes · 🟠 1 urgente · 🟡 mejoras pendientes · 🟢 sin avisos")


def pintar_recomendaciones(recs: list, titulo: str, vacio: str,
                           limite: int | None = None, expandir: bool = True) -> None:
    """Muestra las recomendaciones accionables, ordenadas por prioridad.

    `limite`: si se indica, solo muestra las N primeras y el resto tras un desplegable
    (evita volcar una pared de avisos en la portada).
    """
    if not recs:
        st.success(f"✅ {vacio}")
        return

    n_alta = sum(1 for r in recs if r.prioridad == "alta")
    st.markdown(f"### {titulo}")
    st.caption(f"{len(recs)} recomendaciones · **{n_alta} de prioridad alta**. "
               "Generadas automáticamente cruzando las 7 inteligencias; cada una declara el dato "
               "que la justifica y su fuente.")

    def _tarjeta(r, abierta: bool) -> None:
        icono = reco.ICONO_PRIORIDAD.get(r.prioridad, "•")
        with st.expander(f"{icono} **{r.titulo}** · _{r.inteligencia}_", expanded=abierta):
            st.markdown(f"**Diagnóstico.** {r.diagnostico}")
            st.markdown(f"**Acción propuesta.** {r.accion}")
            if r.fuente:
                st.caption(f"Fuente: {r.fuente}")

    principales = recs[:limite] if limite else recs
    for r in principales:
        _tarjeta(r, abierta=expandir and r.prioridad == "alta")

    resto = recs[limite:] if limite else []
    if resto:
        with st.expander(f"Ver las otras {len(resto)} recomendaciones"):
            for r in resto:
                _tarjeta(r, abierta=False)


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
# IPA del destino: la importancia REAL (PRCA) si está precalculada; si no, la clásica.
tabla_ipa = ipa_desde_prca("Marco de Jerez")
ipa_es_prca = not tabla_ipa.empty
if not ipa_es_prca:
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
cruceros = cargar_cruceros()
aereo_mercados = cargar_aereo("mercados")
aereo_busquedas = cargar_aereo("busquedas")
aereo_capacidad = cargar_aereo("capacidad")
acevin = cargar_acevin()
acevin_oferta = cargar_acevin_oferta()
acevin_ingresos = cargar_acevin_ingresos()
acevin_demanda = cargar_acevin_demanda()

st.markdown(estilo.css(), unsafe_allow_html=True)
st.markdown(
    estilo.hero("🍷 ENOLYTICS",
                "Inteligencia competitiva integrada para el enoturismo del Marco de Jerez"),
    unsafe_allow_html=True)

if df.empty:
    st.warning(
        "No hay catálogo de bodegas todavía. Genera el catálogo con:\n\n"
        "`python3 scripts/actualizar_catalogo.py`"
    )
    st.stop()

# --- Barra lateral: navegación y filtros ---
# Tres niveles, siguiendo el principio "primero la panorámica; el detalle, a demanda":
#   1) Resumen ejecutivo → ¿cómo vamos y qué hago primero?  (5 segundos)
#   2) Las 7 inteligencias → el análisis por fuente          (el analista)
#   3) Bodega individual → la ficha de cada bodega
VISTA_RESUMEN = "🏠 Resumen ejecutivo"
VISTA_INTELIGENCIAS = "🧭 Las 7 inteligencias"
VISTA_BODEGA = "🏭 Bodega individual"

with st.sidebar:
    st.header("Navegación")
    rol = st.radio("Vista", [VISTA_RESUMEN, VISTA_INTELIGENCIAS, VISTA_BODEGA],
                   captions=["Lo esencial, de un vistazo",
                             "El análisis completo por inteligencia",
                             "Ficha y recomendaciones de una bodega"])
    st.divider()
    localidades = sorted(df["localidad"].dropna().unique())
    with st.expander("Filtrar por localidad", expanded=False):
        sel_local = st.multiselect("Localidad", localidades, default=localidades,
                                   label_visibility="collapsed")
    if len(sel_local) < len(localidades):
        st.caption(f"Filtrando {len(sel_local)} de {len(localidades)} localidades")

df_f = df[df["localidad"].isin(sel_local)]

# --------------------------------------------------------------------------- #
# Cálculos comunes al destino (resumen e inteligencias comparten motor)
# --------------------------------------------------------------------------- #
if rol in (VISTA_RESUMEN, VISTA_INTELIGENCIAS):
    tabla_respuestas = tabla_respuestas_marco(resenas)
    recs_destino = reco.recomendaciones_destino(
        acevin=acevin, acevin_oferta=acevin_oferta, acevin_ingresos=acevin_ingresos,
        acevin_demanda=acevin_demanda, trends=trends_temporal,
        accesibilidad=accesibilidad, transporte=transporte, auditoria=auditoria,
        sostenibilidad=sostenibilidad, resumen_dipa=resumen_dipa(evolucion),
        tabla_ipa=tabla_ipa, respuestas=tabla_respuestas, anotadas=anotadas,
        aereo_mercados=aereo_mercados, aereo_capacidad=aereo_capacidad,
        cruceros=cruceros,
    )

# --------------------------------------------------------------------------- #
# VISTA 1 — RESUMEN EJECUTIVO: ¿cómo vamos y qué hago primero? (5 segundos)
# --------------------------------------------------------------------------- #
if rol == VISTA_RESUMEN:
    st.caption("Lo esencial del destino, de un vistazo. El análisis completo está en "
               "**🧭 Las 7 inteligencias**.")

    # --- Cifras clave ---
    k1, k2, k3, k4 = st.columns(4)
    if not acevin.empty:
        _u = int(acevin["anio"].max())
        _v = acevin[(acevin["anio"] == _u) & (acevin["ruta"] == "Marco de Jerez")]["visitantes"]
        _rank = (acevin[acevin["anio"] == _u].sort_values("visitantes", ascending=False)
                 .reset_index(drop=True))
        _pos = int(_rank.index[_rank["ruta"] == "Marco de Jerez"][0]) + 1 \
            if "Marco de Jerez" in set(_rank["ruta"]) else None
        if not _v.empty:
            k1.metric(f"Visitantes {_u}", f"{int(_v.iloc[0]):,}".replace(",", "."),
                      f"{_pos}º de España" if _pos else None, delta_color="off",
                      help="Visitas a bodegas y museos del Marco (ACEVIN).")
    k2.metric("Bodegas", len(df_f))
    if not resenas.empty:
        _nota = f"{resenas['puntuacion'].mean():.2f}".replace(".", ",")
        k3.metric("Valoración del destino", f"{_nota} / 5",
                  f"{len(resenas):,} reseñas".replace(",", "."), delta_color="off")
    if not acevin_ingresos.empty and not acevin.empty:
        _ing = acevin_ingresos[acevin_ingresos["ruta"] == "Marco de Jerez"]
        if not _ing.empty:
            _me = f"{_ing['ingresos_eur'].iloc[0] / 1e6:.1f}".replace(".", ",")
            k4.metric("Ingresos del enoturismo", f"{_me} M€",
                      help="Visitas a bodegas y museos (ACEVIN). No incluye alojamiento "
                           "ni restauración.")

    st.divider()

    # --- Semáforo: estado de las 7 inteligencias (lo calcula el motor) ---
    with st.container(border=True):
        pintar_semaforo(semaforo_inteligencias(recs_destino))

    st.divider()

    # --- Qué hacer primero: solo las 3 más urgentes ---
    with st.container(border=True):
        pintar_recomendaciones(
            recs_destino,
            titulo="🎯 ¿Qué hacer primero?",
            vacio="No hay recomendaciones pendientes con los datos actuales.",
            limite=3)

    st.caption("👉 El detalle de cada indicador, con sus fuentes y cautelas, está en "
               "**🧭 Las 7 inteligencias** (barra lateral).")
    st.stop()


# --------------------------------------------------------------------------- #
# VISTA 2 — LAS 7 INTELIGENCIAS: el análisis completo
# --------------------------------------------------------------------------- #
if rol == VISTA_INTELIGENCIAS:
    st.caption("Una pestaña por cada una de las **7 inteligencias competitivas** del modelo "
               "ENOLYTICS. Cada una abre con lo esencial; el detalle está en los desplegables.")
    leyenda_origenes()

    with st.expander("🎯 Ver las 12 recomendaciones accionables del destino"):
        pintar_recomendaciones(
            recs_destino,
            titulo="Recomendaciones para el destino",
            vacio="No hay recomendaciones pendientes con los datos actuales.",
            expandir=False)

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
                barras(mon.set_index("ruta")["eur_por_visitante"], destacar="Marco de Jerez")

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
            lineas(pivot)

    # ----- 2. Inteligencia de Mercado -----
    with tab_mer:
        cabecera_inteligencia("mercado")
        st.caption("Demanda y percepción del destino. Fuentes: Google Trends (interés de "
                   "búsqueda) y Dataestur (gasto y percepción). Comparación con las rutas "
                   "del vino competidoras.")
        if gasto_anio.empty and satisf_cadiz.empty and trends_temporal.empty:
            st.info("Sin datos de mercado todavía.")

        # --- 🚢 Cruceristas: el mercado cautivo a 40 minutos ---
        if not cruceros.empty:
            st.subheader("🚢 Cruceristas del puerto de Cádiz: el mercado cautivo")
            fuente("oficial", "Dataestur — tráfico portuario de la **Bahía de Cádiz**. El "
                              "crucerista atraca a **40 minutos de las bodegas de Jerez** y hace "
                              "excursión de día (ACEVIN: ~30% de los enoturistas no pernocta).")

            # Año de referencia: el último COMPLETO que además exista en ACEVIN, para poder
            # comparar peras con peras (los cruceros van más adelantados que ACEVIN).
            anios_ok = cruceros.groupby("AÑO")["MES"].nunique()
            completos = set(int(a) for a in anios_ok[anios_ok >= 12].index)
            anios_acevin = set(int(a) for a in acevin["anio"].unique()) if not acevin.empty else set()
            comunes = completos & anios_acevin
            anio_c = max(comunes) if comunes else (max(completos) if completos
                                                   else int(cruceros["AÑO"].max()))

            g = cruceros[cruceros["AÑO"] == anio_c]
            n_cru = int(g["PASAJEROS_CRUCERO"].sum())
            n_esc = int(g["CRUCEROS"].sum())

            c1, c2, c3 = st.columns(3)
            c1.metric(f"Cruceristas en Cádiz ({anio_c})", f"{n_cru:,}".replace(",", "."))
            c2.metric("Escalas de crucero", f"{n_esc:,}".replace(",", "."))

            # Comparación con los visitantes a bodegas del Marco (ACEVIN)
            if not acevin.empty:
                v = acevin[(acevin["anio"] == anio_c) & (acevin["ruta"] == "Marco de Jerez")]
                if not v.empty:
                    n_bod = int(v["visitantes"].iloc[0])
                    c3.metric("Visitantes a bodegas del Marco", f"{n_bod:,}".replace(",", "."),
                              f"{n_cru - n_bod:+,}".replace(",", ".") + " vs cruceristas")
                    if n_cru > n_bod:
                        st.error(
                            f"🚨 **Llegan MÁS cruceristas al puerto de Cádiz "
                            f"({n_cru:,}".replace(",", ".") +
                            f") que visitantes reciben TODAS las bodegas del Marco juntas "
                            f"({n_bod:,}".replace(",", ".") +
                            f").** Es un **mercado cautivo** que desembarca a 40 minutos de Jerez. "
                            f"Cada crucerista que no sube a una bodega es una oportunidad perdida."
                        )

            # --- El cruce de estacionalidades (la oportunidad) ---
            est_res = estacionalidad_resenas(resenas)
            if not est_res.empty:
                cru_mes = cruceros.groupby("MES")["PASAJEROS_CRUCERO"].mean()
                idx_cru = (cru_mes / cru_mes.max() * 100).round(0)
                idx_eno = (est_res / est_res.max() * 100).round(0)
                meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                comp = pd.DataFrame({
                    "Cruceros": [idx_cru.get(m, 0) for m in range(1, 13)],
                    "Enoturismo": [idx_eno.get(m, 0) for m in range(1, 13)],
                }, index=meses)

                st.markdown("**Estacionalidad cruzada: ¿cuándo hay cruceristas y las bodegas están vacías?**")
                fuente("estimado", "El índice de cruceros es dato oficial; el de enoturismo es un "
                                   "**proxy**: el mes en que se escriben las reseñas (aproxima el "
                                   "mes de visita). Ambos en escala 0-100 sobre su propio máximo.")
                lineas(comp)

                # Meses con crucero alto y enoturismo bajo = oportunidad
                oport = comp[(comp["Cruceros"] >= 70) & (comp["Enoturismo"] <= 65)]
                if not oport.empty:
                    lista = ", ".join(f"**{m}** (cruceros {int(r['Cruceros'])} / enoturismo "
                                      f"{int(r['Enoturismo'])})" for m, r in oport.iterrows())
                    st.warning(
                        f"🎯 **Oportunidad de desestacionalización:** en {lista} el puerto está "
                        f"cerca de su máximo mientras las bodegas caen. **Es la prioridad FEDER "
                        f"P4A (reducir la estacionalidad) servida en bandeja:** hay miles de "
                        f"visitantes potenciales a 40 minutos, justo en el mes en que el "
                        f"enoturismo se vacía."
                    )
            st.divider()

        # --- ✈️ Conectividad aérea: el ÚNICO indicador que mira al futuro ---
        if not aereo_mercados.empty:
            st.subheader("✈️ Demanda aérea futura y mercados emisores")
            fuente("oficial", "Dataestur (SEGITTUR) — conectividad aérea de **Jerez de la "
                              "Frontera** (ciudad destino propia). Búsquedas y reservas de vuelo "
                              "**según la fecha en que se quiere viajar**: es el **único "
                              "indicador de ENOLYTICS que se adelanta al viaje**.")

            # Horizonte futuro
            if not aereo_busquedas.empty and "fecha" in aereo_busquedas.columns:
                ult = aereo_busquedas["fecha"].max()
                hoy = pd.Timestamp.today().normalize().replace(day=1)
                meses_fut = max(0, (ult.year - hoy.year) * 12 + (ult.month - hoy.month))
                if meses_fut > 0:
                    st.success(f"🔮 Hay datos de demanda **hasta {ult:%B de %Y}**: "
                               f"**{meses_fut} mes(es) por delante** de hoy.")

            mer = aereo_mercados[aereo_mercados["pais"] != "Total"].copy()

            # --- Demanda SIN conectividad directa (el hallazgo) ---
            if not aereo_capacidad.empty:
                asientos = (aereo_capacidad[aereo_capacidad["PAIS_ORIGEN"] != "Total"]
                            .groupby("PAIS_ORIGEN")["ASIENTOS"].sum())
                mer["asientos_directos"] = mer["pais"].map(asientos).fillna(0).astype(int)
                sin_vuelo = (mer[(mer["asientos_directos"] == 0) & (mer["busquedas"] >= 100_000)]
                             .sort_values("busquedas", ascending=False))
                if not sin_vuelo.empty:
                    total_b = int(sin_vuelo["busquedas"].sum())
                    st.error(
                        f"🚨 **Demanda potencial desatendida: {total_b:,}".replace(",", ".") +
                        f" búsquedas de vuelo desde países SIN un solo asiento directo a Jerez.**"
                        f" Los mayores: " +
                        ", ".join(f"**{r['pais']}** ({int(r['busquedas']):,})".replace(",", ".")
                                  for _, r in sin_vuelo.head(4).iterrows()) +
                        ". Hay gente buscando cómo venir y **no encuentra vuelo directo**."
                    )
                    st.caption("Países con demanda de búsqueda alta y **cero conectividad directa**")
                    st.dataframe(
                        sin_vuelo[["pais", "busquedas", "reservas", "conversion_pct",
                                   "antelacion_busqueda", "estancia_prevista"]].rename(columns={
                            "pais": "País", "busquedas": "Búsquedas", "reservas": "Reservas",
                            "conversion_pct": "Conversión %",
                            "antelacion_busqueda": "Antelación (días)",
                            "estancia_prevista": "Estancia prevista (días)"}),
                        use_container_width=True, hide_index=True)

            # --- Ranking de mercados emisores (detalle, plegado) ---
            top = mer.sort_values("busquedas", ascending=False).head(12)
            with st.expander("📊 Ver el ranking completo de mercados emisores"):
                st.markdown("**Quién busca volar a Jerez**")
                barras(top.set_index("pais")["busquedas"])
                st.caption("«Conversión» = qué porcentaje de las búsquedas acaba en reserva. Un "
                           "mercado que busca mucho y reserva poco es **demanda no capturada**.")
                st.dataframe(
                    top[["pais", "busquedas", "reservas", "conversion_pct",
                         "antelacion_busqueda", "estancia_prevista"]].rename(columns={
                        "pais": "País", "busquedas": "Búsquedas", "reservas": "Reservas",
                        "conversion_pct": "Conversión %",
                        "antelacion_busqueda": "Antelación (días)",
                        "estancia_prevista": "Estancia prevista (días)"}),
                    use_container_width=True, hide_index=True)

            st.caption("👉 La **antelación de compra** y la **estancia prevista** de cada mercado "
                       "están en la pestaña **😊 Clientes** (perfil y planificación del viaje). "
                       "Los **asientos programados**, en **🏛️ Negocios** (infraestructura).")
            st.divider()

        # --- Interés de búsqueda (Google Trends) — apoyo, plegado ---
        if not trends_temporal.empty:
            with st.expander("🔍 Interés de búsqueda en Google frente a las rutas competidoras"):
                termcols = [c for c in trends_temporal.columns if c != "fecha"]
                foco = next((c for c in termcols if "Jerez" in c), termcols[0])
                # Google devuelve datos semanales en 5 años: remuestreamos a meses.
                mensual = (trends_temporal.set_index("fecha")[termcols]
                           .resample("MS").mean())
                medias = mensual.mean().sort_values(ascending=False)
                rank = list(medias.index).index(foco) + 1

                # Tendencia del foco: primeros vs. últimos 24 meses (2 años)
                serie_foco = mensual[foco].dropna()
                n = min(24, len(serie_foco) // 2)
                ini, fin = serie_foco.head(n).mean(), serie_foco.tail(n).mean()
                var = (fin - ini) / ini * 100 if ini else 0.0

                fuente("observado", "Google Trends sobre el término «bodegas [zona]», usado como "
                                    "**proxy de intención de visita**. Escala relativa (0-100), "
                                    "no es volumen absoluto de búsquedas.")
                c1, c2, c3 = st.columns(3)
                etq_foco = foco.replace("bodegas ", "").strip()
                c1.metric(f"Posición de {etq_foco}", f"{rank}º de {len(termcols)}",
                          help="Ranking por interés medio frente a las rutas competidoras.")
                c2.metric(f"Interés medio de {etq_foco}", f"{medias[foco]:.0f}",
                          f"líder: {medias.index[0].replace('bodegas ', '')} ({medias.iloc[0]:.0f})")
                c3.metric("Tendencia de la demanda", f"{var:+.0f}%",
                          help="Variación entre los primeros y los últimos 2 años.")

                suave = mensual.rolling(6, min_periods=2).mean()
                suave.columns = [c.replace("bodegas ", "") for c in suave.columns]
                st.caption("Evolución del interés (media móvil de 6 meses)")
                lineas(suave)

                if not trends_regiones.empty:
                    top_r = trends_regiones.head(8).set_index("comunidad")["interes"]
                    st.caption(f"Origen de la demanda: comunidades que más buscan «{foco}»")
                    barras(top_r)

        # --- Gasto y percepción (Dataestur) — apoyo, plegado ---
        if not gasto_anio.empty or not satisf_cadiz.empty:
            with st.expander("💳 Gasto y percepción del visitante en Cádiz (Dataestur)"):
                if not gasto_anio.empty:
                    st.markdown(f"**Gasto por procedencia del turista ({anio_ref})**")
                    comp = (gasto_anio[gasto_anio["TIPO_ORIGEN"].isin(
                        ["Internacional", "Interregional", "Regional"])]
                        .groupby("TIPO_ORIGEN")["GASTO"].sum() / 1e6)
                    barras(comp)
                if not satisf_cadiz.empty:
                    idx_cols = [c for c in satisf_cadiz.columns if c.startswith("IN")]
                    medias_p = satisf_cadiz[idx_cols].apply(pd.to_numeric, errors="coerce").mean()
                    st.markdown("**Índices de percepción del visitante (media, sobre 100)**")
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
                    c3.metric(f"Crecimiento vs {prev}", f"{var:+.1f}%".replace(".", ","))

            st.markdown(f"**Visitantes por ruta del vino ({ult})**")
            barras(rank_ult.set_index("ruta")["visitantes"], destacar=FOCO)

            st.markdown("**Evolución de visitantes por ruta**")
            piv = acevin.pivot_table(index="anio", columns="ruta", values="visitantes")
            lineas(piv)

            # Tabla-ranking con crecimiento interanual (detalle, plegado)
            if prev:
                _exp_rank = st.expander("📊 Ver la tabla completa de rutas del vino")
                tab = rank_ult.merge(
                    acevin[acevin["anio"] == prev][["ruta", "visitantes"]],
                    on="ruta", how="left", suffixes=("", "_prev"))
                tab["Crecimiento"] = ((tab["visitantes"] - tab["visitantes_prev"])
                                      / tab["visitantes_prev"] * 100).round(1)
                tab.insert(0, "Pos.", range(1, len(tab) + 1))
                with _exp_rank:
                    st.dataframe(
                        tab[["Pos.", "ruta", "visitantes", "visitantes_prev", "Crecimiento"]].rename(
                        columns={"ruta": "Ruta del vino", "visitantes": f"Visitantes {ult}",
                                     "visitantes_prev": f"Visitantes {prev}",
                                     "Crecimiento": "Crec. %"}),
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
                              f"{pos_of}º de {len(of)} rutas en oferta",
                              delta_color="off")
                if not cruce.empty and FOCO in set(cruce["ruta"]):
                    vps = int(cruce.loc[cruce["ruta"] == FOCO, "vis_por_servicio"].iloc[0])
                    o2.metric("Visitantes por servicio", f"{vps:,}".replace(",", "."),
                              help="Visitantes de la ruta ÷ nº de servicios y entidades. "
                                   "Un valor muy alto indica que la oferta va por detrás "
                                   "de la demanda.")

                st.caption("Top 12 rutas por tamaño de la oferta")
                barras(of.head(12).set_index("ruta")["servicios"], destacar=FOCO)

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
                barras(cruce.set_index("ruta")["vis_por_servicio"], destacar=FOCO)

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
                    barras(cen.head(15).set_index("bodega")["total_resenas"])
                with colb:
                    st.caption("Nota media por bodega (Top 15 por reseñas)")
                    barras(cen.head(15).set_index("bodega")["rating"])
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

        # ----- Planificación del viaje: antelación y estancia por mercado -----
        # Cubre el indicador de la Tabla 1 "Canales utilizados para la planificación y reserva",
        # que estaba a cero.
        if not aereo_mercados.empty:
            with st.container(border=True):
                st.markdown("### 🗓️ Cómo planifica el viaje cada mercado")
                fuente("oficial", "Dataestur — conectividad aérea de Jerez. Antelación con la que "
                                  "se busca el vuelo y estancia media prevista, por país emisor.")

                mer_c = (aereo_mercados[aereo_mercados["pais"] != "Total"]
                         .sort_values("busquedas", ascending=False).head(10))
                mer_c = mer_c.dropna(subset=["antelacion_busqueda"])

                if not mer_c.empty:
                    p1, p2 = st.columns(2)
                    p1.metric("Antelación media de búsqueda",
                              f"{mer_c['antelacion_busqueda'].mean():.0f} días",
                              help="Cuánto tiempo antes del viaje se busca el vuelo.")
                    p2.metric("Estancia media prevista",
                              f"{mer_c['estancia_prevista'].mean():.1f} días")

                    st.markdown("**¿Con cuánta antelación planifica cada mercado?**")
                    st.caption("Dice **cuándo lanzar la campaña** en cada país. Si el alemán "
                               "busca con ~170 días de antelación, promocionar el otoño en "
                               "septiembre **llega tarde**: ese viajero ya decidió en abril.")
                    barras(mer_c.set_index("pais")["antelacion_busqueda"])

                    st.markdown("**¿Cuántos días se quedará cada mercado?**")
                    st.caption("La estancia prevista indica **a quién merece la pena captar**: "
                               "quien se queda más días, gasta más en el destino.")
                    barras(mer_c.set_index("pais")["estancia_prevista"])

                    # El mercado que más se queda
                    largo = mer_c.sort_values("estancia_prevista", ascending=False).iloc[0]
                    st.info(
                        f"💡 **{largo['pais']}** es el mercado de **estancia más larga** "
                        f"(**{largo['estancia_prevista']:.1f} días**) y planifica con "
                        f"**{largo['antelacion_busqueda']:.0f} días** de antelación. "
                        f"Es el perfil de **mayor valor por visitante**."
                    )
            st.divider()

        # ----- Idioma de las reseñas (proxy de procedencia) -----
        if not resenas.empty and "segmento_idioma" in resenas.columns:
            with st.container(border=True):
                panel_idiomas(resenas, anotadas, "Marco")
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
            if ipa_es_prca:
                fuente("estimado", "Calculado sobre 10.972 reseñas de Google. **Importancia** = "
                                   "*impacto en la satisfacción* (regresión PRCA: cuánto mueve la "
                                   "nota global el sentimiento hacia cada atributo), **no** el nº de "
                                   "menciones. **Desempeño** = sentimiento hacia el atributo (BERT "
                                   "multilingüe, frase a frase), no la nota de la visita entera. "
                                   "Así, «Organización» y «Precio» —poco mencionados pero de gran "
                                   "impacto— aparecen en *«Concéntrese aquí»* y no en *«Baja "
                                   "prioridad»*, como ocurría con el método por frecuencia.")
                # La columna Kano NO se muestra aún: por el efecto techo (78,7% de cincos) los
                # 7 atributos salen "Básico", que sin explicación confunde. Decisión pendiente.
                cols = {"atributo": "Atributo", "importancia": "Importancia (impacto)",
                        "desempeno": "Desempeño (sentimiento)", "cuadrante": "Cuadrante IPA",
                        "menciones": "Menciones"}
            else:
                fuente("estimado", "Muestra insuficiente para la importancia por impacto; se usa el "
                                   "método clásico. **Importancia** = nº de menciones; **desempeño** "
                                   "= nota media de las reseñas que lo mencionan.")
                cols = {"atributo": "Atributo", "importancia": "Importancia",
                        "desempeno": "Desempeño", "cuadrante": "Cuadrante IPA"}
            st.plotly_chart(figura_ipa(tabla_ipa, metodo="prca" if ipa_es_prca else "frecuencia"),
                            use_container_width=True)
            st.dataframe(tabla_ipa.rename(columns=cols)[list(cols.values())],
                         use_container_width=True, hide_index=True)
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
                barras(conteo)

        # ----- Infraestructura de llegada: capacidad aérea del destino -----
        if not aereo_capacidad.empty:
            st.divider()
            st.subheader("✈️ Capacidad aérea del destino")
            fuente("oficial", "Dataestur — asientos programados con destino **Jerez de la "
                              "Frontera**. Es la **infraestructura de llegada**: cuánta gente "
                              "*puede* llegar en avión.")

            cap = aereo_capacidad[aereo_capacidad["PAIS_ORIGEN"] != "Total"]
            por_pais = cap.groupby("PAIS_ORIGEN")["ASIENTOS"].sum().sort_values(ascending=False)
            por_pais = por_pais[por_pais > 0]

            n1, n2 = st.columns(2)
            n1.metric("Países con vuelo directo a Jerez", len(por_pais),
                      help="Solo estos países tienen asientos programados hacia Jerez.")
            n2.metric("Asientos programados (total del periodo)",
                      f"{int(por_pais.sum()):,}".replace(",", "."))

            st.markdown("**Asientos programados por país de origen**")
            barras(por_pais)

            if len(por_pais) <= 12:
                st.warning(
                    f"⚠️ **La conectividad aérea es muy estrecha: solo {len(por_pais)} países "
                    f"tienen vuelo directo a Jerez.** Es un cuello de botella de la "
                    f"infraestructura del destino. En la pestaña **📈 Mercado** se ve la demanda "
                    f"que queda desatendida por esta falta de conexiones."
                )

            # Evolución mensual de asientos (estacionalidad de la oferta aérea)
            if "fecha" in aereo_capacidad.columns:
                serie = (aereo_capacidad[aereo_capacidad["PAIS_ORIGEN"] != "Total"]
                         .groupby("fecha")["ASIENTOS"].sum())
                if len(serie) > 3:
                    st.markdown("**Evolución de los asientos programados**")
                    st.caption("Revela la **estacionalidad de la oferta aérea**: cuándo hay "
                               "aviones y cuándo el destino se queda incomunicado.")
                    lineas(serie)
            st.divider()

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
            barras(adopcion)

            with st.expander("📊 Ver el ranking de madurez digital por bodega"):
                st.dataframe(
                    aud_ok.sort_values("madurez_digital", ascending=False)[
                        ["bodega", "localidad", "madurez_digital", "reserva_online",
                         "ingles", "inmersiva"]
                    ].rename(columns={"bodega": "Bodega", "localidad": "Localidad",
                                      "madurez_digital": "Madurez /5",
                                      "reserva_online": "Reserva",
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
                barras(cumpl.sort_values())

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
                barras(adop.sort_values(ascending=False))

            # Ranking por índice de sostenibilidad comunicada
            if tiene_indice:
                with st.expander("📊 Ver el ranking de sostenibilidad comunicada"):
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
                barras(transporte["categoria_transporte"].value_counts())

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
        ipa_bod = ipa_desde_prca(nombre)
        if ipa_bod.empty and not an_bod.empty:
            ipa_bod = ipa_desde_anotadas(an_bod)
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
            if "segmento_idioma" in res_bod.columns:
                with st.container(border=True):
                    panel_idiomas(res_bod, an_bod, nombre)
            st.divider()

        st.subheader("Análisis avanzado (IPA · IPCA · DIPCA)")
        if not an_bod.empty:
            # Sentimiento y cuadrantes IPA de ESTA bodega
            col1, col2 = st.columns([1, 2])
            with col1:
                st.caption("Sentimiento (por estrellas)")
                barras(an_bod["sentimiento"].value_counts())
            with col2:
                # Importancia por impacto (PRCA) si esta bodega tiene muestra; si no, la clásica.
                tabla_ipa_bod = ipa_desde_prca(nombre)
                bod_es_prca = not tabla_ipa_bod.empty
                if not bod_es_prca:
                    tabla_ipa_bod = ipa_desde_anotadas(an_bod)
                if len(tabla_ipa_bod) >= 3:
                    if bod_es_prca:
                        st.caption("Importancia-Desempeño (IPA) de esta bodega · importancia por "
                                   "impacto en la satisfacción (PRCA)")
                    else:
                        st.caption("Importancia-Desempeño (IPA) de esta bodega · método clásico "
                                   "(muestra insuficiente para la importancia por impacto)")
                    st.plotly_chart(
                        figura_ipa(tabla_ipa_bod, metodo="prca" if bod_es_prca else "frecuencia"),
                        use_container_width=True)
                    aviso_omitidos(an_bod)
                else:
                    st.caption("Pocas reseñas con atributos para un IPA fiable de esta bodega.")
                    aviso_omitidos(an_bod)

            # IPCA: esta bodega frente al resto del Marco
            comp_an = anotadas[anotadas["bodega"] != nombre]
            tabla_ipca = ipca_desde_anotadas(an_bod, comp_an)
            if len(tabla_ipca) >= 3:
                st.markdown("**Análisis competitivo (IPCA): esta bodega vs. el Marco de Jerez**")
                st.caption(
                    f"Brecha positiva = la bodega supera la media del Marco en ese atributo; "
                    f"negativa = va por detrás. Las diferencias menores de "
                    f"{modelo_ipa.BANDA_INDIFERENCIA:.2f}★ se marcan **En línea con el Marco**: "
                    f"son demasiado pequeñas para sostener un diagnóstico."
                )
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
