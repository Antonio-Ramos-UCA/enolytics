"""Inteligencia de Sostenibilidad de las bodegas del Marco de Jerez.

Consolida en un único dataset (`datos/procesado/sostenibilidad.csv`) las señales
públicas de compromiso ambiental de cada bodega, sin encuestar a nadie:

  1. Certificación climática **FEV** (Sustainable Wineries for Climate Protection),
     cruzada previamente con el listado oficial de la Federación Española del Vino.
  2. **Sostenibilidad comunicada**: auditoría de la web de cada bodega (home + una
     subpágina de sostenibilidad si la enlaza) buscando señales por ejes temáticos
     (ecológico, clima/carbono, energía, agua, residuos, biodiversidad, general).

Nota del Marco de Jerez: por el sistema de criaderas y solera, los vinos de Jerez y
Manzanilla tradicionales no pueden certificarse como "vino ecológico" (exige uva de
una sola vendimia). Por eso la señal ecológica se interpreta sobre viñedo/vinos
tranquilos y como *comunicación* de compromiso, no como certificación de la solera.

El índice es un proxy de *comunicación* de sostenibilidad, no una certificación.

Uso:
    from enolytics.ingesta import sostenibilidad
    sostenibilidad.auditar_todas()
"""
from __future__ import annotations

import csv
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from enolytics import config
from enolytics.ingesta import ruta_jerez

# Ejes de sostenibilidad y sus señales (palabras clave, ES + EN)
EJES = {
    "ecologico": ["ecológic", "ecologic", "agricultura ecológica", "viñedo ecológico",
                  "vino ecológico", "organic", "certificación ecológica", "caae",
                  "sohiscert", "biodinám", "biodinami", "biodynam"],
    "clima": ["cambio climático", "climate", "huella de carbono", "huella de co2",
              "emisiones de co2", "carbon footprint", "descarboniz", "neutralidad de carbono",
              "net zero", "cero emisiones", "wineries for climate", "climate protection"],
    "energia": ["energía renovable", "energias renovables", "renewable", "fotovoltaic",
                "placas solares", "energía solar", "autoconsumo", "energía limpia",
                "eficiencia energética"],
    "agua": ["gestión del agua", "ahorro de agua", "reutilización de agua", "reutilizacion de agua",
             "depuración de agua", "consumo de agua", "huella hídrica", "huella hidrica"],
    "residuos": ["reciclaj", "residuos", "economía circular", "economia circular",
                 "reutiliza", "compost", "envases sostenibles", "cero residuos"],
    "biodiversidad": ["biodiversidad", "biodiversity", "cubierta vegetal", "flora y fauna",
                      "ecosistema", "regenerativ"],
    "general": ["sostenib", "sustainab", "medio ambiente", "medioambiente", "environment",
                "responsabilidad social", "compromiso ambiental", "desarrollo sostenible",
                "ods ", "agenda 2030", "iso 14001"],
}

# Enlaces internos que probablemente lleven a contenido de sostenibilidad
_PISTAS_ENLACE = ["sosteni", "sustainab", "ecolog", "medio-ambiente", "medioambiente",
                  "compromiso", "medio ambiente", "rsc", "responsabilidad", "clima",
                  "naturaleza", "vinedo", "viñedo"]


def _texto_de(url: str, timeout: int = 12) -> tuple[str, BeautifulSoup | None]:
    """Descarga una página y devuelve (texto_en_minúsculas, soup) o ('', None)."""
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", "text/html"):
            return "", None
        soup = BeautifulSoup(r.text, "html.parser")
        return r.text.lower(), soup
    except requests.RequestException:
        return "", None


def _subpaginas_sostenibilidad(url_base: str, soup: BeautifulSoup, maximo: int = 2) -> list[str]:
    """Enlaces internos cuyo href o texto sugiere contenido de sostenibilidad."""
    dominio = urlparse(url_base).netloc
    candidatos: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        texto = (a.get_text() or "").lower()
        objetivo = urljoin(url_base, href)
        if urlparse(objetivo).netloc != dominio:
            continue
        if any(p in href.lower() for p in _PISTAS_ENLACE) or any(p in texto for p in _PISTAS_ENLACE):
            if objetivo not in candidatos and objetivo.rstrip("/") != url_base.rstrip("/"):
                candidatos.append(objetivo)
        if len(candidatos) >= maximo:
            break
    return candidatos


def auditar_bodega(url: str) -> dict:
    """Señales de sostenibilidad de la web de una bodega, por ejes temáticos."""
    señales = {eje: False for eje in EJES}
    señales["web_ok"] = False
    if not isinstance(url, str) or not url.startswith("http"):
        return señales

    texto, soup = _texto_de(url)
    if not texto:
        return señales
    señales["web_ok"] = True

    # Home + hasta 2 subpáginas de sostenibilidad
    corpus = texto
    if soup is not None:
        for sub in _subpaginas_sostenibilidad(url, soup):
            t_sub, _ = _texto_de(sub)
            if t_sub:
                corpus += " " + t_sub
            time.sleep(config.PAUSA_ENTRE_PETICIONES)

    for eje, claves in EJES.items():
        señales[eje] = any(k in corpus for k in claves)
    return señales


def indice_sostenibilidad(sig: dict) -> int:
    """Nº de ejes temáticos con alguna señal (0-7)."""
    return sum(bool(sig.get(eje)) for eje in EJES)


def _cargar_fev() -> dict:
    """Lee las certificaciones FEV ya cruzadas del sostenibilidad.csv existente."""
    ruta = config.DATOS_PROCESADO / "sostenibilidad.csv"
    fev: dict[str, dict] = {}
    if not ruta.exists():
        return fev
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            fev[fila["bodega"]] = {
                "certificado_swfcp": fila.get("certificado_swfcp", "") in ("True", "true", "1"),
                "sello_fev": fila.get("sello_fev", ""),
            }
    return fev


def auditar_todas(verbose: bool = True) -> list[dict]:
    """Audita todas las bodegas y guarda el dataset de sostenibilidad enriquecido."""
    bodegas = ruta_jerez.cargar_catalogo()
    fev = _cargar_fev()
    filas = []
    for i, b in enumerate(bodegas, 1):
        nombre = b["nombre"]
        sig = auditar_bodega(b.get("web", ""))
        info_fev = fev.get(nombre, {"certificado_swfcp": False, "sello_fev": ""})
        idx = indice_sostenibilidad(sig)
        fila = {
            "bodega": nombre,
            "localidad": b.get("localidad", ""),
            "web": b.get("web", ""),
            "certificado_swfcp": info_fev["certificado_swfcp"],
            "sello_fev": info_fev["sello_fev"],
            **{f"eje_{k}": sig[k] for k in EJES},
            "menciona_ecologico": sig["ecologico"],
            "web_ok": sig["web_ok"],
            "indice_sostenibilidad": idx,
        }
        filas.append(fila)
        if verbose:
            ejes_ok = [k for k in EJES if sig[k]]
            print(f"  {i:>2}/{len(bodegas)} {nombre[:30]:30} "
                  f"web:{int(sig['web_ok'])} FEV:{int(info_fev['certificado_swfcp'])} "
                  f"→ índice {idx}/7 {ejes_ok}")
        time.sleep(config.PAUSA_ENTRE_PETICIONES)

    config.asegurar_directorios()
    ruta = config.DATOS_PROCESADO / "sostenibilidad.csv"
    cols = (["bodega", "localidad", "web", "certificado_swfcp", "sello_fev"]
            + [f"eje_{k}" for k in EJES]
            + ["menciona_ecologico", "web_ok", "indice_sostenibilidad"])
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in filas:
            w.writerow({k: r.get(k, "") for k in cols})
    if verbose:
        n_fev = sum(r["certificado_swfcp"] for r in filas)
        n_eco = sum(r["menciona_ecologico"] for r in filas)
        print(f"\n✓ Sostenibilidad guardada en {ruta.name} ({len(filas)} bodegas · "
              f"FEV {n_fev} · mencionan ecológico {n_eco})")
    return filas


if __name__ == "__main__":
    auditar_todas()
