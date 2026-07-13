"""Observatorio Turístico de las Rutas del Vino de España — ACEVIN.

Fuente **oficial** que alimenta varias inteligencias a la vez:
  · Competidores → visitantes, oferta y precios del Marco frente a las demás rutas.
  · Económica    → ingresos del enoturismo y gasto medio por visitante.
  · Clientes     → perfil, motivaciones y canales del enoturista (benchmark nacional).

Los informes anuales son PDF (https://wineroutesofspain.com/observatorio-turistico-rve/).
Muchas tablas van como imagen, pero las cifras clave están en el texto y se extraen aquí con
expresiones regulares.

Genera en `datos/procesado/acevin/`:
  · `visitantes_rutas.csv`  anio, ruta, visitantes           (informe de visitas)
  · `oferta_rutas.csv`      ruta, servicios, pct_del_total   (informe de visitas)
  · `perfil_demanda.csv`    indicador, valor, unidad, ...    (informe de demanda, NACIONAL)

⚠️ El informe de demanda es **nacional**: no desglosa por ruta. Sirve como *benchmark* contra
el que comparar al Marco, y como plantilla validada para un cuestionario propio.

Uso:
    from enolytics.ingesta import acevin
    acevin.descargar_todo()
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

# Informe de "Análisis de la demanda turística" (perfil del enoturista). NACIONAL, sin desglose
# por ruta: sirve de benchmark y como plantilla de cuestionario.
INFORME_DEMANDA = ("https://wineroutesofspain.com/wp-content/uploads/2023/10/"
                   "informe-analisis-perfil-de-la-demanda-2023.pdf")

# La ruta objeto de estudio (para destacarla en el dashboard)
RUTA_FOCO = "Marco de Jerez"

# Normalización de nombres: el PDF los escribe de formas ligeramente distintas cada año
_ALIAS = {
    "marco de jerez": "Marco de Jerez",
    "y el brandy marco de jerez": "Marco de Jerez",
    "y el brandy del marco de jerez": "Marco de Jerez",
    "ribera del duero": "Ribera del Duero",
    "ribera de duero": "Ribera del Duero",   # el informe de oferta lo escribe así
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


def _parsear_oferta(texto: str) -> dict[str, dict]:
    """Extrae la tabla de oferta: {ruta: {servicios, pct}} (nº de servicios y entidades)."""
    datos: dict[str, dict] = {}
    # Patrón de la tabla: "Marco de Jerez 111 3,61%"
    for m in re.finditer(r"([A-ZÁÉÍÓÚÑ][\wÀ-ÿ\s\-–]{2,30}?)\s+(\d{1,4})\s+(\d{1,2},\d{2})\s*%", texto):
        bruto, servicios, pct = m.group(1).strip(), int(m.group(2)), float(m.group(3).replace(",", "."))
        if bruto.upper().startswith("TOTAL"):
            continue
        ruta = _canonica(bruto)
        # Si no está en el diccionario de alias, conservamos el nombre tal cual (hay 37 rutas)
        nombre = ruta or re.sub(r"\s*-\s*", "-", bruto)
        if 1 <= servicios <= 2000 and nombre not in datos:
            datos[nombre] = {"servicios": servicios, "pct_del_total": pct}
    return datos


# Indicadores del informe de demanda (nacional). Cada uno: (etiqueta, patrón, unidad, categoría)
_INDICADORES_DEMANDA = [
    ("Gasto medio diario", r"Gasto medio diario\s*(\d+(?:\.\d{3})*(?:,\d+)?)\s*€", "€", "Impacto económico"),
    ("Gasto medio por estancia", r"Gasto medio por estancia\s*(\d+(?:\.\d{3})*(?:,\d+)?)\s*€", "€", "Impacto económico"),
    ("Gasto medio diario del turista español",
     r"Gasto medio diario del turista español\s*(\d+(?:\.\d{3})*(?:,\d+)?)\s*€", "€", "Impacto económico"),
    ("Estancia media", r"Estancia media\s*(\d+(?:\.\d{3})*(?:,\d+)?)\s", "días", "Comportamiento"),
    ("Tamaño medio del grupo", r"Tamaño medio del grupo\s*(\d+(?:\.\d{3})*(?:,\d+)?)\s", "personas", "Perfil"),
    ("Mujeres", r"Sexo\s*(\d+(?:\.\d{3})*(?:,\d+)?)%\s*mujeres", "%", "Perfil"),
    ("Entre 46 y 65 años", r"Edad\s*(\d+(?:\.\d{3})*(?:,\d+)?)%\s*entre\s*46\s*y\s*65", "%", "Perfil"),
    ("Aficionados al vino",
     r"Relación con el mundo del vino\s*(\d+(?:\.\d{3})*(?:,\d+)?)%\s*son aficionados", "%", "Perfil"),
    ("Llegan en vehículo propio o alquilado",
     r"vehículo propio o alquilado\s*(\d+(?:\.\d{3})*(?:,\d+)?)%", "%", "Comportamiento"),
    ("Han reservado online", r"han reservado online\s*(\d+(?:\.\d{3})*(?:,\d+)?)%", "%", "Promoción y comercialización"),
    ("Conocen la marca Rutas del Vino",
     r"conocedores del Club RVE\s*(\d+(?:\.\d{3})*(?:,\d+)?)%", "%", "Promoción y comercialización"),
    ("Recomendados por familiares y amigos",
     r"recomendados por familiares y amigos\s*(\d+(?:\.\d{3})*(?:,\d+)?)%", "%", "Promoción y comercialización"),
    ("Pernoctan en el destino",
     r"aumentado hasta alcanzar el\s*(\d+(?:\.\d{3})*(?:,\d+)?)%\s*del total de visitantes", "%", "Comportamiento"),
    ("Realizan visita a bodegas", r"Visita a bodegas\s*\((\d+(?:\.\d{3})*(?:,\d+)?)%\)", "%", "Comportamiento"),
    ("Bodegas visitadas de media", r"visitan\s*(\d+(?:\.\d{3})*(?:,\d+)?)\s*bodegas de media", "bodegas", "Comportamiento"),
    ("Motivación principal: enoturismo", r"Enoturismo\s*\((\d+(?:\.\d{3})*(?:,\d+)?)%\)", "%", "Perfil"),
]


def _parsear_demanda(texto: str) -> list[dict]:
    """Extrae los indicadores clave del informe de demanda (nacional)."""
    filas = []
    for etiqueta, patron, unidad, categoria in _INDICADORES_DEMANDA:
        m = re.search(patron, texto, flags=re.IGNORECASE)
        if m:
            valor = float(m.group(1).replace(".", "").replace(",", "."))
            filas.append({"indicador": etiqueta, "valor": valor,
                          "unidad": unidad, "categoria": categoria})
    return filas


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


def _parsear_ingresos(texto: str) -> dict:
    """Ingresos del enoturismo en bodegas y museos.

    ⚠️ Cobertura parcial: el informe solo cita en TEXTO las rutas destacadas (el resto va en
    un gráfico como imagen). Devuelve {'total': X, 'rutas': {ruta: euros}}.
    """
    res: dict = {"total": None, "rutas": {}}

    m = re.search(r"ascendió a\s*(\d+(?:\.\d{3})*)\s*€", texto)
    if m:
        res["total"] = int(m.group(1).replace(".", ""))

    # "Rioja Alta (22,2 millones €), Penedès (19,2 millones €) y Marco de Jerez (17,2 millones €)"
    for m in re.finditer(r"([A-ZÁÉÍÓÚÑ][\wÀ-ÿ\s]{2,30}?)\s*\(\s*(\d+(?:,\d+)?)\s*millones?\s*€\s*\)", texto):
        ruta = _canonica(m.group(1))
        if ruta:
            res["rutas"][ruta] = int(float(m.group(2).replace(",", ".")) * 1_000_000)
    return res


def descargar_ingresos(anio: int = 2024, verbose: bool = True) -> dict:
    """Ingresos del enoturismo en bodegas y museos, por ruta (cobertura parcial)."""
    r = requests.get(INFORMES[anio], timeout=60, headers={"User-Agent": config.USER_AGENT})
    r.raise_for_status()
    datos = _parsear_ingresos(_texto_pdf(r.content))

    destino = config.DATOS_PROCESADO / "acevin"
    destino.mkdir(parents=True, exist_ok=True)
    filas = [{"anio": anio, "ruta": ruta, "ingresos_eur": eur}
             for ruta, eur in sorted(datos["rutas"].items(), key=lambda x: -x[1])]
    if datos["total"]:
        filas.append({"anio": anio, "ruta": "TOTAL Rutas del Vino de España",
                      "ingresos_eur": datos["total"]})
    with open(destino / "ingresos_rutas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["anio", "ruta", "ingresos_eur"])
        w.writeheader()
        w.writerows(filas)
    if verbose:
        print(f"  ✓ ingresos_rutas.csv ({len(filas)} filas · cobertura PARCIAL: solo las rutas "
              f"citadas en el texto)")
        for x in filas:
            print(f"      · {x['ruta']}: {x['ingresos_eur']:,} €".replace(",", "."))
    return datos


def descargar_oferta(anio: int = 2024, verbose: bool = True) -> list[dict]:
    """Oferta enoturística (servicios y entidades) de cada ruta del vino."""
    url = INFORMES[anio]
    r = requests.get(url, timeout=60, headers={"User-Agent": config.USER_AGENT})
    r.raise_for_status()
    datos = _parsear_oferta(_texto_pdf(r.content))

    filas = [{"ruta": ruta, "servicios": d["servicios"], "pct_del_total": d["pct_del_total"]}
             for ruta, d in sorted(datos.items(), key=lambda x: -x[1]["servicios"])]

    destino = config.DATOS_PROCESADO / "acevin"
    destino.mkdir(parents=True, exist_ok=True)
    with open(destino / "oferta_rutas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ruta", "servicios", "pct_del_total"])
        w.writeheader()
        w.writerows(filas)
    if verbose:
        foco = next((x for x in filas if x["ruta"] == RUTA_FOCO), None)
        print(f"  ✓ oferta_rutas.csv ({len(filas)} rutas)" +
              (f" · {RUTA_FOCO}: {foco['servicios']} servicios ({foco['pct_del_total']}%)"
               if foco else ""))
    return filas


def descargar_demanda(verbose: bool = True) -> list[dict]:
    """Perfil del enoturista (informe de demanda de ACEVIN). ⚠️ Dato NACIONAL, no por ruta."""
    r = requests.get(INFORME_DEMANDA, timeout=60, headers={"User-Agent": config.USER_AGENT})
    r.raise_for_status()
    filas = _parsear_demanda(_texto_pdf(r.content))

    destino = config.DATOS_PROCESADO / "acevin"
    destino.mkdir(parents=True, exist_ok=True)
    with open(destino / "perfil_demanda.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["indicador", "valor", "unidad", "categoria"])
        w.writeheader()
        w.writerows(filas)
    if verbose:
        print(f"  ✓ perfil_demanda.csv ({len(filas)}/{len(_INDICADORES_DEMANDA)} indicadores)")
        for x in filas:
            print(f"      · {x['indicador']}: {x['valor']} {x['unidad']}")
    return filas


def descargar_todo(verbose: bool = True) -> None:
    """Descarga las tres salidas de ACEVIN."""
    config.asegurar_directorios()
    if verbose:
        print("ACEVIN — Observatorio Turístico Rutas del Vino de España")
    descargar_visitantes(verbose=verbose)
    descargar_oferta(verbose=verbose)
    descargar_ingresos(verbose=verbose)
    descargar_demanda(verbose=verbose)


if __name__ == "__main__":
    descargar_todo()
