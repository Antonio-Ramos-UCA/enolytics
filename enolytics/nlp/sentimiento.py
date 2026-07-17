"""Sentimiento POR ATRIBUTO con BERT multilingüe, frase a frase.

Por qué existe este módulo
--------------------------
Hasta ahora el desempeño de un atributo era **la nota media (estrellas) de las reseñas que lo
mencionaban**. Pero las estrellas son de la VISITA ENTERA, no del atributo: a una reseña que
dice *"it is expensive but a special place"* con 5★ le asignábamos **desempeño del Precio =
5,0**. Medido en el corpus: el 44% de las 96 quejas explícitas de precio tienen 4-5★, y los 7
atributos se apiñaban entre 4,00 y 4,71 en torno a la nota global (σ = 0,288).

La solución (Bi et al., 2019, *Tourism Management*, ec. 1-2): el desempeño de un atributo es la
media del **sentimiento hacia ESE atributo**, no la nota global. Para eso hace falta bajar al
nivel de FRASE: *"La visita fue genial, pero la reserva un caos"* aporta positivo a «Visita» y
negativo a «Organización», en vez de aportar la misma nota a los dos.

Modelo
------
`nlptown/bert-base-multilingual-uncased-sentiment`: entrenado sobre RESEÑAS en EN, NL, DE, FR,
ES e IT — nuestros idiomas, e incluye el **neerlandés** (63 reseñas) que ni siquiera está en el
léxico. Devuelve **5 clases con probabilidades**, que es literalmente lo que piden las
ecuaciones 2-3 de Zhang et al. (2021) para la PRCA.

Coste y arquitectura
--------------------
~3 min para las 7.277 reseñas con texto (42 reseñas/s con MPS). Se ejecuta **en local** y deja
un CSV; el dashboard SOLO lee el CSV. `torch`/`transformers` NO entran en `requirements.txt`
(Streamlit Cloud tiene ~1 GB de RAM y se ahogaría). Es el mismo patrón que el resto de fuentes.

Uso
---
    python -m enolytics.nlp.sentimiento     # calcula y guarda el CSV
"""
from __future__ import annotations

import re

import pandas as pd

from enolytics import config
from enolytics.nlp import analisis

MODELO = "nlptown/bert-base-multilingual-uncased-sentiment"

# Frases más cortas que esto no se analizan: sin contenido semántico, sólo meten ruido.
# (Han et al., 2026, hacen lo mismo: "filter out short sentences that lack semantic content".)
MIN_CARACTERES_FRASE = 12

# Las 5 clases del modelo, en el orden s0..s4 de las ecuaciones de Zhang et al. (2021):
# s0 = muy negativo (1 estrella) ... s4 = muy positivo (5 estrellas).
CLASES = ["s0", "s1", "s2", "s3", "s4"]

SALIDA = config.DATOS_PROCESADO / "sentimiento_atributos.csv"


def trocear(texto: str) -> list[str]:
    """Parte una reseña en frases. Multilingüe: no asume idioma."""
    if not isinstance(texto, str) or not texto.strip():
        return []
    limpio = re.sub(r"<[^>]+>", " ", texto)  # quita <br> y demás
    try:
        from nltk.tokenize import sent_tokenize
        frases = sent_tokenize(limpio)
    except Exception:  # sin punkt: corte por puntuación, suficiente
        frases = re.split(r"(?<=[.!?])\s+|\n+", limpio)
    return [f.strip() for f in frases if len(f.strip()) >= MIN_CARACTERES_FRASE]


def _clasificador(lote: int = 32):
    """Pipeline de BERT. Usa la GPU del Mac (MPS) si está disponible."""
    import torch
    from transformers import pipeline
    dispositivo = "mps" if torch.backends.mps.is_available() else "cpu"
    return pipeline("sentiment-analysis", model=MODELO, device=dispositivo,
                    top_k=None, truncation=True, max_length=256, batch_size=lote)


def _distribucion(salida_bert) -> dict[str, float]:
    """Convierte la salida del modelo en {s0..s4: probabilidad}."""
    d = {c: 0.0 for c in CLASES}
    for item in salida_bert:
        estrellas = int(item["label"][0])       # "1 star" .. "5 stars"
        d[f"s{estrellas - 1}"] = float(item["score"])
    return d


def analizar(resenas: pd.DataFrame, lote: int = 32, verboso: bool = True) -> pd.DataFrame:
    """Sentimiento por (reseña, atributo) a partir de las frases.

    Cada frase se asigna a los atributos que menciona (mismo léxico que el IPA) y se le mide el
    sentimiento. Si una reseña habla dos veces del vino, se promedian esas frases.

    Devuelve: resena_id, bodega, puntuacion, atributo, n_frases, s0..s4, sentimiento (1-5).

    Nota: una frase que menciona dos atributos aporta su sentimiento a AMBOS. Han et al. (2026)
    usan un desempate por prioridad; aquí no, porque ningún atributo es el foco.
    """
    filas_frase = []
    for _, r in resenas.iterrows():
        for frase in trocear(r.get("texto")):
            attrs = analisis.detectar_atributos(frase)
            if attrs:
                filas_frase.append({"resena_id": r["resena_id"], "frase": frase,
                                    "atributos": attrs})
    if not filas_frase:
        return pd.DataFrame(columns=["resena_id", "atributo", "n_frases", *CLASES, "sentimiento"])

    fr = pd.DataFrame(filas_frase)
    if verboso:
        print(f"  {len(fr)} frases con atributo, de {len(resenas)} reseñas. Pasando BERT...")

    clf = _clasificador(lote)
    salidas = clf(fr["frase"].tolist())
    dist = pd.DataFrame([_distribucion(s) for s in salidas])
    fr = pd.concat([fr.reset_index(drop=True), dist], axis=1)

    # Una fila por (reseña, atributo): la frase aporta a cada atributo que menciona.
    fr = fr.explode("atributos").rename(columns={"atributos": "atributo"})
    g = (fr.groupby(["resena_id", "atributo"])
           .agg(n_frases=("frase", "count"), **{c: (c, "mean") for c in CLASES})
           .reset_index())

    # Renormaliza (promediar distribuciones puede desviar levemente de 1) y valor esperado 1-5.
    total = g[CLASES].sum(axis=1)
    for c in CLASES:
        g[c] = (g[c] / total).round(6)
    g["sentimiento"] = sum(g[c] * (i + 1) for i, c in enumerate(CLASES)).round(3)

    meta = resenas[["resena_id", "bodega", "puntuacion"]].drop_duplicates("resena_id")
    return g.merge(meta, on="resena_id", how="left")


def calcular_y_guardar(lote: int = 32) -> pd.DataFrame:
    """Ejecuta el análisis sobre el corpus completo y guarda el CSV."""
    from enolytics.etl import resenas as etl
    res = etl.cargar_resenas()
    con = res[res["texto"].fillna("").str.strip() != ""]
    print(f"Reseñas con texto: {len(con)}")
    tabla = analizar(con, lote=lote)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    print(f"Guardado: {SALIDA}  ({len(tabla)} filas reseña-atributo)")
    return tabla


def cargar() -> pd.DataFrame:
    """Lee el CSV precalculado. Es lo único que hace el dashboard."""
    if not SALIDA.exists():
        return pd.DataFrame()
    return pd.read_csv(SALIDA)


if __name__ == "__main__":
    calcular_y_guardar()
