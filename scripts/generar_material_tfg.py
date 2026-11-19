"""Genera el material de trabajo del TFG de Daniela (Excel + figuras).

El trabajo
----------
Comparar **qué valora el turista nacional y qué el internacional** en las bodegas del
Marco de Jerez, mediante dos matrices importancia-desempeño construidas sobre 10.972 reseñas.
Es una pregunta de gestión de destinos, no de medición: a un tribunal de Turismo le interesa
saber si el destino debe atender a una agenda o a dos.

Qué entrega
-----------
Un Excel en `docs/tfg/daniela/material/` y tres figuras listas para el documento y para las
diapositivas de la defensa.

Dos decisiones metodológicas que hay que saber defender
--------------------------------------------------------
1. **El desempeño NO son las estrellas, es el sentimiento hacia el atributo.** La nota es de la
   visita entera: una reseña de 5★ que dice *«carísimo pero merece la pena»* asignaría
   desempeño 5 al precio, que es falso. Se usa el sentimiento frase a frase (BERT multilingüe),
   siguiendo a Bi et al. (2019) y Zhang et al. (2021).
2. **Los umbrales son COMUNES a los dos segmentos.** Si cada matriz se partiera por sus propias
   medias, un atributo podría «cambiar de cuadrante» solo porque la rejilla se ha movido, no
   porque el visitante opine distinto. Con una rejilla única, el movimiento es real. Se calculan
   sobre el conjunto de reseñas con idioma determinado.

La importancia se mide aquí por **frecuencia relativa**: qué porcentaje de las reseñas de cada
segmento menciona el atributo. Es la medida clásica de importancia inferida, y es la que permite
comparar segmentos de tamaño distinto.

Seudonimización
---------------
La columna `autor` y el enlace a la reseña **no salen de aquí**: se sustituyen por un
identificador estable derivado del `resena_id`. Es RGPD, no una preferencia. Ojo al residuo que
no se puede automatizar: hay nombres de persona dentro del TEXTO de algunas reseñas (guías que
el visitante menciona, o firmas). Ver el aviso en la hoja LEEME.

Uso
---
    python3 scripts/generar_material_tfg.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

PROC = RAIZ / "datos" / "procesado"
SALIDA = RAIZ / "docs" / "tfg" / "daniela" / "material"

NACIONAL = "Nacional"
INTERNAC = "Internacional"
SEGMENTOS = [NACIONAL, INTERNAC]
CORTO = {NACIONAL: NACIONAL, INTERNAC: INTERNAC}

# Lenguas de España. El castellano y las cooficiales marcan al visitante NACIONAL.
# El catalán estaba cayendo en "internacional", que es sencillamente falso: son españoles.
LENGUAS_ESPANA = {"es", "ca", "gl", "eu"}

# Por debajo de esto, el dato del atributo en ese segmento es demasiado fino para sostener nada.
MIN_FIABLE = 50

CUADRANTES = {
    (True, False): "Concéntrese aquí",
    (True, True): "Mantener el buen trabajo",
    (False, False): "Baja prioridad",
    (False, True): "Posible exceso",
}


def seudonimo(resena_id: str) -> str:
    """Identificador estable y no reversible a partir del id de la reseña."""
    return "V-" + hashlib.sha256(str(resena_id).encode()).hexdigest()[:8].upper()


def segmentar(idioma) -> str:
    """Nacional / Internacional a partir del idioma detectado.

    El idioma es un PROXY de procedencia, y el proxy tiene dos fugas. Una se corrige y la
    otra se mide:
    · Se corrige: el catalán (y el gallego o el euskera, si aparecen) es lengua de España.
      Quien escribe en catalán es un visitante nacional, no internacional.
    · Se mide: un latinoamericano escribe en español y se contaría como nacional. Según
      Dataestur, solo el **0,87 %** de las búsquedas de vuelo internacionales hacia Jerez
      procede de países hispanohablantes (93.918 de 10.836.376), así que el sesgo por esa vía
      es inferior al 1 %. Es la cifra que justifica el diseño, y va citada en el TFG.
    """
    if not isinstance(idioma, str) or not idioma:
        return "Sin determinar"
    return NACIONAL if idioma.lower() in LENGUAS_ESPANA else INTERNAC


def cargar():
    res = pd.read_csv(PROC / "resenas.csv")
    sa = pd.read_csv(PROC / "sentimiento_atributos.csv")
    res["segmento"] = res["idioma"].map(segmentar)
    seg = res[["resena_id", "segmento"]].drop_duplicates("resena_id")
    d = (sa.drop_duplicates(["resena_id", "atributo"])
           .merge(seg, on="resena_id", how="left"))
    return res, d[d["segmento"].isin(SEGMENTOS)]


def tabla_segmento(d: pd.DataFrame, segmento: str) -> pd.DataFrame:
    """Importancia (% de reseñas del segmento que lo mencionan) y desempeño (sentimiento)."""
    sub = d[d["segmento"] == segmento]
    total = sub["resena_id"].nunique()
    t = (sub.groupby("atributo")
            .agg(menciones=("resena_id", "nunique"),
                 desempeno=("sentimiento", "mean"))
            .reset_index())
    t["importancia"] = (t["menciones"] / total * 100).round(2)
    t["desempeno"] = t["desempeno"].round(3)
    t["segmento"] = segmento
    t["muestra_fina"] = t["menciones"] < MIN_FIABLE
    return t.sort_values("importancia", ascending=False)


def umbrales(tablas: list[pd.DataFrame]) -> tuple[float, float]:
    """Rejilla COMÚN: media de los dos segmentos juntos. Ver la cabecera del módulo."""
    todo = pd.concat(tablas)
    return todo["importancia"].mean(), todo["desempeno"].mean()


def con_cuadrante(t: pd.DataFrame, u_i: float, u_d: float) -> pd.DataFrame:
    t = t.copy()
    t["cuadrante"] = [CUADRANTES[(i >= u_i, d >= u_d)]
                      for i, d in zip(t["importancia"], t["desempeno"])]
    return t


# --------------------------------------------------------------------------- #
# Figuras
# --------------------------------------------------------------------------- #
def _marco(ax, u_i, u_d, ejes, titulo):
    ax.axvline(u_i, color="#8B877E", lw=1, ls="--")
    ax.axhline(u_d, color="#8B877E", lw=1, ls="--")
    ax.margins(x=0.18, y=0.14)
    ax.set_xlabel(ejes[0]); ax.set_ylabel(ejes[1])
    ax.set_title(titulo, fontsize=12, loc="left", pad=12)
    ax.spines[["top", "right"]].set_visible(False)


def _esquinas(ax):
    xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
    for x, y, txt, ha, va in [(xmax, ymin, "Concéntrese aquí", "right", "bottom"),
                              (xmax, ymax, "Mantener el buen trabajo", "right", "top"),
                              (xmin, ymin, "Baja prioridad", "left", "bottom"),
                              (xmin, ymax, "Posible exceso", "left", "top")]:
        ax.text(x, y, txt, ha=ha, va=va, fontsize=8.5, style="italic",
                color="#8B877E", alpha=.9)


EJES = ("Importancia (% de reseñas del segmento que lo mencionan)",
        "Desempeño (sentimiento hacia el atributo, 1-5)")


def figura_simple(t, u_i, u_d, titulo, color, destino):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=160)
    _marco(ax, u_i, u_d, EJES, titulo)
    ax.scatter(t["importancia"], t["desempeno"], s=95, color=color, zorder=3)
    medio = (t["importancia"].min() + t["importancia"].max()) / 2
    for _, r in t.iterrows():
        der = r["importancia"] > medio
        etq = r["atributo"] + (" *" if r["muestra_fina"] else "")
        ax.annotate(etq, (r["importancia"], r["desempeno"]),
                    textcoords="offset points", xytext=(-10, 8) if der else (10, 8),
                    ha="right" if der else "left", fontsize=9)
    _esquinas(ax)
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


def figura_movimiento(th, ti, u_i, u_d, destino):
    """Las dos nubes sobre la MISMA rejilla, con una flecha por atributo.

    Es la figura de la defensa: de un vistazo se ve hacia dónde se mueve cada atributo al
    pasar del turista nacional al internacional.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7), dpi=160)
    j = th.merge(ti, on="atributo", suffixes=("_h", "_i"))
    for _, r in j.iterrows():
        ax.annotate("", xy=(r["importancia_i"], r["desempeno_i"]),
                    xytext=(r["importancia_h"], r["desempeno_h"]),
                    arrowprops=dict(arrowstyle="->", color="#C9C5BA", lw=1.6,
                                    shrinkA=7, shrinkB=7))
    ax.scatter(j["importancia_h"], j["desempeno_h"], s=95, color="#2a78d6",
               zorder=3, label="Turista nacional")
    ax.scatter(j["importancia_i"], j["desempeno_i"], s=95, color="#eb6834",
               zorder=3, label="Turista internacional")
    _marco(ax, u_i, u_d, EJES,
           "Qué cambia del turista nacional al internacional")
    medio = j[["importancia_h", "importancia_i"]].values.mean()
    for _, r in j.iterrows():
        der = r["importancia_i"] > medio
        ax.annotate(r["atributo"], (r["importancia_i"], r["desempeno_i"]),
                    textcoords="offset points", xytext=(-11, -16) if der else (11, -16),
                    ha="right" if der else "left", fontsize=9)
    _esquinas(ax)
    ax.legend(frameon=False, loc="lower left", fontsize=9,
              bbox_to_anchor=(0, 1.02), ncol=2)
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


LEEME = [
    ("GUION DE INTERPRETACION — TFG Daniela", ""),
    ("", ""),
    ("LA PREGUNTA DEL TRABAJO",
     "Valoran lo mismo el turista nacional y el internacional? O el Marco de Jerez "
     "deberia atender a dos agendas distintas?"),
    ("", ""),
    ("Que hay en este libro", ""),
    ("Resenas", "Las 10.972 resenas SEUDONIMIZADAS, con su segmento. En vez del nombre del "
                "autor hay un codigo estable (V-XXXXXXXX). Hay una columna por atributo con el "
                "sentimiento de esa resena hacia el (1 a 5; vacia si no lo menciona). Usa los "
                "filtros: por ejemplo, segmento = Internacional y Organizacion y reserva no vacia "
                "da las 202 resenas que tienes que leer para el epigrafe 5.2; por debajo de 3, "
                "las negativas."),
    ("COMO SE DEFINE EL SEGMENTO",
     "Por el IDIOMA detectado de la resena. Castellano, catalan, gallego o euskera = turista NACIONAL; cualquier otro = INTERNACIONAL. Es un proxy, y tiene dos fugas: una se corrige y la otra se mide. Se corrige: el catalan es lengua de Espana, asi que quien escribe en catalan es nacional (39 resenas que antes caian en internacional). Se mide: un latinoamericano escribe en espanol y se contaria como nacional, pero segun Dataestur solo el 0,87 % de las busquedas de vuelo internacionales hacia Jerez procede de paises hispanohablantes (93.918 de 10.836.376). CITA ESA CIFRA en la metodologia: es lo que justifica el diseno."),
    ("Comparacion", "LA HOJA CLAVE. Que porcentaje de las resenas de cada segmento menciona "
                    "cada atributo, con que sentimiento, y si cambia de cuadrante."),
    ("IPA nacional", "La matriz del turista nacional: escribe en castellano, catalan, gallego o euskera."),
    ("IPA internacional", "La matriz del turista internacional: escribe en cualquier otro idioma."),
    ("Atributos", "Tabla base por segmento, con menciones en bruto."),
    ("", ""),
    ("AVISO RGPD",
     "El TEXTO de algunas resenas contiene nombres de personas: guias que el visitante menciona "
     "('nuestra guia Lucia') o firmas de quien escribe. No se han borrado porque un filtro "
     "automatico se llevaria por delante nombres del dominio: Pedro Ximenez es un vino, y Pedro "
     "Romero o Luis Perez son bodegas. REGLA: si citas una resena como ejemplo, sustituye "
     "cualquier nombre de persona por [guia] o [visitante]."),
    ("", ""),
    ("Como se leen los cuadrantes", ""),
    ("Concentrese aqui", "Importancia alta, desempeno bajo. Prioridad de actuacion."),
    ("Mantener el buen trabajo", "Importancia alta, desempeno alto. Va bien: sostenerlo."),
    ("Baja prioridad", "Importancia baja, desempeno bajo. No urge."),
    ("Posible exceso", "Importancia baja, desempeno alto. Se invierte de mas."),
    ("", ""),
    ("DOS DECISIONES QUE TIENES QUE SABER DEFENDER", ""),
    ("1. El desempeno no son las estrellas",
     "Es el sentimiento hacia ESE atributo, frase a frase. La nota en estrellas es de la visita "
     "entera: una resena de 5 estrellas que dice 'carisimo pero merece la pena' daria desempeno "
     "5 al precio, que es falso. Es lo que proponen Bi et al. (2019) y Zhang et al. (2021)."),
    ("2. Los umbrales son COMUNES a los dos segmentos",
     "Si cada matriz se partiera por sus propias medias, un atributo podria cambiar de cuadrante "
     "solo porque la rejilla se movio. Con una rejilla unica, el movimiento es real. Los valores "
     "exactos estan escritos en cada hoja: citalos en la metodologia."),
    ("", ""),
    ("EL HALLAZGO, Y COMO CONTARLO", ""),
    ("Los ocho atributos comparten cuadrante en los dos segmentos",
     "Eso NO es que no haya resultado: es el resultado. El destino no necesita dos estrategias distintas de prioridades. Lo que cambia no es QUE priorizar, sino cuanto PESA cada cosa para cada visitante."),
    ("Organizacion y reserva: 2,6 % frente a 13,3 %",
     "El visitante internacional la menciona cinco veces mas, pero sobre todo para bien: dos de cada tres de sus menciones son positivas. El nacional la menciona poco y con mas critica: su desempeno, 3,24, es el mas bajo de toda la comparacion (el internacional, 3,70). Mas menciones no significa mas quejas: presenta siempre la frecuencia junto al reparto entre positivas y negativas."),
    ("Una pregunta abierta para la discusion",
     "La auditoria web del proyecto dice que la mayoria de bodegas no tiene reserva online ni version en ingles. Cabria esperar que el extranjero se quejara mas, y pasa lo contrario. Por que? Lee las resenas de organizacion de cada segmento (son pocas) y contrasta hipotesis: intermediarios que gestionan la visita del internacional, o diferencias del diccionario entre idiomas ('booking' es neutro; 'espera' o 'cola' ya son queja)."),
    ("Instalaciones: 62,0 % frente a 44,6 %",
     "Al reves: el visitante nacional habla de las instalaciones 17 puntos mas que el internacional. Por que? Leelo en las resenas de cada segmento antes de proponer una explicacion."),
    ("Las preguntas que tienes que responder",
     "1) Por que el internacional menciona mas la organizacion y la valora mejor. 2) Por que el nacional habla mucho mas de las instalaciones. 3) Que implica para la gestion una agenda de prioridades comun con distinto peso en cada segmento. Las respuestas estan en el texto de las resenas, no en las tablas."),
    ("", ""),
    ("LIMITACIONES QUE DEBES DECLARAR", ""),
    ("El idioma es un proxy de la procedencia",
     "No es lo mismo escribir en espanol que residir en Espana. Lo honesto es declararlo Y acotarlo: el sesgo por latinoamericanos contados como nacionales afecta a menos del 1 % de la demanda internacional hacia Jerez (Dataestur). Declaralo en Metodologia, no solo en limitaciones."),
    ("Muestra fina en un atributo",
     "Entorno y vinedo tiene solo 37 menciones en el segmento internacional. Va marcado con un "
     "asterisco en las figuras. No construyas ninguna conclusion sobre el."),
    ("Las resenas no son muestra aleatoria",
     "Quien escribe resenas tiende a los extremos, y solo cuentan los usuarios de Google."),
    ("Efecto techo",
     "El 75,9 % de las valoraciones son de 5 estrellas, asi que casi no hay margen por encima de "
     "la media. Senalarlo suma: los articulos que vas a citar trabajan con corpus mas repartidos "
     "y no se enfrentan a este problema."),
    ("", ""),
    ("Cifras para citar", ""),
    ("Resenas totales", "10.972"),
    ("Bodegas", "41"),
    ("Resenas con atributo detectado", "6.542"),
    ("  de ellas, nacionales", "4.893"),
    ("  de ellas, internacionales", "1.556"),
    ("  sin idioma determinado", "132 (solo el 2 %)"),
    ("Periodo", "22/07/2011 - 06/07/2026"),
    ("Valoraciones de 5 estrellas", "75,9 %"),
]


def figura_brechas(comp: pd.DataFrame, destino: Path) -> None:
    """Barras divergentes: cuánto más (o menos) habla de cada atributo el internacional.

    Es LA figura del trabajo. La matriz de cuadrantes no enseña esto, porque los dos
    segmentos comparten cuadrante en los ocho atributos: lo que los separa no es la
    prioridad, es el PESO que le dan.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c = comp.sort_values("brecha_importancia_pp")
    colores = ["#2a78d6" if v < 0 else "#eb6834" for v in c["brecha_importancia_pp"]]
    fig, ax = plt.subplots(figsize=(9.5, 5.6), dpi=160)
    ax.barh(c["atributo"], c["brecha_importancia_pp"], color=colores, height=.66)
    ax.axvline(0, color="#1C1B19", lw=1)
    for y, (v, fina) in enumerate(zip(c["brecha_importancia_pp"], c["muestra_fina_internac"])):
        ax.text(v + (.5 if v >= 0 else -.5), y, f"{v:+.1f}" + (" *" if fina else ""),
                va="center", ha="left" if v >= 0 else "right", fontsize=9)
    ax.set_xlabel("Diferencia en % de reseñas que mencionan el atributo "
                  "(puntos porcentuales)")
    ax.set_title("De qué habla más cada segmento", fontsize=12.5, loc="left", pad=26)
    ax.text(0, 1.045, "← lo menciona más el turista NACIONAL        "
                      "lo menciona más el INTERNACIONAL →",
            transform=ax.transAxes, fontsize=9, color="#57544E")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)
    ax.margins(x=.16)
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    res, d = cargar()

    th = tabla_segmento(d, NACIONAL)
    ti = tabla_segmento(d, INTERNAC)
    u_i, u_d = umbrales([th, ti])
    th, ti = con_cuadrante(th, u_i, u_d), con_cuadrante(ti, u_i, u_d)

    cols = ["atributo", "menciones", "importancia", "desempeno", "cuadrante", "muestra_fina"]
    comp = (th[cols].rename(columns={c: c + "_nac" for c in cols[1:]})
            .merge(ti[cols].rename(columns={c: c + "_internac" for c in cols[1:]}),
                   on="atributo"))
    comp["brecha_importancia_pp"] = (comp["importancia_internac"]
                                     - comp["importancia_nac"]).round(2)
    comp["brecha_desempeno"] = (comp["desempeno_internac"]
                                - comp["desempeno_nac"]).round(3)
    comp["CAMBIA_CUADRANTE"] = comp["cuadrante_nac"] != comp["cuadrante_internac"]
    comp = comp.sort_values("brecha_importancia_pp")

    # --- Figuras --------------------------------------------------------------
    figura_simple(th, u_i, u_d, "IPA del Marco — turista NACIONAL",
                  "#2a78d6", SALIDA / "ipa_nacional.png")
    figura_simple(ti, u_i, u_d, "IPA del Marco — turista INTERNACIONAL",
                  "#eb6834", SALIDA / "ipa_internacional.png")
    figura_movimiento(th, ti, u_i, u_d, SALIDA / "ipa_movimiento.png")
    figura_brechas(comp, SALIDA / "brechas_por_segmento.png")

    # --- Excel ----------------------------------------------------------------
    r = res.copy()
    r["visitante"] = r["resena_id"].map(seudonimo)
    # Una columna por atributo con el sentimiento de la reseña hacia él (vacía si no lo menciona),
    # para que la estudiante pueda filtrar y LEER las reseñas de un atributo y un segmento: las
    # preguntas abiertas del plan (5.2, instalaciones) se responden con el texto, no con las tablas.
    piv = d.pivot_table(index="resena_id", columns="atributo",
                        values="sentimiento", aggfunc="mean").round(2)
    atributos = list(th.sort_values("importancia", ascending=False)["atributo"])
    r = r.merge(piv[atributos], left_on="resena_id", right_index=True, how="left")
    r = r[["visitante", "bodega", "puntuacion", "fecha", "idioma", "segmento"]
          + atributos + ["texto"]]
    assert "autor" not in r.columns and "enlace_resena" not in r.columns

    destino = SALIDA / "material_tfg_daniela.xlsx"
    with pd.ExcelWriter(destino, engine="xlsxwriter") as xl:
        pd.DataFrame(LEEME, columns=["", " "]).to_excel(xl, sheet_name="LEEME", index=False)
        comp.to_excel(xl, sheet_name="Comparacion", index=False, startrow=4)
        th.to_excel(xl, sheet_name="IPA nacional", index=False, startrow=3)
        ti.to_excel(xl, sheet_name="IPA internacional", index=False, startrow=3)
        pd.concat([th, ti]).to_excel(xl, sheet_name="Atributos", index=False)
        r.to_excel(xl, sheet_name="Resenas", index=False)
        hr = xl.sheets["Resenas"]
        hr.autofilter(0, 0, len(r), len(r.columns) - 1)
        hr.freeze_panes(1, 0)

        neg = xl.book.add_format({"bold": True})
        for hoja in ["IPA nacional", "IPA internacional", "Comparacion"]:
            h = xl.sheets[hoja]
            h.write(0, 0, f"Umbral de importancia (comun a los dos segmentos): {u_i:.3f} %", neg)
            h.write(1, 0, f"Umbral de desempeno  (comun a los dos segmentos): {u_d:.3f}", neg)
        h = xl.sheets["Comparacion"]
        h.write(2, 0, "brecha_importancia_pp = cuanto mas (o menos) habla de ello el "
                      "internacional, en puntos porcentuales.", neg)
        h.write(3, 0, f"{int(comp['CAMBIA_CUADRANTE'].sum())} atributos cambian de cuadrante "
                      f"entre segmentos.", neg)
        for hoja in xl.sheets.values():
            hoja.set_column(0, 0, 32)
            hoja.set_column(1, 14, 20)

    print(f"Excel:   {destino}")
    print(f"Figuras: ipa_nacional.png · ipa_internacional.png · ipa_movimiento.png")
    print(f"\nUmbrales comunes: importancia {u_i:.3f} % · desempeño {u_d:.3f}")
    print(f"\nAtributos que CAMBIAN de cuadrante: {int(comp['CAMBIA_CUADRANTE'].sum())}")
    for _, x in comp[comp["CAMBIA_CUADRANTE"]].iterrows():
        print(f"  · {x['atributo']:28s} {x['cuadrante_nac']:25s} -> {x['cuadrante_internac']}")
    print("\nMayores brechas de importancia (pp, + = habla más el internacional):")
    for _, x in comp.iloc[[0, 1, -2, -1]].iterrows():
        aviso = "  ⚠ muestra fina" if x["muestra_fina_internac"] else ""
        print(f"  · {x['atributo']:28s} {x['brecha_importancia_pp']:+6.2f} pp{aviso}")


if __name__ == "__main__":
    main()
