"""Cruceristas del puerto de la Bahía de Cádiz (Dataestur) — mercado cautivo del Marco.

Idea de Antonio: el crucerista que atraca en Cádiz está a **40 minutos de las bodegas de Jerez**
y hace excursiones de día. Encaja con el dato de ACEVIN de que ~30% de los enoturistas son
**excursionistas que no pernoctan**.

Y el volumen es asombroso: en 2024 llegaron **696.151 cruceristas** a la Bahía de Cádiz (6º puerto
de España), **más que los 425.652 visitantes que recibieron TODAS las bodegas del Marco juntas**.

Lo más valioso es el **cruce de estacionalidades**: el crucero **hace pico en octubre-noviembre**,
justo cuando el enoturismo cae. Es la prioridad **FEDER P4A** (reducir la estacionalidad) servida
en bandeja.

⚠️ Nota técnica: el endpoint `PUERTOS_DL` de Dataestur **devuelve un fichero Excel, no CSV**
(igual que `AFILIACION_TURISMO_DL`). El cliente `dataestur.py` ya detecta ambos formatos.

Genera `datos/procesado/cruceros/cruceros_cadiz.csv` y `ranking_puertos.csv`.

Uso:
    from enolytics.ingesta import cruceros
    cruceros.descargar()
"""
from __future__ import annotations

import pandas as pd

from enolytics import config
from enolytics.ingesta import dataestur

PUERTO = "BAHÍA DE CÁDIZ"
ENDPOINT = "PUERTOS_DL"


def descargar(desde_anio: int = 2022, verbose: bool = True) -> dict[str, pd.DataFrame]:
    """Descarga el tráfico de cruceros del puerto de la Bahía de Cádiz y el ranking nacional."""
    df = dataestur.consultar(ENDPOINT, **{"desde (año)": desde_anio})
    if df.empty:
        raise RuntimeError("Dataestur no devolvió datos de PUERTOS_DL.")

    df["AUT_PORTUARIA"] = df["AUT_PORTUARIA"].astype(str).str.strip()

    # --- Puerto de la Bahía de Cádiz ---
    cad = df[df["AUT_PORTUARIA"].str.upper() == PUERTO].copy()
    cad["fecha"] = pd.to_datetime(
        cad["AÑO"].astype(int).astype(str) + "-" + cad["MES"].astype(int).astype(str).str.zfill(2) + "-01",
        errors="coerce")
    cad = cad.sort_values("fecha")

    # --- Ranking nacional (último año completo) ---
    anios_completos = df.groupby("AÑO")["MES"].nunique()
    anio_ref = int(anios_completos[anios_completos >= 12].index.max())
    ranking = (df[df["AÑO"] == anio_ref]
               .groupby("AUT_PORTUARIA")
               .agg(pasajeros_crucero=("PASAJEROS_CRUCERO", "sum"),
                    escalas=("CRUCEROS", "sum"))
               .sort_values("pasajeros_crucero", ascending=False)
               .reset_index())
    ranking.insert(0, "anio", anio_ref)
    ranking.insert(0, "posicion", range(1, len(ranking) + 1))

    config.asegurar_directorios()
    destino = config.DATOS_PROCESADO / "cruceros"
    destino.mkdir(parents=True, exist_ok=True)
    cad.to_csv(destino / "cruceros_cadiz.csv", index=False)
    ranking.to_csv(destino / "ranking_puertos.csv", index=False)

    if verbose:
        print(f"Cruceros · puerto: {PUERTO}")
        for anio, g in cad.groupby("AÑO"):
            print(f"  {int(anio)}: {int(g['PASAJEROS_CRUCERO'].sum()):>9,} cruceristas · "
                  f"{int(g['CRUCEROS'].sum()):>4} escalas".replace(",", "."))
        pos = ranking[ranking["AUT_PORTUARIA"].str.upper() == PUERTO]
        if not pos.empty:
            p = pos.iloc[0]
            print(f"\n  ✓ Ranking nacional {anio_ref}: **{int(p['posicion'])}º puerto de España** "
                  f"({int(p['pasajeros_crucero']):,} cruceristas)".replace(",", "."))
        print(f"  ✓ Guardado en {destino.name}/ (cruceros_cadiz.csv, ranking_puertos.csv)")

    return {"cadiz": cad, "ranking": ranking}


if __name__ == "__main__":
    descargar()
