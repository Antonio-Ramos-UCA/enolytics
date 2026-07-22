"""Extractor de PRECIOS de visitas/experiencias desde la web propia de cada bodega.

HUMANO EN EL BUCLE (a propósito): esto **no publica precios solos**. Recorre la web de la
bodega, localiza sus páginas de *visitas / experiencias / reservas* y saca los importes en €
**junto a la frase donde aparecen**, para que una persona confirme a qué experiencia
corresponde cada precio antes de darlo por bueno. Es la vía más defendible (web propia,
información pública) y la que mejor cobertura da de las bodegas que publican tarifas.

Por qué así y no un scraper "a ciegas":
  · Un precio sin contexto engaña: en el Marco conviven visita simple, visita+cata de N vinos,
    cata premium, con maridaje, privada/grupo, por idioma... Guardar "15 €" a secas es ruido.
  · Se aplica el principio de la casa: **donde no hay precio publicado, se informa** ("consultar
    con la bodega"), no se inventa. El cuestionario a bodegas confirma y completa.

Uso:
    from enolytics.ingesta import precios
    cands = precios.candidatos_bodega("Bodegas Barbadillo", "https://www.barbadillo.com/")
    precios.explorar()          # prueba sobre una muestra e imprime la tasa de acierto

Salida por candidato: {bodega, url, precio_eur, contexto, tipo_probable, metodo}.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from enolytics.ingesta import navegador

# Palabras que delatan una página (o un enlace) de visitas/experiencias/reservas.
PALABRAS_VISITA = [
    "visita", "visitas", "visitanos", "visítanos", "experiencia", "experiencias",
    "enoturismo", "enoturistica", "reserva", "reservar", "reservas", "tour", "tours",
    "cata", "catas", "entradas", "tickets", "book", "booking", "shop", "tienda-visitas",
]

# Para clasificar (orientativo) a qué se refiere un precio, por la palabra más cercana.
TIPOS_CONTEXTO = [
    ("maridaje", "visita con gastronomía/maridaje"),
    ("gastron", "visita con gastronomía/maridaje"),
    ("almuerzo", "visita con gastronomía/maridaje"),
    ("premium", "cata premium"),
    ("privad", "visita privada"),
    ("cata", "visita + cata"),
    ("tast", "visita + cata"),
    ("experiencia", "experiencia"),
    ("tour", "visita guiada"),
    ("visita", "visita"),
]

# Un importe en euros: "15€", "15 €", "15,50€", "€15", "desde 20 euros". El ancla es el
# símbolo/moneda, para no confundir con años, teléfonos o cantidades sueltas.
RE_PRECIO = re.compile(
    r"(?:(\d{1,4}(?:[.,]\d{1,2})?)\s*(?:€|eur\b|euros?\b))"
    r"|(?:(?:€|eur)\s*(\d{1,4}(?:[.,]\d{1,2})?))",
    re.IGNORECASE,
)

# Señales de que un importe es de TIENDA (botella, envío), no de una visita → se descarta.
# OJO: no incluir "añada", que es legítima en catas ("Colección de Añadas", "Fino de Añada").
RUIDO_TIENDA = [
    "envío", "envio", "pedido", "carrito", "comprar", "añadir al", "cesta", "compra",
    "botella", "botellas", "magnum", "caja de", "docena", "0,5 l", "0,75",
    "precio regular", "precio de venta", "precio unitario", "iva incluido", "/ud", "/ ud",
]

# Rango plausible de una visita/experiencia enoturística (€). Fuera de esto, casi seguro ruido.
PRECIO_MIN = 3.0
PRECIO_MAX = 600.0

# Muestra por defecto para el prototipo: bodegas con reserva online (más probable que publiquen).
MUESTRA_DEFECTO = [
    ("Bodegas Barbadillo", "https://www.barbadillo.com/"),
    ("Bodegas Barón", "https://bodegasbaron.es/"),
    ("Bodegas Caydsa", "https://www.caydsa.es/cooperativa-caydsa-visitas/"),
    ("Bodegas Cayetano Del Pino", "https://cayetanodelpino.com/visitas"),
    ("Bodegas Dios Baco", "https://bodegasdiosbaco.com/"),
    ("Bodega Cooperativa Albarizas", "https://vinosdealbarizas.com/"),
]


def _texto(html: str) -> str:
    """Texto plano legible del HTML (sin scripts ni estilos), con espacios normalizados."""
    soup = BeautifulSoup(html, "html.parser")
    for etq in soup(["script", "style", "noscript"]):
        etq.decompose()
    texto = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", texto).strip()


def _mismo_dominio(base: str, url: str) -> bool:
    try:
        return urlparse(base).netloc.split(":")[0].replace("www.", "") == \
               urlparse(url).netloc.split(":")[0].replace("www.", "")
    except ValueError:
        return False


def _enlaces_visita(html: str, base_url: str, limite: int = 4) -> list[str]:
    """Enlaces del mismo dominio cuyo destino o texto huele a visitas/experiencias/reservas."""
    soup = BeautifulSoup(html, "html.parser")
    vistos: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        destino = urljoin(base_url, href)
        if not destino.startswith("http") or not _mismo_dominio(base_url, destino):
            continue
        gancho = (href + " " + a.get_text(" ")).lower()
        if any(p in gancho for p in PALABRAS_VISITA) and destino not in vistos:
            vistos.append(destino)
        if len(vistos) >= limite:
            break
    return vistos


def _a_float(bruto: str) -> float | None:
    """'15,50' o '1.250' → float. Devuelve None si no es un número usable."""
    s = bruto.replace(" ", "")
    # Si hay coma, es el decimal (formato ES). Si solo hay punto con 2 decimales, también.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _tipo_probable(contexto: str) -> str:
    bajo = contexto.lower()
    for clave, etiqueta in TIPOS_CONTEXTO:
        if clave in bajo:
            return etiqueta
    return "sin clasificar"


def _precios_en_texto(texto: str, ventana: int = 90) -> list[dict]:
    """Importes en € con su contexto (la frase alrededor), tipo y nivel de confianza.

    Descarta el ruido de tienda (botella/envío). La confianza es *alta* cuando cerca del
    precio hay una palabra de visita/cata/experiencia; *baja* si no (para revisar a mano).
    """
    fuera: list[dict] = []
    for m in RE_PRECIO.finditer(texto):
        bruto = m.group(1) or m.group(2)
        precio = _a_float(bruto)
        if precio is None or not (PRECIO_MIN <= precio <= PRECIO_MAX):
            continue
        ini = max(0, m.start() - ventana)
        fin = min(len(texto), m.end() + ventana)
        contexto = texto[ini:fin].strip()
        bajo = contexto.lower()
        if any(r in bajo for r in RUIDO_TIENDA):
            continue  # precio de tienda (botella/envío), no de una visita
        tipo = _tipo_probable(contexto)
        fuera.append({
            "precio_eur": precio,
            "contexto": contexto,
            "tipo_probable": tipo,
            "confianza": "alta" if tipo != "sin clasificar" else "baja",
        })
    return fuera


def _parece_spa(html: str) -> bool:
    """True si la página es un cascarón de JavaScript (SPA): apenas texto y sin enlaces útiles.

    Estas webs (p. ej. Williams & Humbert) pintan el contenido con JS tras cargar; nuestro
    lector se queda con el esqueleto. Se marcan para la vía WebFetch o el cuestionario.
    """
    if not html:
        return False
    texto = _texto(html).lower()
    n_enlaces = len(re.findall(r"href=", html))
    return len(texto) < 800 or n_enlaces <= 2


def candidatos_bodega(nombre: str, web: str, max_paginas: int = 4) -> dict:
    """Precios candidatos de una bodega: home + sus páginas de visitas/experiencias.

    Devuelve {estado, candidatos, paginas}. `estado`:
      · "ok"         → se hallaron precios candidatos (revisión humana).
      · "sin_precio" → web legible pero sin importes (probable "consultar con la bodega").
      · "spa"        → web de JavaScript no legible por el lector → vía WebFetch/cuestionario.
      · "sin_web"    → sin URL válida.
      · "fetch_error"→ la web no respondió.
    NO decide el precio final: los candidatos son para verificación humana.
    """
    if not isinstance(web, str) or not web.startswith("http"):
        return {"estado": "sin_web", "candidatos": [], "paginas": 0}

    html, metodo = navegador.obtener_html(web)
    if not html:
        return {"estado": "fetch_error", "candidatos": [], "paginas": 0}

    paginas = [(web, html, metodo)]
    for enlace in _enlaces_visita(html, web, limite=max_paginas - 1):
        h, met = navegador.obtener_html(enlace)
        if h:
            paginas.append((enlace, h, met))

    candidatos: list[dict] = []
    vistos: set[tuple[float, str]] = set()
    for url, h, met in paginas:
        for c in _precios_en_texto(_texto(h)):
            clave = (c["precio_eur"], c["contexto"][:40])
            if clave in vistos:
                continue
            vistos.add(clave)
            candidatos.append({"bodega": nombre, "url": url, "metodo": met, **c})

    if candidatos:
        estado = "ok"
    elif len(paginas) == 1 and _parece_spa(html):
        estado = "spa"
    else:
        estado = "sin_precio"
    return {"estado": estado, "candidatos": candidatos, "paginas": len(paginas)}


def explorar(muestra: list[tuple[str, str]] | None = None) -> dict:
    """Corre el extractor sobre una muestra e imprime la tasa de acierto (prototipo)."""
    muestra = muestra or MUESTRA_DEFECTO
    resumen: dict[str, dict] = {}
    for nombre, web in muestra:
        try:
            res = candidatos_bodega(nombre, web)
        except Exception as e:  # el prototipo no debe caerse por una web rota
            print(f"⚠️  {nombre}: error ({e})")
            res = {"estado": "error", "candidatos": []}
        resumen[nombre] = res
        cands = res["candidatos"]
        print(f"\n### {nombre}  ({web})  →  {res['estado']}")
        for c in cands[:8]:
            print(f"   {c['precio_eur']:>6.2f} €  [{c['tipo_probable']}·{c['confianza']}]  "
                  f"…{c['contexto'][:100]}…")

    con = sum(1 for v in resumen.values() if v["candidatos"])
    print(f"\n=== {con}/{len(muestra)} bodegas con al menos un precio candidato ===")
    return resumen


# Columnas del CSV de candidatos (para revisión humana; NO es el precio final).
COLS = ["bodega", "estado", "precio_eur", "tipo_probable", "confianza", "contexto",
        "url", "metodo", "fecha_consulta"]


def procesar_todas(fecha: str, salida: str | None = None, verbose: bool = True) -> dict:
    """Recorre TODAS las webs válidas (auditoría) y escribe el CSV de candidatos.

    `fecha` se pasa desde fuera (AAAA-MM-DD) para que cada precio lleve su fecha de consulta.
    Devuelve un resumen con los estados. Las bodegas 'spa'/'sin_precio'/'sin_web' quedan
    listadas aparte: son las que hay que resolver por WebFetch o cuestionario.
    """
    import csv

    import pandas as pd

    from enolytics import config

    aud = pd.read_csv(config.DATOS_PROCESADO / "auditoria_web.csv")
    aud = aud[aud["web_ok"] == True]  # noqa: E712 — comparación de columna pandas
    salida = salida or str(config.DATOS_PROCESADO / "precios_experiencias_candidatos.csv")

    filas: list[dict] = []
    estados: dict[str, str] = {}
    for _, b in aud.iterrows():
        nombre, web = b["bodega"], b.get("web", "")
        try:
            res = candidatos_bodega(nombre, web)
        except Exception as e:
            res = {"estado": f"error: {e}", "candidatos": []}
        estados[nombre] = res["estado"]
        if res["candidatos"]:
            for c in res["candidatos"]:
                filas.append({
                    "bodega": nombre, "estado": res["estado"],
                    "precio_eur": c["precio_eur"], "tipo_probable": c["tipo_probable"],
                    "confianza": c["confianza"], "contexto": c["contexto"],
                    "url": c["url"], "metodo": c["metodo"], "fecha_consulta": fecha,
                })
        else:
            filas.append({"bodega": nombre, "estado": res["estado"], "precio_eur": "",
                          "tipo_probable": "", "confianza": "", "contexto": "",
                          "url": web, "metodo": "", "fecha_consulta": fecha})
        if verbose:
            n = len(res["candidatos"])
            print(f"  {res['estado']:12s} {n:2d} precios  {nombre}")

    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)

    from collections import Counter
    cuenta = Counter(estados.values())
    con_precio = sum(1 for e in estados.values() if e == "ok")
    print(f"\n=== {con_precio}/{len(estados)} bodegas con precios candidatos ===")
    print("Estados:", dict(cuenta))
    pendientes = [n for n, e in estados.items() if e != "ok"]
    print(f"Pendientes (WebFetch/cuestionario): {len(pendientes)}")
    for n in pendientes:
        print(f"   · {estados[n]:10s} {n}")
    print(f"\nCSV escrito en: {salida}")
    return {"estados": estados, "salida": salida}


if __name__ == "__main__":
    explorar()
