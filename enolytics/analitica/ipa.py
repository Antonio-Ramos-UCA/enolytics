"""Análisis de Importancia-Desempeño y extensiones: IPA / IPCA / DIPA / DIPCA.

Núcleo analítico diferenciador de ENOLYTICS (ver memoria científico-técnica).

  - IPA   Importancia-Desempeño clásico. 4 cuadrantes:
            (1) Concéntrese aquí   -> alta importancia, bajo desempeño
            (2) Siga así           -> alta importancia, alto desempeño
            (3) Baja prioridad     -> baja importancia, bajo desempeño
            (4) Posible exceso     -> baja importancia, alto desempeño
  - IPCA  IPA competitivo: añade comparación frente a competidores (brecha).
  - DIPA  IPA dinámico: evolución temporal de importancia/desempeño.
  - DIPCA IPA dinámico + competitivo.

Estado: ESQUELETO con la firma de las funciones y la lógica de cuadrantes del IPA
básico ya esbozada. Se completará cuando tengamos atributos con medidas de
importancia y desempeño (salida del módulo NLP sobre reseñas).
"""
from __future__ import annotations

from dataclasses import dataclass


CUADRANTES = {
    1: "Concéntrese aquí",
    2: "Siga con el buen trabajo",
    3: "Baja prioridad",
    4: "Posible exceso",
}


@dataclass
class PuntoIPA:
    atributo: str
    importancia: float
    desempeno: float
    cuadrante: int = 0
    etiqueta: str = ""


def clasificar_cuadrante(importancia: float, desempeno: float,
                         umbral_imp: float, umbral_des: float) -> int:
    """Asigna el cuadrante IPA (1-4) según los umbrales (p. ej. las medias)."""
    alta_imp = importancia >= umbral_imp
    alto_des = desempeno >= umbral_des
    if alta_imp and not alto_des:
        return 1  # Concéntrese aquí
    if alta_imp and alto_des:
        return 2  # Siga así
    if not alta_imp and not alto_des:
        return 3  # Baja prioridad
    return 4      # Posible exceso


def calcular_ipa(atributos: list[dict],
                 umbral_imp: float | None = None,
                 umbral_des: float | None = None) -> list[PuntoIPA]:
    """IPA básico.

    Args:
        atributos: lista de dicts {atributo, importancia, desempeno}.
        umbral_imp / umbral_des: umbrales de los ejes; por defecto, las medias.
    """
    if not atributos:
        return []
    imps = [a["importancia"] for a in atributos]
    dess = [a["desempeno"] for a in atributos]
    ui = umbral_imp if umbral_imp is not None else sum(imps) / len(imps)
    ud = umbral_des if umbral_des is not None else sum(dess) / len(dess)
    puntos = []
    for a in atributos:
        c = clasificar_cuadrante(a["importancia"], a["desempeno"], ui, ud)
        puntos.append(PuntoIPA(a["atributo"], a["importancia"], a["desempeno"], c, CUADRANTES[c]))
    return puntos


# --- IPCA: análisis competitivo de importancia-desempeño (Albayrak, 2015) ---
CUADRANTES_IPCA = {
    1: "Actuar: por detrás del Marco",   # alta importancia, brecha negativa
    2: "Fortaleza competitiva",          # alta importancia, brecha positiva
    3: "Ventaja menor",                  # baja importancia, brecha positiva
    4: "Debilidad menor",                # baja importancia, brecha negativa
    5: "En línea con el Marco",          # brecha dentro de la banda de indiferencia
}

# Banda de indiferencia de la brecha, en estrellas. Sin ella, `brecha >= 0` convertía el
# ruido en diagnóstico: en Barbadillo, "Vino y cata" con brecha −0,004 salía como "Actuar:
# por detrás del Marco" y "Instalaciones" con +0,001 como "Fortaleza competitiva" —
# etiquetas opuestas para diferencias inexistentes.
# El valor sale de la distribución real de las 162 brechas bodega-atributo del Marco:
# percentil 25 = 0,093 y mediana = 0,202. Con ±0,10 se declara "sin diferencia" el 26,5%
# de los casos (el cuartil inferior, donde vive el ruido) y se mantiene lo que sí separa.
BANDA_INDIFERENCIA = 0.10


@dataclass
class PuntoIPCA:
    atributo: str
    importancia: float
    desempeno_focal: float
    desempeno_competencia: float
    brecha: float
    cuadrante: int = 0
    etiqueta: str = ""


def clasificar_cuadrante_ipca(importancia: float, brecha: float, umbral_imp: float,
                              banda: float = BANDA_INDIFERENCIA) -> int:
    """Cuadrante IPCA según importancia y brecha (focal - competencia).

    Las brechas dentro de ±`banda` se declaran "En línea con el Marco": son diferencias
    demasiado pequeñas para sostener un diagnóstico (ver BANDA_INDIFERENCIA).
    """
    if abs(brecha) < banda:
        return 5  # En línea con el Marco: la diferencia no es interpretable
    alta = importancia >= umbral_imp
    ventaja = brecha > 0
    if alta and not ventaja:
        return 1  # Actuar: importante y por detrás
    if alta and ventaja:
        return 2  # Fortaleza competitiva
    if not alta and ventaja:
        return 3  # Ventaja menor
    return 4      # Debilidad menor


def calcular_ipca(atributos_focal: list[dict],
                  desempeno_competencia: dict[str, float],
                  umbral_imp: float | None = None,
                  banda: float = BANDA_INDIFERENCIA) -> list[PuntoIPCA]:
    """IPA competitivo: compara el desempeño de una bodega con el de la competencia.

    Args:
        atributos_focal: lista de dicts {atributo, importancia, desempeno} de la bodega.
        desempeno_competencia: {atributo: desempeño medio} del resto del Marco.
        umbral_imp: umbral del eje de importancia (por defecto, la media).
        banda: brechas dentro de ±banda se declaran "En línea con el Marco".
    """
    if not atributos_focal:
        return []
    imps = [a["importancia"] for a in atributos_focal]
    ui = umbral_imp if umbral_imp is not None else sum(imps) / len(imps)
    puntos = []
    for a in atributos_focal:
        comp = desempeno_competencia.get(a["atributo"])
        if comp is None:
            continue
        brecha = round(a["desempeno"] - comp, 3)
        c = clasificar_cuadrante_ipca(a["importancia"], brecha, ui, banda)
        puntos.append(PuntoIPCA(a["atributo"], a["importancia"], a["desempeno"],
                                round(comp, 3), brecha, c, CUADRANTES_IPCA[c]))
    return puntos


def calcular_dipa(desempeno_inicial: dict[str, float],
                  desempeno_final: dict[str, float],
                  umbral_cambio: float = 0.1) -> list[dict]:
    """IPA dinámico: cambio de desempeño de cada atributo entre dos periodos.

    Args:
        desempeno_inicial / desempeno_final: {atributo: desempeño} en cada periodo.
        umbral_cambio: variación mínima para considerar mejora/empeoramiento (si no, estable).

    Devuelve, por atributo, el desempeño inicial y final, la variación y una etiqueta
    (Mejora / Empeora / Estable).
    """
    filas = []
    for atributo in desempeno_final:
        if atributo not in desempeno_inicial:
            continue
        ini, fin = desempeno_inicial[atributo], desempeno_final[atributo]
        delta = round(fin - ini, 3)
        if delta >= umbral_cambio:
            tendencia = "Mejora"
        elif delta <= -umbral_cambio:
            tendencia = "Empeora"
        else:
            tendencia = "Estable"
        filas.append({
            "atributo": atributo, "desempeno_inicial": round(ini, 3),
            "desempeno_final": round(fin, 3), "variacion": delta, "tendencia": tendencia,
        })
    return sorted(filas, key=lambda x: x["variacion"])


def calcular_dipca(brecha_inicial: dict[str, float],
                   brecha_final: dict[str, float],
                   umbral_cambio: float = 0.1) -> list[dict]:
    """DIPCA: evolución de la brecha competitiva de una bodega en el tiempo.

    Combina IPCA (brecha frente a la competencia) y DIPA (evolución temporal): mira
    cómo cambia la brecha de cada atributo entre dos periodos.

    Args:
        brecha_inicial / brecha_final: {atributo: brecha (focal - competencia)} en cada periodo.
        umbral_cambio: variación mínima de la brecha para considerar que gana/pierde terreno.

    Devuelve, por atributo, la brecha en cada periodo, su cambio y una etiqueta
    (Gana terreno / Pierde terreno / Estable).
    """
    filas = []
    for atributo in brecha_final:
        if atributo not in brecha_inicial:
            continue
        bi, bf = brecha_inicial[atributo], brecha_final[atributo]
        cambio = round(bf - bi, 3)
        if cambio >= umbral_cambio:
            etiqueta = "Gana terreno"
        elif cambio <= -umbral_cambio:
            etiqueta = "Pierde terreno"
        else:
            etiqueta = "Estable"
        filas.append({
            "atributo": atributo, "brecha_inicial": round(bi, 3),
            "brecha_final": round(bf, 3), "cambio_brecha": cambio, "tendencia": etiqueta,
        })
    return sorted(filas, key=lambda x: x["cambio_brecha"])
