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

# --- Fuente: Google Trends (Inteligencia de Mercado) ---
# Interés de búsqueda del enoturismo de Jerez frente a sus rutas competidoras.
# Los términos se comparan entre sí (Google los normaliza 0-100), así que deben
# compartir la misma intención de búsqueda para que la comparación sea justa.
GOOGLE_TRENDS_GEO = "ES"                # España
GOOGLE_TRENDS_PERIODO = "today 5-y"     # últimos 5 años
# El primero es el foco (Jerez); el resto, competidores del modelo (memoria).
# "bodegas <zona>" funciona como proxy de intención de visita (enoturismo) y tiene
# mucho más volumen de búsqueda que "enoturismo <zona>", que salía casi a cero.
TERMINOS_TRENDS = [
    "bodegas Jerez",
    "bodegas Rioja",
    "bodegas Ribera del Duero",
    "bodegas Rías Baixas",
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

# Objetivo de cada inteligencia, según la Memoria Científico-Técnica (p. 5), y su
# categoría en el marco de indicadores de SEGITTUR (Tabla 1). Se muestran en el
# dashboard para que cada pestaña declare qué persigue y de dónde bebe.
OBJETIVOS_INTELIGENCIAS = {
    "economica": {
        "titulo": "Inteligencia Económica",
        "segittur": "Sostenibilidad",
        "objetivo": (
            "Evalúa el impacto económico del enoturismo en el territorio, la rentabilidad "
            "del sector y su contribución al empleo y desarrollo local."
        ),
        "indicadores": ["Impacto económico del enoturismo",
                        "Contribución al empleo y desarrollo local",
                        "Rentabilidad del sector enoturístico"],
    },
    "mercado": {
        "titulo": "Inteligencia de Mercado",
        "segittur": "Demanda",
        "objetivo": (
            "Analiza tendencias del turismo del vino, patrones de búsqueda en plataformas "
            "digitales y la predisposición de los turistas al gasto en experiencias enoturísticas."
        ),
        "indicadores": ["Patrones de búsquedas online y redes sociales",
                        "Tendencias emergentes en el turismo del vino",
                        "Comparación de la demanda con otros destinos",
                        "Predisposición al gasto en enoturismo"],
    },
    "competidores": {
        "titulo": "Inteligencia de Competidores",
        "segittur": "Oferta / Demanda / Sostenibilidad",
        "objetivo": (
            "Compara la oferta del Marco de Jerez con otros destinos enoturísticos, "
            "identificando estrategias diferenciadoras y posicionamiento relativo en el mercado."
        ),
        "indicadores": ["Comparación de la oferta con otros destinos",
                        "Estrategias diferenciadoras de otras regiones",
                        "Reputación online del destino",
                        "Comparación de precios con otros destinos"],
    },
    "clientes": {
        "titulo": "Inteligencia de Clientes",
        "segittur": "Demanda",
        "objetivo": (
            "Examina el perfil y comportamiento de los visitantes, sus motivaciones, "
            "niveles de satisfacción y fidelización."
        ),
        "indicadores": ["Perfil y comportamiento de los visitantes",
                        "Motivaciones de visita y fidelización",
                        "Canales de planificación y reserva",
                        "Volumen de visitas a bodegas y museos",
                        "Nivel de satisfacción y percepción"],
    },
    "negocios": {
        "titulo": "Inteligencia de Negocios",
        "segittur": "Oferta / Sostenibilidad",
        "objetivo": (
            "Mide la capacidad del sector enoturístico en términos de infraestructura, "
            "servicios, formación del personal y estrategias de innovación."
        ),
        "indicadores": ["Nº de bodegas abiertas al turismo",
                        "Nº de museos y centros de interpretación",
                        "Nº de enotecas, agencias y empresas de servicios",
                        "Nº de eventos enoturísticos organizados",
                        "Nº de empleados y nivel de formación del personal",
                        "Estrategias de innovación en bodegas"],
    },
    "tecnologica": {
        "titulo": "Inteligencia Tecnológica",
        "segittur": "Oferta / Sostenibilidad",
        "objetivo": (
            "Evalúa la implementación de tecnologías en la experiencia enoturística y la "
            "accesibilidad del destino, incluyendo la adopción de herramientas digitales "
            "para mejorar la interacción con los visitantes."
        ),
        "indicadores": ["Adopción de tecnologías (realidad aumentada, visitas virtuales, "
                        "reservas digitales)",
                        "Grado de accesibilidad universal en instalaciones y servicios",
                        "Índice de accesibilidad digital en sitios web"],
    },
    "sostenibilidad": {
        "titulo": "Inteligencia en Sostenibilidad",
        "segittur": "Sostenibilidad",
        "objetivo": (
            "Evalúa el impacto ambiental, social y económico del enoturismo, con especial "
            "atención a la eficiencia en el uso de recursos y la adopción de estrategias de "
            "economía circular."
        ),
        "indicadores": ["Impacto ambiental (consumo de agua, energía, huella de carbono)",
                        "Certificaciones ambientales",
                        "Prácticas de economía circular",
                        "Uso de medios de transporte sostenibles"],
    },
}

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
    for d in (DATOS_CATALOGO, DATOS_CRUDO_RESENAS, DATOS_PROCESADO,
              DATOS_PROCESADO / "google_trends"):
        d.mkdir(parents=True, exist_ok=True)
