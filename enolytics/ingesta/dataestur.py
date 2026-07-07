"""Ingesta de datos oficiales de turismo desde la API de Dataestur (SEGITTUR).

API pública y GRATUITA (sin clave) del site nacional de datos de turismo. Reúne
fuentes oficiales (INE, AEAT, Seguridad Social, Banco de España, SEPE…) en 124
conjuntos de datos: gasto turístico, empleo, empresas, precios, ocupación,
satisfacción del visitante, etc. Filtrable por año/mes y territorio (CCAA/provincia).

Doc/Swagger: https://www.dataestur.es/apidata/
Spec OpenAPI: https://www.dataestur.es/app/themes/mini-mandrake/apidata/openapi.json

Uso:
    from enolytics.ingesta import dataestur
    df = dataestur.consultar("GASTO_TPV_DESTINO_PROV_MES_HISTORICO_DL", provincia="Cádiz")
"""
from __future__ import annotations

import io

import pandas as pd
import requests

from enolytics import config

BASE_URL = "https://www.dataestur.es/API-SEGITTUR-v2"

# Conjuntos de datos más relevantes para ENOLYTICS (endpoint -> descripción)
CONJUNTOS_RELEVANTES = {
    "GASTO_TPV_DESTINO_PROV_MES_HISTORICO_DL": "Gasto y transacciones con tarjeta por provincia destino",
    "AFILIACION_TURISMO_DL": "Empleo turístico (afiliación a la Seguridad Social)",
    "DIRCE_EMPRESAS_TURISMO_DL": "Nº de empresas turísticas (DIRCE)",
    "IND_SATISFACCION_PERCEPCION_DL": "Satisfacción y percepción del visitante",
    "EGATUR_DL": "Gasto de visitantes internacionales",
    "FRONTUR_DL": "Llegadas de turistas internacionales",
    "TURISMO_RECEPTOR_PROV_PAIS_DL": "Procedencia de turistas extranjeros por provincia",
    "IPC_CCAA_DL": "Índice de precios de turismo y hostelería por CCAA",
    "MUSEO_DL": "Museos y colecciones museográficas",
}


def consultar(endpoint: str, provincia: str | None = None,
              desde_anio: int | None = None, hasta_anio: int | None = None,
              **extra) -> pd.DataFrame:
    """Consulta un endpoint de Dataestur y devuelve un DataFrame.

    Args:
        endpoint: nombre del conjunto (p. ej. 'GASTO_TPV_DESTINO_PROV_MES_HISTORICO_DL').
        provincia: filtro de provincia destino (se aplica en cliente por robustez).
        desde_anio / hasta_anio: rango de años.
        extra: otros parámetros de query admitidos por el endpoint.
    """
    params: dict = {}
    if desde_anio is not None:
        params["desde (año)"] = desde_anio
    if hasta_anio is not None:
        params["hasta (año)"] = hasta_anio
    params.update(extra)

    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()

    # El API devuelve CSV con separador ';'. La codificación suele ser latin-1/cp1252.
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(io.BytesIO(r.content), sep=";", encoding=enc, decimal=",")
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    else:
        raise ValueError(f"No se pudo decodificar la respuesta de {endpoint}")

    df.columns = [c.strip() for c in df.columns]

    # Filtro por provincia en cliente (el nombre de columna varía por endpoint)
    if provincia:
        col_prov = next((c for c in df.columns if "PROVINCIA" in c.upper()), None)
        if col_prov:
            df = df[df[col_prov].astype(str).str.strip().str.lower() == provincia.lower()]
    return df.reset_index(drop=True)


def guardar(endpoint: str, df: pd.DataFrame) -> None:
    """Guarda un conjunto descargado en datos/procesado/dataestur/."""
    destino = config.DATOS_PROCESADO / "dataestur"
    destino.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino / f"{endpoint}.csv", index=False)
