"""Configuración central de ENOLYTICS.

Rutas del proyecto, constantes de las fuentes de datos y parámetros comunes.
Todo el resto del paquete importa desde aquí para no repetir rutas ni constantes.
"""
from __future__ import annotations

from pathlib import Path

# --- Rutas del proyecto (se resuelven solas, funcionen desde donde funcionen) ---
RAIZ = Path(__file__).resolve().parent.parent          # carpeta "PROTOTIPO ENOLYTICS"
DATOS = RAIZ / "datos"
DATOS_CATALOGO = DATOS / "catalogo"                     # catálogo de bodegas
DATOS_CRUDO = DATOS / "crudo"                           # datos sin procesar (reseñas descargadas)
DATOS_CRUDO_RESENAS = DATOS_CRUDO / "resenas"
DATOS_PROCESADO = DATOS / "procesado"                   # datasets ya limpios/derivados

# Ficheros clave del catálogo
CATALOGO_BASE_CSV = DATOS_CATALOGO / "catalogo_bodegas_rutadelvinojerez.csv"
CATALOGO_CSV = DATOS_CATALOGO / "bodegas_enriquecido.csv"
CATALOGO_JSON = DATOS_CATALOGO / "bodegas_enriquecido.json"

# --- Fuente: Ruta del Vino y Brandy de Jerez ---
RUTA_JEREZ_HOST = "https://rutadelvinojerez.es"
RUTA_JEREZ_CATEGORIA_BASE = "https://rutadelvinojerez.es/empresas-y-servicios/categoria"
RUTA_JEREZ_BASE = f"{RUTA_JEREZ_CATEGORIA_BASE}/bodegas/"  # compatibilidad

# Categorías de la oferta enoturística en la web de la Ruta (para inteligencia de negocios)
CATEGORIAS_RUTA = [
    "bodegas", "alojamientos", "restaurantes", "museos", "enotecas",
    "actividades-y-ocio", "agencias", "caterings",
    "recursos-culturales", "recursos-naturales", "turismo-accesible",
]

# --- Parámetros de scraping (cortesía con los servidores) ---
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
)
PAUSA_ENTRE_PETICIONES = 0.3   # segundos entre requests
TIMEOUT_PETICION = 15          # segundos

# Localidades del Marco de Jerez (para normalización y validación)
LOCALIDADES_MARCO = [
    "Jerez de la Frontera",
    "El Puerto de Santa María",
    "Sanlúcar de Barrameda",
    "Chiclana de la Frontera",
    "Trebujena",
    "Rota",
    "Lebrija",
]

# Las 7 fuentes de inteligencia competitiva del modelo ENOLYTICS
INTELIGENCIAS = [
    "economica",
    "mercado",
    "competidores",
    "clientes",
    "negocios",
    "tecnologica",
    "sostenibilidad",
]

# Fuentes de reseñas previstas (para el módulo de ingesta de reseñas)
FUENTES_RESENAS = ["google", "tripadvisor"]

# --- Descarga de reseñas: enfoque HÍBRIDO ---
# Scraper propio para fuentes estables (catálogo, webs); API de terceros para
# reseñas de Google/TripAdvisor (más fiable y con textos completos).
# Proveedor por defecto: Outscraper. La clave se lee de una variable de entorno
# (nunca se escribe en el código ni se versiona).
import os

PROVEEDOR_RESENAS = os.getenv("ENOLYTICS_PROVEEDOR_RESENAS", "outscraper")
OUTSCRAPER_API_KEY = os.getenv("OUTSCRAPER_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")


def hay_clave_resenas() -> bool:
    """True si hay credencial configurada para el proveedor de reseñas elegido."""
    return bool({
        "outscraper": OUTSCRAPER_API_KEY,
        "serpapi": SERPAPI_API_KEY,
        "apify": APIFY_API_TOKEN,
    }.get(PROVEEDOR_RESENAS, ""))


def asegurar_directorios() -> None:
    """Crea las carpetas de datos si no existen (idempotente)."""
    for d in (DATOS_CATALOGO, DATOS_CRUDO_RESENAS, DATOS_PROCESADO):
        d.mkdir(parents=True, exist_ok=True)
