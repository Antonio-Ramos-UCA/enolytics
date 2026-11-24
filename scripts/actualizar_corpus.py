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
    python3 scripts/actualizar_corpus.py --api                      # descarga y actualiza
    python3 scripts/actualizar_corpus.py --api --simular            # mira sin tocar nada
    python3 scripts/actualizar_corpus.py ~/Downloads/descarga.xlsx  # desde el panel web
    python3 scripts/actualizar_corpus.py descarga.xlsx --simular
    python3 scripts/actualizar_corpus.py descarga.xlsx --sin-bert   # deja el sentimiento

Con `--api` hace falta OUTSCRAPER_API_KEY en el entorno. Es lo que ejecuta el cron mensual.
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


# Margen que se resta a la fecha de la última reseña al pedir la tanda siguiente. Pedir
# exactamente desde ese día dejaría fuera cualquier reseña publicada el mismo día a una hora
# anterior, y una reseña editada puede además cambiar de fecha. Lo que se repita lo descarta
# la deduplicación, así que el margen no cuesta nada y cubre el borde.
MARGEN_DIAS = 3


def origen_api(verbose: bool = True):
    """Descarga de Outscraper lo posterior a la última reseña del corpus."""
    from enolytics.ingesta import resenas as ingesta
    corpus = pd.read_csv(config.DATOS_PROCESADO / "resenas.csv")
    ultima = pd.to_datetime(corpus["fecha"], errors="coerce", utc=True).max()
    desde = (ultima - pd.Timedelta(days=MARGEN_DIAS)).date()
    if verbose:
        print(f"Última reseña del corpus: {ultima.date()}. "
              f"Se pide desde el {desde} ({MARGEN_DIAS} días de margen).")
    return ingesta.descargar_nuevas(desde, verbose=verbose)


def _titulo(n: int, texto: str) -> None:
    print(f"\n{'─' * 70}\n{n}. {texto}\n{'─' * 70}")


def simular(origen) -> dict:
    """Dice qué entraría, sin tocar ningún archivo."""
    nuevas = etl.normalizar_export_outscraper(origen)
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


def actualizar(descarga, con_bert: bool = True, origen: str = "panel") -> None:
    t0 = time.time()

    _titulo(1, "Fusionar la descarga con el corpus")
    resumen = etl.fusionar_export(descarga)
    etl.registrar_actualizacion(resumen, origen=origen)
    if resumen["nuevas"] == 0:
        print("\nNo hay reseñas nuevas. La cadena se detiene aquí: "
              "nada de lo que viene después cambiaría.")
        print("La pasada queda anotada igualmente en el historial, con un cero: así se")
        print("distingue un mes sin novedades de un robot que no llegó a ejecutarse.")
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
    por_api = "--api" in sys.argv

    if por_api:
        try:
            descarga, etiqueta = origen_api(), "api"
        except RuntimeError as e:
            # Falta la clave o la biblioteca: es un fallo de configuración, no un error del
            # programa. En el registro de GitHub Actions se lee mejor una línea que una traza.
            sys.exit(f"\n✗ {e}")
    else:
        if not args:
            sys.exit(__doc__)
        descarga = Path(args[0]).expanduser()
        etiqueta = "panel"
        if not descarga.exists():
            sys.exit(f"No existe el archivo: {descarga}")

    if "--simular" in sys.argv:
        simular(descarga)
    else:
        actualizar(descarga, con_bert="--sin-bert" not in sys.argv, origen=etiqueta)


if __name__ == "__main__":
    main()
