"""Informe competitivo descargable por bodega, en PDF (Pieza 1 de la propuesta de Paula).

Genera un PDF de una página con la estructura del ejemplo de Paula:
  · PARTE A «Quién eres»  — reputación y procedencia.
  · PARTE B «Cómo compites» — grupo competitivo (Zhou et al., 2026), fortalezas/debilidades,
    presencia digital y sostenibilidad, qué hacer, y el contexto del Marco.

Se genera **en vivo en el servidor** con `fpdf2` (puro Python, sin dependencias de sistema —
weasyprint no vale en Streamlit Cloud). El dashboard lo ofrece con `st.download_button`.

Nota de codificación: las fuentes básicas de fpdf usan latin-1; `_t()` sanea los caracteres que
no encajan (★, flechas, €, emojis) para que nunca aparezca un "?" ni reviente la generación.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd

from enolytics import config
from enolytics.nlp import analisis

# --- Paleta (identidad del Marco: caoba de oloroso) ---
CAOBA = (122, 59, 30)
CAOBA_OSC = (59, 30, 18)
INK = (28, 27, 25)
INK_SUAVE = (87, 84, 78)
GRIS = (139, 135, 126)
LINEA = (228, 224, 214)
PLANO = (243, 240, 233)
OK = (12, 163, 12)
MAL = (208, 59, 59)

_REEMPLAZOS = {
    "★": "*", "↗": "(+)", "↘": "(-)", "→": "->", "↔": "<->", "€": " EUR",
    "—": "-", "–": "-", "…": "...", "“": '"', "”": '"', "’": "'",
    "🎯": "[Core]", "🔄": "[Sust.]", "➖": "[Marg.]", "🌱": "[Pot.]", "⭐": "*",
}


def _t(s) -> str:
    """Texto seguro para las fuentes latin-1 de fpdf (sin '?' ni caracteres rotos)."""
    s = str(s)
    for a, b in _REEMPLAZOS.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "ignore").decode("latin-1")


def _pie_documento(pdf, W, nota_fuentes: str, size_nota: float = 7.0) -> None:
    """Pie de los PDF: nota de fuentes + banda de logos + cláusula de financiación.

    La cláusula y los logos los exige la Resolución de 23/12/2024 de la UCA para los
    medios de difusión de la actuación financiada. El texto y la imagen viven en
    `config`, para que el cuadro de mando y los dos PDF digan exactamente lo mismo.

    Se compone con el **salto de página automático desactivado**: el pie se ancla al
    final de la página en curso y, al dibujar la banda de logos, fpdf saltaba de página
    y dejaba la cláusula sola en una hoja nueva.
    """
    auto_previo = pdf.auto_page_break
    margen_previo = pdf.b_margin
    pdf.set_auto_page_break(False)

    alto_banda = 7.0
    # altura total reservada: regla + nota + banda + cláusula
    pdf.set_y(-(10 + alto_banda + 14))
    pdf.set_draw_color(*LINEA)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + W, pdf.get_y())
    pdf.ln(1.5)

    pdf.set_font("Helvetica", "", size_nota)
    pdf.set_text_color(*GRIS)
    pdf.multi_cell(W, 3, _t(nota_fuentes), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # getattr por lo mismo que en el cuadro de mando: un config desfasado no debe
    # impedir que la bodega se descargue su informe.
    logos = getattr(config, "LOGOS_FEDER", None)
    if logos is not None and logos.exists():
        # la banda es apaisada (1330 x 103 px): se escala por altura y se centra
        ancho = min(alto_banda * (1330 / 103), W)
        pdf.image(str(logos), x=pdf.l_margin + (W - ancho) / 2, y=pdf.get_y(), w=ancho)
        pdf.ln(alto_banda + 1.5)

    clausula = getattr(config, "CLAUSULA_FINANCIACION", "")
    if clausula:
        pdf.set_font("Helvetica", "", 6.2)
        pdf.set_text_color(*GRIS)
        pdf.multi_cell(W, 2.6, _t(clausula), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_auto_page_break(auto_previo, margin=margen_previo)


def _perfil_sentimiento(nombre: str) -> pd.Series:
    """Sentimiento medio por atributo de la bodega (para fortalezas/debilidades)."""
    from enolytics.nlp import sentimiento
    s = sentimiento.cargar()
    sub = s[s["bodega"] == nombre]
    if sub.empty:
        return pd.Series(dtype=float)
    return sub.groupby("atributo")["sentimiento"].mean().sort_values(ascending=False)


def _fila_csv(nombre: str, archivo: str) -> dict:
    ruta = config.DATOS_PROCESADO / archivo
    if not ruta.exists():
        return {}
    df = pd.read_csv(ruta)
    f = df[df["bodega"] == nombre]
    return f.iloc[0].to_dict() if not f.empty else {}


def generar_pdf_bodega(nombre: str, recs: list, res_bod: pd.DataFrame,
                       rating_marco: float | None = None) -> bytes:
    """Devuelve el informe de la bodega como PDF (bytes)."""
    from fpdf import FPDF

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    W = pdf.w - pdf.l_margin - pdf.r_margin  # ancho útil

    def sety(y):
        pdf.set_y(y)

    def titulo_seccion(txt):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*CAOBA)
        pdf.cell(0, 7, _t(txt), new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y()
        pdf.set_draw_color(*LINEA)
        pdf.line(pdf.l_margin, y, pdf.l_margin + W, y)
        pdf.ln(2)

    def etiqueta_parte(txt):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(*PLANO)
        pdf.set_text_color(*CAOBA)
        pdf.cell(0, 6, _t("  " + txt), new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(1)

    def parrafo(txt, size=9.5, color=INK_SUAVE, marcado=True):
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*color)
        pdf.multi_cell(W, 4.6, _t(txt), markdown=marcado,
                       new_x="LMARGIN", new_y="NEXT")

    # ---------- Cabecera (banda caoba) ----------
    pdf.set_fill_color(*CAOBA)
    pdf.rect(0, 0, pdf.w, 30, style="F")
    pdf.set_xy(pdf.l_margin, 7)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(235, 225, 215)
    pdf.cell(0, 4, _t("ENOLYTICS · INFORME COMPETITIVO DE BODEGA"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 9, _t(nombre), new_x="LMARGIN", new_y="NEXT")
    loc = ""
    try:
        cat = pd.read_csv(config.CATALOGO_CSV)
        fc = cat[cat["nombre"] == nombre]
        loc = fc.iloc[0]["localidad"] if not fc.empty else ""
    except Exception:
        pass
    hoy = _dt.date.today().strftime("%d/%m/%Y")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(230, 220, 210)
    pdf.cell(0, 5, _t(f"{loc} · Marco de Jerez   |   Generado el {hoy} · Universidad de Cádiz"),
             new_x="LMARGIN", new_y="NEXT")
    sety(36)

    # ---------- PARTE A ----------
    etiqueta_parte("PARTE A · QUIÉN ERES")

    # Reputación
    n = len(res_bod)
    val = res_bod["puntuacion"].mean() if n else float("nan")
    con_texto = int((res_bod["texto"].astype(str).str.len() > 5).sum()) if n else 0
    from enolytics.analitica import reputacion as rep
    tr = rep.tasa_respuesta(res_bod) if n else {}
    contestadas = tr.get("pct_total", 0.0)
    titulo_seccion("Tu reputación online")
    kpis = [("Valoración", f"{val:.2f}".replace(".", ","), f"{n} reseñas"),
            ("vs. media del Marco",
             (f"{val - rating_marco:+.2f}".replace(".", ",") if rating_marco else "-"),
             (f"media de todas las reseñas: {rating_marco:.2f}".replace(".", ",")
              if rating_marco else "")),
            ("Con texto", str(con_texto), f"de {n}"),
            ("Contestadas", f"{contestadas:.0f}%", "de las reseñas")]
    _kpi_row(pdf, W, kpis)

    # ---------- PARTE B ----------
    etiqueta_parte("PARTE B · CÓMO COMPITES Y QUÉ HACER")

    # Competidores directos
    from enolytics.analitica import competidores as competi
    df_comp, viables = competi.cargar()
    titulo_seccion("Tu grupo competitivo")
    if nombre in viables and not df_comp.empty:
        sub = df_comp[df_comp["bodega"] == nombre].sort_values("rango")
        parrafo("Las bodegas más parecidas a la tuya por mercado (a qué cliente sirves) y por "
                "recursos (con los que cuentas para competir). No es todo el Marco, sino tu "
                "grupo, ordenado de más a menos cercano.")
        nucleo = int((sub["tipo"] == "Core").sum())
        parrafo(f"De las {len(sub)}, {nucleo} {'es' if nucleo == 1 else 'son'} de núcleo: mismo "
                f"cliente y recursos parecidos, o sea tu rival más directo."
                if nucleo else
                "Ninguna es un rival directo: ninguna comparte a la vez cliente y recursos "
                "contigo. Son competidores cercanos por un eje u otro; mira la etiqueta de cada "
                "una.", size=8.5)
        pdf.ln(1)
        for _, r in sub.iterrows():
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(*INK)
            pdf.cell(8, 5, _t(f"{int(r['rango'])}."))
            pdf.cell(78, 5, _t(str(r["competidor"])[:42]))
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*CAOBA)
            pdf.cell(24, 5, _t(str(r["tipo"])))
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(*GRIS)
            pdf.cell(0, 5, _t(f"{str(r['rating_comp'])}*  ·  {r['localidad_comp']}"),
                     new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*GRIS)
        pdf.multi_cell(W, 3.6, _t("Core: mismo cliente y recursos (rival directo) · Sustituto: "
                                  "mismo cliente, recursos distintos · Marginal: recursos "
                                  "parecidos, otro cliente · Potencial: distinto en ambos."),
                       new_x="LMARGIN", new_y="NEXT")
    else:
        parrafo("Muestra insuficiente para el análisis de competidores de esta bodega.")

    # Fortalezas y debilidades
    perfil = _perfil_sentimiento(nombre)
    if not perfil.empty:
        titulo_seccion("Tus fortalezas y debilidades")
        y0 = pdf.get_y()
        _lista_box(pdf, pdf.l_margin, y0, W / 2 - 3, "EN LO QUE DESTACAS",
                   list(perfil.head(3).index), OK)
        _lista_box(pdf, pdf.l_margin + W / 2 + 3, y0, W / 2 - 3, "LO QUE FLOJEA",
                   list(perfil.tail(3).index[::-1]), MAL)
        pdf.set_y(y0 + 26)

    # Presencia digital y sostenibilidad
    aud = _fila_csv(nombre, "auditoria_web.csv")
    sos = _fila_csv(nombre, "sostenibilidad.csv")
    tra = _fila_csv(nombre, "transporte_sostenible.csv")
    titulo_seccion("Tu presencia digital y sostenibilidad")
    kpis2 = [
        ("Madurez digital", f"{int(aud.get('madurez_digital', 0))} / 5", ""),
        ("Reserva online", "Sí" if aud.get("reserva_online") else "No", ""),
        ("Certificación FEV", "Sí" if pd.notna(sos.get("sello_fev")) else "No", ""),
        ("Transporte público", "Sí" if tra.get("accesible_transporte_publico") else "No", ""),
    ]
    _kpi_row(pdf, W, kpis2)

    # Qué hacer
    titulo_seccion("Qué hacer para ganar clientes")
    altas = [r for r in (recs or []) if getattr(r, "prioridad", "") == "alta"][:3]
    if not altas:
        altas = (recs or [])[:3]
    for i, r in enumerate(altas, 1):
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*INK)
        pdf.multi_cell(W, 4.6, _t(f"{i}. {r.titulo}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*INK_SUAVE)
        pdf.multi_cell(W, 4.2, _t("   " + r.accion), markdown=True,
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)
    if not altas:
        parrafo("Sin recomendaciones críticas con los datos disponibles.")

    # Contexto del Marco
    pdf.ln(1)
    pdf.set_fill_color(*PLANO)
    y0 = pdf.get_y()
    pdf.rect(pdf.l_margin, y0, W, 14, style="F")
    pdf.set_xy(pdf.l_margin + 3, y0 + 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*CAOBA)
    pdf.cell(0, 4, _t("EL MARCO DE JEREZ, EN CONTEXTO"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 3)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*INK_SUAVE)
    pdf.cell(0, 5, _t("425.652 visitantes (1.º de España)   ·   40,4 EUR por visitante "
                      "(Rioja: 70)   ·   3,3 M búsquedas de vuelo desde países sin vuelo directo"))

    # ---------- Pie ----------
    _pie_documento(pdf, W,
                   "Fuentes: reseñas de Google · ACEVIN · Dataestur/SEGITTUR · FEV · auditoría "
                   "web propia. Competidores: Zhou et al. (2026), Int. J. Hospitality "
                   "Management. ENOLYTICS · Universidad de Cádiz.", size_nota=6.8)

    return bytes(pdf.output())


def _kpi_row(pdf, W, kpis):
    """Fila de tarjetas KPI."""
    n = len(kpis)
    gap = 3
    w = (W - gap * (n - 1)) / n
    x0, y0 = pdf.l_margin, pdf.get_y()
    for i, (lab, val, sub) in enumerate(kpis):
        x = x0 + i * (w + gap)
        pdf.set_draw_color(*LINEA)
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(x, y0, w, 16, style="D")
        pdf.set_xy(x + 2, y0 + 1.5)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*GRIS)
        pdf.cell(w - 4, 3, _t(lab.upper()))
        pdf.set_xy(x + 2, y0 + 5)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*INK)
        pdf.cell(w - 4, 6, _t(val))
        pdf.set_xy(x + 2, y0 + 11.5)
        pdf.set_font("Helvetica", "", 6.8)
        pdf.set_text_color(*INK_SUAVE)
        pdf.cell(w - 4, 3, _t(sub))
    pdf.set_y(y0 + 18)


def _lista_box(pdf, x, y, w, titulo, items, color):
    """Caja de lista (fortalezas / debilidades)."""
    pdf.set_draw_color(*LINEA)
    pdf.rect(x, y, w, 24, style="D")
    pdf.set_xy(x + 2, y + 2)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*color)
    pdf.cell(w - 4, 4, _t(titulo))
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*INK_SUAVE)
    for i, it in enumerate(items):
        pdf.set_xy(x + 3, y + 7 + i * 5)
        pdf.cell(w - 5, 4, _t("- " + str(it)))


def generar_guia_pdf(glosario: list, fuentes: list,
                     umbrales_metodo: list, umbrales_equipo: list) -> bytes:
    """Guía de uso / metodología como PDF (anexo de metodología para FEDER).

    `fuentes`: (nombre, descripción, clave de origen) — cuelgan del color que les toca.
    `umbrales_*`: (umbral, por qué) de los dos bloques de la sección 5.
    """
    from fpdf import FPDF
    from enolytics import config as _cfg

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    W = pdf.w - pdf.l_margin - pdf.r_margin

    def h2(txt):
        pdf.ln(2.5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*CAOBA)
        pdf.cell(0, 7, _t(txt), new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y()
        pdf.set_draw_color(*LINEA)
        pdf.line(pdf.l_margin, y, pdf.l_margin + W, y)
        pdf.ln(1.5)

    def parr(txt, size=9.5, color=INK_SUAVE, bold_lead=None):
        """Un párrafo del documento, compuesto en UNA sola celda.

        Antes el rótulo en negrita se escribía con `write()` —que deja el cursor a la
        derecha— y a continuación se pedía una celda del ancho ÚTIL COMPLETO desde esa
        posición: el texto se componía más ancho que el papel y perdía las últimas
        palabras de cada línea (24 de 73 líneas se salían; el borde derecho llegaba a
        599,6 pt en una página de 595,3). Observación 7 de Paula.

        Ahora se compone todo de una vez con `markdown=True`, que además convierte el
        marcado `**negrita**` del texto de origen en lugar de imprimir los asteriscos
        (observación 8).
        """
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*color)
        completo = f"**{bold_lead}** {txt}" if bold_lead else txt
        pdf.multi_cell(W, 4.6, _t(completo), markdown=True,
                       new_x="LMARGIN", new_y="NEXT")

    # Cabecera
    pdf.set_fill_color(*CAOBA)
    pdf.rect(0, 0, pdf.w, 28, style="F")
    pdf.set_xy(pdf.l_margin, 7)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(235, 225, 215)
    pdf.cell(0, 4, _t("ENOLYTICS · GUÍA DE USO Y METODOLOGÍA"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 9, _t("Cómo leer la plataforma, y de dónde sale cada dato"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(34)

    # Una sola sección para «qué significa cada color» y «de dónde salen los datos»: son la
    # misma pregunta contada dos veces (observación 3 de Paula).
    h2("1 · De dónde salen los datos, y cómo de firmes son")
    parr("Cada dato lleva una marca que dice cómo de firme es y de qué fuente viene. Nunca se "
         "mezcla una estadística oficial con una estimación sin avisar.")
    for clave, (icono, nombre, desc) in _cfg.ORIGENES_DATO.items():
        pdf.ln(1)
        parr(desc, bold_lead=f"[{nombre}]")
        propias = [(n, d) for n, d, o in fuentes if o == clave]
        for nom, desc_f in propias:
            parr(desc_f, bold_lead=f"   . {nom} -", size=9)
        if not propias:
            parr("   . Sin fuente propia: no es un origen, es un cálculo nuestro a partir de "
                 "los datos anteriores.", size=9, color=CAOBA)

    h2("2 · Las formas de mirar la plataforma")
    for nom, desc in [("Resumen ejecutivo", "Lo esencial de un vistazo y las 3 acciones urgentes."),
                      ("Las 7 inteligencias", "El análisis completo, una pestaña por inteligencia."),
                      ("Bodega individual", "Ficha de una bodega: reputación, competidores, análisis "
                       "e informe descargable."),
                      ("Guía y metodología", "Esta guía.")]:
        parr(desc, bold_lead=nom + " -")

    h2("3 · Las 7 inteligencias: qué responde cada una")
    for info in _cfg.OBJETIVOS_INTELIGENCIAS.values():
        parr(info["objetivo"], bold_lead=f"{info['titulo']} ({info['segittur']}):")

    h2("4 · Los análisis, explicados sin jerga")
    for term, sig, expl in glosario:
        parr(expl, bold_lead=f"{term} ({sig}):")
    pdf.ln(1)
    parr("Principio de la casa: los resúmenes de reputación NO los genera una IA. Se componen de "
         "los datos reales agregados (mismo dato, mismo texto, siempre): reproducible y auditable.",
         size=9, color=CAOBA)

    # Los umbrales, declarados. Un motor de recomendaciones con los listones dichos es
    # defendible y publicable; uno cuyos listones no se sabe de dónde salen, no (obs. 10).
    h2("5 · Los umbrales: de dónde sale cada listón")
    parr("Una recomendación aparece cuando un dato cruza un listón. No son la misma clase de "
         "decisión, así que van separados.")
    pdf.ln(1)
    parr("Los que tienen base metodológica", size=9.5, color=INK)
    for umbral, porque in umbrales_metodo:
        parr(porque, bold_lead=f"   . {umbral} -", size=9)
    pdf.ln(1)
    parr("Los que son criterio del equipo de ENOLYTICS", size=9.5, color=INK)
    for umbral, porque in umbrales_equipo:
        parr(porque, bold_lead=f"   . {umbral} -", size=9)

    _pie_documento(pdf, W,
                   "Documento vivo, generado del catálogo de indicadores del proyecto. "
                   "ENOLYTICS · Universidad de Cádiz · alineado con la norma UNE 178502.")
    return bytes(pdf.output())
