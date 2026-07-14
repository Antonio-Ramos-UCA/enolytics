"""Conectividad aérea de Jerez (Dataestur) — el primer indicador PREDICTIVO de ENOLYTICS.

Hasta ahora **todos** nuestros datos miraban al pasado (reseñas, visitantes del año anterior,
auditorías). La memoria, en cambio, promete *"modelos de integración de datos en tiempo real que
permitan mejorar la **capacidad predictiva** del sector"* y *"**simulaciones y proyecciones** de
escenarios turísticos"*. Esta es la fuente que permite empezar a cumplirlo.

**Jerez de la Frontera figura como ciudad destino propia** en Dataestur (no hace falta aproximar
con Sevilla).

Cuatro conjuntos, y tres de ellos **se adelantan al viaje**:
  · `BUSQUEDAS_INICIO_VIAJE`  búsquedas de vuelo **según la fecha en que se quiere viajar** →
    intención de viaje *antes* de que ocurra.
  · `RESERVAS_INICIO_VIAJE`   reservas ya confirmadas para fechas futuras → demanda comprometida.
  · `CAPACIDAD`               asientos programados → cuánta gente *puede* llegar.
  · `TRAFICO_PASAJEROS`       pasajeros reales (retrospectivo, para contrastar).

Cada registro viene **por país emisor** e incluye **antelación de compra** (días) y
**estancia media** prevista: material directo para planificar campañas.

Genera en `datos/procesado/conectividad_aerea/`:
  · `busquedas.csv` · `reservas.csv` · `capacidad.csv` · `trafico.csv`
  · `mercados.csv`  resumen por país: búsquedas, reservas, **conversión**, antelación, estancia.

Uso:
    from enolytics.ingesta import conectividad_aerea
    conectividad_aerea.descargar_todo()
"""
from __future__ import annotations

import pandas as pd

from enolytics import config
from enolytics.ingesta import dataestur

CIUDAD = "Jerez de la Frontera"

# El API agrega también un pseudo-país "Total": hay que excluirlo de los rankings por mercado.
PSEUDO_PAISES = {"Total", "España (todas)"}

CONJUNTOS = {
    "busquedas": ("CONECTIVIDAD_AEREA_BUSQUEDAS_INICIO_VIAJE_DL", "BUSQUEDAS"),
    "reservas": ("CONECTIVIDAD_AEREA_RESERVAS_INICIO_VIAJE_DL", "PASAJEROS"),
    "capacidad": ("CONECTIVIDAD_AEREA_CAPACIDAD_DL", "ASIENTOS"),
    "trafico": ("CONECTIVIDAD_AEREA_TRAFICO_PASAJEROS_DL", "PASAJEROS"),
}


def _destino() -> "pd.io.formats.style.Styler | object":
    d = config.DATOS_PROCESADO / "conectividad_aerea"
    d.mkdir(parents=True, exist_ok=True)
    return d


def descargar_conjunto(clave: str, desde_anio: int = 2023) -> pd.DataFrame:
    """Descarga uno de los conjuntos de conectividad aérea, ya filtrado a Jerez."""
    endpoint, _ = CONJUNTOS[clave]
    df = dataestur.consultar(endpoint, **{"desde (año)": desde_anio, "Ciudad destino": CIUDAD})
    if df.empty:
        return df
    df = df[df["CIUDAD_DESTINO"] == CIUDAD].copy()
    # Fecha normalizada (primer día del mes) para poder ordenar y graficar
    df["fecha"] = pd.to_datetime(
        df["AÑO"].astype(int).astype(str) + "-" + df["MES"].astype(int).astype(str).str.zfill(2) + "-01",
        errors="coerce")
    return df.sort_values("fecha")


def resumen_mercados(busquedas: pd.DataFrame, reservas: pd.DataFrame) -> pd.DataFrame:
    """Por país emisor: búsquedas, reservas, **tasa de conversión**, antelación y estancia.

    La *conversión búsqueda→reserva* es el indicador que propone Dataestur: mide cuánta de la
    intención de viaje acaba materializándose. Un mercado que busca mucho y reserva poco es
    **demanda potencial no capturada**.
    """
    if busquedas.empty or reservas.empty:
        return pd.DataFrame()

    b = (busquedas[~busquedas["PAIS_ORIGEN"].isin(PSEUDO_PAISES)]
         .groupby("PAIS_ORIGEN")
         .agg(busquedas=("BUSQUEDAS", "sum"),
              antelacion_busqueda=("ANTELACION", "mean"),
              estancia_prevista=("ESTANCIA_MEDIA", "mean")))
    r = (reservas[~reservas["PAIS_ORIGEN"].isin(PSEUDO_PAISES)]
         .groupby("PAIS_ORIGEN")
         .agg(reservas=("PASAJEROS", "sum"),
              antelacion_reserva=("ANTELACION", "mean")))

    m = b.join(r, how="outer").fillna({"busquedas": 0, "reservas": 0})
    m["conversion_pct"] = (m["reservas"] / m["busquedas"] * 100).where(m["busquedas"] > 0)
    m = m.reset_index().rename(columns={"PAIS_ORIGEN": "pais"})
    return m.sort_values("busquedas", ascending=False).round(2)


def descargar_todo(desde_anio: int = 2023, verbose: bool = True) -> dict[str, pd.DataFrame]:
    """Descarga los cuatro conjuntos y calcula el resumen por mercado emisor."""
    config.asegurar_directorios()
    destino = _destino()
    datos: dict[str, pd.DataFrame] = {}

    if verbose:
        print(f"Conectividad aérea · destino: {CIUDAD}")

    for clave, (_, metrica) in CONJUNTOS.items():
        df = descargar_conjunto(clave, desde_anio=desde_anio)
        datos[clave] = df
        if df.empty:
            if verbose:
                print(f"  ⚠️ {clave}: sin datos")
            continue
        df.to_csv(destino / f"{clave}.csv", index=False)
        if verbose:
            ini, fin = df["fecha"].min(), df["fecha"].max()
            total = int(pd.to_numeric(df[metrica], errors="coerce").sum())
            print(f"  ✓ {clave:10} {len(df):>5} filas · {ini:%Y-%m} → {fin:%Y-%m} · "
                  f"{metrica.lower()}: {total:,}".replace(",", "."))

    mercados = resumen_mercados(datos.get("busquedas", pd.DataFrame()),
                                datos.get("reservas", pd.DataFrame()))
    if not mercados.empty:
        mercados.to_csv(destino / "mercados.csv", index=False)
        datos["mercados"] = mercados
        if verbose:
            print(f"\n  ✓ mercados.csv ({len(mercados)} países emisores)")
            top = mercados.head(5)
            print(f"\n  {'PAÍS':16} {'búsquedas':>11} {'reservas':>9} {'conv.':>7} {'antelac.':>9}")
            for _, x in top.iterrows():
                conv = f"{x['conversion_pct']:.2f}%" if pd.notna(x["conversion_pct"]) else "—"
                print(f"  {str(x['pais'])[:16]:16} {int(x['busquedas']):>11,} "
                      f"{int(x['reservas']):>9,} {conv:>7} {x['antelacion_busqueda']:>6.0f} d"
                      .replace(",", "."))
    return datos


if __name__ == "__main__":
    descargar_todo()
