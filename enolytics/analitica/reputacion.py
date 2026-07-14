"""Ficha de reputación por bodega, al estilo Booking/Amazon.

Presenta el análisis de reseñas en el formato que el sector ya reconoce (distribución de
estrellas, puntuación por categoría, resumen de "lo que dicen los clientes", aspectos con su
signo), pero apoyado en **nuestro** motor de atributos, no en una caja negra.

Diferencia clave con Amazon: su resumen *"Los clientes dicen"* lo **genera una IA** a partir del
texto (puede alucinar y no es reproducible). **Aquí el resumen se compone a partir de los datos
agregados reales** (menciones y nota media por atributo): es determinista, auditable y
reproducible — condición necesaria para un proyecto de investigación.

Cubre lo que promete la memoria: *"identificar los factores más valorados por los turistas y
detectar áreas de mejora en la oferta enoturística"*.

Uso:
    from enolytics.analitica import reputacion
    dist = reputacion.distribucion_estrellas(resenas_bodega)
    asp  = reputacion.aspectos(anotadas_bodega)
    txt  = reputacion.resumen_textual(asp)
"""
from __future__ import annotations

import pandas as pd

# Umbrales para clasificar el signo de un aspecto (nota media sobre 5)
UMBRAL_POSITIVO = 4.40
UMBRAL_NEGATIVO = 3.80

SIGNOS = {
    "positivo": ("↗", "Lo destacan"),
    "mixto": ("~", "Opiniones variadas"),
    "negativo": ("↘", "Expresan descontento"),
}

# Nº mínimo de menciones para que un aspecto se muestre (evita conclusiones de 2 reseñas)
MIN_MENCIONES = 5


def distribucion_estrellas(resenas: pd.DataFrame) -> pd.DataFrame:
    """Reparto de reseñas por nº de estrellas (5→1), con su porcentaje."""
    if resenas.empty or "puntuacion" not in resenas.columns:
        return pd.DataFrame()
    total = len(resenas)
    filas = []
    for estrellas in (5, 4, 3, 2, 1):
        n = int((resenas["puntuacion"] == estrellas).sum())
        filas.append({"estrellas": estrellas, "n": n,
                      "pct": round(n / total * 100, 1) if total else 0.0})
    return pd.DataFrame(filas)


def _signo(desempeno: float) -> str:
    if desempeno >= UMBRAL_POSITIVO:
        return "positivo"
    if desempeno < UMBRAL_NEGATIVO:
        return "negativo"
    return "mixto"


def aspectos(anotadas: pd.DataFrame, min_menciones: int = MIN_MENCIONES) -> pd.DataFrame:
    """Aspectos mencionados: nº de menciones, nota media y signo (positivo/mixto/negativo).

    `anotadas` son reseñas ya pasadas por `nlp.anotar_resenas` (una columna booleana por
    atributo). Devuelve las columnas: atributo, menciones, desempeno, signo, icono, etiqueta.
    """
    from enolytics.nlp import analisis as nlp

    if anotadas.empty or "atributos" not in anotadas.columns:
        return pd.DataFrame()

    # `atributos` es una lista de nombres de atributo por reseña (salida de anotar_resenas)
    con_atributos = anotadas[anotadas["atributos"].map(len) > 0]
    filas = []
    for atributo in nlp.ATRIBUTOS:
        sub = con_atributos[con_atributos["atributos"].map(lambda a: atributo in a)]
        if len(sub) < min_menciones:
            continue
        desempeno = float(sub["puntuacion"].mean())
        s = _signo(desempeno)
        icono, etiqueta = SIGNOS[s]
        filas.append({"atributo": atributo, "menciones": len(sub),
                      "desempeno": round(desempeno, 2), "signo": s,
                      "icono": icono, "etiqueta": etiqueta})

    if not filas:
        return pd.DataFrame()
    return pd.DataFrame(filas).sort_values("menciones", ascending=False).reset_index(drop=True)


def resumen_textual(asp: pd.DataFrame) -> str:
    """Redacta 'lo que dicen los visitantes' a partir de los datos agregados.

    Determinista: la misma tabla produce siempre el mismo texto. No usa un modelo generativo,
    así que no puede inventarse nada que los datos no digan.
    """
    if asp.empty:
        return "Aún no hay suficientes reseñas para resumir la opinión de los visitantes."

    def _listar(nombres: list[str]) -> str:
        nombres = [n.lower() for n in nombres]
        if len(nombres) == 1:
            return f"**{nombres[0]}**"
        return ", ".join(f"**{n}**" for n in nombres[:-1]) + f" y **{nombres[-1]}**"

    partes = []
    pos = asp[asp["signo"] == "positivo"].head(3)["atributo"].tolist()
    mix = asp[asp["signo"] == "mixto"]["atributo"].tolist()
    neg = asp[asp["signo"] == "negativo"]["atributo"].tolist()

    if pos:
        partes.append(f"Los visitantes destacan {_listar(pos)}.")
    if neg:
        partes.append(f"Sin embargo, expresan descontento con {_listar(neg)}.")
    if mix:
        verbo = "son variadas" if len(mix) > 1 else "son variadas"
        partes.append(f"Las opiniones sobre {_listar(mix)} {verbo}.")

    return " ".join(partes)


def resenas_destacadas(resenas: pd.DataFrame, n: int = 2) -> dict[str, pd.DataFrame]:
    """Reseñas representativas: las mejor valoradas y las críticas más útiles.

    Se priorizan las que tienen texto y más 'me gusta' (proxy de utilidad, como en Amazon).
    """
    if resenas.empty or "texto" not in resenas.columns:
        return {"positivas": pd.DataFrame(), "negativas": pd.DataFrame()}

    con_texto = resenas[resenas["texto"].astype(str).str.len() > 40].copy()
    if con_texto.empty:
        return {"positivas": pd.DataFrame(), "negativas": pd.DataFrame()}
    con_texto["likes"] = pd.to_numeric(con_texto.get("likes"), errors="coerce").fillna(0)

    pos = (con_texto[con_texto["puntuacion"] >= 4]
           .sort_values(["likes", "puntuacion"], ascending=False).head(n))
    neg = (con_texto[con_texto["puntuacion"] <= 2]
           .sort_values(["likes"], ascending=False).head(n))
    return {"positivas": pos, "negativas": neg}


def tasa_respuesta(resenas: pd.DataFrame) -> dict:
    """% de reseñas contestadas por la bodega (y % de las negativas).

    No lo muestran Amazon ni Booking, pero es un indicador de **gestión de la reputación**:
    responder a una crítica es la acción más barata y visible que puede tomar una bodega.
    """
    if resenas.empty or "respuesta_propietario" not in resenas.columns:
        return {}
    resp = resenas["respuesta_propietario"].notna() & (
        resenas["respuesta_propietario"].astype(str).str.strip() != "")
    neg = resenas["puntuacion"] <= 2
    return {
        "pct_total": round(resp.mean() * 100, 1),
        "n_respondidas": int(resp.sum()),
        "pct_negativas": round(resp[neg].mean() * 100, 1) if neg.any() else None,
        "n_negativas": int(neg.sum()),
    }
