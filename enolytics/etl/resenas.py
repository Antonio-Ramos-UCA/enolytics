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
    """Normaliza un export y REEMPLAZA el corpus con él.

    Es la carga inicial, la que se hizo una vez con el export completo de las 41 bodegas.
    Para una descarga posterior, que trae solo lo nuevo, usa `fusionar_export`: esta
    función sobrescribe `resenas.csv` y perdería todo lo anterior.
    """
    config.asegurar_directorios()
    resenas = normalizar_export_outscraper(ruta_xlsx)
    censo = censo_desde_resenas(resenas)
    resenas.to_csv(config.DATOS_PROCESADO / "resenas.csv", index=False)
    censo.to_csv(config.DATOS_PROCESADO / "censo_google.csv", index=False)
    return resenas, censo


def fusionar_export(ruta_xlsx: str | Path, verbose: bool = True) -> dict:
    """Añade al corpus las reseñas de un export que no estuvieran ya, y reescribe el CSV.

    Es la vía de actualización: el panel de Outscraper no sabe «dame lo posterior al 6 de
    julio», así que una descarga nueva trae también reseñas que ya tenemos. La
    deduplicación va por `resena_id`, que es el identificador de Google, estable entre
    descargas.

    Ante un duplicado gana la fila que YA estaba, no la recién descargada. El motivo es que
    las filas antiguas llevan anotado el idioma y el segmento, y volver a detectarlos
    costaría una pasada de langdetect que además no es determinista: una reseña corta puede
    cambiar de idioma entre dos ejecuciones. Lo único que se refresca de las filas viejas es
    `respuesta_propietario`, porque la bodega puede haber contestado después, y la nota y el
    total de reseñas de la bodega, que son del establecimiento y no de la reseña.

    Devuelve un resumen con lo que ha entrado, para poder decidir si merece la pena seguir
    con el resto de la cadena.
    """
    config.asegurar_directorios()
    ruta = config.DATOS_PROCESADO / "resenas.csv"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Para la carga inicial usa procesar_y_guardar()."
        )

    viejas = pd.read_csv(ruta)
    viejas["fecha"] = pd.to_datetime(viejas["fecha"], errors="coerce", utc=True)
    nuevas = normalizar_export_outscraper(ruta_xlsx)

    conocidas = set(viejas["resena_id"].astype(str))
    entran = nuevas[~nuevas["resena_id"].astype(str).isin(conocidas)].copy()

    # Campos del establecimiento o de la conversación que sí conviene refrescar.
    refrescables = [c for c in ("respuesta_propietario", "rating_bodega",
                                "total_resenas_bodega") if c in nuevas.columns]
    refrescadas = 0
    if refrescables:
        idx = nuevas.drop_duplicates("resena_id").set_index(nuevas["resena_id"]
                                                            .drop_duplicates().astype(str))
        clave = viejas["resena_id"].astype(str)
        for col in refrescables:
            trae = clave.map(idx[col])
            if col == "respuesta_propietario":
                # solo rellenar: una respuesta que teníamos no se borra porque el export
                # nuevo venga sin ella
                hueco = viejas[col].isna() & trae.notna()
                refrescadas += int(hueco.sum())
                viejas.loc[hueco, col] = trae[hueco]
            else:
                viejas.loc[trae.notna(), col] = trae[trae.notna()]

    corpus = pd.concat([viejas, entran], ignore_index=True)
    corpus = corpus.sort_values("fecha", na_position="first").reset_index(drop=True)

    censo = censo_desde_resenas(corpus)
    corpus.to_csv(ruta, index=False)
    censo.to_csv(config.DATOS_PROCESADO / "censo_google.csv", index=False)

    resumen = {
        "en_el_export": len(nuevas),
        "ya_estaban": len(nuevas) - len(entran),
        "nuevas": len(entran),
        "respuestas_nuevas": refrescadas,
        "corpus_antes": len(viejas),
        "corpus_despues": len(corpus),
        "fecha_mas_reciente": (corpus["fecha"].max().date().isoformat()
                               if corpus["fecha"].notna().any() else None),
        "bodegas_afectadas": sorted(entran["bodega"].dropna().unique().tolist()),
    }
    if verbose:
        print(f"Export: {resumen['en_el_export']} reseñas · "
              f"{resumen['ya_estaban']} ya estaban · {resumen['nuevas']} nuevas")
        if refrescadas:
            print(f"  + {refrescadas} respuestas del propietario que antes no teníamos")
        print(f"Corpus: {resumen['corpus_antes']} → {resumen['corpus_despues']} "
              f"(hasta {resumen['fecha_mas_reciente']})")
        if resumen["bodegas_afectadas"]:
            print(f"Bodegas con reseñas nuevas: {len(resumen['bodegas_afectadas'])}")
    return resumen


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
