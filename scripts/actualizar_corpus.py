"""Incorpora al corpus una descarga nueva de reseñas y rehace lo que depende de ella.

Para qué
--------
El dashboard no calcula nada en vivo: lee los CSV de `datos/procesado/`. Actualizar los datos
no es, por tanto, descargar reseñas, sino volver a recorrer la cadena que produce esos CSV.
Este guion la recorre entera a partir de un export de Outscraper.

    descarga (.xlsx)
      → etl.resenas.fusionar_export      resenas.csv, censo_google.csv
      → nlp.idioma                       idioma y segmento de lo nuevo
      → nlp.sentimiento                  sentimiento_atributos.csv  (el paso caro)
      → analitica.prca                   prca_kano.csv
      → analitica.competidores           competidores.csv

Cada paso solo toca lo que ha entrado: la deduplicación va por el identificador de reseña de
Google, el idioma se detecta únicamente en las filas sin anotar y el BERT puntúa solo las
reseñas que aún no estaban puntuadas. Los dos últimos pasos sí recalculan sobre el corpus
completo, porque son agregados del destino y cambian al cambiar cualquier reseña.

Lo que NO hace, a propósito: recalibrar umbrales. La banda de indiferencia del IPCA sale del
percentil 25 de las brechas, y si se recalculara en cada pasada cambiaría en silencio lo que
la plataforma declara. Los umbrales se re-derivan a mano, cuando toque.

Antes de escribir
-----------------
Los cinco CSV están versionados en git, de modo que cualquier paso se deshace con
`git checkout datos/procesado/`. Aun así, conviene mirar primero qué va a entrar:

    python3 scripts/actualizar_corpus.py descarga.xlsx --simular

Uso
---
    python3 scripts/actualizar_corpus.py ~/Downloads/outscraper_nov2026.xlsx
    python3 scripts/actualizar_corpus.py descarga.xlsx --simular    # no escribe nada
    python3 scripts/actualizar_corpus.py descarga.xlsx --sin-bert   # deja el sentimiento
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from enolytics import config  # noqa: E402
from enolytics.etl import resenas as etl  # noqa: E402


def _titulo(n: int, texto: str) -> None:
    print(f"\n{'─' * 70}\n{n}. {texto}\n{'─' * 70}")


def simular(ruta_xlsx: Path) -> dict:
    """Dice qué entraría, sin tocar ningún archivo."""
    nuevas = etl.normalizar_export_outscraper(ruta_xlsx)
    viejas = pd.read_csv(config.DATOS_PROCESADO / "resenas.csv")
    conocidas = set(viejas["resena_id"].astype(str))
    entran = nuevas[~nuevas["resena_id"].astype(str).isin(conocidas)]

    print(f"Export:  {len(nuevas)} reseñas")
    print(f"  ya en el corpus: {len(nuevas) - len(entran)}")
    print(f"  nuevas:          {len(entran)}")
    if not entran.empty:
        fechas = pd.to_datetime(entran["fecha"], errors="coerce", utc=True)
        print(f"  van del {fechas.min().date()} al {fechas.max().date()}")
        print(f"  en {entran['bodega'].nunique()} bodegas")
        sin_bodega = int(entran["bodega"].isna().sum())
        if sin_bodega:
            print(f"  ⚠ {sin_bodega} sin bodega asignada: revisa el mapa de place_id")
        con_texto = int((entran["texto"].fillna("").str.strip() != "").sum())
        print(f"  con texto (irán al BERT): {con_texto}")
    print("\nNo se ha escrito nada. Quita --simular para aplicarlo.")
    return {"nuevas": len(entran)}


def actualizar(ruta_xlsx: Path, con_bert: bool = True) -> None:
    t0 = time.time()

    _titulo(1, "Fusionar la descarga con el corpus")
    resumen = etl.fusionar_export(ruta_xlsx)
    if resumen["nuevas"] == 0:
        print("\nNo hay reseñas nuevas. La cadena se detiene aquí: "
              "nada de lo que viene después cambiaría.")
        return

    _titulo(2, "Idioma y segmento de las reseñas nuevas")
    from enolytics.nlp import idioma
    idioma.procesar_y_guardar(solo_nuevas=True)

    if con_bert:
        _titulo(3, "Sentimiento por atributo (BERT, solo lo nuevo)")
        from enolytics.nlp import sentimiento
        sentimiento.calcular_y_guardar(incremental=True)
    else:
        _titulo(3, "Sentimiento por atributo — OMITIDO (--sin-bert)")
        print("⚠ El sentimiento queda desfasado respecto al corpus. Los dos pasos siguientes")
        print("  trabajarán sobre datos incompletos. Úsalo solo para probar la fusión.")

    _titulo(4, "PRCA y perfil Kano")
    from enolytics.analitica import prca
    prca.calcular_y_guardar()

    _titulo(5, "Posición competitiva")
    from enolytics.analitica import competidores
    competidores.calcular_y_guardar()

    print(f"\n{'═' * 70}")
    print(f"Corpus: {resumen['corpus_antes']} → {resumen['corpus_despues']} reseñas "
          f"(+{resumen['nuevas']}), hasta {resumen['fecha_mas_reciente']}")
    print(f"Tiempo: {time.time() - t0:.0f} s")
    print("\nSiguiente paso, a mano: revisar el diff y hacer commit. Streamlit Cloud")
    print("redespliega solo al empujar a main.")
    print("  git diff --stat datos/procesado/")
    print("  git checkout datos/procesado/     ← para deshacerlo todo")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    ruta = Path(args[0]).expanduser()
    if not ruta.exists():
        sys.exit(f"No existe el archivo: {ruta}")

    if "--simular" in sys.argv:
        simular(ruta)
    else:
        actualizar(ruta, con_bert="--sin-bert" not in sys.argv)


if __name__ == "__main__":
    main()
