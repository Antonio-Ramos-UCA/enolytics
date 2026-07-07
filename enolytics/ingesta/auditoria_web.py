"""Auditoría automática de las webs de las bodegas (Inteligencia Tecnológica).

Sin encuestar a nadie: visita la web de cada bodega y detecta señales públicas de
madurez digital: HTTPS, adaptación móvil, multiidioma (inglés), reserva online y
tecnologías inmersivas (visita virtual / 360 / realidad aumentada).

Es un proxy basado en la home; con el corpus completo o subpáginas se puede afinar.

Uso:
    from enolytics.ingesta import auditoria_web
    auditoria_web.auditar_todas()
"""
from __future__ import annotations

import csv
import re

import requests
from bs4 import BeautifulSoup

from enolytics import config
from enolytics.ingesta import ruta_jerez

# Señales por palabras clave (en varios idiomas)
_KW_RESERVA = ["reserva", "reservar", "reserva online", "book now", "book online",
               "comprar entradas", "entradas", "tickets", "buy tickets", "book a visit",
               "reservar visita", "compra tu entrada"]
_KW_INMERSIVA = ["visita virtual", "tour virtual", "realidad virtual", "realidad aumentada",
                 "360", "virtual tour", "recorrido virtual", "experiencia inmersiva"]
_PLATAFORMAS_RESERVA = ["civitatis", "getyourguide", "wetravel", "fareharbor", "regiondo",
                        "booking.com", "turitop", "bookingkit", "ticketing"]


def auditar_bodega(url: str, timeout: int = 10) -> dict:
    """Devuelve señales de madurez digital de la web de una bodega."""
    d = {"web_ok": False, "https": False, "movil": False, "ingles": False,
         "reserva_online": False, "inmersiva": False, "idiomas": 0}
    if not isinstance(url, str) or not url.startswith("http"):
        return d
    d["https"] = url.startswith("https")
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return d
        html = r.text
        low = html.lower()
        d["web_ok"] = True
        soup = BeautifulSoup(html, "html.parser")

        # adaptación móvil: meta viewport
        d["movil"] = bool(soup.find("meta", attrs={"name": "viewport"}))

        # idiomas: hreflang alternates + detección de inglés
        hreflangs = {a.get("hreflang", "").split("-")[0]
                     for a in soup.find_all("link", rel="alternate") if a.get("hreflang")}
        hreflangs.discard("")
        d["idiomas"] = len(hreflangs) if hreflangs else 1
        d["ingles"] = ("en" in hreflangs) or bool(re.search(r'/en[/"]', low)) or \
                      ("english" in low and "language" in low)

        # reserva online (palabras clave o plataformas de reserva enlazadas)
        d["reserva_online"] = any(k in low for k in _KW_RESERVA) or \
                              any(p in low for p in _PLATAFORMAS_RESERVA)

        # tecnologías inmersivas
        d["inmersiva"] = any(k in low for k in _KW_INMERSIVA)
    except requests.RequestException:
        pass
    return d


def indice_madurez(sig: dict) -> int:
    """Índice de madurez digital (0-5) a partir de las señales."""
    return sum([sig["https"], sig["movil"], sig["ingles"],
                sig["reserva_online"], sig["inmersiva"]])


def auditar_todas(verbose: bool = True) -> list[dict]:
    """Audita la web de todas las bodegas del catálogo y guarda el resultado."""
    bodegas = ruta_jerez.cargar_catalogo()
    filas = []
    for i, b in enumerate(bodegas, 1):
        sig = auditar_bodega(b.get("web", ""))
        fila = {"bodega": b["nombre"], "localidad": b.get("localidad", ""),
                "web": b.get("web", ""), **sig, "madurez_digital": indice_madurez(sig)}
        filas.append(fila)
        if verbose:
            print(f"  {i:>2}/{len(bodegas)} {b['nombre'][:32]:32} "
                  f"web:{int(sig['web_ok'])} móvil:{int(sig['movil'])} EN:{int(sig['ingles'])} "
                  f"reserva:{int(sig['reserva_online'])} 360:{int(sig['inmersiva'])} "
                  f"→ madurez {fila['madurez_digital']}/5")

    config.asegurar_directorios()
    ruta = config.DATOS_PROCESADO / "auditoria_web.csv"
    cols = ["bodega", "localidad", "web", "web_ok", "https", "movil", "ingles",
            "idiomas", "reserva_online", "inmersiva", "madurez_digital"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in filas:
            w.writerow({k: r.get(k, "") for k in cols})
    if verbose:
        print(f"\n✓ Auditoría guardada en {ruta.name} ({len(filas)} bodegas)")
    return filas
