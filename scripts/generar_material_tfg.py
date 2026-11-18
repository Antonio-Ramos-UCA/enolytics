"""Genera el material de trabajo del TFG de Daniela (Excel + figuras).

Qué entrega
-----------
Un único Excel en `docs/tfg/daniela/material/` con todo lo que necesita para escribir, y
las dos matrices IPA en PNG para que las pegue en el documento y en las diapositivas.

Por qué existe este script y no un Excel hecho a mano
-----------------------------------------------------
1. **Reproducibilidad.** Si los datos cambian, se vuelve a ejecutar. Un Excel tocado a mano
   deja de corresponderse con el proyecto en cuanto alguien lo edita.
2. **Seudonimización garantizada.** La columna `autor` y el enlace a la reseña **no salen de
   aquí**: se sustituyen por un identificador estable derivado del `resena_id`. Es RGPD, no una
   preferencia. Ver el pendiente del 18/11/2026 en `docs/pendientes.md`.

Las dos formas de medir la importancia
---------------------------------------
Es el eje del TFG, así que el Excel trae **las dos**, cada una en su hoja:

- **Clásica (frecuencia):** importancia = nº de reseñas que mencionan el atributo;
  desempeño = nota media en estrellas de esas reseñas.
- **Por impacto (PRCA):** importancia = cuánto mueve la valoración global el sentimiento hacia
  el atributo (regresión de penalización-recompensa); desempeño = sentimiento medio hacia ese
  atributo, no las estrellas de la visita entera.

Los umbrales que parten los cuadrantes son **la media de cada eje**, que es el criterio
clásico de Martilla y James. Van escritos en la hoja para que Daniela pueda citarlos.

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

CUADRANTES = {
    (True, False): "Concéntrese aquí",
    (True, True): "Mantener el buen trabajo",
    (False, False): "Baja prioridad",
    (False, True): "Posible exceso",
}


def seudonimo(resena_id: str) -> str:
    """Identificador estable y no reversible a partir del id de la reseña.

    Estable: la misma reseña da siempre el mismo código, así que Daniela puede referirse a
    una reseña concreta sin nombrar a nadie. No reversible: del código no se vuelve al autor.
    """
    return "V-" + hashlib.sha256(resena_id.encode()).hexdigest()[:8].upper()


def _cuadrantes(df: pd.DataFrame, col_imp: str, col_des: str) -> pd.DataFrame:
    """Asigna cuadrante partiendo cada eje por su media."""
    u_imp, u_des = df[col_imp].mean(), df[col_des].mean()
    df = df.copy()
    df["cuadrante"] = [
        CUADRANTES[(i >= u_imp, d >= u_des)]
        for i, d in zip(df[col_imp], df[col_des])
    ]
    return df, u_imp, u_des


def tabla_clasica(sa: pd.DataFrame):
    """IPA clásico: importancia = frecuencia de mención, desempeño = nota media."""
    uno = sa.drop_duplicates(["resena_id", "atributo"])
    t = (uno.groupby("atributo")
           .agg(menciones=("resena_id", "nunique"), desempeno=("puntuacion", "mean"))
           .reset_index())
    t = t.sort_values("menciones", ascending=False)
    return _cuadrantes(t, "menciones", "desempeno")


def tabla_impacto(prca: pd.DataFrame):
    """IPA por impacto: importancia = coeficiente PRCA, desempeño = sentimiento."""
    t = (prca[prca["ambito"] == "Marco de Jerez"]
         [["atributo", "importancia", "desempeno", "menciones", "kano", "perfil"]]
         .reset_index(drop=True))
    t = t.sort_values("importancia", ascending=False)
    return _cuadrantes(t, "importancia", "desempeno")


def figura(t: pd.DataFrame, col_imp, col_des, u_imp, u_des, titulo, ejes, destino):
    """Dibuja la matriz IPA de cuadrantes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=160)
    ax.axvline(u_imp, color="#8B877E", lw=1, ls="--")
    ax.axhline(u_des, color="#8B877E", lw=1, ls="--")
    ax.scatter(t[col_imp], t[col_des], s=90, color="#7A3B1E", zorder=3)
    # Aire a los lados: sin él, las etiquetas de los puntos extremos se salen del gráfico
    # al pegarlo en el documento.
    ax.margins(x=0.16, y=0.11)
    medio = (t[col_imp].min() + t[col_imp].max()) / 2
    for _, r in t.iterrows():
        # Los puntos de la mitad derecha rotulan a su izquierda, para no salirse del marco
        # ni pisar al vecino.
        der = r[col_imp] > medio
        ax.annotate(r["atributo"], (r[col_imp], r[col_des]),
                    textcoords="offset points",
                    xytext=(-10, 8) if der else (10, 8),
                    ha="right" if der else "left", fontsize=9)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    etiquetas = [(xmax, ymin, "Concéntrese aquí", "right", "bottom"),
                 (xmax, ymax, "Mantener el buen trabajo", "right", "top"),
                 (xmin, ymin, "Baja prioridad", "left", "bottom"),
                 (xmin, ymax, "Posible exceso", "left", "top")]
    for x, y, txt, ha, va in etiquetas:
        ax.text(x, y, txt, ha=ha, va=va, fontsize=9, style="italic",
                color="#8B877E", alpha=.9)
    ax.set_xlabel(ejes[0]); ax.set_ylabel(ejes[1])
    ax.set_title(titulo, fontsize=12, loc="left", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


LEEME = [
    ("GUION DE INTERPRETACION — TFG Daniela", ""),
    ("", ""),
    ("Que hay en este libro", ""),
    ("Resenas", "Las 10.972 resenas, SEUDONIMIZADAS. En vez del nombre del autor hay un codigo "
                "estable (V-XXXXXXXX): la misma resena da siempre el mismo codigo, pero del "
                "codigo no se vuelve al autor."),
    ("AVISO RGPD", "El TEXTO de algunas resenas contiene nombres de personas: guias que el "
                   "visitante menciona ('nuestra guia Lucia') o firmas de quien escribe. No se "
                   "han borrado porque un filtro automatico se llevaria por delante nombres del "
                   "dominio: Pedro Ximenez es un vino, y Pedro Romero o Luis Perez son bodegas. "
                   "REGLA: si citas una resena como ejemplo en el TFG, sustituye cualquier "
                   "nombre de persona por [guia] o [visitante]. Nunca lo reproduzcas."),
    ("Atributos", "Tabla base: cuantas resenas mencionan cada atributo, con que sentimiento y "
                  "con que nota media."),
    ("IPA frecuencia", "El IPA clasico. Importancia = numero de menciones. Desempeno = nota "
                       "media en estrellas de las resenas que lo mencionan."),
    ("IPA impacto", "El IPA por impacto. Importancia = cuanto mueve la valoracion global el "
                    "sentimiento hacia ese atributo (regresion PRCA). Desempeno = sentimiento "
                    "medio hacia el atributo, NO las estrellas de la visita entera."),
    ("Comparacion", "LO IMPORTANTE: que atributos cambian de cuadrante segun como se mida la "
                    "importancia. Es tu aportacion al TFG."),
    ("", ""),
    ("Como se leen los cuadrantes", ""),
    ("Concentrese aqui", "Importancia alta, desempeno bajo. Es la prioridad de actuacion."),
    ("Mantener el buen trabajo", "Importancia alta, desempeno alto. Va bien: sostenerlo."),
    ("Baja prioridad", "Importancia baja, desempeno bajo. No urge."),
    ("Posible exceso", "Importancia baja, desempeno alto. Se esta invirtiendo de mas."),
    ("", ""),
    ("Los umbrales", "Cada eje se parte por su MEDIA, que es el criterio clasico de Martilla y "
                     "James (1977). Los valores exactos estan escritos en cada hoja: citalos en "
                     "la metodologia."),
    ("", ""),
    ("Que tienes que explicar en el TFG", ""),
    ("1", "Por que el desempeno por impacto NO usa las estrellas: la nota es de la visita "
          "entera, no del atributo. Una resena de 5 estrellas que dice 'carisimo pero merece la "
          "pena' daria desempeno 5 al precio, que es falso."),
    ("2", "Por que la frecuencia es una mala medida de importancia: de algunas cosas solo se "
          "habla cuando fallan."),
    ("3", "El efecto techo: el 75,9 % de las valoraciones son de 5 estrellas, asi que casi no "
          "hay margen por encima de la media. Es una limitacion real y senalarla suma."),
    ("", ""),
    ("Cifras para citar", ""),
    ("Resenas", "10.972"),
    ("Bodegas", "41"),
    ("Con texto analizable", "7.258"),
    ("Periodo", "22/07/2011 - 06/07/2026"),
    ("Valoraciones de 5 estrellas", "75,9 %"),
    ("Resenas criticas (<=2 estrellas)", "646"),
]


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    res = pd.read_csv(PROC / "resenas.csv")
    sa = pd.read_csv(PROC / "sentimiento_atributos.csv")
    prca = pd.read_csv(PROC / "prca_kano.csv")

    # --- Reseñas seudonimizadas: autor y enlace NO salen de aquí --------------
    r = res.copy()
    r["visitante"] = r["resena_id"].astype(str).map(seudonimo)
    r = r[["visitante", "bodega", "puntuacion", "fecha", "texto", "idioma",
           "segmento_idioma"]]

    # --- Las dos tablas IPA ---------------------------------------------------
    clas, uc_i, uc_d = tabla_clasica(sa)
    imp, ui_i, ui_d = tabla_impacto(prca)

    # --- Comparación: quién cambia de cuadrante -------------------------------
    comp = (clas[["atributo", "menciones", "desempeno", "cuadrante"]]
            .rename(columns={"menciones": "importancia_frecuencia",
                             "desempeno": "desempeno_estrellas",
                             "cuadrante": "cuadrante_frecuencia"})
            .merge(imp[["atributo", "importancia", "desempeno", "cuadrante"]]
                   .rename(columns={"importancia": "importancia_impacto",
                                    "desempeno": "desempeno_sentimiento",
                                    "cuadrante": "cuadrante_impacto"}),
                   on="atributo"))
    comp["CAMBIA"] = comp["cuadrante_frecuencia"] != comp["cuadrante_impacto"]
    comp = comp.sort_values("CAMBIA", ascending=False)

    # --- Figuras --------------------------------------------------------------
    figura(clas, "menciones", "desempeno", uc_i, uc_d,
           "IPA del Marco de Jerez — importancia por FRECUENCIA",
           ("Importancia (nº de reseñas que lo mencionan)", "Desempeño (nota media, 1-5)"),
           SALIDA / "ipa_frecuencia.png")
    figura(imp, "importancia", "desempeno", ui_i, ui_d,
           "IPA del Marco de Jerez — importancia por IMPACTO (PRCA)",
           ("Importancia (impacto en la valoración global)", "Desempeño (sentimiento, 1-5)"),
           SALIDA / "ipa_impacto.png")

    # --- Excel ----------------------------------------------------------------
    destino = SALIDA / "material_tfg_daniela.xlsx"
    with pd.ExcelWriter(destino, engine="xlsxwriter") as xl:
        pd.DataFrame(LEEME, columns=["", " "]).to_excel(xl, "LEEME", index=False)
        r.to_excel(xl, "Resenas", index=False)
        base = (sa.drop_duplicates(["resena_id", "atributo"])
                  .groupby("atributo")
                  .agg(menciones=("resena_id", "nunique"),
                       sentimiento_medio=("sentimiento", "mean"),
                       nota_media=("puntuacion", "mean"))
                  .reset_index().sort_values("menciones", ascending=False))
        base.to_excel(xl, "Atributos", index=False)
        clas.to_excel(xl, "IPA frecuencia", index=False, startrow=3)
        imp.to_excel(xl, "IPA impacto", index=False, startrow=3)
        comp.to_excel(xl, "Comparacion", index=False, startrow=3)

        libro = xl.book
        neg = libro.add_format({"bold": True})
        for hoja, ui, ud, et in [
            ("IPA frecuencia", uc_i, uc_d, ("menciones", "estrellas")),
            ("IPA impacto", ui_i, ui_d, ("impacto PRCA", "sentimiento")),
        ]:
            h = xl.sheets[hoja]
            h.write(0, 0, f"Umbral de importancia ({et[0]}): {ui:.4f}", neg)
            h.write(1, 0, f"Umbral de desempeno ({et[1]}): {ud:.4f}", neg)
        h = xl.sheets["Comparacion"]
        n = int(comp["CAMBIA"].sum())
        h.write(0, 0, f"{n} de {len(comp)} atributos CAMBIAN de cuadrante segun como se mida "
                      f"la importancia.", neg)
        h.write(1, 0, "Esa discrepancia es la aportacion propia del TFG.", neg)
        for hoja in xl.sheets.values():
            hoja.set_column(0, 0, 34)
            hoja.set_column(1, 12, 20)

    print(f"Excel:   {destino}")
    print(f"Figuras: {SALIDA/'ipa_frecuencia.png'}\n         {SALIDA/'ipa_impacto.png'}")
    print(f"\nAtributos que cambian de cuadrante: {int(comp['CAMBIA'].sum())} de {len(comp)}")
    for _, x in comp[comp["CAMBIA"]].iterrows():
        print(f"  · {x['atributo']:28s} {x['cuadrante_frecuencia']:25s} -> {x['cuadrante_impacto']}")
    print(f"\nComprobacion de seudonimizacion: columnas del Excel = {list(r.columns)}")
    assert "autor" not in r.columns and "enlace_resena" not in r.columns


if __name__ == "__main__":
    main()
