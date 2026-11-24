"""Ingesta de reseñas online (Google, TripAdvisor, …).

Este módulo define la INTERFAZ COMÚN de descarga de reseñas. La idea es poder
enchufar detrás distintos backends (scraper propio con Playwright, o una API de
terceros tipo Outscraper/Apify) sin cambiar el resto del sistema.

    from enolytics.ingesta import resenas
    nuevas = resenas.descargar_resenas(bodega, fuente="google")

Decisión de arquitectura (enfoque HÍBRIDO):
  - Fuentes estables (catálogo, webs propias)  -> scraper propio.
  - Reseñas de Google / TripAdvisor            -> API de terceros (Outscraper por
    defecto; interfaz agnóstica para poder cambiar a SerpAPI/Apify).

Motivo: la prueba de viabilidad mostró que Google exige navegador y TripAdvisor
bloquea; el scraper propio de Google Maps es frágil y confunde bodegas. La API
devuelve JSON limpio con nota, nº de reseñas y textos, y resuelve bien la identidad
del sitio. Coste cubierto por la partida de 4.000 € del presupuesto.

Estado: Google implementado sobre la API de Outscraper (requiere OUTSCRAPER_API_KEY en el
entorno). TripAdvisor sigue sin backend, a propósito: aparcado hasta que el circuito de
Google lleve meses funcionando.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time, timezone
from typing import Optional

import pandas as pd

from enolytics import config

# Cuántas reseñas pedir como máximo por bodega en una pasada. No es un presupuesto de gasto,
# sino un tope de seguridad: entre las 41 bodegas entran unas 4,5 reseñas al día, de modo que
# ni el mes más movido se acerca a este número. Si alguna vez lo tocara, la pasada avisa.
TOPE_POR_BODEGA = 200


@dataclass
class Resena:
    """Una reseña individual, normalizada e independiente de la fuente."""
    bodega_slug: str
    fuente: str                       # "google" | "tripadvisor" | ...
    id_externo: str                   # id de la reseña en la plataforma (para deduplicar)
    autor: str = ""
    puntuacion: Optional[float] = None
    fecha: Optional[str] = None       # ISO 8601 (YYYY-MM-DD)
    titulo: str = ""
    texto: str = ""
    idioma: str = ""
    idioma_original: str = ""
    metadatos: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def descargar_resenas(
    bodega: dict,
    fuente: str,
    desde: Optional[date] = None,
    incremental: bool = True,
) -> list[Resena]:
    """Descarga reseñas de una bodega desde una fuente concreta.

    Args:
        bodega: registro del catálogo enriquecido (incluye nombre, gps_lat/lon, web…).
        fuente: una de config.FUENTES_RESENAS ("google", "tripadvisor").
        desde: si se indica, solo descarga reseñas posteriores a esa fecha.
        incremental: si True, solo trae lo nuevo respecto a lo ya almacenado.

    Returns:
        Lista de objetos Resena (normalizados).

    Nota: backend pendiente de implementar (scraper propio vs. API de terceros).
    """
    if fuente not in config.FUENTES_RESENAS:
        raise ValueError(f"Fuente no soportada: {fuente!r}. Opciones: {config.FUENTES_RESENAS}")

    if fuente == "google":
        return _descargar_google(bodega, desde=desde, incremental=incremental)
    if fuente == "tripadvisor":
        return _descargar_tripadvisor(bodega, desde=desde, incremental=incremental)
    raise ValueError(fuente)


def _cliente():
    """Devuelve el cliente de Outscraper, con un error legible si falta la clave."""
    if not config.hay_clave_resenas():
        raise RuntimeError(
            "Falta OUTSCRAPER_API_KEY en el entorno. En local, expórtala en la terminal; "
            "en GitHub Actions es un secret del repositorio."
        )
    try:
        from outscraper import OutscraperClient
    except ImportError as e:
        raise RuntimeError(
            "Falta la biblioteca 'outscraper'. Instálala con "
            "pip install -r requirements-automatizacion.txt"
        ) from e
    return OutscraperClient(api_key=config.OUTSCRAPER_API_KEY)


def _marca_de_tiempo(dia: date) -> int:
    """Convierte una fecha en el timestamp UTC que espera el parámetro `cutoff`."""
    return int(datetime.combine(dia, time.min, tzinfo=timezone.utc).timestamp())


def descargar_nuevas(desde: date, place_ids: Optional[list[str]] = None,
                     tope: int = TOPE_POR_BODEGA, verbose: bool = True) -> pd.DataFrame:
    """Trae de Google, vía Outscraper, las reseñas posteriores a `desde`.

    Devuelve un DataFrame con los mismos nombres de campo que el export del panel, de manera
    que `etl.resenas.fusionar_export` lo trata igual que a un XLSX descargado a mano.

    Dos decisiones que conviene no tocar sin pensarlo:

    **No se pasa `language`.** Si se indica, Google puede devolver las reseñas traducidas, y
    el idioma del texto es justamente lo que usamos para separar al visitante nacional del
    internacional. Una traducción silenciosa convertiría todo el corpus en español y haría
    desaparecer el segmento internacional sin que saltara ningún error. El corpus original se
    bajó sin ese parámetro y es multilingüe; se mantiene así.

    **`cutoff` marca la reseña más antigua que queremos**, y al usarlo la API ordena por las
    más recientes. Aun así la fusión deduplica por identificador: el corte se aplica sobre la
    fecha que Google publica, que para una reseña editada puede no ser la que teníamos.
    """
    cliente = _cliente()
    if place_ids is None:
        mapa = pd.read_csv(config.DATOS_PROCESADO / "mapa_placeid_bodega.csv")
        place_ids = mapa["place_id"].dropna().astype(str).tolist()

    corte = _marca_de_tiempo(desde)
    if verbose:
        print(f"Pidiendo a Outscraper las reseñas posteriores al {desde.isoformat()} "
              f"de {len(place_ids)} bodegas (tope {tope} por bodega)…")

    respuesta = cliente.google_maps_reviews(
        place_ids,
        reviews_limit=tope,
        limit=1,              # un lugar por consulta: cada place_id identifica una bodega
        sort="newest",
        cutoff=corte,
    )

    filas, topados = [], []
    for lugar in respuesta or []:
        cabecera = {k: lugar.get(k) for k in
                    ("query", "name", "place_id", "rating", "reviews")}
        criticas = lugar.get("reviews_data") or []
        if len(criticas) >= tope:
            topados.append(lugar.get("name") or lugar.get("place_id"))
        for r in criticas:
            filas.append({**cabecera, **r})

    df = pd.DataFrame(filas)
    if verbose:
        print(f"Recibidas {len(df)} reseñas de {len(respuesta or [])} bodegas.")
        if topados:
            print(f"⚠ {len(topados)} bodegas alcanzaron el tope de {tope}: puede faltar "
                  f"alguna reseña. Revisa {', '.join(topados[:3])}…")
    return df


def _descargar_google(bodega, desde=None, incremental=True) -> list[Resena]:
    """Descarga de una sola bodega, en la interfaz común de objetos Resena.

    La vía que usa la actualización periódica es `descargar_nuevas`, que pide las 41 bodegas
    de una vez y devuelve un DataFrame. Esta función existe para casos sueltos.
    """
    pid = bodega.get("place_id") if isinstance(bodega, dict) else None
    if not pid:
        raise ValueError("La bodega no trae place_id, que es como se identifica en Google.")
    df = descargar_nuevas(desde or date(2000, 1, 1), place_ids=[pid], verbose=False)
    return [
        Resena(
            bodega_slug=bodega.get("slug") or bodega.get("bodega") or "",
            fuente="google",
            id_externo=str(r.get("review_id") or ""),
            autor=r.get("author_title") or "",
            puntuacion=r.get("review_rating"),
            fecha=str(r.get("review_datetime_utc") or "") or None,
            texto=r.get("review_text") or "",
        )
        for _, r in df.iterrows()
    ]


def _descargar_tripadvisor(bodega, desde=None, incremental=True) -> list[Resena]:
    if not config.hay_clave_resenas():
        raise NotImplementedError(
            "Falta credencial del proveedor de reseñas. Configura la API key en el entorno."
        )
    raise NotImplementedError(
        f"Backend de TripAdvisor vía '{config.PROVEEDOR_RESENAS}' pendiente de implementar."
    )
