"""PRCA + modelo de Kano: importancia por impacto en la satisfacción.

Qué problema resuelve
---------------------
Hasta ahora la IMPORTANCIA de un atributo era **el número de reseñas que lo mencionaban**. Que
se hable mucho del vino no demuestra que el vino determine la satisfacción. Consecuencia real
en el dashboard: «Organización y reserva» —el PEOR atributo del Marco— caía en el cuadrante
*"Baja prioridad"* por tener sólo 331 menciones. El producto le decía a las bodegas
**"lo que peor haces, no lo toques"**.

Además, la frecuencia **no aparece en la taxonomía de la literatura**: Bi et al. (2019, secc.
2.1) sólo reconocen dos familias, la *declarada* (encuesta) y la *implícita* (deducir el
impacto sobre la satisfacción). Esto implementa la segunda.

El método (Zhang et al., 2021, *Tourism Management*, `BIBLIOGRAFIA/Zhang_2021_TM.pdf`)
---------------------------------------------------------------------------------------
**PRCA** (*penalty–reward contrast analysis*, Brandt, 1987): una regresión donde cada atributo
entra con DOS variables, para dejar que lo bueno y lo malo pesen distinto:

    nota = β₀ + Σ ( β_penalty(i)·d_low(i) + β_reward(i)·d_high(i) ) + ε        (ec. 1)

    d_low  = (p_s0·2 + p_s1·1) / (p_s0·2 + p_s1·1 + p_s3·1 + p_s4·2)          (ec. 2)
    d_high = (p_s4·2 + p_s3·1) / (p_s0·2 + p_s1·1 + p_s3·1 + p_s4·2)          (ec. 3)

Lo intenso pesa doble; **el neutro (s2) se descarta**. d_low + d_high = 1.

De los MISMOS dos coeficientes salen las dos respuestas:

    λ = (|β_reward| − |β_penalty|) / (|β_reward| + |β_penalty|)                (ec. 4)  -> KANO
    Importancia = √(β_penalty² + β_reward²) / Σ √(...)                         (ec. 5)  -> IPA

La magnitud dice *cuánto mueve la nota*; la asimetría, *hacia dónde la mueve*. Kano no es un
modelo aparte: es leer la misma regresión de otra manera.

Kano (umbrales de Pratt et al., 2020, usados por Han et al., 2026):
  · λ > 0,20     ENTUSIASMO  deleita si está; no penaliza si falta.
  · −0,20 … 0,20 DESEMPEÑO   lineal: mejor rendimiento, más satisfacción.
  · λ < −0,20    BÁSICO      se da por supuesto; si falla, resta; si va bien, no suma.

Resultado en el Marco (17/07): la IMPORTANCIA funciona; KANO no es interpretable
--------------------------------------------------------------------------------
✅ **La importancia arregla el consejo invertido.** Con frecuencia, «Precio» (771 menciones) y
«Organización» (331) —los dos PEORES atributos— caían en *"Baja prioridad"*: el producto decía
*"lo que peor haces, no lo toques"*. Con la PRCA suben a **16,9% y 16,1%** de importancia y
pasan a **"Concéntrese aquí"**. Además «Vino y cata», lo más mencionado (4.248), baja a 11,1%
y sale *"Posible exceso"*: se habla mucho del vino pero no mueve la nota, porque siempre es bueno.
Modelo sano: R² = 0,55, F significativa, 465 obs/variable.

🚨 **KANO NO SALE: los 7 atributos dan "Básico" por EFECTO TECHO.** No es un hallazgo, es
aritmética. Medido para «Organización y reserva»: la nota de referencia (quien no lo menciona)
ya es **4,61 sobre 5**; hablar maravillas sube **+0,23**, hablar mal hunde **−2,56**. Once veces
de asimetría *mecánica*: no queda margen donde premiar. Con **78,7% de cincos**, β_penalty >>
β_reward para CUALQUIER atributo, y λ sale siempre muy negativo (−0,39 a −0,96).
→ **Es la objeción (1) de Bi et al. (2019) confirmada**: la nota es una J, no una Gaussiana.
  Zhang y Han no la comprobaron; sus reseñas de Yelp están más repartidas que las nuestras de
  Google Maps. **λ absoluto NO es interpretable aquí**; su ORDEN relativo quizá sí.
  Vías abiertas: regresión ordinal (modela la satisfacción latente y trata el techo como umbral)
  o aceptar el resultado negativo. Ver docs/pendientes.md.

Requisito y cautelas
--------------------
- **Exige `nlp/sentimiento.py`**: la PRCA regresa el sentimiento del atributo contra la nota.
  Si el sentimiento saliera de la nota (como antes), la regresión sería CIRCULAR.
- **Multicolinealidad**: dentro de la regresión sube a 0,51 (no los 0,103 de las menciones
  binarias), porque d_low + d_high = 1 en los atributos mencionados. Manejable, pero infla los
  errores estándar. Es la objeción (3) de Bi, que sobre indicadores no aplicaba y aquí sí asoma.
- **Tamaño**: 14 variables (7 atributos × 2). El destino tiene 465 obs/variable. Sólo 12 de las
  40 bodegas llegan a 10 obs/variable; el resto se queda con el IPA clásico.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

CLASES = ["s0", "s1", "s2", "s3", "s4"]

# Umbrales de Kano (Pratt et al., 2020).
UMBRAL_KANO = 0.20
KANO_ENTUSIASMO = "Entusiasmo"
KANO_DESEMPENO = "Desempeño"
KANO_BASICO = "Básico"

# Mínimo de observaciones por variable de la regresión, para no sobreajustar.
MIN_OBS_POR_VARIABLE = 10

# Mínimo de reseñas para que un atributo entre en la regresión. Es el mismo criterio que
# `nlp.MIN_MENCIONES`, y hace falta AQUÍ TAMBIÉN: sin él, Barbadillo daba «Entorno y viñedo»
# con un 52,6% de importancia calculado sobre 6 menciones — el coeficiente es inestable y, al
# normalizar, se comía más de la mitad del reparto. Un atributo casi no mencionado no puede
# ser el más importante.
MIN_MENCIONES_ATRIBUTO = 8


@dataclass
class ResultadoPRCA:
    atributo: str
    beta_penalty: float
    beta_reward: float
    p_penalty: float
    p_reward: float
    importancia: float      # normalizada: las de todos los atributos suman 1
    lambda_kano: float
    kano: str
    desempeno: float        # sentimiento medio hacia el atributo (1-5)
    menciones: int


def _pesos(dist: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """d_low y d_high (ec. 2-3). Lo intenso pesa doble; el neutro se descarta."""
    malo = dist["s0"] * 2 + dist["s1"] * 1
    bueno = dist["s4"] * 2 + dist["s3"] * 1
    total = malo + bueno
    # Si una reseña es 100% neutra sobre el atributo, no informa: se queda en 0/0.
    seguro = total.replace(0, np.nan)
    return (malo / seguro).fillna(0.0), (bueno / seguro).fillna(0.0)


def matriz(sent: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Construye la matriz de la regresión: una fila por reseña, 2 columnas por atributo.

    Los atributos que una reseña no menciona quedan en 0 en ambas columnas (el "Mv" de Bi).
    """
    d = sent.copy()
    # Fuera los atributos con muy pocas menciones: su coeficiente sería ruido y, al normalizar
    # la importancia, contaminaría el reparto de todos los demás.
    suficientes = d["atributo"].value_counts()
    d = d[d["atributo"].isin(suficientes[suficientes >= MIN_MENCIONES_ATRIBUTO].index)]
    if d.empty:
        return pd.DataFrame(), pd.Series(dtype=float), []
    d["d_low"], d["d_high"] = _pesos(d)
    atributos = sorted(d["atributo"].unique())

    low = d.pivot_table(index="resena_id", columns="atributo", values="d_low", aggfunc="mean")
    high = d.pivot_table(index="resena_id", columns="atributo", values="d_high", aggfunc="mean")
    low = low.reindex(columns=atributos).add_suffix("__low").fillna(0.0)
    high = high.reindex(columns=atributos).add_suffix("__high").fillna(0.0)

    X = pd.concat([low, high], axis=1).sort_index()
    y = (d.drop_duplicates("resena_id").set_index("resena_id")["puntuacion"]
          .reindex(X.index))
    ok = y.notna()
    return X[ok], y[ok], atributos


def calcular(sent: pd.DataFrame) -> list[ResultadoPRCA]:
    """Ejecuta la PRCA y devuelve importancia + Kano por atributo.

    Args:
        sent: salida de `nlp.sentimiento` (resena_id, atributo, s0..s4, puntuacion).
    """
    if sent.empty:
        return []
    X, y, atributos = matriz(sent)
    if X.empty or len(X) < len(X.columns) * MIN_OBS_POR_VARIABLE:
        return []  # muestra insuficiente para una regresión honesta

    import statsmodels.api as sm
    modelo = sm.OLS(y.values, sm.add_constant(X.values)).fit()
    coef = pd.Series(modelo.params[1:], index=X.columns)
    pval = pd.Series(modelo.pvalues[1:], index=X.columns)

    desemp = sent.groupby("atributo")["sentimiento"].mean()
    menc = sent.groupby("atributo").size()

    magnitudes = {a: float(np.hypot(coef[f"{a}__low"], coef[f"{a}__high"])) for a in atributos}
    suma = sum(magnitudes.values()) or 1.0

    salida = []
    for a in atributos:
        bp, br = float(coef[f"{a}__low"]), float(coef[f"{a}__high"])
        denom = abs(br) + abs(bp)
        lam = (abs(br) - abs(bp)) / denom if denom else 0.0
        kano = (KANO_ENTUSIASMO if lam > UMBRAL_KANO
                else KANO_BASICO if lam < -UMBRAL_KANO
                else KANO_DESEMPENO)
        salida.append(ResultadoPRCA(
            atributo=a, beta_penalty=round(bp, 4), beta_reward=round(br, 4),
            p_penalty=round(float(pval[f"{a}__low"]), 4),
            p_reward=round(float(pval[f"{a}__high"]), 4),
            importancia=round(magnitudes[a] / suma, 4),
            lambda_kano=round(lam, 4), kano=kano,
            desempeno=round(float(desemp.get(a, np.nan)), 3),
            menciones=int(menc.get(a, 0)),
        ))
    return sorted(salida, key=lambda r: -r.importancia)


def tabla(sent: pd.DataFrame) -> pd.DataFrame:
    """`calcular()` como DataFrame, listo para el dashboard."""
    r = calcular(sent)
    if not r:
        return pd.DataFrame(columns=["atributo", "importancia", "desempeno", "kano",
                                     "lambda_kano", "beta_penalty", "beta_reward", "menciones"])
    return pd.DataFrame([vars(x) for x in r])




def calcular_y_guardar() -> pd.DataFrame:
    """Precalcula la PRCA del destino y de cada bodega con muestra suficiente, y guarda el CSV.

    Se ejecuta EN LOCAL. El dashboard sólo lee el CSV: así `statsmodels` no entra en
    `requirements.txt` y el servidor sigue ligero (mismo patrón que el resto de fuentes).

        python -m enolytics.analitica.prca
    """
    from enolytics import config
    from enolytics.nlp import sentimiento

    sent = sentimiento.cargar()
    if sent.empty:
        print("No hay sentimiento_atributos.csv. Ejecuta antes: python -m enolytics.nlp.sentimiento")
        return pd.DataFrame()

    filas = []
    t = tabla(sent)
    t.insert(0, "ambito", "Marco de Jerez")
    filas.append(t)
    print(f"Destino: {len(t)} atributos")

    saltadas = 0
    for bodega, g in sent.groupby("bodega"):
        tb = tabla(g)
        if tb.empty:  # muestra insuficiente para una regresión honesta
            saltadas += 1
            continue
        tb.insert(0, "ambito", bodega)
        filas.append(tb)
    print(f"Bodegas con PRCA propia: {len(filas)-1}   ·   sin muestra suficiente: {saltadas}")

    todo = pd.concat(filas, ignore_index=True)
    destino = config.DATOS_PROCESADO / "prca_kano.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    todo.to_csv(destino, index=False)
    print(f"Guardado: {destino}  ({len(todo)} filas)")
    return todo


def cargar() -> pd.DataFrame:
    """Lee el CSV precalculado. Es lo único que hace el dashboard."""
    from enolytics import config
    ruta = config.DATOS_PROCESADO / "prca_kano.csv"
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


def diagnostico(sent: pd.DataFrame) -> dict:
    """Salud del modelo. Existe para NO ocultar la objeción de Bi et al. (2019)."""
    X, y, _ = matriz(sent)
    if X.empty or len(X) < len(X.columns) * MIN_OBS_POR_VARIABLE:
        return {"suficiente": False, "n": int(len(X)), "variables": int(len(X.columns))}
    import statsmodels.api as sm
    m = sm.OLS(y.values, sm.add_constant(X.values)).fit()
    return {
        "suficiente": True,
        "n": int(len(X)),
        "variables": int(len(X.columns)),
        "obs_por_variable": round(len(X) / len(X.columns), 1),
        "r2": round(float(m.rsquared), 4),
        "r2_ajustado": round(float(m.rsquared_adj), 4),
        "f_pvalor": float(m.f_pvalue),
        "asimetria_nota": round(float(pd.Series(y).skew()), 3),  # la "J" de Bi
        "multicolinealidad_max": round(float(X.corr().where(
            ~np.eye(len(X.columns), dtype=bool)).abs().max().max()), 3),
    }
if __name__ == "__main__":
    calcular_y_guardar()
