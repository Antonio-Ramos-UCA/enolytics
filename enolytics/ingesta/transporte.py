"""Transporte sostenible: accesibilidad de las bodegas en transporte público.

Cubre el indicador de la memoria (Tabla 1, Inteligencia en Sostenibilidad):
*"Uso de medios de transporte sostenibles en el destino"*.

Enfoque: en lugar de preguntar a los visitantes cómo se desplazan (que exigiría encuesta), se
mide la **condición previa que lo hace posible**: ¿está la bodega a una distancia razonable a pie
de una estación de tren o una parada de autobús? Si no lo está, el visitante *no puede* elegir el
transporte público, por mucho que quiera.

Contexto (ACEVIN): el 75,6% de los enoturistas llega en vehículo propio o alquilado. Este módulo
ayuda a explicar **por qué**.

Fuente: **OpenStreetMap** vía la API de Overpass (abierta y gratuita).
Salida: `datos/procesado/transporte_sostenible.csv`

Uso:
    from enolytics.ingesta import transporte
    transporte.analizar_todas()
"""
from __future__ import annotations

import csv
import math
import time

import requests

from enolytics import config
from enolytics.ingesta import ruta_jerez

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Overpass RECHAZA (HTTP 406) los User-Agent de navegador: exige que la aplicación se
# identifique. Es además la norma de cortesía de OpenStreetMap.
USER_AGENT_OSM = ("ENOLYTICS/1.0 (proyecto de investigacion, Universidad de Cadiz; "
                  "inteligencia.turistica@gm.uca.es)")

# Umbrales de accesibilidad (km). Basados en distancias caminables razonables.
UMBRAL_BUS_A_PIE = 0.5      # una parada de bus a 500 m es "a pie"
UMBRAL_TREN_A_PIE = 1.0     # a una estación se acepta caminar algo más
UMBRAL_CERCANO_BUS = 1.5
UMBRAL_CERCANO_TREN = 3.0


def _bbox(bodegas: list[dict], margen: float = 0.05) -> tuple[float, float, float, float]:
    """Caja que engloba todas las bodegas, con un margen."""
    lats = [float(b["gps_lat"]) for b in bodegas if b.get("gps_lat")]
    lons = [float(b["gps_lon"]) for b in bodegas if b.get("gps_lon")]
    return (min(lats) - margen, min(lons) - margen,
            max(lats) + margen, max(lons) + margen)


def _consultar_overpass(bbox: tuple[float, float, float, float], reintentos: int = 3) -> list[dict]:
    """Descarga las paradas de transporte público del área (tren y autobús)."""
    sur, oeste, norte, este = bbox
    caja = f"{sur},{oeste},{norte},{este}"
    consulta = f"""
    [out:json][timeout:90];
    (
      node["railway"~"^(station|halt)$"]({caja});
      node["amenity"="bus_station"]({caja});
      node["highway"="bus_stop"]({caja});
    );
    out body;
    """
    for intento in range(1, reintentos + 1):
        try:
            r = requests.post(OVERPASS_URL, data={"data": consulta}, timeout=120,
                              headers={"User-Agent": USER_AGENT_OSM})
            r.raise_for_status()
            return r.json().get("elements", [])
        except Exception as e:  # pragma: no cover - depende de la red
            print(f"  · Overpass falló ({e}); reintento {intento}/{reintentos}...")
            time.sleep(10 * intento)
    raise RuntimeError("No se pudo consultar OpenStreetMap (Overpass).")


def _clasificar(elems: list[dict]) -> tuple[list[tuple], list[tuple]]:
    """Separa las paradas en (tren, autobús) como listas de (lat, lon, nombre)."""
    tren, bus = [], []
    for e in elems:
        lat, lon = e.get("lat"), e.get("lon")
        if lat is None or lon is None:
            continue
        tags = e.get("tags", {})
        nombre = tags.get("name", "(sin nombre)")
        if tags.get("railway") in ("station", "halt"):
            tren.append((lat, lon, nombre))
        else:  # bus_station / bus_stop
            bus.append((lat, lon, nombre))
    return tren, bus


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en línea recta (haversine) entre dos puntos, en km."""
    radio = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return radio * 2 * math.asin(math.sqrt(a))


def _mas_cercana(lat: float, lon: float, paradas: list[tuple]) -> tuple[float, str]:
    """Distancia y nombre de la parada más cercana. (inf, '') si no hay ninguna."""
    if not paradas:
        return float("inf"), ""
    d, nombre = min(((distancia_km(lat, lon, p[0], p[1]), p[2]) for p in paradas),
                    key=lambda x: x[0])
    return d, nombre


def categoria(dist_tren: float, dist_bus: float) -> str:
    """Clasifica la accesibilidad en transporte público de una bodega."""
    if dist_bus <= UMBRAL_BUS_A_PIE or dist_tren <= UMBRAL_TREN_A_PIE:
        return "A pie desde el transporte público"
    if dist_bus <= UMBRAL_CERCANO_BUS or dist_tren <= UMBRAL_CERCANO_TREN:
        return "Cercano (paseo largo o taxi corto)"
    return "Requiere vehículo privado"


def analizar_todas(verbose: bool = True) -> list[dict]:
    """Calcula la accesibilidad en transporte público de cada bodega y la guarda."""
    bodegas = [b for b in ruta_jerez.cargar_catalogo() if b.get("gps_lat") and b.get("gps_lon")]
    if not bodegas:
        raise RuntimeError("No hay bodegas con coordenadas GPS en el catálogo.")

    if verbose:
        print(f"Consultando OpenStreetMap (paradas de transporte) para {len(bodegas)} bodegas...")
    elems = _consultar_overpass(_bbox(bodegas))
    tren, bus = _clasificar(elems)
    if verbose:
        print(f"  ✓ {len(tren)} estaciones/apeaderos de tren · {len(bus)} paradas de autobús")

    filas = []
    for b in bodegas:
        lat, lon = float(b["gps_lat"]), float(b["gps_lon"])
        d_tren, n_tren = _mas_cercana(lat, lon, tren)
        d_bus, n_bus = _mas_cercana(lat, lon, bus)
        cat = categoria(d_tren, d_bus)
        filas.append({
            "bodega": b["nombre"],
            "localidad": b.get("localidad", ""),
            "dist_tren_km": round(d_tren, 2) if d_tren != float("inf") else "",
            "estacion_tren": n_tren,
            "dist_bus_km": round(d_bus, 2) if d_bus != float("inf") else "",
            "parada_bus": n_bus,
            "accesible_transporte_publico": cat != "Requiere vehículo privado",
            "categoria_transporte": cat,
        })

    config.asegurar_directorios()
    ruta = config.DATOS_PROCESADO / "transporte_sostenible.csv"
    cols = ["bodega", "localidad", "dist_tren_km", "estacion_tren", "dist_bus_km",
            "parada_bus", "accesible_transporte_publico", "categoria_transporte"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)

    if verbose:
        from collections import Counter
        conteo = Counter(f["categoria_transporte"] for f in filas)
        n_ok = sum(f["accesible_transporte_publico"] for f in filas)
        print(f"\n✓ {ruta.name} ({len(filas)} bodegas)")
        for cat, n in conteo.most_common():
            print(f"    {cat}: {n}")
        print(f"  → {n_ok}/{len(filas)} ({n_ok / len(filas) * 100:.0f}%) accesibles "
              f"en transporte público")
    return filas


if __name__ == "__main__":
    analizar_todas()
