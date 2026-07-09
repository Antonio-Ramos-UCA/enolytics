"""Interés de búsqueda en Google Trends (Inteligencia de Mercado).

Sin encuestar a nadie: mide la demanda/atención hacia el enoturismo de Jerez y la
compara con las rutas del vino competidoras (Rioja, Ribera del Duero, Rías Baixas).
Google normaliza los términos entre sí en una escala 0-100, así que el resultado es
directamente comparativo.

Genera dos salidas en `datos/procesado/google_trends/`:
  - `interes_temporal.csv`   evolución mensual del interés por término (últimos 5 años).
  - `interes_regiones.csv`   interés por comunidad autónoma para el término foco (Jerez).

Se apoya en `pytrends` (API no oficial de Google Trends), que puede limitar las
peticiones (error 429). Por eso hay reintentos con espera creciente. Es una
dependencia de desarrollo (requirements-dev.txt): el dashboard solo lee los CSV.

Uso:
    from enolytics.ingesta import google_trends
    google_trends.descargar_todo()
"""
from __future__ import annotations

import time

import pandas as pd

from enolytics import config


def _cliente(reintentos: int = 4, espera: float = 3.0):
    """Crea el cliente de pytrends, con reintentos si Google limita la conexión."""
    from pytrends.request import TrendReq

    # No se pasan `retries`/`backoff_factor`: pytrends construiría un urllib3.Retry
    # con el argumento `method_whitelist`, eliminado en urllib3>=2. Los reintentos
    # los gestiona este módulo (_construir_payload).
    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            return TrendReq(hl="es-ES", tz=60, timeout=(10, 25))
        except Exception as e:  # pragma: no cover - depende de la red
            ultimo_error = e
            print(f"  · reintento cliente {intento}/{reintentos} tras error: {e}")
            time.sleep(espera * intento)
    raise RuntimeError(f"No se pudo crear el cliente de Google Trends: {ultimo_error}")


def _con_reintentos(fn, descripcion: str, reintentos: int = 6, espera_base: float = 20.0):
    """Ejecuta `fn` reintentando ante el límite de peticiones de Google (429).

    Google Trends limita con dureza; la espera crece con cada intento (20s, 40s...).
    """
    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            return fn()
        except Exception as e:  # pragma: no cover - depende de la red
            ultimo_error = e
            es_429 = "429" in str(e) or "TooManyRequests" in type(e).__name__
            motivo = "límite de Google (429)" if es_429 else str(e)
            if intento < reintentos:
                pausa = espera_base * intento
                print(f"  · {descripcion}: {motivo}; espero {pausa:.0f}s y reintento "
                      f"{intento}/{reintentos}...")
                time.sleep(pausa)
    raise RuntimeError(f"Google Trends rechazó '{descripcion}' tras {reintentos} intentos: "
                       f"{ultimo_error}")


def descargar_interes_temporal(terminos: list[str] | None = None) -> pd.DataFrame:
    """Evolución mensual del interés de búsqueda por término (0-100, comparativo)."""
    terminos = terminos or config.TERMINOS_TRENDS
    py = _cliente()

    def _consulta():
        py.build_payload(terminos, timeframe=config.GOOGLE_TRENDS_PERIODO,
                         geo=config.GOOGLE_TRENDS_GEO)
        return py.interest_over_time()

    df = _con_reintentos(_consulta, "interés temporal")
    if df.empty:
        return df
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])
    df = df.reset_index().rename(columns={"date": "fecha"})
    return df


def descargar_interes_regiones(termino: str | None = None) -> pd.DataFrame:
    """Interés por comunidad autónoma para el término foco (de dónde se busca Jerez)."""
    termino = termino or config.TERMINOS_TRENDS[0]
    py = _cliente()

    def _consulta():
        py.build_payload([termino], timeframe=config.GOOGLE_TRENDS_PERIODO,
                         geo=config.GOOGLE_TRENDS_GEO)
        return py.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=False)

    df = _con_reintentos(_consulta, "interés por regiones")
    if df.empty:
        return df
    df = df.reset_index().rename(columns={"geoName": "comunidad", termino: "interes"})
    df = df.sort_values("interes", ascending=False).reset_index(drop=True)
    return df


def descargar_todo(verbose: bool = True) -> dict[str, pd.DataFrame]:
    """Descarga las dos salidas de Google Trends y las guarda en CSV."""
    config.asegurar_directorios()
    destino = config.DATOS_PROCESADO / "google_trends"
    resultados: dict[str, pd.DataFrame] = {}

    if verbose:
        print(f"Google Trends · términos: {', '.join(config.TERMINOS_TRENDS)}")

    temporal = descargar_interes_temporal()
    if not temporal.empty:
        ruta = destino / "interes_temporal.csv"
        temporal.to_csv(ruta, index=False)
        resultados["temporal"] = temporal
        if verbose:
            medias = temporal.drop(columns=["fecha"]).mean().round(1).to_dict()
            print(f"  ✓ interes_temporal.csv ({len(temporal)} meses) · interés medio: {medias}")

    # Pausa de cortesía entre consultas para no toparse con el límite de Google
    time.sleep(15)

    regiones = descargar_interes_regiones()
    if not regiones.empty:
        ruta = destino / "interes_regiones.csv"
        regiones.to_csv(ruta, index=False)
        resultados["regiones"] = regiones
        if verbose:
            top = regiones.head(5)[["comunidad", "interes"]].to_dict("records")
            print(f"  ✓ interes_regiones.csv ({len(regiones)} CCAA) · top: {top}")

    return resultados


if __name__ == "__main__":
    descargar_todo()
