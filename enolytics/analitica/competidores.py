"""Identificación y categorización de competidores por bodega.

Método: **Zhou et al. (2026)**, *"A data-driven approach to competitor identification and
categorization in the hotel industry"* (Int. J. Hospitality Management),
`BIBLIOGRAFIA/Zhou_2026_IJHM.pdf`. Adaptado del hotel a la bodega enoturística.

Tres etapas del paper:
  1. **Rasgos.** Se reúnen los rasgos de cada bodega y se transforman (one-hot de servicios,
     estandarización de numéricos, distancia geográfica de lat/lon).
  2. **Identificación → K-prototypes** (Ji et al., 2012): clustering que maneja a la vez datos
     numéricos y categóricos. Las bodegas del MISMO clúster que la bodega objetivo = sus
     competidores.
  3. **Categorización → teoría de Kamensky** (2000), con **distancia de Gower**: cada competidor
     se sitúa en dos ejes —Comunalidad de Mercado (MC) y Similitud de Recursos (RS)— y se
     clasifica en 4 tipos: core, sustituto, marginal, potencial.

Reparto de rasgos (validado con Antonio, fiel a Zhou):
  · **RS (recursos, lado oferta — "lo que la bodega tiene/es"):** servicios (one-hot),
    certificación FEV, madurez digital, tamaño (nº reseñas, proxy de escala).
  · **MC (mercado, lado demanda — "a qué cliente sirve"):** perfil de sentimiento por atributo
    (= las "notas de detalle" de Zhou; preferencia revelada), nota global de Google, ubicación
    (distancia geográfica) y mezcla de idioma nacional/internacional.

Decisiones de la v1 (con Antonio):
  · **Sin precio de la visita** (no lo tenemos aún): el MC se calcula sin él. Gower degrada con
    elegancia (promedia sobre los rasgos presentes). Se añadirá cuando exista.
  · **Cobertura:** solo bodegas con perfil mínimo viable (≥`MIN_ATRIBUTOS` atributos con
    sentimiento + GPS + servicios); a las demás, mensaje honesto en la ficha.

Gower (ec. 1-3 del paper): d_ij = Σ_k w_k·d_ijk. Numérico: |x_ik−x_jk|/(max−min). Categórico:
1 si difieren, 0 si coinciden. Rango [0,1]; mayor distancia = menos parecido. Pesos iguales.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from enolytics import config
from enolytics.nlp import analisis

ATRIBUTOS = list(analisis.ATRIBUTOS.keys())          # los 8 atributos (perfil de sentimiento)
MIN_ATRIBUTOS = 4                                    # perfil mínimo viable para entrar
MIN_FREC_SERVICIO = 0.10                             # servicios en <10% de bodegas se descartan
TOP_COMPETIDORES = 5                                 # cuántos mostrar por bodega

SALIDA = config.DATOS_PROCESADO / "competidores.csv"

INTL = "Internacional (no hispanohablante)"


def _norm_servicio(s: str) -> str:
    """Normaliza un servicio para consolidar variantes."""
    s = analisis._normalizar(s).strip()
    # consolidaciones sencillas (como el "washing machine"/"laundry room" de Zhou)
    if "cata" in s or "degust" in s:
        return "catas"
    if "marida" in s:
        return "maridaje"
    if "tienda" in s or "venta" in s:
        return "tienda"
    if "restaurante" in s or "gastro" in s or "comida" in s:
        return "restauracion"
    if "evento" in s or "celebrac" in s or "boda" in s:
        return "eventos"
    if "aloja" in s or "hotel" in s or "hospeda" in s:
        return "alojamiento"
    if "visita" in s or "tour" in s or "guiada" in s:
        return "visitas guiadas"
    if "experiencia" in s:
        return "experiencias"
    return s


def cargar_rasgos() -> pd.DataFrame:
    """Reúne los rasgos de cada bodega desde todas las fuentes (indexado por 'bodega')."""
    D = config.DATOS_PROCESADO
    cat = pd.read_csv(config.CATALOGO_CSV).rename(columns={"nombre": "bodega"})
    cen = pd.read_csv(D / "censo_google.csv")
    aud = pd.read_csv(D / "auditoria_web.csv")
    sos = pd.read_csv(D / "sostenibilidad.csv")

    df = cat[["bodega", "localidad", "servicios", "gps_lat", "gps_lon"]].copy()
    df = df.merge(cen[["bodega", "rating", "total_resenas"]], on="bodega", how="left")
    df = df.merge(aud[["bodega", "madurez_digital"]], on="bodega", how="left")
    df = df.merge(sos[["bodega", "sello_fev", "indice_sostenibilidad"]], on="bodega", how="left")

    # --- MC: perfil de sentimiento por atributo (media por atributo) ---
    from enolytics.nlp import sentimiento
    sent = sentimiento.cargar()
    perfil = (sent.groupby(["bodega", "atributo"])["sentimiento"].mean()
              .unstack("atributo").reindex(columns=ATRIBUTOS))
    perfil.columns = [f"sent__{a}" for a in perfil.columns]
    df = df.merge(perfil, on="bodega", how="left")

    # --- MC: mezcla de idioma (% internacional) ---
    from enolytics.etl import resenas as etl
    res = etl.cargar_resenas()
    if "segmento_idioma" in res.columns:
        con_seg = res[res["segmento_idioma"].notna()]
        pct_intl = (con_seg.assign(intl=con_seg["segmento_idioma"] == INTL)
                    .groupby("bodega")["intl"].mean())
        df = df.merge(pct_intl.rename("pct_internacional"), on="bodega", how="left")
    else:
        df["pct_internacional"] = np.nan

    return df.set_index("bodega")


def _servicios_onehot(rasgos: pd.DataFrame) -> pd.DataFrame:
    """One-hot de servicios: separa por '|', normaliza, y filtra los raros (<MIN_FREC)."""
    listas = rasgos["servicios"].fillna("").map(
        lambda s: sorted({_norm_servicio(x) for x in str(s).split("|") if x.strip()}))
    todos = pd.Series([s for lst in listas for s in lst]).value_counts()
    frec = todos / len(rasgos)
    validos = frec[frec >= MIN_FREC_SERVICIO].index.tolist()
    oh = pd.DataFrame({f"srv__{s}": listas.map(lambda lst: int(s in lst)) for s in validos},
                      index=rasgos.index)
    return oh


def _haversine_km(la1, lo1, la2, lo2) -> float:
    """Distancia en km entre dos puntos (para la componente geográfica del MC)."""
    r = 6371.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = math.radians(la2 - la1), math.radians(lo2 - lo1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


def _matriz_geo(rasgos: pd.DataFrame) -> pd.DataFrame:
    """Distancia geográfica normalizada [0,1] entre bodegas (término de Gower para el MC)."""
    idx = list(rasgos.index)
    n = len(idx)
    m = np.zeros((n, n))
    lat, lon = rasgos["gps_lat"].values, rasgos["gps_lon"].values
    for i in range(n):
        for j in range(i + 1, n):
            d = _haversine_km(lat[i], lon[i], lat[j], lon[j])
            m[i, j] = m[j, i] = d
    mx = m.max() or 1.0
    return pd.DataFrame(m / mx, index=idx, columns=idx)


def _minmax(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza cada columna numérica a [0,1] (para que |x_i−x_j| sea el término de Gower)."""
    out = df.copy().astype(float)
    for c in out.columns:
        col = out[c]
        col = col.fillna(col.mean())
        rng = col.max() - col.min()
        out[c] = (col - col.min()) / rng if rng else 0.0
    return out


def _gower(num: pd.DataFrame, cat: pd.DataFrame, geo: pd.DataFrame | None = None) -> pd.DataFrame:
    """Matriz de distancias de Gower (ec. 1-3). Pesos iguales. num ya viene en [0,1]."""
    idx = num.index if not num.empty else cat.index
    n = len(idx)
    total = np.zeros((n, n))
    nfeat = 0
    if not num.empty:
        A = num.values
        for k in range(A.shape[1]):
            col = A[:, k][:, None]
            total += np.abs(col - col.T)
        nfeat += A.shape[1]
    if not cat.empty:
        C = cat.astype(str).values
        for k in range(C.shape[1]):
            col = C[:, k][:, None]
            total += (col != col.T).astype(float)
        nfeat += C.shape[1]
    if geo is not None:
        total += geo.loc[idx, idx].values
        nfeat += 1
    return pd.DataFrame(total / max(nfeat, 1), index=idx, columns=idx)


def _bloques(rasgos: pd.DataFrame):
    """Prepara los rasgos viables y devuelve las matrices de MC y RS (Gower) + datos de clustering."""
    sent_cols = [c for c in rasgos.columns if c.startswith("sent__")]
    n_atr = rasgos[sent_cols].notna().sum(axis=1)
    viable = ((n_atr >= MIN_ATRIBUTOS) & rasgos["gps_lat"].notna()
              & rasgos["servicios"].notna() & rasgos["rating"].notna())
    r = rasgos[viable].copy()
    oh = _servicios_onehot(r)

    # --- RS (recursos, oferta) ---
    rs_cat = pd.concat([oh, (r["sello_fev"].notna()).astype(int).rename("cert_fev")], axis=1)
    rs_num = _minmax(r[["madurez_digital", "total_resenas", "indice_sostenibilidad"]])
    # --- MC (mercado, demanda) ---
    mc_num = _minmax(r[sent_cols + ["rating", "pct_internacional"]])
    geo = _matriz_geo(r)

    d_rs = _gower(rs_num, rs_cat)
    d_mc = _gower(mc_num, pd.DataFrame(index=r.index), geo=geo)

    # Para K-prototypes: numéricos estandarizados + categóricos (servicios+cert) como texto
    num_clu = pd.concat([rs_num, mc_num], axis=1)
    cat_clu = rs_cat.astype(int).astype(str)
    X = pd.concat([num_clu, cat_clu], axis=1)
    cat_idx = list(range(num_clu.shape[1], X.shape[1]))
    return r, d_mc, d_rs, X, cat_idx


def _clusters(X: pd.DataFrame, cat_idx: list, d_comb: pd.DataFrame) -> pd.Series:
    """K-prototypes; elige k por silueta sobre la distancia de Gower combinada."""
    from kmodes.kprototypes import KPrototypes
    from sklearn.metrics import silhouette_score
    Xv = X.values
    mejor_k, mejor_lab, mejor_sil = None, None, -1
    for k in range(3, min(8, len(X) - 1) + 1):
        try:
            kp = KPrototypes(n_clusters=k, init="Huang", n_init=5, random_state=0, verbose=0)
            lab = kp.fit_predict(Xv, categorical=cat_idx)
        except Exception:
            continue
        if len(set(lab)) < 2:
            continue
        sil = silhouette_score(d_comb.values, lab, metric="precomputed")
        if sil > mejor_sil:
            mejor_k, mejor_lab, mejor_sil = k, lab, sil
    return pd.Series(mejor_lab, index=X.index, name="cluster"), mejor_k, mejor_sil


def _tipo_kamensky(dmc: float, drs: float, umbral_mc: float, umbral_rs: float) -> str:
    """4 tipos de Kamensky. Distancia baja = alta comunalidad/similitud."""
    mismo_mercado = dmc < umbral_mc
    mismos_recursos = drs < umbral_rs
    if mismo_mercado and mismos_recursos:
        return "Core"
    if mismo_mercado and not mismos_recursos:
        return "Sustituto"
    if not mismo_mercado and mismos_recursos:
        return "Marginal"
    return "Potencial"


def calcular_y_guardar() -> pd.DataFrame:
    """Precalcula los competidores de cada bodega y guarda el CSV. Se ejecuta EN LOCAL."""
    rasgos = cargar_rasgos()
    r, d_mc, d_rs, X, cat_idx = _bloques(rasgos)
    d_comb = (d_mc + d_rs) / 2
    labels, k, sil = _clusters(X, cat_idx, d_comb)
    print(f"K-prototypes: k={k} (silueta {sil:.3f}) sobre {len(r)} bodegas viables")

    # Umbrales por cuantil (mediana de las distancias fuera de la diagonal)
    off = ~np.eye(len(r), dtype=bool)
    umbral_mc = float(np.median(d_mc.values[off]))
    umbral_rs = float(np.median(d_rs.values[off]))

    filas = []
    for objetivo in r.index:
        clu = labels[objetivo]
        companeros = [b for b in labels.index[labels == clu] if b != objetivo]
        companeros.sort(key=lambda b: d_comb.loc[objetivo, b])   # más cercano primero
        for rango, comp_b in enumerate(companeros[:TOP_COMPETIDORES], 1):
            dmc, drs = d_mc.loc[objetivo, comp_b], d_rs.loc[objetivo, comp_b]
            filas.append({
                "bodega": objetivo, "competidor": comp_b, "rango": rango,
                "tipo": _tipo_kamensky(dmc, drs, umbral_mc, umbral_rs),
                "dist_mercado": round(float(dmc), 3),
                "dist_recursos": round(float(drs), 3),
                "dist_combinada": round(float(d_comb.loc[objetivo, comp_b]), 3),
                "localidad_comp": r.loc[comp_b, "localidad"],
                "rating_comp": r.loc[comp_b, "rating"],
                "umbral_mc": round(umbral_mc, 3), "umbral_rs": round(umbral_rs, 3),
            })
    salida = pd.DataFrame(filas)
    salida.attrs["viables"] = list(r.index)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    salida.to_csv(SALIDA, index=False)
    # Guarda también qué bodegas entraron (para que la ficha sepa a quién informar)
    pd.Series(list(r.index), name="bodega").to_csv(
        SALIDA.with_name("competidores_viables.csv"), index=False)
    print(f"Guardado: {SALIDA}  ({len(salida)} filas, "
          f"{salida['bodega'].nunique()} bodegas con competidores)")
    return salida


def cargar() -> tuple[pd.DataFrame, set]:
    """Lee el CSV precalculado y el conjunto de bodegas viables. Es lo único que hace el dashboard."""
    if not SALIDA.exists():
        return pd.DataFrame(), set()
    df = pd.read_csv(SALIDA)
    vpath = SALIDA.with_name("competidores_viables.csv")
    viables = set(pd.read_csv(vpath)["bodega"]) if vpath.exists() else set(df["bodega"])
    return df, viables


if __name__ == "__main__":
    calcular_y_guardar()
