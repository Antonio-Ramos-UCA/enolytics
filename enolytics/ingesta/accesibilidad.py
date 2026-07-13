"""Accesibilidad universal de las bodegas (Inteligencia Tecnológica).

Cubre el indicador de la memoria (Tabla 1): *"Grado de accesibilidad universal en instalaciones
y servicios (% de bodegas con accesibilidad física total, % con audioguías o material accesible,
aseos adaptados, **índice de accesibilidad digital en sitios web**)"*.

Mide dos planos, con distinto grado de fiabilidad:

1. **Accesibilidad DIGITAL** (índice 0-8) — comprobaciones objetivas sobre el HTML, inspiradas en
   las WCAG. Es un dato *observado*, no una auditoría WCAG completa (el contraste de color o la
   navegación por teclado exigen renderizar la página).

2. **Accesibilidad FÍSICA** (señales) — *proxy*: detecta si la web menciona accesibilidad para
   personas con movilidad reducida, audioguías, etc. Mide lo que la bodega **comunica**, no lo que
   realmente ofrece. Para el dato real hará falta Google Maps o preguntar a la bodega.

Uso:
    from enolytics.ingesta import accesibilidad
    accesibilidad.auditar_todas()
"""
from __future__ import annotations

import csv
import re

import requests
from bs4 import BeautifulSoup

from enolytics import config
from enolytics.ingesta import ruta_jerez

# --- Accesibilidad digital: 8 comprobaciones objetivas sobre el HTML (base WCAG) ---
COMPROBACIONES = {
    "idioma_declarado": "El HTML declara el idioma (<html lang>) — vital para lectores de pantalla",
    "titulo_pagina": "La página tiene un <title> descriptivo",
    "imagenes_con_alt": "Al menos el 80% de las imágenes tienen texto alternativo (alt)",
    "zoom_permitido": "No se bloquea el zoom (sin user-scalable=no ni maximum-scale=1)",
    "encabezado_h1": "Existe un encabezado principal <h1>",
    "jerarquia_encabezados": "Hay una jerarquía real de encabezados (h1 + h2)",
    "formularios_etiquetados": "Los campos de formulario tienen etiqueta (label/aria-label)",
    "estructura_semantica": "Usa marcado semántico o landmarks ARIA (main/nav/header/role)",
}

# --- Accesibilidad física: señales que la web comunica (proxy) ---
_KW_FISICA = [
    "accesible", "accesibilidad", "silla de ruedas", "movilidad reducida", "minusvál",
    "discapacidad", "adaptado", "wheelchair", "accessible", "rampa",
]
_KW_SENSORIAL = [
    "audioguía", "audioguia", "audio guía", "braille", "lengua de signos",
    "bucle magnético", "subtitul", "material accesible", "signoguía", "signoguia",
]

# Enlaces poco descriptivos (mala práctica de accesibilidad)
_ENLACES_VAGOS = {"clic aquí", "click aquí", "aquí", "leer más", "más info", "ver más",
                  "click here", "read more", "here"}


def _analizar_digital(soup: BeautifulSoup, html: str) -> dict:
    """Aplica las 8 comprobaciones de accesibilidad digital."""
    r = {}

    # 1. Idioma declarado
    etiqueta_html = soup.find("html")
    r["idioma_declarado"] = bool(etiqueta_html and etiqueta_html.get("lang"))

    # 2. Título de página
    r["titulo_pagina"] = bool(soup.title and (soup.title.string or "").strip())

    # 3. Texto alternativo en imágenes (≥80%)
    imgs = soup.find_all("img")
    if imgs:
        con_alt = sum(1 for i in imgs if i.get("alt") is not None)
        r["imagenes_con_alt"] = (con_alt / len(imgs)) >= 0.8
    else:
        r["imagenes_con_alt"] = True  # sin imágenes, no hay barrera

    # 4. Zoom no bloqueado
    vp = soup.find("meta", attrs={"name": "viewport"})
    contenido_vp = (vp.get("content", "") if vp else "").lower().replace(" ", "")
    r["zoom_permitido"] = not ("user-scalable=no" in contenido_vp
                               or "maximum-scale=1" in contenido_vp)

    # 5 y 6. Encabezados
    r["encabezado_h1"] = bool(soup.find("h1"))
    r["jerarquia_encabezados"] = bool(soup.find("h1") and soup.find("h2"))

    # 7. Formularios etiquetados
    campos = [c for c in soup.find_all(["input", "select", "textarea"])
              if (c.get("type") or "text") not in ("hidden", "submit", "button", "image")]
    if campos:
        ids_con_label = {lb.get("for") for lb in soup.find_all("label") if lb.get("for")}
        etiquetados = sum(
            1 for c in campos
            if c.get("aria-label") or c.get("aria-labelledby") or c.get("title")
            or (c.get("id") and c.get("id") in ids_con_label)
            or c.find_parent("label") is not None
        )
        r["formularios_etiquetados"] = (etiquetados / len(campos)) >= 0.8
    else:
        r["formularios_etiquetados"] = True  # sin formularios, no hay barrera

    # 8. Estructura semántica / landmarks
    r["estructura_semantica"] = bool(
        soup.find(["main", "nav", "header", "footer"]) or soup.find(attrs={"role": True})
    )
    return r


def _analizar_fisica(texto: str) -> dict:
    """Señales de accesibilidad física/sensorial comunicadas en la web (proxy)."""
    return {
        "menciona_accesibilidad_fisica": any(k in texto for k in _KW_FISICA),
        "menciona_apoyo_sensorial": any(k in texto for k in _KW_SENSORIAL),
    }


def _enlaces_vagos(soup: BeautifulSoup) -> int:
    """Nº de enlaces con texto no descriptivo ('clic aquí', 'leer más'...)."""
    n = 0
    for a in soup.find_all("a"):
        t = (a.get_text() or "").strip().lower()
        if t in _ENLACES_VAGOS:
            n += 1
    return n


def auditar_bodega(url: str, timeout: int = 12) -> dict:
    """Audita la accesibilidad digital y las señales de accesibilidad física de una web."""
    base = {k: False for k in COMPROBACIONES}
    base.update({"web_ok": False, "menciona_accesibilidad_fisica": False,
                 "menciona_apoyo_sensorial": False, "enlaces_poco_descriptivos": 0,
                 "indice_accesibilidad_digital": 0})
    if not isinstance(url, str) or not url.startswith("http"):
        return base
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": config.USER_AGENT})
        if resp.status_code != 200:
            return base
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
    except requests.RequestException:
        return base

    base["web_ok"] = True
    base.update(_analizar_digital(soup, html))
    base.update(_analizar_fisica(html.lower()))
    base["enlaces_poco_descriptivos"] = _enlaces_vagos(soup)
    base["indice_accesibilidad_digital"] = sum(bool(base[k]) for k in COMPROBACIONES)
    return base


def auditar_todas(verbose: bool = True) -> list[dict]:
    """Audita la accesibilidad de todas las bodegas del catálogo y guarda el resultado."""
    bodegas = ruta_jerez.cargar_catalogo()
    filas = []
    for i, b in enumerate(bodegas, 1):
        sig = auditar_bodega(b.get("web", ""))
        fila = {"bodega": b["nombre"], "localidad": b.get("localidad", ""),
                "web": b.get("web", ""), **sig}
        filas.append(fila)
        if verbose:
            fallos = [k for k in COMPROBACIONES if sig["web_ok"] and not sig[k]]
            print(f"  {i:>2}/{len(bodegas)} {b['nombre'][:30]:30} "
                  f"web:{int(sig['web_ok'])} → accesibilidad digital "
                  f"{sig['indice_accesibilidad_digital']}/8"
                  + (f"  ✗ {', '.join(fallos)}" if fallos else ""))

    config.asegurar_directorios()
    ruta = config.DATOS_PROCESADO / "accesibilidad.csv"
    cols = (["bodega", "localidad", "web", "web_ok"] + list(COMPROBACIONES)
            + ["enlaces_poco_descriptivos", "menciona_accesibilidad_fisica",
               "menciona_apoyo_sensorial", "indice_accesibilidad_digital"])
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in filas:
            w.writerow({k: r.get(k, "") for k in cols})

    if verbose:
        ok = [r for r in filas if r["web_ok"]]
        if ok:
            media = sum(r["indice_accesibilidad_digital"] for r in ok) / len(ok)
            n_fis = sum(r["menciona_accesibilidad_fisica"] for r in ok)
            n_sen = sum(r["menciona_apoyo_sensorial"] for r in ok)
            print(f"\n✓ {ruta.name}: {len(ok)}/{len(filas)} webs auditadas · "
                  f"accesibilidad digital media {media:.1f}/8 · "
                  f"{n_fis} mencionan accesibilidad física · {n_sen} apoyo sensorial")
    return filas


if __name__ == "__main__":
    auditar_todas()
