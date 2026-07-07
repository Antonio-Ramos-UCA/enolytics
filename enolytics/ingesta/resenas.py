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

Estado: ESQUELETO. Falta implementar el backend de Outscraper (requiere
OUTSCRAPER_API_KEY en el entorno). Por ahora las funciones lanzan
NotImplementedError para dejar clara la frontera de lo pendiente.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional

from enolytics import config


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


def _descargar_google(bodega, desde=None, incremental=True) -> list[Resena]:
    if not config.hay_clave_resenas():
        raise NotImplementedError(
            "Falta credencial del proveedor de reseñas. Configura OUTSCRAPER_API_KEY "
            "en el entorno (ver README) para activar la descarga de Google Reviews."
        )
    raise NotImplementedError(
        f"Backend de Google Reviews vía '{config.PROVEEDOR_RESENAS}' pendiente de implementar."
    )


def _descargar_tripadvisor(bodega, desde=None, incremental=True) -> list[Resena]:
    if not config.hay_clave_resenas():
        raise NotImplementedError(
            "Falta credencial del proveedor de reseñas. Configura la API key en el entorno."
        )
    raise NotImplementedError(
        f"Backend de TripAdvisor vía '{config.PROVEEDOR_RESENAS}' pendiente de implementar."
    )
