"""Análisis de reseñas: sentimiento y extracción de atributos (aspect-based).

Prueba de concepto del núcleo analítico de ENOLYTICS. Convierte las reseñas en
medidas de IMPORTANCIA y DESEMPEÑO por atributo, que alimentan los modelos IPA.

Enfoque (aspect-based, alineado con Shin & Nicolau 2022 y Wu et al. 2024):
  1. Se define un léxico de atributos clave del enoturismo (vino, personal, visita,
     instalaciones, precio, entorno, organización).
  2. Por cada reseña se detecta qué atributos menciona.
  3. IMPORTANCIA de un atributo  = frecuencia con que se menciona (derived importance).
     DESEMPEÑO de un atributo     = puntuación media (estrellas) de las reseñas que lo
                                    mencionan.
  4. Esas dos medidas se pasan al módulo IPA para clasificar cada atributo en cuadrantes.

Nota: para la muestra usamos sentimiento por estrellas (fiable e inmediato) y un
léxico en español. Con el corpus completo se sustituirá por sentimiento BERT
multilingüe y extracción de aspectos por modelo. La forma del pipeline es la misma.
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

# Léxico de atributos del enoturismo, MULTILINGÜE.
#
# Motivo: con el léxico solo en español, el 35,8% de las reseñas internacionales no aportaba
# ningún atributo (frente al 5,1% de las hispanohablantes) → el IPA se construía casi solo con la
# voz del visitante hispanohablante. Se añaden EN/DE/IT/FR, que cubren ~90% del visitante
# extranjero del Marco (inglés 905, alemán 290, italiano 180, francés 91 de 1.750 reseñas).
#
# Nota: el texto se normaliza (minúsculas, sin tildes) antes de casar, así que las claves van sin
# acentos. Se evitan palabras demasiado genéricas (p. ej. el inglés "time") que dispararían
# falsos positivos.
ATRIBUTOS: dict[str, list[str]] = {
    "Vino y cata": [
        # ES
        "vino", "vinos", "cata", "catas", "degustacion", "degustaciones", "sabor",
        "fino", "oloroso", "amontillado", "manzanilla", "brandy", "jerez", "copa",
        "maridaje", "probar", "catar",
        # EN
        "wine", "wines", "sherry", "tasting", "tastings", "taste", "flavour", "flavor",
        "glass", "pairing", "sample", "vintage", "palomino",
        # DE
        "wein", "weine", "weinprobe", "verkostung", "geschmack", "glas",
        # IT
        "vini", "degustazione", "degustazioni", "assaggio", "sapore", "bicchiere",
        # FR
        "vin", "vins", "degustation", "gout", "verre",
    ],
    "Personal y trato": [
        # ES
        "personal", "atencion", "trato", "amable", "amabilidad", "guia", "guias",
        "simpatico", "simpatica", "profesional", "cercano", "camarero", "staff",
        "atendieron", "atendio", "acompaño",
        # EN
        "guide", "guides", "service", "friendly", "welcoming", "host", "attentive",
        "professional", "kind", "helpful", "knowledgeable", "hospitality",
        # DE
        "freundlich", "mitarbeiter", "betreuung", "gastfreundlich",
        # IT
        "personale", "guida", "servizio", "gentile", "cordiale", "accoglienza",
        # FR
        "personnel", "accueil", "aimable", "sympathique", "chaleureux",
    ],
    "Visita y experiencia": [
        # ES
        "visita", "visitas", "tour", "recorrido", "experiencia", "guiada", "explicacion",
        "explicaciones", "aprender", "historia", "interesante", "educativa",
        # EN
        "visit", "tours", "experience", "guided", "explanation", "learn", "history",
        "interesting", "informative", "educational",
        # DE
        "besuch", "fuhrung", "erlebnis", "erklarung", "lernen", "geschichte", "interessant",
        # IT
        "esperienza", "spiegazione", "storia", "interessante",
        # FR
        "visite", "experience", "guidee", "explication", "histoire", "interessant",
    ],
    "Instalaciones": [
        # ES
        "bodega", "bodegas", "instalaciones", "edificio", "patio", "museo", "sala",
        "lugar", "sitio", "espacio", "tienda", "bonita", "bonito", "cuidado",
        # EN
        "winery", "wineries", "cellar", "cellars", "facilities", "building", "courtyard",
        "museum", "shop", "venue", "beautiful", "impressive",
        # DE
        "weingut", "keller", "gebaude", "laden",
        # IT
        "cantina", "cantine", "edificio", "museo", "negozio",
        # FR
        "cave", "caves", "domaine", "batiment", "musee", "boutique",
    ],
    "Precio y valor": [
        # ES
        "precio", "precios", "caro", "cara", "barato", "barata", "valor", "dinero",
        "coste", "economico", "vale la pena", "merece la pena",
        # EN
        "price", "prices", "expensive", "cheap", "value", "money", "cost", "worth",
        "affordable", "overpriced", "pricey",
        # DE
        "preis", "preise", "teuer", "gunstig", "wert", "geld", "kosten", "preiswert",
        # IT
        "prezzo", "prezzi", "costoso", "valore", "denaro",
        # FR
        "prix", "cher", "chere", "bon marche", "valeur", "argent",
    ],
    "Entorno y viñedo": [
        # ES
        "viñedo", "viñedos", "viña", "viñas", "paisaje", "entorno", "vistas",
        "campo", "naturaleza",
        # EN
        "vineyard", "vineyards", "landscape", "scenery", "views", "countryside",
        "nature", "surroundings",
        # DE
        "weinberg", "weinberge", "landschaft", "aussicht", "natur", "umgebung",
        # IT
        "vigneto", "vigneti", "vigna", "paesaggio", "panorama", "natura", "campagna",
        # FR
        "vignoble", "vignobles", "vigne", "paysage", "vue", "campagne",
    ],
    "Organización y reserva": [
        # ES
        # OJO: se eliminó la clave suelta "tiempo". Es polisémica en español (el clima, la
        # duración, uso genérico) y generaba ruido: disparaba 118 reseñas, la mayoría sin
        # relación con la reserva ("nada de las típicas turistadas", reseñas de logística de
        # camiones...). Se sustituye por la locución "tiempo de espera", que sí es inequívoca.
        "reserva", "reservar", "organizacion", "puntual", "espera", "tiempo de espera",
        "horario", "idioma", "puntualidad", "cita", "cola",
        # EN
        "booking", "reservation", "reserve", "organisation", "organization", "punctual",
        "waiting", "queue", "schedule", "appointment", "language", "english", "booked",
        # DE
        "reservierung", "buchung", "buchen", "punktlich", "warten", "wartezeit",
        "termin", "sprache",
        # IT
        "prenotazione", "prenotare", "organizzazione", "puntuale", "attesa", "orario",
        "appuntamento", "lingua",
        # FR
        "reservation", "reserver", "ponctuel", "attente", "horaire", "langue",
    ],
}


def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin HTML — para casar palabras del léxico."""
    if not isinstance(texto, str):
        return ""
    texto = re.sub(r"<[^>]+>", " ", texto)                     # quita <br> etc.
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def sentimiento_por_estrellas(puntuacion: float) -> str:
    """Etiqueta de sentimiento a partir de las estrellas (1-5)."""
    if pd.isna(puntuacion):
        return "desconocido"
    if puntuacion >= 4:
        return "positivo"
    if puntuacion <= 2:
        return "negativo"
    return "neutro"


def detectar_atributos(texto: str) -> list[str]:
    """Devuelve la lista de atributos mencionados en una reseña."""
    t = _normalizar(texto)
    if not t:
        return []
    encontrados = []
    for atributo, claves in ATRIBUTOS.items():
        if any(re.search(r"\b" + re.escape(_normalizar(k)) + r"\b", t) for k in claves):
            encontrados.append(atributo)
    return encontrados


def anotar_resenas(resenas: pd.DataFrame) -> pd.DataFrame:
    """Añade a cada reseña su sentimiento y los atributos que menciona."""
    df = resenas.copy()
    df["sentimiento"] = df["puntuacion"].map(sentimiento_por_estrellas)
    df["atributos"] = df["texto"].map(detectar_atributos)
    return df


def evolucion_atributos(resenas_anotadas: pd.DataFrame, freq: str = "Y",
                        min_menciones: int = 8) -> pd.DataFrame:
    """Evolución temporal de importancia y desempeño por atributo (base del DIPA).

    Agrupa las reseñas por periodo (por defecto anual, freq='Y') y atributo. Descarta
    las celdas periodo-atributo con muy pocas menciones para evitar ruido.

    Devuelve columnas: periodo, atributo, menciones, desempeno.
    """
    df = resenas_anotadas.copy()
    df = df[df["fecha"].notna()]
    if df.empty:
        return pd.DataFrame(columns=["periodo", "atributo", "menciones", "desempeno"])
    fechas = pd.to_datetime(df["fecha"]).dt.tz_localize(None)  # quitar zona horaria
    df["periodo"] = fechas.dt.to_period(freq).dt.to_timestamp()
    ex = df.explode("atributos")
    ex = ex[ex["atributos"].notna()]
    g = (ex.groupby(["periodo", "atributos"])
           .agg(menciones=("resena_id", "count"), desempeno=("puntuacion", "mean"))
           .reset_index()
           .rename(columns={"atributos": "atributo"}))
    g = g[g["menciones"] >= min_menciones]
    g["desempeno"] = g["desempeno"].round(3)
    return g.sort_values(["atributo", "periodo"])


def tabla_importancia_desempeno(resenas_anotadas: pd.DataFrame) -> pd.DataFrame:
    """Calcula importancia y desempeño por atributo (base para el IPA).

    IMPORTANCIA = nº de reseñas que mencionan el atributo (derived importance).
    DESEMPEÑO   = puntuación media (estrellas) de esas reseñas.
    """
    con_texto = resenas_anotadas[resenas_anotadas["atributos"].map(len) > 0]
    filas = []
    for atributo in ATRIBUTOS:
        mask = con_texto["atributos"].map(lambda a: atributo in a)
        sub = con_texto[mask]
        if len(sub) == 0:
            continue
        filas.append({
            "atributo": atributo,
            "importancia": len(sub),                         # nº menciones
            "desempeno": round(sub["puntuacion"].mean(), 3),  # nota media
            "menciones": len(sub),
        })
    return pd.DataFrame(filas).sort_values("importancia", ascending=False)
