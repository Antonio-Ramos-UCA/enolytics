"""Observatorio Turístico de las Rutas del Vino de España — ACEVIN (Inteligencia de Competidores).

Fuente **oficial** para comparar el Marco de Jerez con las demás rutas del vino: número de
visitantes a bodegas y museos por ruta y año. Es la fuente que la propia memoria del proyecto
cita (382.716 visitantes en el Marco en 2023).

Los informes anuales son PDF (https://wineroutesofspain.com/observatorio-turistico-rve/). Las
tablas completas van como imagen, pero el texto sí incluye el ranking de las rutas más
visitadas, que es lo que aquí se extrae por expresiones regulares.

Genera `datos/procesado/acevin/visitantes_rutas.csv` con columnas: anio, ruta, visitantes.

Uso:
    from enolytics.ingesta import acevin
    acevin.descargar_visitantes()
"""
from __future__ import annotations

import csv
import re
import unicodedata

import requests

from enolytics import config

# Informes anuales de visitas a bodegas y museos (Observatorio Turístico RVE)
INFORMES = {
    2024: "https://wineroutesofspain.com/wp-content/uploads/2025/10/informe-visitas-a-bodegas-y-museos-rutas-del-vino-de-espana-2024.pdf",
    2023: "https://wineroutesofspain.com/wp-content/uploads/2024/06/informe-visitas-a-bodegas-y-museos-rutas-del-vino-de-espana-2023.pdf",
    2022: "https://wineroutesofspain.com/wp-content/uploads/2023/06/informe-visitas-a-bodegas-y-museos-rve-2022.pdf",
}

# La ruta objeto de estudio (para destacarla en el dashboard)
RUTA_FOCO = "Marco de Jerez"

# Normalización de nombres: el PDF los escribe de formas ligeramente distintas cada año
_ALIAS = {
    "marco de jerez": "Marco de Jerez",
    "y el brandy marco de jerez": "Marco de Jerez",
    "y el brandy del marco de jerez": "Marco de Jerez",
    "ribera del duero": "Ribera del Duero",
    "rioja alta": "Rioja Alta",
    "rioja alavesa": "Rioja Alavesa",
    "penedes": "Penedès",
    "calatayud": "Calatayud",
    "de calatayud": "Calatayud",
    "rias baixas": "Rías Baixas",
    "somontano": "Somontano",
    "rueda": "Rueda",
    "utiel requena": "Utiel-Requena",
    "navarra": "Navarra",
}


def _norm(s: str) -> str:
    """Minúsculas sin tildes ni sobrantes, para casar nombres de rutas."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\bruta\s+del\s+vino\b", " ", s)
    s = re.sub(r"[^a-z\s-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _canonica(nombre: str) -> str | None:
    """Devuelve el nombre canónico de la ruta, o None si no se reconoce."""
    n = _norm(nombre)
    if n in _ALIAS:
        return _ALIAS[n]
    # coincidencia por contención (el PDF a veces añade palabras)
    for clave, valor in _ALIAS.items():
        if clave in n or n in clave:
            return valor
    return None


def _texto_pdf(contenido: bytes) -> str:
    """Extrae y normaliza el texto de todas las páginas del PDF."""
    import io
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    lector = PdfReader(io.BytesIO(contenido))
    texto = " ".join((p.extract_text() or "") for p in lector.pages)
    return re.sub(r"\s+", " ", texto)


def _parsear_visitantes(texto: str) -> dict[str, int]:
    """Extrae {ruta: visitantes} del texto del informe."""
    datos: dict[str, int] = {}

    # Formato A (lista numerada):  "Ruta del Vino X, con 425.652 visitantes"
    for m in re.finditer(r"Ruta\s+del\s+Vino\s+([^,\.\d]{3,60}?)\s*,?\s*con\s+([\d\.]{5,9})\s*visitantes",
                         texto, flags=re.IGNORECASE):
        ruta, cifra = _canonica(m.group(1)), m.group(2)
        if ruta:
            datos.setdefault(ruta, int(cifra.replace(".", "")))

    # Formato B (entre paréntesis): "Penedès (305.590)" / "Rioja Alta (316.922)"
    for m in re.finditer(r"([A-ZÁÉÍÓÚÑ][\wÀ-ÿ\s\-]{2,40}?)\s*\(\s*([\d\.]{5,9})\s*(?:visitantes)?\s*\)", texto):
        ruta, cifra = _canonica(m.group(1)), m.group(2)
        if ruta:
            datos.setdefault(ruta, int(cifra.replace(".", "")))

    # Descarta cifras absurdas (totales nacionales, importes económicos...)
    return {r: v for r, v in datos.items() if 10_000 <= v <= 900_000}


def descargar_visitantes(verbose: bool = True) -> list[dict]:
    """Descarga los informes ACEVIN y guarda los visitantes por ruta y año."""
    filas: list[dict] = []
    for anio, url in sorted(INFORMES.items()):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": config.USER_AGENT})
            r.raise_for_status()
            datos = _parsear_visitantes(_texto_pdf(r.content))
        except Exception as e:  # pragma: no cover - depende de la red
            if verbose:
                print(f"  ⚠️ {anio}: no se pudo procesar ({e})")
            continue
        for ruta, visitantes in sorted(datos.items(), key=lambda x: -x[1]):
            filas.append({"anio": anio, "ruta": ruta, "visitantes": visitantes})
        if verbose:
            print(f"  ✓ {anio}: {len(datos)} rutas — " +
                  ", ".join(f"{r} {v:,}".replace(",", ".") for r, v in
                            sorted(datos.items(), key=lambda x: -x[1])[:3]))

    config.asegurar_directorios()
    destino = config.DATOS_PROCESADO / "acevin"
    destino.mkdir(parents=True, exist_ok=True)
    ruta_csv = destino / "visitantes_rutas.csv"
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["anio", "ruta", "visitantes"])
        w.writeheader()
        w.writerows(filas)
    if verbose:
        print(f"\n✓ Guardado en {ruta_csv.name} ({len(filas)} filas)")
    return filas


if __name__ == "__main__":
    descargar_visitantes()
