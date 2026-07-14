"""Detección del idioma de las reseñas (proxy de procedencia del visitante).

Enriquece `datos/procesado/resenas.csv` con dos columnas: `idioma` (código ISO) y
`segmento_idioma`. Se ejecuta **una sola vez, fuera del dashboard**, y el resultado se guarda en
el CSV: así el cuadro de mando no necesita `langdetect` ni gasta tiempo en cada carga.

⚠️ TRES CAUTELAS METODOLÓGICAS (van etiquetadas en el dashboard como 🟡 estimado):

1. **Idioma ≠ nacionalidad.** Un mexicano o un argentino escriben en español y son turistas
   *internacionales*; un español puede escribir en inglés. Por eso **no** hablamos de "turista
   nacional/extranjero", sino de **idioma de la reseña**. Es menos vistoso, pero es lo cierto.

2. **Un tercio de las reseñas no tiene texto** (solo estrellas): a esas no se les puede detectar
   idioma jamás. Todo porcentaje se calcula sobre las reseñas *con texto suficiente*, y el
   dashboard lo dice.

3. **Los textos muy cortos rompen al detector** ("Excelente", "Muy bien"). Se exige un mínimo de
   `MIN_CARACTERES`; por debajo, el idioma queda como "Sin determinar" en lugar de arriesgar un
   dato falso.

Uso:
    python3 -m enolytics.nlp.idioma
"""
from __future__ import annotations

import pandas as pd

from enolytics import config

# Por debajo de este nº de caracteres, la detección es poco fiable → no se arriesga
MIN_CARACTERES = 20

SEGMENTO_HISPANO = "Hispanohablante"
SEGMENTO_INTERNACIONAL = "Internacional (no hispanohablante)"
SEGMENTO_DESCONOCIDO = "Sin determinar"

# Nombres legibles de los idiomas más frecuentes en el enoturismo
NOMBRES_IDIOMA = {
    "es": "Español", "en": "Inglés", "de": "Alemán", "fr": "Francés", "it": "Italiano",
    "nl": "Neerlandés", "pt": "Portugués", "sv": "Sueco", "da": "Danés", "no": "Noruego",
    "fi": "Finés", "pl": "Polaco", "ru": "Ruso", "ca": "Catalán", "eu": "Euskera",
    "gl": "Gallego", "ja": "Japonés", "zh-cn": "Chino", "ko": "Coreano", "tr": "Turco",
    "cs": "Checo", "ro": "Rumano", "hu": "Húngaro", "el": "Griego",
}


def _detector():
    """Devuelve la función de detección, con semilla fija para que sea REPRODUCIBLE.

    `langdetect` es probabilístico: sin fijar la semilla, el mismo texto puede dar resultados
    distintos entre ejecuciones. En investigación eso es inaceptable.
    """
    from langdetect import DetectorFactory, detect
    DetectorFactory.seed = 0
    return detect


def detectar_idioma(texto: str, detect=None) -> str | None:
    """Idioma de un texto (código ISO), o None si no es fiable determinarlo."""
    if detect is None:
        detect = _detector()
    if not isinstance(texto, str):
        return None
    t = texto.strip()
    if len(t) < MIN_CARACTERES:
        return None
    try:
        return detect(t)
    except Exception:
        return None


def segmento(idioma: str | None) -> str:
    """Agrupa el idioma en el segmento que usamos en el dashboard."""
    if not idioma:
        return SEGMENTO_DESCONOCIDO
    return SEGMENTO_HISPANO if idioma == "es" else SEGMENTO_INTERNACIONAL


def nombre_idioma(codigo: str | None) -> str:
    if not codigo:
        return SEGMENTO_DESCONOCIDO
    return NOMBRES_IDIOMA.get(codigo, codigo)


def anotar_idiomas(resenas: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Añade las columnas `idioma` y `segmento_idioma` al DataFrame de reseñas."""
    detect = _detector()
    df = resenas.copy()
    df["idioma"] = df["texto"].map(lambda t: detectar_idioma(t, detect))
    df["segmento_idioma"] = df["idioma"].map(segmento)

    if verbose:
        n = len(df)
        det = df["idioma"].notna().sum()
        print(f"Reseñas: {n} · idioma detectado en {det} ({det / n * 100:.1f}%)")
        print(f"  (el resto no tiene texto o es más corto de {MIN_CARACTERES} caracteres)")
        print("\nSegmentos:")
        for seg, k in df["segmento_idioma"].value_counts().items():
            print(f"  {seg:36} {k:>5}  ({k / n * 100:5.1f}% del total)")
        print("\nIdiomas detectados (top 10):")
        for cod, k in df["idioma"].value_counts().head(10).items():
            print(f"  {nombre_idioma(cod):14} ({cod:5}) {k:>5}  ({k / det * 100:5.1f}% de los detectados)")
    return df


def procesar_y_guardar(verbose: bool = True) -> pd.DataFrame:
    """Detecta el idioma de las reseñas ya procesadas y reescribe `resenas.csv`."""
    ruta = config.DATOS_PROCESADO / "resenas.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}. Procesa antes las reseñas.")
    df = pd.read_csv(ruta)
    df = anotar_idiomas(df, verbose=verbose)
    df.to_csv(ruta, index=False)
    if verbose:
        print(f"\n✓ Guardado en {ruta.name} (columnas nuevas: idioma, segmento_idioma)")
    return df


if __name__ == "__main__":
    procesar_y_guardar()
