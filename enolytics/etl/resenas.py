"""ETL de reseñas: normaliza las descargas (Outscraper u otras) a un formato común.

Convierte el export crudo de Outscraper (Google Maps Reviews, 32 columnas) en:
  - un dataset de reseñas individuales limpio (una fila = una reseña).
  - un censo por bodega (nota, nº total de reseñas, place_id).

Ambos se vinculan con el catálogo de bodegas a través de la consulta lanzada
("Nombre, Localidad, España"), de modo que cada reseña queda asociada a la bodega
de nuestro catálogo aunque Google use otro nombre.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from enolytics import config

# Columnas del export de Outscraper que nos interesan y su nombre normalizado
_MAPA_COLUMNAS = {
    "query": "consulta",
    "name": "nombre_google",
    "place_id": "place_id",
    "rating": "rating_bodega",
    "reviews": "total_resenas_bodega",
    "review_id": "resena_id",
    "author_title": "autor",
    "review_rating": "puntuacion",
    "review_text": "texto",
    "review_datetime_utc": "fecha",
    "review_likes": "likes",
    "owner_answer": "respuesta_propietario",
    "review_link": "enlace_resena",
}


def _cargar_mapa_placeid() -> dict[str, str]:
    """Mapa place_id -> nombre de bodega del catálogo (si existe el fichero)."""
    ruta = config.DATOS_PROCESADO / "mapa_placeid_bodega.csv"
    if not ruta.exists():
        return {}
    m = pd.read_csv(ruta)
    return dict(zip(m["place_id"], m["bodega"]))


def _bodega_desde_consulta(consulta: str) -> str:
    """De 'Nombre, Localidad, España' recupera el nombre de bodega del catálogo."""
    if not isinstance(consulta, str):
        return ""
    return consulta.rsplit(", ", 2)[0].strip()


def normalizar_export_outscraper(ruta_xlsx: str | Path) -> pd.DataFrame:
    """Lee un export de Outscraper y devuelve las reseñas normalizadas.

    Vincula cada reseña con la bodega del catálogo: si la consulta fue un place_id,
    se usa el mapa place_id->bodega; si fue "Nombre, Localidad, España", se parsea.
    """
    df = pd.read_excel(ruta_xlsx)
    cols = {k: v for k, v in _MAPA_COLUMNAS.items() if k in df.columns}
    out = df[list(cols)].rename(columns=cols)

    mapa_pid = _cargar_mapa_placeid()

    def _bodega(row):
        # 1) por place_id (descargas del corpus por place_id)
        if row.get("place_id") in mapa_pid:
            return mapa_pid[row["place_id"]]
        # 2) por texto de consulta "Nombre, Localidad, España"
        return _bodega_desde_consulta(row.get("consulta"))

    out["bodega"] = out.apply(_bodega, axis=1)
    out["fuente"] = "google"
    # tipos
    out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce", utc=True)
    for c in ("puntuacion", "rating_bodega", "total_resenas_bodega", "likes"):
        if c in out:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    # solo filas que son reseña real (tienen id de reseña)
    out = out[out["resena_id"].notna()].reset_index(drop=True)
    return out


def censo_desde_resenas(resenas: pd.DataFrame) -> pd.DataFrame:
    """Resumen por bodega: nota, nº total de reseñas y muestra descargada."""
    cen = (resenas.groupby("bodega")
           .agg(nombre_google=("nombre_google", "first"),
                place_id=("place_id", "first"),
                rating=("rating_bodega", "first"),
                total_resenas=("total_resenas_bodega", "first"),
                muestra_descargada=("resena_id", "count"))
           .reset_index()
           .sort_values("total_resenas", ascending=False))
    return cen


def procesar_y_guardar(ruta_xlsx: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normaliza un export, guarda reseñas y censo en datos/procesado/ y los devuelve."""
    config.asegurar_directorios()
    resenas = normalizar_export_outscraper(ruta_xlsx)
    censo = censo_desde_resenas(resenas)
    resenas.to_csv(config.DATOS_PROCESADO / "resenas.csv", index=False)
    censo.to_csv(config.DATOS_PROCESADO / "censo_google.csv", index=False)
    return resenas, censo


def cargar_resenas() -> pd.DataFrame:
    """Lee el dataset de reseñas ya normalizado (si existe)."""
    ruta = config.DATOS_PROCESADO / "resenas.csv"
    if not ruta.exists():
        return pd.DataFrame()
    return pd.read_csv(ruta, parse_dates=["fecha"])


def cargar_censo() -> pd.DataFrame:
    ruta = config.DATOS_PROCESADO / "censo_google.csv"
    if not ruta.exists():
        return pd.DataFrame()
    return pd.read_csv(ruta)
