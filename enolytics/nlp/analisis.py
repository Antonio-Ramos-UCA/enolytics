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

⚠️ ESTADO: PRUEBA DE CONCEPTO, NO MÉTRICA DEFINITIVA. El sentimiento se deriva de las
estrellas, que son de la VISITA ENTERA y no del atributo → el desempeño está comprimido
en torno a la nota global y no mide lo que su nombre sugiere. La cautela completa, con las
pruebas medidas en nuestro corpus, está en el docstring de `tabla_importancia_desempeno()`.
Léela antes de citar estos números fuera del prototipo.

El arreglo (sentimiento por atributo con BERT + importancia por regresión penalty–reward,
que además habilita el modelo Kano) es la PRIORIDAD 1 del proyecto: ver docs/pendientes.md.
La forma del pipeline no cambia; cambia cómo se calculan los dos números.
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
        # OJO: "cara" suelta NO se usa (es polisémica, como lo era "tiempo"): en español es
        # "costosa" pero también "rostro" ("se les ilumina la cara") y el modismo "de cara al
        # público". Disparaba 11 falsos positivos de 29. Se sustituye por locuciones, que además
        # rescatan el portugués ("mais/embora cara"), idioma que no está en el léxico. Se pierde
        # 1 acierto ("se hace corta o cara"), asumible. "caro" en masculino NO es ambigua.
        "precio", "precios", "caro", "barato", "barata", "valor", "dinero",
        "coste", "economico", "vale la pena", "merece la pena",
        "muy cara", "mas cara", "mais cara", "un poco cara", "algo cara", "pelin cara",
        "demasiado cara", "bastante cara", "aunque cara", "embora cara", "es cara",
        "tienda cara", "comida cara", "entrada cara", "visita cara", "cara para",
        "resulta cara", "parece cara",
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
    "Gastronomía y restauración": [
        # Añadido tras un LDA exploratorio (18/07): la comida emergía como tema propio en el
        # 11% de las reseñas —más que Precio, Organización o Entorno— y no estaba cubierta. En
        # el enoturismo del Marco el "vino + tapeo/restaurante" es central. Validado el léxico
        # (751 reseñas, 11%) y descartada "menu" por polisémica ("four-glass set menu" es de
        # vinos, no de comida; menús de hotel).
        # ES
        "comida", "comidas", "restaurante", "restaurantes", "tapa", "tapas", "tapeo",
        "almuerzo", "almorzar", "cena", "cenar", "gastronomia", "gastronomico", "gastronomica",
        "plato", "platos", "cocina", "raciones", "aperitivo", "picoteo", "comer",
        # EN
        "food", "restaurant", "lunch", "dinner", "dining", "meal", "meals", "dish", "dishes",
        "cuisine", "snack",
        # DE
        "essen", "mittagessen", "abendessen", "gericht", "kueche",
        # IT
        "cibo", "ristorante", "pranzo", "cucina", "piatto", "piatti", "mangiare",
        # FR
        "nourriture", "dejeuner", "diner", "plat", "plats", "repas", "manger",
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


COLUMNAS_IMP_DES = ["atributo", "importancia", "desempeno", "menciones"]

# Mínimo de reseñas para que un atributo tenga una media publicable. Por debajo, el
# desempeño es ruido: en Barbadillo, "Entorno y viñedo" salía 5,000★ con 6 reseñas — una
# sola de 3★ lo habría dejado en 4,71. Se alinea con `evolucion_atributos` (8), que ya
# filtraba, mientras que esta función no filtraba nada.
MIN_MENCIONES = 8


def tabla_importancia_desempeno(resenas_anotadas: pd.DataFrame,
                                min_menciones: int = MIN_MENCIONES) -> pd.DataFrame:
    """Calcula importancia y desempeño por atributo (base para el IPA).

    IMPORTANCIA = nº de reseñas que mencionan el atributo (derived importance).
    DESEMPEÑO   = puntuación media (estrellas) de esas reseñas.

    Los atributos con menos de `min_menciones` reseñas se DESCARTAN: su media no es
    publicable. A nivel de destino no afecta (el menor tiene 208); a nivel de bodega sí.

    ⚠️ CAUTELA METODOLÓGICA (auditoría 17/07) — LEER ANTES DE CITAR ESTOS NÚMEROS:

    El DESEMPEÑO **no mide el atributo, mide la visita entera**. Las estrellas son de la
    experiencia completa, así que a una reseña que dice "es caro, pero el sitio es especial"
    con 5★ le asignamos desempeño del Precio = 5,0. Medido en nuestro corpus: el 44% de las
    96 reseñas que se quejan explícitamente del precio tienen 4-5★; y los 7 atributos se
    apiñan entre 4,00 y 4,71 en torno a la nota global (4,573), con σ = 0,288 — esa compresión
    es la huella del sesgo. El ORDEN entre atributos probablemente aguante, pero el valor NO
    es "qué tal funciona el atributo": es "la satisfacción global de quien lo mencionó".

    La IMPORTANCIA por frecuencia es una debilidad conceptual (que se hable mucho de algo no
    prueba que determine la satisfacción), aunque es coherente internamente: el DIPA solo usa
    desempeño y el IPCA compara importancia dentro de la misma bodega.

    Ambas se arreglan con sentimiento por atributo (BERT) + regresión penalty–reward (PRCA),
    que además habilita el modelo Kano. Ver docs/pendientes.md → "PRIORIDAD 1" y
    "MODELO KANO + PRCA" (Han et al., 2026, IJCHM, DOI 10.1108/IJCHM-01-2026-0071).
    """
    if resenas_anotadas.empty or "atributos" not in resenas_anotadas.columns:
        return pd.DataFrame(columns=COLUMNAS_IMP_DES)
    con_texto = resenas_anotadas[resenas_anotadas["atributos"].map(len) > 0]
    if con_texto.empty:  # p. ej. Viñedos Bodega El Piraña: 1 reseña, sin texto
        return pd.DataFrame(columns=COLUMNAS_IMP_DES)
    filas = []
    for atributo in ATRIBUTOS:
        mask = con_texto["atributos"].map(lambda a: atributo in a)
        sub = con_texto[mask]
        if len(sub) < max(min_menciones, 1):  # nunca una fila sin reseñas detrás
            continue
        filas.append({
            "atributo": atributo,
            "importancia": len(sub),                         # nº menciones
            "desempeno": round(sub["puntuacion"].mean(), 3),  # nota media
            "menciones": len(sub),
        })
    if not filas:  # ninguna reseña con atributo (p. ej. una bodega sin textos)
        return pd.DataFrame(columns=COLUMNAS_IMP_DES)
    return pd.DataFrame(filas).sort_values("importancia", ascending=False)
