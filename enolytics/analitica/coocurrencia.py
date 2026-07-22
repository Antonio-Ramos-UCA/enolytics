"""Co-ocurrencias de atributos en las reseñas: el método CO-WORD de la bibliometría.

Idea (a propuesta de Antonio): representar qué atributos **se mencionan juntos** dentro de una
misma reseña. Si «Vino y cata» aparece casi siempre con «Visita y experiencia», en la mente del
enoturista van de la mano. Es el análisis de co-palabras (Callon et al., 1983) aplicado a
nuestros 8 atributos en vez de a las keywords de un corpus de artículos.

Dos medidas del vínculo entre dos atributos i y j:
  · **Bruto**: nº de reseñas que mencionan LOS DOS. Intuitivo, pero lo dominan los atributos
    grandes (Visita, Vino), que se juntan con todo solo por ser frecuentes.
  · **Equivalencia de Callon** (normalizado): e_ij = c_ij² / (c_i · c_j) ∈ [0, 1]. Mide la
    asociación **por encima de lo esperable por su frecuencia** — saca a la luz vínculos reales,
    no artefactos del tamaño. Es la medida canónica del co-word.

Capa de sentimiento: el mismo cálculo sobre las reseñas **positivas** (≥4★) y **negativas**
(≤2★) por separado revela qué atributos se agrupan en los elogios frente a en las quejas.

El dato ya existe: la columna `atributos` de las reseñas anotadas (lista de atributos por
reseña). No hace falta nada nuevo.
"""
from __future__ import annotations

import itertools
from collections import Counter

import pandas as pd


def _pares_y_marginales(anotadas: pd.DataFrame) -> tuple[Counter, Counter, int]:
    """Cuenta co-ocurrencias por par y nº de reseñas por atributo (marginales).

    Solo cuentan las reseñas con ≥1 atributo; los pares, las de ≥2.
    """
    co: Counter = Counter()
    marg: Counter = Counter()
    n = 0
    for atrs in anotadas["atributos"]:
        s = sorted(set(atrs))
        if not s:
            continue
        n += 1
        for a in s:
            marg[a] += 1
        for a, b in itertools.combinations(s, 2):
            co[(a, b)] += 1
    return co, marg, n


def tabla_pares(anotadas: pd.DataFrame) -> tuple[pd.DataFrame, dict, int]:
    """Devuelve (df de pares, marginales, nº reseñas con atributo).

    El df tiene: atributo_a, atributo_b, coocurrencias (bruto), equivalencia (Callon).
    """
    co, marg, n = _pares_y_marginales(anotadas)
    filas = []
    for (a, b), c in co.items():
        denom = marg[a] * marg[b]
        equiv = (c * c) / denom if denom else 0.0
        filas.append({"atributo_a": a, "atributo_b": b,
                      "coocurrencias": int(c), "equivalencia": round(equiv, 4)})
    df = pd.DataFrame(filas)
    if not df.empty:
        df = df.sort_values("coocurrencias", ascending=False).reset_index(drop=True)
    return df, dict(marg), n


def matriz(pares: pd.DataFrame, atributos: list[str],
           valor: str = "coocurrencias") -> pd.DataFrame:
    """Matriz cuadrada atributo×atributo (simétrica, diagonal 0) para el mapa de calor.

    `valor`: 'coocurrencias' (bruto) o 'equivalencia' (normalizado).
    """
    m = pd.DataFrame(0.0, index=atributos, columns=atributos)
    for _, r in pares.iterrows():
        a, b = r["atributo_a"], r["atributo_b"]
        if a in m.index and b in m.columns:
            m.loc[a, b] = r[valor]
            m.loc[b, a] = r[valor]
    return m


def por_sentimiento(anotadas: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tabla de pares para el corpus completo y para positivas/negativas por separado.

    Usa la columna `sentimiento` (positivo/negativo, derivada de las estrellas de la reseña:
    aquí es correcto usar la nota global, porque clasificamos la RESEÑA entera, no un atributo).

    Devuelve {'todas': {...}, 'positivas': {...}, 'negativas': {...}}, donde cada valor es
    {'pares': df, 'marginales': dict, 'n': int}.
    """
    out = {}
    subconjuntos = {"todas": anotadas}
    if "sentimiento" in anotadas.columns:
        subconjuntos["positivas"] = anotadas[anotadas["sentimiento"] == "positivo"]
        subconjuntos["negativas"] = anotadas[anotadas["sentimiento"] == "negativo"]
    for clave, sub in subconjuntos.items():
        df, marg, n = tabla_pares(sub)
        out[clave] = {"pares": df, "marginales": marg, "n": n}
    return out
