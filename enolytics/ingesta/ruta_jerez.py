"""Ingesta del catálogo de bodegas de la Ruta del Vino y Brandy de Jerez.

Dos etapas:
  1. `descargar_catalogo()`  -> listado de bodegas inscritas (nombre, localidad, ficha).
  2. `enriquecer_bodegas()`  -> visita cada ficha y extrae dirección, teléfono, email,
                                web, GPS, RRSS oficiales, servicios y descripción completa.

La web randomiza el orden de las tarjetas en cada carga y su paginación (/page/N/)
no es estable, por eso `descargar_catalogo()` hace varias pasadas acumulando hasta
que no aparecen bodegas nuevas.

Uso rápido:
    from enolytics.ingesta import ruta_jerez
    bodegas = ruta_jerez.actualizar_catalogo_completo()   # descarga + enriquece + guarda
"""
from __future__ import annotations

import json
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from enolytics import config

# --- Constantes de parseo ---
_RE_FICHA = re.compile(r"https://rutadelvinojerez\.es/empresas-y-servicios/([a-z0-9\-]+)$")
_DOMINIOS_SOCIAL = [
    "facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com",
    "youtu.be", "tiktok.com", "linkedin.com", "vimeo.com", "wa.me", "whatsapp",
]
_HANDLES_RUTA = ["rutadelvinojerez", "ruta-del-vino-jerez", "rutavinojerez"]
_RE_CALLE = re.compile(
    r"^(Calle|C/|C\.|Avda|Avenida|Av\.|Ctra|Carretera|Plaza|Pza|Pol|Polígono|"
    r"Camino|Paraje|Finca|Autovía|Ronda|Cortijo|Siete|Viña)\b",
    re.I,
)


def _limpiar(texto: Optional[str]) -> str:
    """Colapsa espacios en blanco y recorta."""
    return re.sub(r"\s+", " ", texto or "").strip()


def _crear_sesion() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": config.USER_AGENT})
    return s


# --------------------------------------------------------------------------- #
# Etapa 1: listado de bodegas
# --------------------------------------------------------------------------- #
def descargar_catalogo(categoria: str = "bodegas", max_pasadas_sin_novedad: int = 3,
                       verbose: bool = True) -> list[dict]:
    """Descarga el listado de una categoría de la Ruta, con pasadas repetidas.

    La web randomiza el orden de las tarjetas, por eso se repiten pasadas hasta que
    no aparecen registros nuevos.

    Devuelve una lista de dicts: {slug, nombre, localidad, url_ficha, categoria}.
    """
    sesion = _crear_sesion()
    base = f"{config.RUTA_JEREZ_CATEGORIA_BASE}/{categoria}/"
    bodegas: dict[str, dict] = {}
    pasadas_sin_novedad = 0
    pasada = 0

    while pasadas_sin_novedad < max_pasadas_sin_novedad and pasada < 12:
        pasada += 1
        nuevas = 0
        for p in range(1, 6):
            url = base if p == 1 else f"{base}page/{p}/"
            try:
                r = sesion.get(url, timeout=config.TIMEOUT_PETICION)
            except requests.RequestException:
                continue
            if r.status_code != 200:
                break
            soup = BeautifulSoup(r.text, "html.parser")
            tarjetas = soup.find_all("div", class_="desc_emp_list")
            if not tarjetas:
                break
            for caja in tarjetas:
                a = caja.find_parent("a", href=True)
                if not a:
                    continue
                m = _RE_FICHA.match(a["href"])
                if not m:
                    continue
                slug = m.group(1)
                if slug in bodegas:
                    continue
                h4s = caja.find_all("h4")
                nombre = _limpiar(h4s[0].get_text()) if h4s else ""
                localidad = _limpiar(h4s[1].get_text()) if len(h4s) > 1 else ""
                bodegas[slug] = {
                    "slug": slug,
                    "nombre": nombre.title() if nombre.isupper() else nombre,
                    "localidad": localidad,
                    "url_ficha": a["href"],
                    "categoria": categoria,
                }
                nuevas += 1
            time.sleep(config.PAUSA_ENTRE_PETICIONES)
        pasadas_sin_novedad = pasadas_sin_novedad + 1 if nuevas == 0 else 0
        if verbose:
            print(f"  [{categoria}] pasada {pasada}: +{nuevas} nuevas | acumuladas {len(bodegas)}")

    return sorted(bodegas.values(), key=lambda b: b["nombre"].lower())


def descargar_oferta_completa(verbose: bool = True) -> list[dict]:
    """Descarga el listado de TODAS las categorías de la Ruta (oferta enoturística).

    Base de la inteligencia de negocios: nº de recursos por categoría (bodegas, museos,
    enotecas, restaurantes, alojamientos, actividades…).
    """
    import csv

    todos: list[dict] = []
    for cat in config.CATEGORIAS_RUTA:
        if verbose:
            print(f"\n== Categoría: {cat} ==")
        try:
            todos.extend(descargar_catalogo(categoria=cat, verbose=verbose))
        except requests.RequestException as e:
            if verbose:
                print(f"  (error en {cat}: {e})")

    config.asegurar_directorios()
    ruta = config.DATOS_PROCESADO / "oferta_enoturistica.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["categoria", "nombre", "localidad", "url_ficha", "slug"])
        w.writeheader()
        for r in todos:
            w.writerow({k: r.get(k, "") for k in ["categoria", "nombre", "localidad", "url_ficha", "slug"]})
    if verbose:
        print(f"\n✓ Oferta guardada en {ruta.name}: {len(todos)} recursos")
    return todos


# --------------------------------------------------------------------------- #
# Etapa 2: enriquecer cada ficha
# --------------------------------------------------------------------------- #
def _parsear_ficha(html: str) -> dict:
    """Extrae todos los campos de la página de ficha de una bodega."""
    soup = BeautifulSoup(html, "html.parser")
    d: dict = {}

    # GPS desde el enlace "cómo llegar" de Google Maps
    m = re.search(r"maps/dir//\s*([\-0-9.]+),\s*([\-0-9.]+)", html)
    d["gps_lat"], d["gps_lon"] = (m.group(1), m.group(2)) if m else ("", "")

    # Teléfono español
    m = re.search(r"(\+34[\d\s]{9,13})", html)
    d["telefono"] = _limpiar(m.group(1)) if m else ""

    parrafos = [_limpiar(p.get_text()) for p in soup.find_all("p")]

    # Email real (excluye placeholder y correos de la propia Ruta)
    d["email"] = ""
    for e in re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", html):
        el = e.lower()
        if any(x in el for x in ("your@email", "rutadeljerez", "rutadelvino", "sentry")):
            continue
        d["email"] = e
        break

    # Dirección: empieza por palabra de vía, o contiene código postal + localidad
    d["direccion"] = ""
    for t in parrafos:
        if not t or t.startswith("http") or "@" in t or t.startswith("+34") or len(t) > 170:
            continue
        if _RE_CALLE.match(t) or (
            re.search(r"\b\d{5}\b", t)
            and re.search(r"(Cádiz|Jerez|Sanlúcar|Puerto|Trebujena|Chiclana|Rota|Lebrija)", t)
        ):
            d["direccion"] = t
            break

    # Web oficial (primer enlace de texto que no es red social ni de la Ruta)
    d["web"] = next(
        (t for t in parrafos
         if t.startswith("http")
         and not any(s in t for s in _DOMINIOS_SOCIAL)
         and "rutadelvinojerez" not in t
         and "cookiedatabase" not in t),
        "",
    )

    # RRSS oficiales de la bodega (excluye las de la Ruta y los botones de compartir)
    rrss = []
    for a in soup.find_all("a", href=True):
        u = a["href"]
        if not any(s in u for s in _DOMINIOS_SOCIAL):
            continue
        if any(x in u.lower() for x in _HANDLES_RUTA):
            continue
        if any(x in u for x in ("sharer", "share-offsite", "intent/tweet", "/send?text")):
            continue
        if u.rstrip("/") in (
            "https://www.instagram.com", "https://instagram.com",
            "https://www.facebook.com", "https://twitter.com",
        ):
            continue
        rrss.append(u)
    d["rrss"] = sorted(set(rrss))

    # Descripción (tras <h3>Descripción) y servicios (tras <h3>Servicios)
    descripcion, servicios, modo = [], [], None
    for el in soup.find_all(["h3", "p", "li"]):
        t = _limpiar(el.get_text())
        if el.name == "h3":
            low = t.lower()
            modo = "desc" if "descrip" in low else ("serv" if "servicio" in low else None)
            continue
        if modo == "desc" and el.name == "p" and t:
            descripcion.append(t)
        elif modo == "serv" and el.name == "li" and t:
            servicios.append(t)
    d["descripcion"] = _limpiar(" ".join(descripcion))
    vistos = set()
    d["servicios"] = [s for s in servicios if not (s in vistos or vistos.add(s))]

    return d


def enriquecer_bodegas(bodegas: list[dict], verbose: bool = True) -> list[dict]:
    """Visita la ficha de cada bodega y le añade todos los campos detallados."""
    sesion = _crear_sesion()
    enriquecidas = []
    for i, b in enumerate(bodegas, 1):
        try:
            r = sesion.get(b["url_ficha"], timeout=config.TIMEOUT_PETICION)
            info = _parsear_ficha(r.text) if r.status_code == 200 else {}
        except requests.RequestException:
            info = {}
        enriquecidas.append({**b, **info})
        if verbose:
            print(f"  {i:>2}/{len(bodegas)} {b['nombre'][:32]:32} "
                  f"tel:{int(bool(info.get('telefono')))} web:{int(bool(info.get('web')))} "
                  f"gps:{int(bool(info.get('gps_lat')))} rrss:{len(info.get('rrss', []))} "
                  f"serv:{len(info.get('servicios', []))}")
        time.sleep(config.PAUSA_ENTRE_PETICIONES)
    return enriquecidas


# --------------------------------------------------------------------------- #
# Guardado
# --------------------------------------------------------------------------- #
_COLUMNAS_CSV = [
    "nombre", "localidad", "direccion", "telefono", "email", "web",
    "gps_lat", "gps_lon", "rrss", "servicios", "url_ficha", "slug", "descripcion",
]


def guardar_catalogo(bodegas: list[dict]) -> None:
    """Guarda el catálogo enriquecido en CSV (plano) y JSON (estructurado)."""
    import csv

    config.asegurar_directorios()
    with open(config.CATALOGO_JSON, "w", encoding="utf-8") as f:
        json.dump(bodegas, f, ensure_ascii=False, indent=2)
    with open(config.CATALOGO_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(_COLUMNAS_CSV)
        for b in bodegas:
            w.writerow([
                " | ".join(b.get(c, [])) if c in ("rrss", "servicios") else b.get(c, "")
                for c in _COLUMNAS_CSV
            ])


def actualizar_catalogo_completo(verbose: bool = True) -> list[dict]:
    """Pipeline completo: descarga el listado, enriquece cada ficha y guarda."""
    if verbose:
        print("1) Descargando listado de bodegas…")
    bodegas = descargar_catalogo(verbose=verbose)
    if verbose:
        print(f"\n2) Enriqueciendo {len(bodegas)} fichas…")
    bodegas = enriquecer_bodegas(bodegas, verbose=verbose)
    guardar_catalogo(bodegas)
    if verbose:
        print(f"\n✓ Guardado en {config.CATALOGO_CSV.name} y {config.CATALOGO_JSON.name} "
              f"({len(bodegas)} bodegas)")
    return bodegas


def cargar_catalogo() -> list[dict]:
    """Lee el catálogo enriquecido ya guardado (desde el JSON)."""
    if not config.CATALOGO_JSON.exists():
        raise FileNotFoundError(
            f"No existe {config.CATALOGO_JSON}. Ejecuta antes actualizar_catalogo_completo()."
        )
    with open(config.CATALOGO_JSON, encoding="utf-8") as f:
        return json.load(f)
