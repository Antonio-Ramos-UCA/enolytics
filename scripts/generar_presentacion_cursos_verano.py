"""Genera la presentación PPTX de ENOLYTICS para los Cursos de Verano de la UCA.

Dos partes: I) el proyecto según la memoria científico-técnica; II) la aplicación
desarrollada. Estilo académico y sobrio, para alumnado universitario. Gráficos nativos
(editables en PowerPoint), notas del ponente en todas las diapositivas.

Todas las cifras están verificadas contra los CSV de datos/procesado (sesión 10-11/09/2026).
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree

# ---------- Identidad (paleta del cuadro de mando, en versión sobria) ----------
ACENTO = RGBColor(0x7A, 0x3B, 0x1E)   # oloroso
INK = RGBColor(0x1C, 0x1B, 0x19)
INK2 = RGBColor(0x57, 0x54, 0x4E)
TENUE = RGBColor(0x8B, 0x87, 0x7E)
REGLA = RGBColor(0xD3, 0xCC, 0xBC)
PLANO = RGBColor(0xF3, 0xF0, 0xE9)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
PX = RGBColor(0x3B, 0x1E, 0x12)
CREMA = RGBColor(0xF6, 0xEF, 0xE3)
AZUL = RGBColor(0x2A, 0x78, 0xD6)
NARANJA = RGBColor(0xEB, 0x68, 0x34)
CONTEXTO = RGBColor(0xC9, 0xC5, 0xBA)
VERDE = RGBColor(0x0C, 0xA3, 0x0C)
ESCALA = ["EBD98A", "C6902F", "A45E2A", "7A3B1E", "3B1E12"]

TITULO_F = "Georgia"
CUERPO_F = "Calibri"

W, H = Inches(13.333), Inches(7.5)
MX = Inches(0.75)          # margen lateral
ANCHO = W - 2 * MX

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]
n_slide = [0]
PIE = "ENOLYTICS · Universidad de Cádiz · Cursos de Verano 2026"


# ============================ utilidades ============================
def rgb(hexstr):
    return RGBColor.from_string(hexstr)


def caja(slide, l, t, w, h, texto="", size=16, bold=False, color=INK, font=CUERPO_F,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False):
    tb = slide.shapes.add_textbox(int(l), int(t), int(w), int(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = texto
    f = r.font
    f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, font
    f.color.rgb = color
    return tb


def parrafo(tf, texto, size=16, color=INK2, bold=False, font=CUERPO_F, space_after=6,
            bullet=False, nivel=0, italic=False):
    """Añade un párrafo a un text_frame ya creado. Admite negritas con **...**."""
    p = tf.add_paragraph() if tf.paragraphs[0].runs or len(tf.paragraphs) > 1 else tf.paragraphs[0]
    p.space_after = Pt(space_after)
    if bullet:
        pPr = p._p.get_or_add_pPr()
        indent = Emu(Inches(0.22 + 0.25 * nivel))
        pPr.set("marL", str(int(indent)))
        pPr.set("indent", str(-int(Inches(0.22))))
        bu = etree.SubElement(pPr, qn("a:buChar"))
        bu.set("char", "•" if nivel == 0 else "–")
    # negritas con **
    partes = texto.split("**")
    for i, trozo in enumerate(partes):
        if not trozo:
            continue
        r = p.add_run()
        r.text = trozo
        f = r.font
        f.size, f.name, f.italic = Pt(size), font, italic
        f.bold = bold or (i % 2 == 1)
        f.color.rgb = INK if (i % 2 == 1 and color == INK2) else color
    return p


def rect(slide, l, t, w, h, fill, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, int(l), int(t), int(w), int(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    s.shadow.inherit = False
    return s


def filo(slide, t=Emu(0), h=Inches(0.07)):
    """Franja de la escala de color del vino (fino → PX), como el filo del cuadro de mando."""
    seg = W / len(ESCALA)
    for i, c in enumerate(ESCALA):
        rect(slide, int(seg * i), t, int(seg) + 1, h, rgb(c))


def pie(slide, oscuro=False):
    n_slide[0] += 1
    col = CREMA if oscuro else TENUE
    caja(slide, MX, H - Inches(0.42), Inches(8), Inches(0.3), PIE, size=9, color=col)
    caja(slide, W - MX - Inches(1), H - Inches(0.42), Inches(1), Inches(0.3), str(n_slide[0]),
         size=9, color=col, align=PP_ALIGN.RIGHT)


def notas(slide, texto):
    slide.notes_slide.notes_text_frame.text = texto.strip()


def lamina(titulo, eyebrow=None, subtitulo=None):
    """Lámina estándar: filo, eyebrow, título, subtítulo opcional. Devuelve (slide, y_inicio)."""
    s = prs.slides.add_slide(BLANK)
    filo(s)
    y = Inches(0.45)
    if eyebrow:
        caja(s, MX, y, ANCHO, Inches(0.3), eyebrow.upper(), size=10, bold=True, color=ACENTO)
        y += Inches(0.32)
    caja(s, MX, y, ANCHO, Inches(0.7), titulo, size=30 if len(titulo) <= 52 else 25, bold=True, color=INK, font=TITULO_F)
    y += Inches(0.72)
    if subtitulo:
        caja(s, MX, y, ANCHO, Inches(0.55), subtitulo, size=15, color=INK2)
        y += Inches(0.6)
    # regla bajo el título
    rect(s, MX, y, ANCHO, Emu(9525), REGLA)
    y += Inches(0.22)
    pie(s)
    return s, y


def separador(numero, titulo, bajada):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, W, H, PX)
    filo(s, t=H - Inches(0.07))
    caja(s, MX, Inches(1.9), ANCHO, Inches(0.5), numero, size=14, bold=True, color=rgb("EBD98A"))
    caja(s, MX, Inches(2.4), ANCHO, Inches(1.6), titulo, size=44, bold=True, color=CREMA, font=TITULO_F)
    caja(s, MX, Inches(4.2), Inches(9.5), Inches(1.2), bajada, size=17, color=rgb("C9BEAC"))
    pie(s, oscuro=True)
    return s


def cuerpo(slide, l, t, w, h):
    """Devuelve un text_frame vacío para meter párrafos/viñetas."""
    tb = slide.shapes.add_textbox(int(l), int(t), int(w), int(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    return tf


def vinetas(slide, l, t, w, h, items, size=16, space=7):
    tf = cuerpo(slide, l, t, w, h)
    for it in items:
        if isinstance(it, tuple):
            parrafo(tf, it[0], size=size - 1, bullet=True, nivel=1, space_after=space - 2)
        else:
            parrafo(tf, it, size=size, bullet=True, space_after=space)
    return tf


def tarjeta(slide, l, t, w, h, rotulo, valor=None, texto=None, foco=False, size_val=30):
    rect(slide, l, t, w, h, BLANCO, line=REGLA)
    if foco:
        rect(slide, l, t, Inches(0.06), h, ACENTO)
    x = l + Inches(0.22)
    caja(slide, x, t + Inches(0.16), w - Inches(0.4), Inches(0.3), rotulo.upper(), size=9, bold=True, color=TENUE)
    y = t + Inches(0.46)
    if valor:
        caja(slide, x, y, w - Inches(0.4), Inches(0.6), valor, size=size_val, bold=True, color=INK, font=TITULO_F)
        y += Inches(0.62)
    if texto:
        tf = cuerpo(slide, x, y, w - Inches(0.4), h - (y - t) - Inches(0.15))
        parrafo(tf, texto, size=12.5, color=INK2, space_after=0)


def tabla(slide, l, t, w, filas, anchos, size=12, cab_size=10, alto_fila=Inches(0.42)):
    n_r, n_c = len(filas), len(filas[0])
    shp = slide.shapes.add_table(n_r, n_c, int(l), int(t), int(w), int(alto_fila * n_r))
    tb = shp.table
    for j, a in enumerate(anchos):
        tb.columns[j].width = int(a)
    for i, fila in enumerate(filas):
        for j, val in enumerate(fila):
            c = tb.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.04)
            c.fill.solid()
            c.fill.fore_color.rgb = PLANO if i == 0 else (BLANCO if i % 2 else rgb("FBFAF7"))
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            partes = str(val).split("**")
            for k, trozo in enumerate(partes):
                if not trozo:
                    continue
                r = p.add_run()
                r.text = trozo
                r.font.size = Pt(cab_size if i == 0 else size)
                r.font.name = CUERPO_F
                r.font.bold = (i == 0) or (k % 2 == 1)
                r.font.color.rgb = TENUE if i == 0 else INK
    return tb


def cita_pie(slide, texto):
    caja(slide, MX, H - Inches(0.78), ANCHO, Inches(0.3), texto, size=9.5, color=TENUE, italic=True)


def remate(slide, texto, y=None):
    y = y or H - Inches(1.45)
    rect(slide, MX, y, ANCHO, Emu(19050), ACENTO)
    caja(slide, MX, y + Inches(0.12), ANCHO, Inches(0.55), texto, size=17, bold=True, color=INK, font=TITULO_F)


def estilo_chart(chart, leyenda=False):
    chart.font.name = CUERPO_F
    chart.font.size = Pt(11)
    chart.font.color.rgb = INK2
    chart.has_legend = leyenda
    if leyenda:
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(11)
    for ax in (chart.category_axis, chart.value_axis):
        ax.format.line.color.rgb = REGLA
        ax.tick_labels.font.size = Pt(11)
        ax.tick_labels.font.color.rgb = TENUE
    chart.value_axis.major_gridlines.format.line.color.rgb = rgb("E4E0D6")
    chart.category_axis.has_major_gridlines = False


# ============================ PORTADA ============================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, W, H, PX)
filo(s, t=H - Inches(0.07))
caja(s, MX, Inches(1.3), ANCHO, Inches(0.4), "PROYECTO ENOLYTICS · FEDER ANDALUCÍA 2021-2027", size=12, bold=True, color=rgb("EBD98A"))
caja(s, MX, Inches(1.85), Inches(11.5), Inches(2.2),
     "Inteligencia competitiva integrada para la gestión enoturística del Marco de Jerez",
     size=40, bold=True, color=CREMA, font=TITULO_F)
caja(s, MX, Inches(4.15), Inches(11), Inches(0.9),
     "De la memoria científico-técnica a la plataforma: minería de textos, análisis de "
     "importancia-desempeño y un cuadro de mando para bodegas y gestores del destino.",
     size=17, color=rgb("C9BEAC"))
caja(s, MX, Inches(5.55), Inches(6), Inches(0.35), "Cursos de Verano de la Universidad de Cádiz · 2026", size=13, color=CREMA)
caja(s, MX, Inches(5.9), Inches(11), Inches(0.9),
     "IP: María Paula Lechuga Sancho · Co-IP: Antonio Rafael Ramos Rodríguez\n"
     "Equipo: Alfredo Sánchez-Roselly Navarro · Fernando Martín-Hidalgo (Bodegas Emilio Hidalgo) · "
     "Águeda Caputto Mateos (Bodegas Tradición) · José Luis Baños Ramírez (Ruta del Vino y Brandy de Jerez)",
     size=11, color=rgb("C9BEAC"))
pie(s, oscuro=True)
notas(s, """
Presentación del proyecto. Dos partes: (I) el proyecto tal como se concibió en la memoria científico-técnica,
firmada en febrero de 2025; (II) la aplicación desarrollada durante el primer año, con sus datos, métodos,
módulos, funcionalidades y aportaciones.
Encuadre para el alumnado: es un ejemplo completo de investigación aplicada, desde la solicitud hasta el
prototipo, incluyendo lo que se ha desviado de lo previsto y por qué.
""")

# ============================ ÍNDICE ============================
s, y = lamina("Estructura de la sesión", eyebrow="Índice")
col_w = (ANCHO - Inches(0.6)) / 2
rect(s, MX, y, col_w, Inches(4.6), PLANO)
rect(s, MX + col_w + Inches(0.6), y, col_w, Inches(4.6), PLANO)
caja(s, MX + Inches(0.3), y + Inches(0.25), col_w, Inches(0.4), "PARTE I · EL PROYECTO", size=12, bold=True, color=ACENTO)
caja(s, MX + Inches(0.3), y + Inches(0.6), col_w - Inches(0.6), Inches(0.5), "Según la memoria científico-técnica", size=18, bold=True, font=TITULO_F)
vinetas(s, MX + Inches(0.3), y + Inches(1.2), col_w - Inches(0.6), Inches(3.2), [
    "El enoturismo como objeto de estudio",
    "Inteligencia competitiva e inteligencia integrada",
    "Destinos y empresas turísticas inteligentes: UNE 178502 y UNE 178510",
    "Reseñas online, big data y ética del dato",
    "Análisis IPA, objetivo, indicadores y arquitectura",
    "Alineación estratégica, equipo, cronograma y presupuesto",
], size=14, space=6)
x2 = MX + col_w + Inches(0.6)
caja(s, x2 + Inches(0.3), y + Inches(0.25), col_w, Inches(0.4), "PARTE II · LA APLICACIÓN", size=12, bold=True, color=ACENTO)
caja(s, x2 + Inches(0.3), y + Inches(0.6), col_w - Inches(0.6), Inches(0.5), "Desarrollo, datos, análisis y aportaciones", size=18, bold=True, font=TITULO_F)
vinetas(s, x2 + Inches(0.3), y + Inches(1.2), col_w - Inches(0.6), Inches(3.2), [
    "Cómo se ha construido: arquitectura y decisiones",
    "Qué datos usa: fuentes, corpus y trazabilidad",
    "Qué análisis hace: PLN y su validación, PRCA, IPA/IPCA/DIPA, tres factores, Kano, competidores",
    "Funcionalidades y validación con usuarios",
    "Aportaciones al sector, encaje en la UNE 178510, limitaciones y líneas futuras",
], size=14, space=6)
notas(s, "Anunciar la estructura y que la parte II incluye una demostración de la aplicación en vivo.")

# ============================ PARTE I ============================
separador("PARTE I", "El proyecto según la memoria científico-técnica",
          "Contexto, marco teórico, objetivo, sistema de indicadores, arquitectura prevista, "
          "alineación estratégica, equipo y presupuesto. Memoria firmada el 14 de febrero de 2025.")

# ---- I.1 Contexto ----
s, y = lamina("El enoturismo como sector estratégico", eyebrow="Parte I · Contexto",
              subtitulo="Actividad clave del turismo y motor de la economía rural en las regiones vitivinícolas.")
cw = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw, Inches(1.75), "Visitantes a bodegas y museos · España 2023", "2.977.115",
        "Crecimiento del **+18,2 %** respecto al año anterior (ACEVIN, 2024).")
tarjeta(s, MX + cw + Inches(0.25), y, cw, Inches(1.75), "Impacto económico · España 2023", "76,5 M€",
        "Gasto medio diario del enoturista: **201,80 €** (ACEVIN, 2023).")
tarjeta(s, MX + 2 * (cw + Inches(0.25)), y, cw, Inches(1.75), "Marco de Jerez · 2023", "382.716",
        "Entre las **tres rutas del vino más visitadas** de España. En 2024: 425.652.", foco=True)
vinetas(s, MX, y + Inches(2.05), ANCHO, Inches(2.0), [
    "El crecimiento plantea retos: **diferenciar la oferta**, **gestionar la experiencia** del visitante y "
    "**adaptar la promoción** a un mercado digitalizado (KPMG, 2023; ACEVIN, 2024).",
    "Las expectativas del consumidor, la segmentación y una competencia cada vez más intensa dificultan "
    "la captación y fidelización (Shin y Nicolau, 2022).",
    "Consecuencia: las bodegas deben analizar **de forma continua** a competidores y consumidores.",
], size=15)
cita_pie(s, "Fuentes: memoria científico-técnica del proyecto; ACEVIN (2023, 2024); KPMG (2023); Shin y Nicolau (2022).")
notas(s, """
Cifras tal como aparecen en la memoria (datos de 2023). El dato de 2024 del Marco (425.652) ya es del
observatorio ACEVIN publicado después; se incluye para actualizar.
Idea clave: crecer no es el problema; el problema es decidir con información en un entorno más competitivo.
""")

# ---- I.2 Marco teórico: inteligencia competitiva ----
s, y = lamina("Inteligencia competitiva", eyebrow="Parte I · Marco teórico",
              subtitulo="Definición adoptada por el proyecto y su relevancia para las empresas turísticas.")
rect(s, MX, y, ANCHO, Inches(1.55), PLANO)
rect(s, MX, y, Inches(0.06), Inches(1.55), ACENTO)
tf = cuerpo(s, MX + Inches(0.3), y + Inches(0.18), ANCHO - Inches(0.6), Inches(1.3))
parrafo(tf, "«Proceso de identificación de los competidores, recopilación de inteligencia relacionada con las "
            "prácticas de los competidores de una manera ética y legal, almacenamiento de esta inteligencia en una "
            "estructura de fácil acceso, difusión de manera oportuna y análisis de la inteligencia recopilada para "
            "decidir cómo ser más reactivo o proactivo en la industria.»", size=14, color=INK, italic=True, space_after=4)
parrafo(tf, "Köseoglu, Sehitoglu, Ross y Parnell (2021, p. 532), Tourism Management Perspectives.", size=11, color=TENUE, space_after=0)
vinetas(s, MX, y + Inches(1.8), ANCHO, Inches(2.4), [
    "Proceso de **recopilación, procesamiento, análisis y difusión** que convierte la información en "
    "inteligencia procesable: conocimiento que ayuda a decidir y planificar (du Toit, 2015).",
    "También es un **producto**: informa sobre el comportamiento presente y futuro de clientes, competidores, "
    "proveedores, mercado, tecnología y entorno (Yap et al., 2014).",
    "Considerada la **cuarta razón de supervivencia empresarial**, tras el capital, la tecnología y el talento (Bao, 2020).",
    "Las empresas turísticas operan en entornos inciertos, dinámicos y competitivos, lo que la hace crucial "
    "(Köseoglu et al., 2021; Settembre-Blundo et al., 2021).",
], size=14, space=6)
notas(s, """
Subrayar «de una manera ética y legal»: la inteligencia competitiva trabaja con información pública.
Distinguir dato → información → inteligencia. Un dato que llega tarde o no se entiende no es inteligencia.
La definición integra trabajos previos: Bennett (2003), Bulger (2016), Porter (1980), Simkin y Cheng (1997).
""")

# ---- I.3 Inteligencia integrada: las siete ----
s, y = lamina("Inteligencia integrada: seis fuentes y una séptima", eyebrow="Parte I · Marco teórico",
              subtitulo="El modelo de Bulger (2016), ampliado por el proyecto con la Inteligencia en Sostenibilidad.")
filas = [
    ["Fuente de inteligencia", "Qué evalúa", "Categoría SEGITTUR"],
    ["Económica", "Impacto económico en el territorio, rentabilidad, contribución al empleo", "Sostenibilidad"],
    ["De mercado", "Tendencias, patrones de búsqueda online, predisposición al gasto", "Demanda"],
    ["De competidores", "Oferta frente a otros destinos, estrategias diferenciadoras, precios, reputación", "Oferta / Demanda / Sost."],
    ["De clientes", "Perfil, motivaciones, satisfacción, fidelización, canales de reserva", "Demanda"],
    ["De negocios", "Infraestructura, servicios, formación del personal, innovación", "Oferta / Sostenibilidad"],
    ["Tecnológica", "Adopción de tecnologías y accesibilidad universal", "Oferta / Sostenibilidad"],
    ["**En sostenibilidad (nueva)**", "**Impacto ambiental, certificaciones, economía circular, transporte sostenible**", "**Sostenibilidad**"],
]
tabla(s, MX, y, ANCHO, filas, [Inches(2.7), Inches(6.6), Inches(2.53)], size=12, alto_fila=Inches(0.4))
tf = cuerpo(s, MX, y + Inches(3.45), ANCHO, Inches(1.1))
parrafo(tf, "La inteligencia integrada enfatiza la **naturaleza colectiva** de todos los conjuntos de inteligencia para lograr "
            "ventaja competitiva, en lugar de centrarse en uno solo (Bulger, 2011, 2016; Köseoglu et al., 2021). "
            "La séptima fuente se apoya en el marco de indicadores de SEGITTUR y en la Inteligencia Sostenible Integrada "
            "de Silvestre y Fonseca (2020), y en la visión de Ahmad (2015) del Business Intelligence como fuente de ventaja "
            "competitiva sostenible.", size=13, space_after=0)
cita_pie(s, "Tabla 1 de la memoria (elaboración propia a partir de SEGITTUR). Alineado con la norma UNE 178502 sobre Destinos Turísticos Inteligentes.")
notas(s, """
Bulger (2016) propone seis subcampos. La aportación conceptual del proyecto es la séptima: tratar la sostenibilidad
como inteligencia propia, no como un apartado.
SEGITTUR organiza sus indicadores en tres dimensiones (oferta, demanda, sostenibilidad); cada inteligencia se mapea
sobre ellas. Nótese que la inteligencia económica cae en «sostenibilidad»: en ese marco la sostenibilidad incluye el
pilar económico y social, no solo el ambiental.
""")


# ---- I.3b DTI y ETI ----
s, y = lamina("Destinos y empresas turísticas inteligentes", eyebrow="Parte I · Marco normativo",
              subtitulo="El marco de SEGITTUR y el CTN 178 de UNE: del destino (UNE 178501 y 178502) a la empresa (UNE 178510:2023).")
cw2 = (ANCHO - Inches(0.5)) / 2
# columna DTI
rect(s, MX, y, cw2, Inches(3.3), BLANCO, line=REGLA)
caja(s, MX + Inches(0.25), y + Inches(0.18), cw2 - Inches(0.5), Inches(0.3), "DESTINO TURÍSTICO INTELIGENTE (DTI)", size=10, bold=True, color=ACENTO)
tf = cuerpo(s, MX + Inches(0.25), y + Inches(0.5), cw2 - Inches(0.5), Inches(3.0))
parrafo(tf, "Modelo impulsado por la Secretaría de Estado de Turismo a través de SEGITTUR: mejora de la competitividad "
            "basada en la **gobernanza y la corresponsabilidad** turística.", size=12.5, space_after=6)
parrafo(tf, "**Cinco ejes:** gobernanza · innovación · tecnología · accesibilidad · sostenibilidad.", size=12.5, space_after=6)
parrafo(tf, "**Objetivos:** competitividad y posicionamiento; experiencia del turista antes, durante y después del viaje; "
            "calidad de vida de los residentes; alianzas público-privadas; conectividad; **desestacionalización**.", size=12.5, space_after=6)
parrafo(tf, "**Normas:** UNE 178501:2018 (sistema de gestión del DTI) y **UNE 178502:2022** (indicadores y herramientas), "
            "con la que se alinea el sistema de indicadores de ENOLYTICS.", size=12.5, space_after=0)
# columna ETI
x2 = MX + cw2 + Inches(0.5)
rect(s, x2, y, cw2, Inches(3.3), rgb("FDF6F1"), line=ACENTO)
caja(s, x2 + Inches(0.25), y + Inches(0.18), cw2 - Inches(0.5), Inches(0.3), "EMPRESA TURÍSTICA INTELIGENTE (ETI) · UNE 178510:2023", size=10, bold=True, color=ACENTO)
tf = cuerpo(s, x2 + Inches(0.25), y + Inches(0.5), cw2 - Inches(0.5), Inches(3.0))
parrafo(tf, "«Empresa turística que utiliza la tecnología y enfoques innovadores para mejorar sus sistemas de gestión, servicios, "
            "productos y la experiencia general de los turistas, aumentando su competitividad, buscando la accesibilidad para todos y la "
            "sostenibilidad en sus tres vertientes» (3.2).", size=12, italic=True, color=INK, space_after=6)
parrafo(tf, "**Cinco ejes en paralelo con el DTI:** gestión · innovación · tecnología · accesibilidad · sostenibilidad, articulados en un "
            "sistema de gestión con ciclo **Planificar–Hacer–Verificar–Actuar**.", size=12.5, space_after=6)
parrafo(tf, "**Lo que la distingue (4.1):** «basa la toma de decisiones en el uso de dato». Recopila, procesa y analiza datos para "
            "comprender el mercado, personalizar, anticipar tendencias y **gestionar comentarios y reseñas**.", size=12.5, space_after=0)
remate(s, "La ETI debe transformar datos en conocimiento y aplicarlo a la decisión (4.2). ENOLYTICS es una herramienta para eso.", y=y + Inches(3.5))
cita_pie(s, "UNE 178510:2023, apartados 0.2, 0.3, 3.2, 4.1 y 4.2; anexo B (panorama normativo DTI). Convive con el Sistema de Sostenibilidad Turística Integral (SSTI) de la Secretaría de Estado de Turismo.")
notas(s, """
Explicar el paralelismo: el DTI es el destino; la ETI es la empresa dentro del destino. Mismos cinco ejes, con
«gobernanza» en el destino y «gestión» en la empresa.
Dato clave para conectar con el proyecto: la norma dice que la ETI se distingue por decidir con datos y cita
explícitamente la gestión de reseñas y la escucha activa en redes sociales (5.3 a). También pide (5.3 b) una
sistemática tecnológica de recopilación, análisis y explotación de datos para decidir, y (5.3 h, anexo A.1) que
la empresa comparta información con el destino a través de una plataforma. Ese intercambio ETI-DTI es la
arquitectura de dos perfiles de ENOLYTICS.
La norma es aplicable a cualquier empresa turística, de cualquier tamaño, y es certificable frente a terceros.
""")

# ---- I.4 Reseñas online y big data ----
s, y = lamina("Reseñas online y big data como fuente de inteligencia", eyebrow="Parte I · Marco teórico")
cw2 = (ANCHO - Inches(0.5)) / 2
vinetas(s, MX, y, cw2, Inches(4.4), [
    "Más de 3.900 millones de usuarios de Internet; **más del 60 %** ha escrito reseñas online (Global Web Index, 2021).",
    "En turismo, la **intangibilidad** del servicio hace que la experiencia de otros consumidores sea determinante "
    "en la decisión (Hu y Yang, 2021; Line et al., 2020).",
    "El enfoque **big data analytics** aprovecha datos de amplitud, profundidad y escala sin precedentes "
    "(Manyika et al., 2011; Mayer-Schönberger y Cukier, 2013).",
    "En enoturismo, las reseñas influyen en la elección de bodega y sirven de **retroalimentación** para anticipar "
    "demandas (Quadri-Felitti y Fiore, 2016; Wu et al., 2024).",
], size=14, space=7)
rect(s, MX + cw2 + Inches(0.5), y, cw2, Inches(4.4), PLANO)
tf = cuerpo(s, MX + cw2 + Inches(0.8), y + Inches(0.25), cw2 - Inches(0.6), Inches(4))
parrafo(tf, "TÉCNICAS PREVISTAS EN LA MEMORIA", size=10, bold=True, color=ACENTO, space_after=10)
for t_ in ["**Minería de textos** para descubrir atributos del servicio en el texto libre.",
           "**Análisis de sentimiento** para medir el tono hacia cada atributo.",
           "**Modelado de temas** (LDA, BERT) para identificar temas latentes.",
           "**Aprendizaje automático y PLN** (Bi et al., 2019; Wu et al., 2024)."]:
    parrafo(tf, t_, size=13.5, bullet=True, space_after=8)
parrafo(tf, "Atributos ya identificados en la literatura: calidad del vino, servicio del personal, paisaje y valor "
            "educativo (Shin y Nicolau, 2022; Wu et al., 2024). La insatisfacción suele derivar de ineficiencias "
            "operativas —esperas, personal inconsistente— (Meneses et al., 2023).", size=12, color=INK2, space_after=0)
notas(s, """
Ventaja metodológica de las reseñas frente a la encuesta: son datos NO reactivos, nadie los escribió para el
investigador. Desventaja: sesgo de autoselección (escribe el muy satisfecho y el muy insatisfecho).
Anticipar que Meneses et al. (2023) señalan las esperas y la organización como origen de insatisfacción: en la
parte II veremos que el corpus del Marco lo confirma.
""")


# ---- I.4b Ética y legalidad del dato ----
s, y = lamina("Ética y legalidad del dato", eyebrow="Parte I · Marco teórico",
              subtitulo="La definición adoptada exige recopilar «de una manera ética y legal». Qué significa eso en la práctica.")
cw3 = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw3, Inches(2.75), "Qué datos se usan", None,
        "Solo **contenido público** (reseñas publicadas para ser leídas, webs de las bodegas) y **estadísticas oficiales**. "
        "Ningún dato privado ni de clientes. Las reseñas se obtienen a través de un **proveedor de datos con API**, no por "
        "extracción directa del sitio; el navegador automatizado solo se usa sobre las webs de las propias bodegas.")
tarjeta(s, MX + cw3 + Inches(0.25), y, cw3, Inches(2.75), "Cómo se tratan", None,
        "Principios del RGPD: **minimización** (art. 5.1.c) y **limitación de finalidad**, con las garantías del art. 89 para fines "
        "de investigación. El nombre del autor **no interviene en ningún análisis**: se trabaja con textos agregados por bodega, "
        "atributo e idioma. El corpus crudo no se versiona ni se redistribuye; solo los agregados.", foco=True)
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y, cw3, Inches(2.75), "Qué exige el marco", None,
        "La **UNE 178510** (5.3 d) obliga a la ETI a tratar los datos personales conforme al RGPD y a proteger la información "
        "(5.3 e). La definición de inteligencia competitiva de Köseoglu et al. (2021) hace de la ética y la legalidad parte del "
        "propio concepto, no un añadido.")
vinetas(s, MX, y + Inches(3.0), ANCHO, Inches(1.3), [
    "**Se analizan textos, no personas.** Ninguna conclusión de la plataforma se refiere a un individuo; todas se refieren a bodegas, "
    "atributos o al destino.",
    "**Punto en revisión:** el listado de reseñas de cada ficha reproduce el nombre público del perfil, como hace la propia plataforma "
    "de origen. Se está valorando mostrarlo sin ese nombre.",
], size=13, space=6)
cita_pie(s, "Reglamento (UE) 2016/679 (RGPD), arts. 4, 5 y 89 · UNE 178510:2023, 5.3 d) y e) · Köseoglu et al. (2021).")
notas(s, """
Es la pregunta que más sale en cualquier sala («¿esto no es espiar?»). Contestarla antes de que la hagan.
Distinción útil para el alumnado: dato PÚBLICO no equivale a dato LIBRE. Una reseña es pública, pero su autor
sigue siendo una persona identificable; por eso los análisis son agregados y el autor no entra en ninguno.
Reconocer el punto en revisión (nombre de perfil en el listado de la ficha) es más creíble que afirmar que
todo está resuelto.
""")

# ---- I.5 IPA y extensiones ----
s, y = lamina("Análisis de importancia-desempeño y sus extensiones", eyebrow="Parte I · Marco teórico",
              subtitulo="El módulo analítico comprometido: IPA, IPCA, DIPA y DIPCA. Valor añadido frente a Shin y Nicolau (2022) y Wu et al. (2024).")
# cuadrantes
qx, qy, qw, qh = MX, y, Inches(6.0), Inches(3.9)
cw3, ch3 = (qw - Inches(0.1)) / 2, (qh - Inches(0.1)) / 2
cuad = [
    (0, 0, "Posible exceso", "Baja importancia, alto desempeño: recursos que podrían reasignarse.", False),
    (1, 0, "Siga con el buen trabajo", "Alta importancia, alto desempeño: la fortaleza a sostener.", False),
    (0, 1, "Baja prioridad", "Baja importancia, bajo desempeño: no merece recursos hoy.", False),
    (1, 1, "Concéntrese aquí", "Alta importancia, bajo desempeño: donde actuar primero.", True),
]
for cx, cy, tit, desc, foco in cuad:
    l = qx + cx * (cw3 + Inches(0.1)); t = qy + cy * (ch3 + Inches(0.1))
    rect(s, l, t, cw3, ch3, rgb("FDF6F1") if foco else BLANCO, line=ACENTO if foco else REGLA)
    caja(s, l + Inches(0.18), t + Inches(0.18), cw3 - Inches(0.3), Inches(0.4), tit, size=15, bold=True,
         color=ACENTO if foco else INK, font=TITULO_F)
    caja(s, l + Inches(0.18), t + Inches(0.62), cw3 - Inches(0.3), ch3 - Inches(0.7), desc, size=11.5, color=INK2)
caja(s, qx, qy + qh + Inches(0.05), qw, Inches(0.3), "Eje horizontal: importancia (baja → alta)   |   eje vertical: desempeño (bajo → alto)", size=9.5, color=TENUE)
xr = MX + qw + Inches(0.4); wr = ANCHO - qw - Inches(0.4)
tf = cuerpo(s, xr, y, wr, Inches(4.3))
parrafo(tf, "**IPA** — Importance-Performance Analysis (Martilla y James, 1977). Cruza importancia y desempeño de "
            "cada atributo en cuatro cuadrantes con nomenclatura de Albayrak (2015).", size=13, space_after=9)
parrafo(tf, "**IPCA** — Importance-Performance Competitor Analysis. Sustituye el desempeño absoluto por la **brecha "
            "frente a los competidores** (Albayrak, 2015). Corrige la principal limitación del IPA.", size=13, space_after=9)
parrafo(tf, "**DIPA** — Dynamic IPA. Aplicación repetida en distintos periodos para detectar **cambios de tendencia** "
            "y actuar de forma proactiva.", size=13, space_after=9)
parrafo(tf, "**DIPCA** — Combinación de ambas: evolución del **desempeño competitivo en el tiempo**.", size=13, space_after=9)
parrafo(tf, "Aplicaciones previas: cruceros (Bi et al., 2019), destinos (Albayrak, 2015), bodegas (Shin y Nicolau, 2022).",
        size=11.5, color=TENUE, space_after=0)
notas(s, """
Recorrer los cuadrantes en voz alta. «Posible exceso» es el que más cuesta entender: se está invirtiendo en
algo que el cliente no valora especialmente. «Concéntrese aquí» justifica todo el método.
Punto para el alumnado: el IPA es de 1977; lo innovador del proyecto no es el gráfico sino (a) de dónde salen
los dos ejes (reseñas) y (b) las extensiones competitiva y dinámica.
""")

# ---- I.6 Objetivo ----
s, y = lamina("Objetivo del proyecto", eyebrow="Parte I · Objetivo")
rect(s, MX, y, ANCHO, Inches(1.7), PLANO)
rect(s, MX, y, Inches(0.06), Inches(1.7), ACENTO)
tf = cuerpo(s, MX + Inches(0.3), y + Inches(0.2), ANCHO - Inches(0.6), Inches(1.4))
parrafo(tf, "«Desarrollar un modelo avanzado de inteligencia competitiva integrada que permita la creación de una "
            "plataforma digital o dashboard para optimizar la gestión y planificación de destinos y empresas "
            "enoturísticas en el Marco de Jerez.»", size=16, color=INK, italic=True, space_after=4)
parrafo(tf, "Memoria científico-técnica, apartado «Introducción».", size=11, color=TENUE, space_after=0)
vinetas(s, MX, y + Inches(2.0), ANCHO, Inches(2.6), [
    "**Técnicas:** minería de textos, análisis de sentimiento y modelado de temas sobre contenido generado por los "
    "usuarios (TripAdvisor, Google Reviews, redes sociales).",
    "**Herramientas analíticas:** IPA, IPCA, DIPA y DIPCA para evaluar la evolución temporal y la competitividad de los atributos.",
    "**Entregable:** un cuadro de mando interactivo que integre datos estructurados (indicadores económicos, sociales, de "
    "sostenibilidad) y no estructurados (reseñas), con **recomendaciones accionables**.",
    "**Diferencial declarado:** «no solo recopila datos, sino que los transforma en inteligencia procesable para la toma "
    "de decisiones estratégicas».",
], size=14, space=7)
notas(s, "Objetivo literal de la memoria. Las cuatro viñetas son la descomposición operativa que luego se contrasta en la parte II.")

# ---- I.7 Sistema de indicadores (Tabla 1) ----
s, y = lamina("Sistema integrado de indicadores y fuentes de datos", eyebrow="Parte I · Tabla 1 de la memoria",
              subtitulo="Núcleo de datos que alimenta los modelos IPA, IPCA, DIPA y DIPCA.")
filas = [
    ["Inteligencia", "Indicadores clave previstos", "Fuentes de datos previstas"],
    ["Económica", "Impacto económico · contribución al empleo · rentabilidad", "INE, Dataestur · cuestionarios a bodegas"],
    ["De mercado", "Búsquedas online y RRSS · tendencias · comparación de demanda · predisposición al gasto", "Google Trends, RRSS · analítica web"],
    ["De competidores", "Oferta vs. otros destinos · estrategias diferenciadoras · reputación online · precios", "Análisis de RRSS y benchmarking · cuestionarios"],
    ["De clientes", "Perfil y comportamiento · motivaciones y fidelización · canales de reserva · volumen de visitas · satisfacción", "Cuestionarios a visitantes · big data"],
    ["De negocios", "Bodegas abiertas al turismo · museos · enotecas · eventos · empleados · formación · innovación", "OGD y AAPP · cuestionarios"],
    ["Tecnológica", "Adopción tecnológica (RA, visitas virtuales, reservas) · accesibilidad universal e índice digital", "Cuestionarios · datos de OGD"],
    ["En sostenibilidad", "Consumo de agua y energía, huella de carbono · certificaciones · economía circular · transporte sostenible", "OMT, Eurostat, INE, OIV… · encuestas"],
]
tabla(s, MX, y, ANCHO, filas, [Inches(2.0), Inches(6.2), Inches(3.63)], size=11, alto_fila=Inches(0.47))
cita_pie(s, "Fuente: Tabla 1 de la memoria, «Sistema Integrado de Indicadores para el Análisis del Enoturismo y fuentes de datos» (elaboración propia a partir de SEGITTUR).")
notas(s, """
No leer la tabla entera. Señalar que combina fuentes públicas (INE, Dataestur, Google Trends) con cuestionarios
propios para lo que no existe en abierto. En la parte II se verá qué indicadores se han cubierto ya con fuentes
públicas y cuáles siguen pendientes de cuestionario.
""")

# ---- I.8 Arquitectura prevista ----
s, y = lamina("Arquitectura del modelo de medición prevista", eyebrow="Parte I · Diseño técnico")
cw2 = (ANCHO - Inches(0.5)) / 2
tarjeta(s, MX, y, cw2, Inches(2.1), "Subsistema ETL", None,
        "**Extracción, transformación y carga.** Recopila de fuentes ad hoc (encuestas), administrativas (APIs), "
        "estadísticas oficiales (INE, Dataestur) y, si procede, proveedores privados. Limpieza, normalización, "
        "eliminación de duplicados y enriquecimiento.")
tarjeta(s, MX + cw2 + Inches(0.5), y, cw2, Inches(2.1), "Subsistema de visualización", None,
        "**Cuadro de mando** con gráficos, mapas, tablas, filtros y personalización; control de permisos; "
        "**simulaciones y proyecciones de escenarios**. Inspirado en el Sistema de Inteligencia Turística de la "
        "Costa del Sol (Málaga).")
tf = cuerpo(s, MX, y + Inches(2.4), ANCHO, Inches(2.2))
parrafo(tf, "**Tecnología prevista:** Azure Data Factory (ingesta), Azure SQL Database y Blob Storage (almacenamiento), "
            "Azure Analysis Services (modelado), **Power BI** (visualización), Active Directory, Key Vault y Monitor.", size=14, space_after=8)
parrafo(tf, "**Implementación en tres fases:** piloto en dos bodegas (Emilio Hidalgo y Tradición) → expansión al resto "
            "del Marco → modelo ontológico para optimizar la recogida y el análisis.", size=14, space_after=8)
parrafo(tf, "En la parte II se explica por qué el prototipo se ha construido finalmente con **Python y Streamlit** y no con "
            "Power BI sobre Azure, y qué implicaciones tiene.", size=13, color=ACENTO, space_after=0)
notas(s, "Anunciar aquí la desviación tecnológica para que no parezca escondida cuando aparezca en la parte II.")

# ---- I.9 Alineación estratégica ----
s, y = lamina("Alineación estratégica y apoyos institucionales", eyebrow="Parte I · Relevancia")
cw3 = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw3, Inches(2.2), "Estrategia del Sector Vitivinícola Español 2022-2027", None,
        "Digitalización y sostenibilidad como ejes de transformación. La plataforma evalúa la **madurez digital** de las bodegas.")
tarjeta(s, MX + cw3 + Inches(0.25), y, cw3, Inches(2.2), "Destinos Turísticos Inteligentes (SEGITTUR)", None,
        "Integrar tecnologías emergentes en la gestión de destinos. Indicadores alineados con la **norma UNE 178502**.")
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y, cw3, Inches(2.2), "Programa Operativo FEDER Andalucía 2021-2027", None,
        "**P1A y P2A:** sistemas y metodologías para gestión y promoción · **P4A:** reducir la estacionalidad · "
        "**P3A:** tecnologías digitales para sostenibilidad y competitividad.", foco=True)
tf = cuerpo(s, MX, y + Inches(2.5), ANCHO, Inches(2.0))
parrafo(tf, "**Apoyos del sector (cartas de interés):** Consejo Regulador de las DD.OO. «Jerez-Xérès-Sherry» y «Manzanilla-Sanlúcar "
            "de Barrameda», asociación Ruta del Vino y Brandy del Marco de Jerez, Patronato Provincial de Turismo de la Diputación "
            "de Cádiz y bodegas de larga trayectoria enoturística.", size=14, space_after=8)
parrafo(tf, "**Diseño modular, escalable y replicable:** el Marco de Jerez como caso inicial y la metodología como modelo de "
            "referencia para otras regiones vitivinícolas de Andalucía y España.", size=14, space_after=0)
notas(s, "La prioridad P4A (desestacionalizar) reaparece en la parte II con el hallazgo de los cruceros.")

# ---- I.10 Equipo y cronograma ----
s, y = lamina("Equipo y cronograma de actuaciones", eyebrow="Parte I · Plan de trabajo",
              subtitulo="Plazo de ejecución: 24 meses, en cinco fases (Tabla 2 de la memoria).")
filas = [
    ["Fase", "Hitos principales", "Meses"],
    ["1 · Planificación y diseño", "Requisitos, análisis de necesidades, diseño del modelo de medición (indicadores y KPI), cuestionarios", "1-4"],
    ["2 · Infraestructura y datos", "Implementación de la arquitectura, recopilación de datos de prueba, desarrollo del dashboard, integración de fuentes", "5-10"],
    ["3 · Prueba piloto", "Lanzamiento en Emilio Hidalgo y Tradición, evaluación de calidad de datos, ajustes, informes preliminares", "11-16"],
    ["4 · Implementación y escalabilidad", "Optimización, expansión a más bodegas y regiones, formación, evaluación de impacto", "17-22"],
    ["5 · Consolidación", "Presentación de resultados y recomendaciones, informe final de impacto", "23-24"],
]
tabla(s, MX, y, Inches(7.6), filas, [Inches(2.2), Inches(4.6), Inches(0.8)], size=11, alto_fila=Inches(0.52))
xr = MX + Inches(7.9); wr = ANCHO - Inches(7.9)
rect(s, xr, y, wr, Inches(3.15), PLANO)
tf = cuerpo(s, xr + Inches(0.25), y + Inches(0.2), wr - Inches(0.5), Inches(2.9))
parrafo(tf, "RESPONSABILIDADES", size=10, bold=True, color=ACENTO, space_after=8)
for t_ in ["**ARRR** · liderazgo técnico, supervisión metodológica, análisis de datos, validación del dashboard",
           "**MPLS** · validación de resultados, integración de indicadores, publicación",
           "**ASR** · desarrollo tecnológico e infraestructura de datos",
           "**FMH, ACM** · vinculación con las bodegas piloto, usabilidad",
           "**JLBR** · conexión con la Ruta del Vino y Brandy de Jerez",
           "**Personal técnico-investigador** (1 año, media jornada) · implantación en bodegas y formación"]:
    parrafo(tf, t_, size=11, bullet=True, space_after=5)
notas(s, "El proyecto se encuentra, en el momento de la sesión, entre las fases 2 y 3: infraestructura construida y piloto en curso.")

# ---- I.11 Presupuesto e impacto ----
s, y = lamina("Presupuesto, impacto esperado y divulgación", eyebrow="Parte I · Resultados esperados")
cw2 = (ANCHO - Inches(0.5)) / 2
tarjeta(s, MX, y, cw2, Inches(2.35), "Presupuesto total (24 meses)", "39.628 €",
        "Costes directos 36.025 € (personal 17.000 · equipamiento y fuentes de datos 7.500 · fungible 3.875 · "
        "servicios externos 4.950 · movilidad 1.500 · auditoría 1.200) · costes indirectos 10 %: 3.603 €.", foco=True)
rect(s, MX + cw2 + Inches(0.5), y, cw2, Inches(2.35), PLANO)
tf = cuerpo(s, MX + cw2 + Inches(0.75), y + Inches(0.18), cw2 - Inches(0.5), Inches(2.1))
parrafo(tf, "IMPACTO ESPERADO", size=10, bold=True, color=ACENTO, space_after=6)
for t_ in ["**Científico:** evidencia empírica sobre inteligencia competitiva en enoturismo, área aún incipiente.",
           "**Técnico:** plataforma big data que convierte datos desestructurados en información accionable.",
           "**Económico:** competitividad, dinamización rural, gasto turístico y empleo, planificación de inversiones.",
           "**Social:** equilibrio territorial, profesionalización, accesibilidad e inclusión, cultura del vino."]:
    parrafo(tf, t_, size=11.5, bullet=True, space_after=4)
tf = cuerpo(s, MX, y + Inches(2.65), ANCHO, Inches(1.8))
parrafo(tf, "**Plan de divulgación:** 1-2 TFM y 2-3 TFG · publicaciones en revistas JCR Q1 (Tourism Review, Current Issues in Tourism, "
            "IJCHM, Tourism Management Perspectives) · repositorio abierto RODIN de la UCA · congresos (Congreso Internacional de "
            "Enoturismo, OMT, ACEDE, AEDEM, EURAM) · ferias (FITUR, Enotur Wine Fest, Wine Innovation Summit) · talleres y guías "
            "para el sector · redes DTI, Redintur, RedVitis, GIENOL, NECSTouR.", size=13, space_after=0)
notas(s, "Mención para el alumnado: los TFG y TFM previstos en el plan de divulgación son una vía real de participación en el proyecto.")

# ============================ PARTE II ============================
separador("PARTE II", "La aplicación desarrollada",
          "Cómo se ha construido, qué datos usa, qué análisis y módulos tiene, sus funcionalidades y sus principales "
          "aportaciones al sector. Estado a septiembre de 2026.")

# ---- II.1 Visión general ----
s, y = lamina("Qué se ha construido", eyebrow="Parte II · Visión general",
              subtitulo="Un cuadro de mando web, público y operativo, con dos perfiles de usuario y cinco vistas.")
cw2 = (ANCHO - Inches(0.5)) / 2
tarjeta(s, MX, y, cw2, Inches(1.65), "Para el gestor del destino", None,
        "Cómo va el Marco en las siete inteligencias, dónde están las fugas de valor y qué palancas mueven la aguja. "
        "Recomendaciones priorizadas para el destino.")
tarjeta(s, MX + cw2 + Inches(0.5), y, cw2, Inches(1.65), "Para cada bodega", None,
        "Su reputación, sus competidores directos, sus fortalezas y debilidades, sus recomendaciones y un informe "
        "descargable de una página.")
filas = [["Vista", "Qué ofrece"],
         ["Resumen ejecutivo", "Cuatro cifras del destino y semáforo de las siete inteligencias; las tres acciones más urgentes"],
         ["Las 7 inteligencias", "El análisis completo, una pestaña por inteligencia, con sus recomendaciones al pie"],
         ["Bodega individual", "Ficha, reputación, competidores directos, análisis IPA/IPCA propio, informe PDF"],
         ["Simulador de escenarios", "Cuatro variables para proyectar escenarios sobre cifras reales"],
         ["Guía y metodología", "Qué es cada apartado, de dónde sale cada dato y qué umbral aplica; descargable en PDF"]]
tabla(s, MX, y + Inches(1.9), ANCHO, filas, [Inches(2.6), Inches(9.23)], size=11.5, alto_fila=Inches(0.4))
cita_pie(s, "Desplegada en Streamlit Community Cloud; código en GitHub (Antonio-Ramos-UCA/enolytics).")
notas(s, "Anunciar que se hará una demostración en vivo al final de esta parte.")

# ---- II.2 Cómo se ha hecho ----
s, y = lamina("Cómo se ha hecho: arquitectura real del prototipo", eyebrow="Parte II · Desarrollo")
# pipeline en 5 cajas
etapas = [("Ingesta", "13 módulos: catálogo, reseñas, ACEVIN, Dataestur, cruceros, conectividad aérea, Google Trends, auditoría web, accesibilidad, transporte, sostenibilidad, precios"),
          ("ETL", "Normalización de reseñas a un formato común; vínculo con el catálogo; censo"),
          ("PLN", "Léxico multilingüe de atributos; sentimiento por frase con BERT multilingüe; idioma"),
          ("Analítica", "PRCA/Kano, IPA-IPCA-DIPA, competidores, co-ocurrencias, reputación, recomendaciones"),
          ("Cuadro de mando", "Streamlit: 5 vistas, informe PDF, simulador, guía; identidad visual propia")]
ew = (ANCHO - Inches(0.4) * 4) / 5
for i, (tit, desc) in enumerate(etapas):
    l = MX + i * (ew + Inches(0.4))
    rect(s, l, y, ew, Inches(2.15), PLANO if i != 4 else rgb("FDF6F1"), line=None if i != 4 else ACENTO)
    caja(s, l + Inches(0.15), y + Inches(0.15), ew - Inches(0.3), Inches(0.35), f"{i+1} · {tit}", size=12, bold=True, color=ACENTO)
    caja(s, l + Inches(0.15), y + Inches(0.52), ew - Inches(0.3), Inches(1.55), desc, size=10.5, color=INK2)
    if i < 4:
        caja(s, l + ew + Inches(0.05), y + Inches(0.85), Inches(0.3), Inches(0.4), "→", size=18, color=TENUE)
cw2 = (ANCHO - Inches(0.5)) / 2
vinetas(s, MX, y + Inches(2.45), cw2, Inches(2.2), [
    "**Python** de extremo a extremo: paquete `enolytics/` con **25 módulos** y unas **8.400 líneas**; nombres en español, coherentes con el dominio.",
    "**19 conjuntos de datos procesados** (CSV, versionados) alimentan el cuadro de mando; el corpus crudo no se versiona.",
    "**Verificación automatizada:** pruebas de las cinco vistas y barridos con navegador real tras cada cambio.",
], size=12.5, space=5)
rect(s, MX + cw2 + Inches(0.5), y + Inches(2.45), cw2, Inches(2.0), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + cw2 + Inches(0.75), y + Inches(2.6), cw2 - Inches(0.5), Inches(1.8))
parrafo(tf, "DESVIACIÓN DOCUMENTADA: STREAMLIT EN LUGAR DE POWER BI / AZURE", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "**Por qué:** reproducibilidad (todo el pipeline en un lenguaje, auditable y depositable en RODIN), ausencia de "
            "licencias y replicabilidad por otros grupos. **Qué se pierde:** integración corporativa y control de permisos "
            "de Azure. Recogida en la auditoría interna de coherencia memoria-prototipo.", size=11.5, space_after=0)
notas(s, """
Explicar el pipeline de izquierda a derecha. Para el alumnado: la estructura en paquetes (ingesta → etl → nlp →
analitica → dashboard) es la traducción directa de los dos subsistemas de la memoria (ETL + visualización).
La desviación tecnológica es legítima porque está argumentada y documentada; lo que no sería aceptable es
ocultarla.
""")

# ---- II.3 Fuentes de datos ----
s, y = lamina("Qué datos usa: fuentes y trazabilidad", eyebrow="Parte II · Datos",
              subtitulo="Cada indicador del cuadro de mando declara su origen con un código de tres niveles.")
filas = [
    ["Fuente", "Qué aporta", "Inteligencia", "Tipo"],
    ["ACEVIN (Observatorio Rutas del Vino)", "Visitantes e ingresos por ruta, oferta, perfil de la demanda", "Económica · Negocios", "Oficial"],
    ["Dataestur / SEGITTUR", "Gasto turístico, percepción, cruceros, conectividad aérea (búsquedas, reservas, asientos)", "Económica · Mercado · Clientes", "Oficial"],
    ["FEV", "Certificación Sustainable Wineries for Climate Protection", "Sostenibilidad", "Oficial"],
    ["Ruta del Vino y Brandy de Jerez", "Catálogo de 42 bodegas: servicios, ubicación, contacto", "Negocios", "Oficial"],
    ["Reseñas de Google (vía Outscraper)", "10.972 reseñas, 41 bodegas, 2011-2026", "Clientes · Competidores", "Observado"],
    ["Google Trends", "Interés de búsqueda frente a Rioja, Ribera del Duero y Rías Baixas", "Mercado", "Observado"],
    ["Auditoría web propia + OpenStreetMap", "Madurez digital, accesibilidad, sostenibilidad comunicada, transporte", "Tecnológica · Sostenibilidad", "Observado"],
]
tabla(s, MX, y, ANCHO, filas, [Inches(3.2), Inches(5.1), Inches(2.4), Inches(1.13)], size=11, alto_fila=Inches(0.42))
tf = cuerpo(s, MX, y + Inches(3.5), ANCHO, Inches(1.0))
parrafo(tf, "**Oficial** = estadística publicada por un organismo · **Observado** = medido por el equipo de fuentes públicas · "
            "**Estimación** = cálculo propio a partir de los anteriores, sin fuente directa, marcado como tal. "
            "Nunca se mezcla un dato oficial con una estimación sin advertirlo.", size=12.5, space_after=0)
cita_pie(s, "Indicadores de la Tabla 1 aún sin fuente abierta (empleo por bodega, consumos ambientales, precios verificados) se cubrirán con cuestionarios.")
notas(s, """
El código de tres niveles es una decisión de rigor: el usuario siempre sabe cuánto fiarse de una cifra.
Ejemplo de estimación: la curva mensual de afluencia enoturística, aproximada por el volumen de reseñas por mes.
""")

# ---- II.4 El corpus ----
s, y = lamina("El corpus de reseñas y el efecto techo", eyebrow="Parte II · Datos")
cw2 = (ANCHO - Inches(0.5)) / 2
cw4 = (cw2 - Inches(0.2)) / 2
tarjeta(s, MX, y, cw4, Inches(1.35), "Reseñas", "10.972", None, foco=True, size_val=26)
tarjeta(s, MX + cw4 + Inches(0.2), y, cw4, Inches(1.35), "Bodegas con reseñas", "41", None, size_val=26)
tarjeta(s, MX, y + Inches(1.5), cw4, Inches(1.35), "Con texto analizable", "7.258", None, size_val=26)
tarjeta(s, MX + cw4 + Inches(0.2), y + Inches(1.5), cw4, Inches(1.35), "Periodo", "2011-2026", None, size_val=22)
vinetas(s, MX, y + Inches(3.05), cw2, Inches(1.6), [
    "Multilingüe: español, inglés, alemán, francés, italiano, neerlandés… El idioma sirve como **proxy de procedencia**.",
    "Coste de descarga del corpus completo: **≈ 36 $** (API comercial). La barrera ya no es económica.",
    "Nota media: **4,56 / 5**. Y ahí empieza el problema.",
], size=12.5, space=5)
# gráfico nativo: distribución de estrellas
cd = CategoryChartData()
cd.categories = ["1 ★", "2 ★", "3 ★", "4 ★", "5 ★"]
cd.add_series("Porcentaje de reseñas", (4.1, 1.8, 3.9, 14.3, 75.9))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, int(MX + cw2 + Inches(0.5)), int(y), int(cw2), int(Inches(3.2)), cd)
ch = gf.chart
estilo_chart(ch)
ch.has_title = True
ch.chart_title.text_frame.text = "Distribución de las puntuaciones (%)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ch.chart_title.text_frame.paragraphs[0].runs[0].font.color.rgb = INK
pl = ch.plots[0]
pl.gap_width = 60
pl.has_data_labels = True
pl.data_labels.font.size = Pt(11)
pl.data_labels.number_format = '0.0"%"'
pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
ser = pl.series[0]
ser.format.fill.solid(); ser.format.fill.fore_color.rgb = CONTEXTO
pt = ser.points[4]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = NARANJA
ch.value_axis.maximum_scale = 100; ch.value_axis.has_major_gridlines = False
ch.value_axis.visible = False
rect(s, MX + cw2 + Inches(0.5), y + Inches(3.35), cw2, Inches(1.3), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + cw2 + Inches(0.7), y + Inches(3.47), cw2 - Inches(0.4), Inches(1.1))
parrafo(tf, "**Efecto techo:** tres de cada cuatro reseñas están en el máximo. Cuando casi todos puntúan 5, la media "
            "deja de discriminar —entre bodegas, entre años, entre atributos—. Obliga a bajar al **texto** y limita "
            "cualquier método que necesite variación.", size=11.5, space_after=0)
notas(s, """
El efecto techo es una limitación conocida en investigación de satisfacción: las escalas se saturan por arriba.
Aquí condiciona dos decisiones: (1) medir el sentimiento del texto, no las estrellas; (2) el modelo de Kano no
resulta aplicable en su versión absoluta (se verá más adelante).
""")

# ---- II.5 Pipeline NLP ----
s, y = lamina("Del comentario libre al atributo puntuado", eyebrow="Parte II · Módulo de PLN")
rect(s, MX, y, ANCHO, Inches(1.1), PLANO)
rect(s, MX, y, Inches(0.06), Inches(1.1), rgb("C6902F"))
tf = cuerpo(s, MX + Inches(0.3), y + Inches(0.15), ANCHO - Inches(0.6), Inches(0.9))
parrafo(tf, "«El vino espectacular y el guía sabía muchísimo, pero tardaron cuarenta minutos en empezar y nadie nos dijo nada. "
            "Por 25 € esperaba otra cosa.»  — reseña real del corpus, 3 ★", size=14, italic=True, color=INK, space_after=0)
cw3 = (ANCHO - Inches(0.5)) / 3
pasos = [("1 · Extracción de atributos", "Cada fragmento se asigna a uno de **ocho atributos** mediante un léxico multilingüe "
          "construido para el dominio: vino y cata, personal y trato, visita y experiencia, instalaciones, precio y valor, "
          "organización y reserva, gastronomía, entorno y viñedo. Esta reseña habla de **cuatro**."),
         ("2 · Sentimiento por atributo", "Un modelo **BERT multilingüe** puntúa cada frase de 1 a 5, **independientemente de "
          "las estrellas** del autor. Esa independencia evita la circularidad en la regresión posterior. Resultado: vino 5, "
          "personal 5, organización 2, precio 2."),
         ("3 · Idioma y procedencia", "Detección del idioma (mínimo 20 caracteres; si no, «sin determinar») como aproximación "
          "a la procedencia del visitante. Permite segmentar hispanohablante / internacional y comparar valoraciones.")]
for i, (tit, desc) in enumerate(pasos):
    l = MX + i * (cw3 + Inches(0.25))
    tarjeta(s, l, y + Inches(1.35), cw3, Inches(2.55), tit, None, desc, foco=(i == 1))
remate(s, "Resultado: 17.246 menciones anotadas, con atributo, sentimiento e idioma. Base de todo lo que sigue.")
notas(s, """
Para el alumnado: elección de léxico + BERT frente a un modelo generativo por TRAZABILIDAD (se puede señalar qué
palabra disparó qué atributo) y REPRODUCIBILIDAD (mismo dato, misma salida).
El léxico incluyó correcciones de polisemia (p. ej., «cara» como rostro vs. como precio) detectadas en revisión.
""")


# ---- II.5b Validación del análisis de texto ----
s, y = lamina("Control de calidad del análisis de texto", eyebrow="Parte II · Módulo de PLN",
              subtitulo="Cómo se sabe que el léxico y el modelo aciertan: decisiones de diseño, errores encontrados y umbrales de fiabilidad.")
cw2 = (ANCHO - Inches(0.5)) / 2
tarjeta(s, MX, y, cw2, Inches(2.05), "Dos errores de polisemia detectados y corregidos", None,
        "**«tiempo»** (clima, duración, uso genérico) contaminaba «organización y reserva»: 118 reseñas ajenas, incluidas de "
        "logística de camiones. Sustituido por **«tiempo de espera»** y **«cola»**: el desempeño del atributo pasó de 3,66 a 4,00. "
        "**«cara»** (rostro, «de cara al público») en «precio»: 11 falsos positivos de 29. Sustituido por locuciones; impacto medido: "
        "+0,014, **ningún ranking cambió**.", foco=True)
tarjeta(s, MX + cw2 + Inches(0.5), y, cw2, Inches(2.05), "Umbrales de fiabilidad, con su porqué", None,
        "**8 menciones** mínimas para publicar la nota de un atributo: con 6, una bodega daba 5,00 y una sola reseña de 3 estrellas la "
        "dejaría en 4,71. **20 caracteres** mínimos para asignar idioma; por debajo, «sin determinar». **10 observaciones por variable** "
        "en la regresión para no sobreajustar.")
tarjeta(s, MX, y + Inches(2.3), cw2, Inches(1.9), "Robustez del modelo de importancia", None,
        "R² = 0,55 con F significativa y 465 observaciones por variable. El **orden** de importancia de los atributos se mantiene "
        "con dos estimadores distintos —regresión lineal y regresión ordinal— con una correlación de **0,79** entre ambos.")
tarjeta(s, MX + cw2 + Inches(0.5), y + Inches(2.3), cw2, Inches(1.9), "Cobertura lingüística declarada", None,
        "Léxico de atributos en **español, inglés, alemán, francés e italiano**. Modelo de sentimiento entrenado sobre reseñas en esos "
        "cinco idiomas y neerlandés. **Pendiente:** ampliar el léxico a portugués y neerlandés. El sentimiento se calcula del texto, "
        "nunca de las estrellas, para evitar circularidad.")
cita_pie(s, "Cada corrección se aplica al léxico, se recalcula todo el pipeline y se mide su impacto antes de aceptarla. Los umbrales están publicados en la guía de la plataforma.")
notas(s, """
Para el alumnado: la validación no es un paso final, es continua. Cada error encontrado se corrige en el léxico,
se recalcula el pipeline completo y se mide cuánto cambian los resultados. El caso de «cara» es instructivo
precisamente porque casi no cambió nada: medir el impacto de una corrección también es validar.
El caso de «tiempo» muestra lo contrario: un error de léxico puede mover un atributo 0,34 puntos.
""")

# ---- II.6 Importancia por impacto ----
s, y = lamina("Medir la importancia: el análisis PRCA", eyebrow="Parte II · Módulo analítico",
              subtitulo="El desempeño se lee; la importancia hay que estimarla. Tres aproximaciones y la elegida.")
cw3 = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw3, Inches(1.95), "Importancia declarada", None,
        "Se pregunta al cliente. **Limitación:** lo que decimos valorar y lo que determina nuestra satisfacción no coinciden.")
tarjeta(s, MX + cw3 + Inches(0.25), y, cw3, Inches(1.95), "Importancia derivada por frecuencia", None,
        "Se cuentan menciones. **Limitación:** confunde frecuencia con relevancia. De lo que nunca falla se habla mucho.")
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y, cw3, Inches(1.95), "Importancia por impacto (PRCA)", None,
        "Regresión de la satisfacción global sobre cada atributo, que entra **dos veces**: como penalización (cuando va mal) "
        "y como recompensa (cuando va bien). Brandt (1987).", foco=True)
# gráfico nativo: importancia por atributo
cd = CategoryChartData()
attrs = ["Visita y experiencia", "Precio y valor", "Organización y reserva", "Instalaciones", "Personal y trato",
         "Vino y cata", "Gastronomía", "Entorno y viñedo"]
imps = (20.8, 14.9, 14.8, 13.8, 13.5, 9.7, 7.7, 4.8)
cd.categories = list(reversed(attrs))
cd.add_series("Importancia (%)", tuple(reversed(imps)))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, int(MX), int(y + Inches(2.15)), int(Inches(7.2)), int(Inches(2.2)), cd)
ch = gf.chart; estilo_chart(ch)
ch.has_title = True
ch.chart_title.text_frame.text = "Importancia por impacto en la satisfacción · Marco de Jerez (%)"
r_ = ch.chart_title.text_frame.paragraphs[0].runs[0]; r_.font.size = Pt(11); r_.font.bold = True; r_.font.color.rgb = INK
pl = ch.plots[0]; pl.gap_width = 45; pl.has_data_labels = True
pl.data_labels.font.size = Pt(10); pl.data_labels.number_format = '0.0"%"'; pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = CONTEXTO
# foco: precio (índice 6 tras invertir) y organización (índice 5)
for idx in (6, 5):
    pt = ser.points[idx]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = AZUL
ch.value_axis.visible = False; ch.value_axis.has_major_gridlines = False; ch.value_axis.maximum_scale = 25
ch.category_axis.tick_labels.font.size = Pt(10)
rect(s, MX + Inches(7.5), y + Inches(2.15), ANCHO - Inches(7.5), Inches(2.2), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + Inches(7.7), y + Inches(2.28), ANCHO - Inches(7.9), Inches(2.0))
parrafo(tf, "LECTURA", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "«Vino y cata» es el segundo atributo **más mencionado** (4.232 menciones) y solo el sexto en importancia: "
            "**no discrimina** porque casi siempre está bien.", size=11.5, space_after=6)
parrafo(tf, "«Organización y reserva» aparece en **331 menciones** (2 %) y pesa el **14,8 %**: poca gente, mucho efecto.", size=11.5, space_after=6)
parrafo(tf, "Con la importancia por frecuencia, precio y organización salían como «baja prioridad». **El consejo estaba invertido.**", size=11.5, space_after=0)
cita_pie(s, "Modelo del Marco: R² = 0,55; F significativa; 465 observaciones por variable; mínimo de 8 menciones por atributo. Penalización y recompensa son asimétricas.")
notas(s, """
Analogía útil: el agua caliente en un hotel. Nadie la menciona cuando funciona; hunde la valoración cuando falta.
Contar menciones la haría parecer irrelevante.
Para el alumnado: la asimetría penalización/recompensa es lo que conecta el PRCA con el modelo de Kano.
""")

# ---- II.7 IPA del Marco (diagrama con formas) ----
s, y = lamina("El IPA del Marco de Jerez", eyebrow="Parte II · Módulo analítico",
              subtitulo="Importancia por impacto (eje X) frente a sentimiento por atributo (eje Y). Umbrales: las medias (12,5 % y 4,05).")
px_, py_, pw_, ph_ = MX + Inches(0.6), y, Inches(7.4), Inches(3.9)
rect(s, px_, py_, pw_, ph_, BLANCO, line=REGLA)
def X(v): return int(px_ + (v - 3) / 19 * pw_)
def Y(v): return int(py_ + ph_ - (v - 3.4) / 1.05 * ph_)
# líneas de umbral
ln = s.shapes.add_connector(1, int(X(12.5)), int(py_), int(X(12.5)), int(py_ + ph_)); ln.line.color.rgb = REGLA; ln.line.width = Pt(1.25); ln.line.dash_style = 4
ln = s.shapes.add_connector(1, int(px_), int(Y(4.05)), int(px_ + pw_), int(Y(4.05))); ln.line.color.rgb = REGLA; ln.line.width = Pt(1.25); ln.line.dash_style = 4
for (tx, ty, txt, col, al) in [(px_ + Inches(0.12), py_ + Inches(0.08), "POSIBLE EXCESO", TENUE, PP_ALIGN.LEFT),
                               (px_ + pw_ - Inches(3.1), py_ + Inches(0.08), "SIGA CON EL BUEN TRABAJO", TENUE, PP_ALIGN.RIGHT),
                               (px_ + Inches(0.12), py_ + ph_ - Inches(0.32), "BAJA PRIORIDAD", TENUE, PP_ALIGN.LEFT),
                               (px_ + pw_ - Inches(3.1), py_ + ph_ - Inches(0.32), "CONCÉNTRESE AQUÍ", ACENTO, PP_ALIGN.RIGHT)]:
    caja(s, tx, ty, Inches(3.0), Inches(0.25), txt, size=9, bold=True, color=col, align=al)
puntos = [("Visita y experiencia", 20.8, 4.24, False, "izq"), ("Instalaciones", 13.8, 4.24, False, "der"),
          ("Personal y trato", 13.5, 4.33, False, "izq"), ("Vino y cata", 9.7, 4.13, False, "der"),
          ("Entorno y viñedo", 4.8, 4.29, False, "der"), ("Gastronomía", 7.7, 3.88, False, "der"),
          ("Precio y valor", 14.9, 3.78, True, "der"), ("Organización y reserva", 14.8, 3.52, True, "der")]
r_pt = Inches(0.13)
for nom, ix, dy, foco, lado in puntos:
    cx, cy = X(ix), Y(dy)
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, int(cx - r_pt), int(cy - r_pt), int(2 * r_pt), int(2 * r_pt))
    o.fill.solid(); o.fill.fore_color.rgb = NARANJA if foco else CONTEXTO
    o.line.color.rgb = BLANCO; o.line.width = Pt(1.5); o.shadow.inherit = False
    if lado == "der":
        caja(s, cx + r_pt + Inches(0.06), cy - Inches(0.12), Inches(2.2), Inches(0.25), nom, size=10.5,
             bold=foco, color=INK if foco else INK2)
    else:
        caja(s, cx - r_pt - Inches(2.26), cy - Inches(0.12), Inches(2.2), Inches(0.25), nom, size=10.5,
             bold=foco, color=INK if foco else INK2, align=PP_ALIGN.RIGHT)
caja(s, px_, py_ + ph_ + Inches(0.05), pw_, Inches(0.25), "Importancia (impacto en la satisfacción) →", size=9.5, color=TENUE, align=PP_ALIGN.CENTER)
xr = px_ + pw_ + Inches(0.4); wr = W - MX - xr
tf = cuerpo(s, xr, y, wr, Inches(4.2))
parrafo(tf, "LECTURA", size=10, bold=True, color=ACENTO, space_after=8)
parrafo(tf, "**Concéntrese aquí:** precio y valor (3,78) y organización y reserva (3,52). Los dos peor valorados son "
            "también de los que más pesan.", size=12.5, space_after=8)
parrafo(tf, "**Siga con el buen trabajo:** visita, instalaciones y personal.", size=12.5, space_after=8)
parrafo(tf, "**Posible exceso:** vino y cata, y entorno. Alta valoración, bajo impacto diferencial.", size=12.5, space_after=8)
parrafo(tf, "Coherente con Meneses et al. (2023): la insatisfacción nace de ineficiencias operativas, no del producto.", size=11.5, color=TENUE, space_after=0)
notas(s, """
Diez segundos de silencio para que lo lean. Después: primero los dos puntos naranjas; luego «vino y cata» en
posible exceso. No dice que el vino no importe: dice que es tan consistentemente bueno que ya no diferencia.
Los umbrales son las medias, criterio habitual en la literatura del IPA; en la guía de la plataforma se declaran.
""")

# ---- II.8 IPCA y DIPA ----
s, y = lamina("Extensiones competitiva y dinámica: IPCA y DIPA", eyebrow="Parte II · Módulo analítico")
cw2 = (ANCHO - Inches(0.5)) / 2
tarjeta(s, MX, y, cw2, Inches(1.85), "IPCA · implementado, por bodega", None,
        "Compara el sentimiento de cada bodega con la **media del resto del Marco**. La brecha se declara «en línea» si cae "
        "dentro de una **banda de indiferencia** (0,07), calculada como el percentil 25 de la distribución real de brechas: "
        "sin ella, diferencias de ±0,004 salían etiquetadas como «actuar» o «fortaleza».", foco=True)
tarjeta(s, MX + cw2 + Inches(0.5), y, cw2, Inches(1.85), "DIPA · implementado, destino y bodega", None,
        "Sentimiento por atributo y periodo. Compara el primer trienio con datos frente al último. Solo se afirma un cambio "
        "si supera la banda de indiferencia. **DIPCA:** pendiente de implementar.", foco=True)
# gráfico nativo DIPA: 2018-20 vs 2024-26
cd = CategoryChartData()
cats = ["Precio y valor", "Gastronomía", "Organización", "Visita", "Entorno", "Personal", "Vino y cata", "Instalaciones"]
cd.categories = cats
cd.add_series("2018-2020", (3.87, 3.82, 3.47, 4.22, 4.37, 4.30, 4.17, 4.28))
cd.add_series("2024-2026", (3.70, 3.95, 3.54, 4.28, 4.30, 4.35, 4.15, 4.26))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, int(MX), int(y + Inches(2.05)), int(Inches(8.0)), int(Inches(2.6)), cd)
ch = gf.chart; estilo_chart(ch, leyenda=True)
ch.has_title = True
ch.chart_title.text_frame.text = "DIPA del Marco · sentimiento medio por atributo y trienio"
r_ = ch.chart_title.text_frame.paragraphs[0].runs[0]; r_.font.size = Pt(11); r_.font.bold = True; r_.font.color.rgb = INK
pl = ch.plots[0]; pl.gap_width = 70; pl.overlap = -10
pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = CONTEXTO
pl.series[1].format.fill.solid(); pl.series[1].format.fill.fore_color.rgb = AZUL
pl.series[1].points[0].format.fill.solid(); pl.series[1].points[0].format.fill.fore_color.rgb = NARANJA
ch.value_axis.minimum_scale = 3.0; ch.value_axis.maximum_scale = 4.6
ch.value_axis.tick_labels.number_format = "0.0"; ch.value_axis.tick_labels.number_format_is_linked = False
ch.category_axis.tick_labels.font.size = Pt(9.5)
rect(s, MX + Inches(8.3), y + Inches(2.05), ANCHO - Inches(8.3), Inches(2.6), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + Inches(8.5), y + Inches(2.2), ANCHO - Inches(8.7), Inches(2.4))
parrafo(tf, "RESULTADO", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "Siete atributos se mueven **dentro del ruido**. Solo **precio y valor** supera la banda: **3,87 → 3,70 (−0,18)**.", size=12, space_after=6)
parrafo(tf, "Organización y reserva no empeora (3,47 → 3,54), pero sigue siendo el **peor valorado**.", size=12, space_after=6)
parrafo(tf, "Contexto económico: 40,4 € de ingreso por visitante, por encima de la media de las rutas (37,0 €) y lejos del líder (70,0 €).", size=11, color=TENUE, space_after=0)
notas(s, """
Lección metodológica: no afirmar cambios por debajo del ruido. Sería fácil decir «la gastronomía mejora»; no es
defendible.
Nota interna: en las notas del proyecto figuró durante meses que el atributo que empeoraba era «organización»;
al recalcular para esta sesión se comprobó que era «precio». Es un buen ejemplo de por qué se rehacen las cifras
antes de presentarlas.
""")


# ---- II.8b Teoría de los tres factores ----
s, y = lamina("La teoría de los tres factores de la satisfacción", eyebrow="Parte II · Marco analítico",
              subtitulo="El puente conceptual entre el PRCA y el modelo de Kano: la satisfacción no responde de forma lineal ni simétrica.")
cw3 = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw3, Inches(1.75), "Factores básicos", None,
        "Requisitos mínimos. Su ausencia genera **insatisfacción**; su presencia no genera satisfacción. Asimetría negativa.")
tarjeta(s, MX + cw3 + Inches(0.25), y, cw3, Inches(1.75), "Factores de desempeño", None,
        "Relación **lineal y simétrica**: cuanto mejor, más satisfacción; cuanto peor, más insatisfacción.")
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y, cw3, Inches(1.75), "Factores de entusiasmo", None,
        "Su presencia genera **satisfacción**; su ausencia no genera insatisfacción. Asimetría positiva.")
cw2 = (ANCHO - Inches(0.5)) / 2
tf = cuerpo(s, MX, y + Inches(2.0), cw2, Inches(2.4))
parrafo(tf, "DE DÓNDE VIENE", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "Kano et al. (1984) formulan la clasificación; Matzler y Sauerwein (2002) la sistematizan como **teoría de los tres factores** "
            "y muestran que puede estimarse a partir de datos de satisfacción reales, sin cuestionario específico.", size=12.5, space_after=6)
parrafo(tf, "El **PRCA** de Brandt (1987) es la operacionalización habitual: cada atributo entra en la regresión con dos variables, una para el "
            "caso «va mal» (penalización) y otra para «va bien» (recompensa). La **diferencia entre los dos coeficientes** revela la asimetría.",
        size=12.5, space_after=0)
rect(s, MX + cw2 + Inches(0.5), y + Inches(2.0), cw2, Inches(2.4), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + cw2 + Inches(0.75), y + Inches(2.15), cw2 - Inches(0.5), Inches(2.2))
parrafo(tf, "POR QUÉ IMPORTA PARA EL IPA", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "El IPA clásico supone que importancia y desempeño se relacionan de forma lineal. Si un atributo es básico, mejorarlo por encima "
            "del mínimo **no sube la satisfacción**: invertir ahí es «posible exceso». Si es de entusiasmo, un pequeño avance puede tener "
            "un efecto desproporcionado.", size=12.5, space_after=6)
parrafo(tf, "En ENOLYTICS, el PRCA aporta la **importancia** (magnitud de los coeficientes) y el índice λ aporta la **asimetría** (perfil de "
            "Kano). Son dos lecturas de la misma regresión.", size=12.5, space_after=0)
cita_pie(s, "Kano, Seraku, Takahashi y Tsuji (1984) · Brandt (1987) · Matzler y Sauerwein (2002) · Mikulić y Prebežac (2008), análisis de asimetría del impacto.")
notas(s, """
Ejemplo con un hotel: el agua caliente es básico (su falta enfada; su presencia no se agradece); el tamaño de
la habitación es de desempeño; una nota de bienvenida manuscrita es de entusiasmo.
Mensaje para el alumnado: el IPA y Kano no son métodos rivales, son dos lecturas de la misma estructura de
datos, y el PRCA es lo que permite obtener las dos de una sola regresión. Esto prepara la diapositiva
siguiente, donde se ve que en el Marco la lectura de Kano no discrimina por el efecto techo.
""")

# ---- II.9 Kano ----
s, y = lamina("El modelo de Kano y el efecto techo", eyebrow="Parte II · Módulo analítico")
cw3 = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw3, Inches(1.55), "Básico / higiénico", None, "Si falla, penaliza mucho; si funciona, apenas recompensa. Se da por supuesto.")
tarjeta(s, MX + cw3 + Inches(0.25), y, cw3, Inches(1.55), "De desempeño", None, "Satisfacción proporcional: cuanto más, mejor.")
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y, cw3, Inches(1.55), "De entusiasmo / deleitador", None, "Si falta, no se echa de menos; si aparece, recompensa mucho.")
cw2 = (ANCHO - Inches(0.5)) / 2
vinetas(s, MX, y + Inches(1.8), cw2, Inches(2.9), [
    "**Cómo se mide:** con los coeficientes del PRCA se calcula un índice λ que compara la magnitud de la recompensa con la "
    "de la penalización. Umbral **±0,20** (Pratt et al., 2020; aplicado en Han et al., 2026, IJCHM).",
    "**Resultado en el Marco:** los **ocho atributos** se clasifican como «básico». Ninguno como deleitador.",
    "**Diagnóstico:** no es un hallazgo, es aritmética. Con el 75,9 % de reseñas en el máximo, casi no existe «recompensa» "
    "observable; todo lo que queda es penalización. Es el efecto techo actuando sobre el método.",
], size=12.5, space=7)
rect(s, MX + cw2 + Inches(0.5), y + Inches(1.8), cw2, Inches(2.9), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + cw2 + Inches(0.75), y + Inches(1.95), cw2 - Inches(0.5), Inches(2.7))
parrafo(tf, "DECISIÓN METODOLÓGICA", size=10, bold=True, color=ACENTO, space_after=8)
parrafo(tf, "Publicar «ocho básicos» habría sido técnicamente correcto e inútil. Se renuncia a la **clasificación absoluta** y se "
            "conserva el **orden relativo**: qué atributos se comportan de forma más higiénica y cuáles más deleitadora dentro "
            "de este corpus. El cuadro de mando lo muestra como un perfil, no como una etiqueta.", size=12, space_after=8)
parrafo(tf, "Para resolverlo haría falta una fuente con más variación: plataformas más críticas o una encuesta con escala forzada. "
            "Está en las líneas futuras.", size=11.5, color=INK2, space_after=0)
notas(s, """
Para el alumnado es probablemente la diapositiva más formativa: qué hacer cuando el modelo previsto no es
aplicable a los datos. La respuesta no es forzarlo ni ocultarlo, sino documentar por qué y adaptar.
Ejemplos de Kano en hotelería: agua caliente (básico), tamaño de habitación (desempeño), nota manuscrita de
bienvenida (deleitador).
""")

# ---- II.10 Competidores ----
s, y = lamina("Identificación de competidores directos", eyebrow="Parte II · Módulo analítico",
              subtitulo="Una bodega no compite con las otras 41: compite con tres o cuatro. Método de Zhou et al. (2026), IJHM.")
cw3 = (ANCHO - Inches(0.5)) / 3
pasos = [("1 · Rasgos por bodega", "**Eje de mercado:** perfil de sentimiento por atributo, nota, ubicación (distancia haversine), "
          "% de visitante internacional. **Eje de recursos:** servicios ofrecidos, certificación FEV, madurez digital, tamaño."),
         ("2 · Agrupación", "**K-prototypes** (variables numéricas y categóricas a la vez); número de grupos elegido por silueta "
          "(k = 3). Mismo grupo = competidores potenciales."),
         ("3 · Categorización de Kamensky", "**Distancia de Gower** en los dos ejes; umbrales por mediana. Cuatro tipos: núcleo "
          "(mismo cliente y recursos), sustituto, marginal y potencial.")]
for i, (tit, desc) in enumerate(pasos):
    tarjeta(s, MX + i * (cw3 + Inches(0.25)), y, cw3, Inches(2.2), tit, None, desc, foco=(i == 2))
vinetas(s, MX, y + Inches(2.45), ANCHO, Inches(1.6), [
    "**37 de 42 bodegas** obtienen análisis. A las 5 restantes, sin perfil suficiente, la plataforma responde que no hay muestra: "
    "se prefiere «no lo sé» a un competidor al azar.",
    "Validación de cara: Barbadillo → Osborne, Lustau, González Byass; Tradición → bodegas de perfil premium. Coherente con el "
    "conocimiento del sector.",
    "El precio de las experiencias **aún no entra** en el eje de recursos: se está recopilando y verificando con las bodegas.",
], size=13, space=6)
notas(s, """
Explicación llana de los dos ejes: dos bodegas compiten de verdad cuando se dirigen al mismo visitante Y tienen
medios parecidos para atenderlo. Si solo coincide una de las dos cosas, la competencia es más floja.
El resultado alimenta el informe PDF por bodega y la pestaña Competidores de la ficha.
""")

# ---- II.11 Co-ocurrencias y recomendaciones ----
s, y = lamina("Co-ocurrencias y motor de recomendaciones", eyebrow="Parte II · Módulos analíticos")
cw2 = (ANCHO - Inches(0.5)) / 2
tarjeta(s, MX, y, cw2, Inches(2.35), "Co-ocurrencias de atributos (método co-word)", None,
        "Tomado de la bibliometría: qué atributos se mencionan **juntos** en una misma reseña. Recuento bruto y "
        "**equivalencia de Callon** (normalizada, que corrige que los atributos frecuentes se asocien con todo). "
        "Grafo de red con capas positiva y negativa. Revela la **estructura de la experiencia**: p. ej., instalaciones "
        "y visita van siempre unidas; organización y precio aparecen juntas en las críticas.")
tarjeta(s, MX + cw2 + Inches(0.5), y, cw2, Inches(2.35), "Motor de recomendaciones accionables", None,
        "El diferencial comprometido en la memoria. Reglas que se disparan **solo si el dato las sostiene**; cada una declara "
        "diagnóstico, acción y fuente. **14 recomendaciones** para el destino (Clientes 5, Mercado 3, Tecnológica 3, Negocios, "
        "Económica y Sostenibilidad 1), y recomendaciones específicas por bodega. Prioridad alta / media / baja.", foco=True)
rect(s, MX, y + Inches(2.6), ANCHO, Inches(1.85), PLANO)
tf = cuerpo(s, MX + Inches(0.3), y + Inches(2.75), ANCHO - Inches(0.6), Inches(1.65))
parrafo(tf, "UMBRALES DECLARADOS EN LA GUÍA DE LA PLATAFORMA, EN DOS BLOQUES", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "**Con base metodológica:** 8 menciones mínimas por atributo · banda de indiferencia 0,10 ★ (IPCA en estrellas) y 0,07 "
            "(en sentimiento, percentil 25 de 94 pares) · λ de Kano ±0,20 · 10 observaciones por variable en la regresión · 20 caracteres para detectar idioma.", size=12, space_after=5)
parrafo(tf, "**Criterio del equipo:** responder al 0 % con ≥ 5 críticas, o < 15 % con ≥ 10 · 3 bodegas mudas con ≥ 50 críticas · 10 € de brecha de "
            "ingreso por visitante · 20 % de webs sin zoom · 80 % de reserva online · 75 % accesibles y 60 % en coche.", size=12, space_after=0)
cita_pie(s, "Un motor con umbrales declarados es defendible y auditable; uno cuyos umbrales no se conocen, no.")
notas(s, """
Distinguir los dos bloques de umbrales es una exigencia de rigor: unos tienen justificación estadística o
bibliográfica; otros son decisiones legítimas del equipo y se presentan como tales.
""")

# ---- II.12 Indicadores de destino y hallazgos ----
s, y = lamina("Indicadores de destino y principales hallazgos", eyebrow="Parte II · Resultados")
cw3 = (ANCHO - Inches(0.5)) / 3
tarjeta(s, MX, y, cw3, Inches(1.5), "Económica · ACEVIN 2024", "17,2 M€", "Ingresos del enoturismo. **40,4 €** por visitante; media de las rutas 37,0 €; líder Rioja Alta 70,0 €.", size_val=24)
tarjeta(s, MX + cw3 + Inches(0.25), y, cw3, Inches(1.5), "Mercado · Google Trends", "2.º de 4", "Interés de búsqueda: Jerez 37 frente a Rioja 56 (índice medio). Tendencia a la baja.", size_val=24)
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y, cw3, Inches(1.5), "Clientes · reseñas", "590", "Críticas de 1-2 ★ sin respuesta del propietario. 11 de 33 bodegas no responden nunca.", size_val=24)
tarjeta(s, MX, y + Inches(1.7), cw3, Inches(1.5), "Tecnológica · auditoría web", "0 de 38", "Bodegas que mencionan apoyo sensorial (audioguías, braille). 12 de 38 bloquean el zoom. Índice digital 6,4/8.", size_val=24)
tarjeta(s, MX + cw3 + Inches(0.25), y + Inches(1.7), cw3, Inches(1.5), "Sostenibilidad · OSM + ACEVIN", "88 %", "Bodegas accesibles en transporte público (36 de 41); el 76 % de los enoturistas llega en coche.", size_val=24)
tarjeta(s, MX + 2 * (cw3 + Inches(0.25)), y + Inches(1.7), cw3, Inches(1.5), "Mercado · Dataestur (predictivo)", "3.253.175", "Búsquedas de vuelo a Jerez desde países **sin un solo asiento directo** (Italia, EE. UU., Francia, P. Bajos).", foco=True, size_val=22)
remate(s, "Ninguno de estos indicadores está en las reseñas: salen de cruzar fuentes públicas que nadie había puesto juntas.", y=y + Inches(3.45))
notas(s, """
La conectividad aérea no estaba en la memoria; apareció trabajando. Se presenta como valor añadido: la memoria
comprometía «capacidad predictiva» sin nombrar fuente, y las búsquedas de vuelo miran al futuro.
Estados Unidos: mejor conversión (5,87 %) y estancia más larga (12,8 días), sin vuelo directo.
""")

# ---- II.13 Cruceros (gráfico nativo de líneas) ----
s, y = lamina("Un hallazgo de destino: los cruceros de Cádiz", eyebrow="Parte II · Resultados",
              subtitulo="696.151 cruceristas en 2024 frente a 425.652 visitantes a todas las bodegas del Marco. Y su calendario es complementario.")
cd = CategoryChartData()
cd.categories = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
cd.add_series("Cruceristas (índice, 100 = máximo)", (23, 9, 29, 66, 63, 41, 70, 68, 84, 100, 85, 39))
cd.add_series("Afluencia enoturística (índice; estimación por volumen de reseñas)", (38, 44, 57, 60, 62, 60, 68, 100, 77, 75, 54, 51))
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, int(MX), int(y), int(Inches(8.2)), int(Inches(3.9)), cd)
ch = gf.chart; estilo_chart(ch, leyenda=True)
pl = ch.plots[0]
for i, col in enumerate((NARANJA, AZUL)):
    sr = pl.series[i]
    sr.format.line.color.rgb = col; sr.format.line.width = Pt(2.5); sr.smooth = False
    sr.marker.size = 7; sr.marker.format.fill.solid(); sr.marker.format.fill.fore_color.rgb = col
    sr.marker.format.line.color.rgb = BLANCO
ch.value_axis.minimum_scale = 0; ch.value_axis.maximum_scale = 100
xr = MX + Inches(8.5); wr = ANCHO - Inches(8.5)
tarjeta(s, xr, y, wr, Inches(1.75), "Noviembre", "85 vs 54", "Cruceros al 85 % de su máximo; enoturismo al 54 %.", foco=True, size_val=26)
tf = cuerpo(s, xr, y + Inches(1.95), wr, Inches(2.0))
parrafo(tf, "Cádiz es el **6.º puerto de España** en cruceros. ACEVIN estima que ~30 % de los enoturistas **no pernocta**: el perfil "
            "de quien baja de un barco por unas horas.", size=12, space_after=6)
parrafo(tf, "**Implicación:** producto de medio día empaquetado con navieras y receptivos. Responde a la prioridad FEDER **P4A** (desestacionalizar).", size=12, space_after=0)
cita_pie(s, "Cruceros: Dataestur / Puertos del Estado (oficial). Afluencia enoturística: estimación propia por volumen mensual de reseñas; útil para la forma, no para cifras.")
notas(s, """
Declarar explícitamente que la curva de enoturismo es un proxy (ámbar en la plataforma). No existe afluencia
mensual publicada por bodega.
Comparación anual con el mismo año (2024) porque ACEVIN llega hasta 2024 y los cruceros hasta 2025.
""")

# ---- II.14 Funcionalidades ----
s, y = lamina("Funcionalidades del cuadro de mando", eyebrow="Parte II · Funcionalidades")
cw3 = (ANCHO - Inches(0.5)) / 3
func = [("Informe PDF por bodega", "Una página, generada en el servidor: reputación, competidores directos, fortalezas y "
         "debilidades, presencia digital y sostenibilidad, qué hacer. Pensado para entregar a la bodega."),
        ("Simulador de escenarios", "Cuatro variables —monetización, captación de cruceristas, respuesta a críticas, calidad "
         "percibida— sobre cifras reales, con la fórmula y el supuesto a la vista. **Proyecta un escenario; no predice.**"),
        ("Guía y metodología", "Qué es cada apartado, de dónde sale cada dato, qué significa cada análisis y qué umbral "
         "aplica. Descargable en PDF como **anexo metodológico** del proyecto."),
        ("Ficha de reputación", "Al estilo de las grandes plataformas, más un indicador que ninguna muestra: la **tasa de "
         "respuesta** del propietario a las reseñas y a las críticas."),
        ("Mapa de competidores", "Terreno competitivo de Kamensky por bodega: distancia de mercado frente a distancia de "
         "recursos, con los cuatro tipos de rival."),
        ("Código de origen del dato", "Oficial / observado / estimación en todas las pantallas. Textos compuestos de datos "
         "agregados, **sin IA generativa**, para que el mismo dato dé siempre el mismo texto.")]
for i, (tit, desc) in enumerate(func):
    l = MX + (i % 3) * (cw3 + Inches(0.25)); t = y + (i // 3) * Inches(2.05)
    tarjeta(s, l, t, cw3, Inches(1.85), tit, None, desc, foco=(i in (0, 1)))
cita_pie(s, "Verificación: pruebas automatizadas de las cinco vistas y barridos con navegador real tras cada cambio; revisión de uso por la IP.")
notas(s, """
Momento de la DEMO en vivo. Recorrido sugerido (8 minutos): Resumen ejecutivo → Las 7 inteligencias / Clientes
(mapa IPA en vivo) → Bodega individual (competidores + descarga del PDF) → Simulador.
Plan B si falla la conexión: capturas de pantalla y un PDF ya descargado. Comprobar media hora antes que la
aplicación está despierta (Streamlit Cloud suspende las que llevan tiempo sin visitas).
""")


# ---- II.14b Validación con usuarios ----
s, y = lamina("Validación con usuarios: la revisión de la investigadora principal", eyebrow="Parte II · Mejora continua",
              subtitulo="La IP usó el cuadro de mando como usuaria y devolvió un documento con diez observaciones numeradas.")
filas = [
    ["#", "Observación", "Tipo", "Qué se hizo"],
    ["4", "La vista de bodega fallaba si el filtro de localidad quedaba vacío", "Error", "Vacío = todas; el filtro pasa a vivir dentro de la vista que filtra"],
    ["5", "Una bodega con dos municipios se contaba como localidad nueva", "Error", "El campo admite varios valores; 7 localidades reales en vez de 8"],
    ["6", "Una tarjeta colgaba la comparación de la cifra equivocada y se leía al revés", "Lectura", "La comparación cuelga de la tarjeta que se juzga; se encontró otra igual"],
    ["8", "Tres gráficos mostraban «undefined» en la leyenda", "Lectura", "La causa real era un título vacío; un arreglo resolvió 29 casos"],
    ["10", "Los umbrales del motor de recomendaciones no estaban documentados", "Lectura", "Nueva sección en la guía, separando base metodológica y criterio del equipo"],
]
tabla(s, MX, y, ANCHO, filas, [Inches(0.45), Inches(5.2), Inches(0.9), Inches(5.28)], size=11, alto_fila=Inches(0.42))
cw2 = (ANCHO - Inches(0.5)) / 2
vinetas(s, MX, y + Inches(2.75), cw2, Inches(1.6), [
    "**Diez observaciones**: dos errores y ocho de lectura en pantalla. Las diez aplicadas y verificadas con pruebas automáticas y "
    "navegador real; el repaso que pedía la IP encontró **dos problemas más** del mismo tipo.",
    "El diagnóstico más útil no fue de código sino de recorrido: «el filtro vive fuera de la vista pero decide lo que la vista puede enseñar».",
], size=12.5, space=6)
rect(s, MX + cw2 + Inches(0.5), y + Inches(2.75), cw2, Inches(1.55), rgb("FDF6F1"), line=ACENTO)
tf = cuerpo(s, MX + cw2 + Inches(0.75), y + Inches(2.9), cw2 - Inches(0.5), Inches(1.3))
parrafo(tf, "LECCIÓN", size=10, bold=True, color=ACENTO, space_after=6)
parrafo(tf, "La usabilidad no se deduce del código: se comprueba con **usuarios reales** que llegan por el camino natural. Es el ciclo "
            "Planificar–Hacer–**Verificar**–Actuar que la UNE 178510 pone en el centro de la empresa turística inteligente, aplicado a la "
            "propia herramienta.", size=12, space_after=0)
notas(s, """
Contar esto es una decisión de credibilidad: una herramienta que nunca ha fallado es una herramienta que nadie
ha usado. La numeración de las observaciones se mantuvo para poder decir «la 4» y entenderse en el equipo.
La observación 8 es un buen ejemplo de diagnóstico: se reportó como un problema de leyenda y la causa estaba en
otro sitio (el título del gráfico sin texto); verificar en un navegador real evitó arreglar el síntoma.
""")

# ---- II.15 Aportaciones al sector ----
s, y = lamina("Principales aportaciones al sector", eyebrow="Parte II · Aportaciones")
vinetas(s, MX, y, ANCHO, Inches(4.6), [
    "**Importancia medida por impacto, no por frecuencia.** Corrige un consejo que salía invertido con el método habitual: "
    "precio y organización pasan de «baja prioridad» a «concéntrese aquí».",
    "**Un sistema de siete inteligencias operativo**, con la de sostenibilidad como fuente propia, alimentado por fuentes "
    "públicas y con trazabilidad del origen de cada dato.",
    "**Indicadores que el sector no tenía:** tasa de respuesta a reseñas, accesibilidad digital y sensorial de las webs, "
    "accesibilidad en transporte público, demanda aérea no atendida, complementariedad con los cruceros.",
    "**Competidores directos por bodega** con un método publicado en 2026, y el reconocimiento explícito de cuándo no hay "
    "muestra para afirmarlo.",
    "**Recomendaciones accionables con umbrales declarados**, auditables y trazables hasta el dato que las justifica.",
    "**Reproducibilidad como principio de diseño:** código abierto en Python, sin licencias, sin textos generados por IA, "
    "depositable en RODIN y replicable en otras denominaciones de origen.",
], size=14.5, space=9)
notas(s, "Cada aportación se corresponde con un compromiso de la memoria o con un valor añadido documentado.")


# ---- II.15b ENOLYTICS y la UNE 178510 ----
s, y = lamina("ENOLYTICS y la Empresa Turística Inteligente", eyebrow="Parte II · Encaje normativo",
              subtitulo="Qué pide la UNE 178510:2023 en cada eje y qué aporta ya la plataforma. Referencias a apartados y al anexo A de indicadores.")
filas = [
    ["Eje", "Qué pide la norma", "Qué aporta ENOLYTICS"],
    ["Gestión", "Grado de satisfacción de clientes; número de quejas; tiempo de respuesta a quejas y reclamaciones (A.2)", "Sentimiento por atributo e IPA; críticas de 1-2 ★ y tasa de respuesta del propietario por bodega"],
    ["Innovación", "Colaboraciones con universidades y centros; proyectos de I+D+i; documentar innovaciones (5.2, A.3)", "Proyecto UCA-bodegas-Ruta; competidores directos y recomendaciones documentadas con su umbral"],
    ["Tecnología", "Sistemática de recopilación, análisis y explotación de datos para decidir (5.3 b); analítica avanzada (5.3 g); espacios de datos ETI-DTI (5.3 h)", "El propio cuadro de mando; dos perfiles —bodega y destino— sobre los mismos datos"],
    ["Accesibilidad", "Web accesible para personas con discapacidad o mayores (5.4 d); informar de accesibilidad; formatos alternativos (A.5); transporte accesible (5.4 f)", "Índice de accesibilidad digital; apoyo sensorial (0 de 38) y zoom bloqueado (12 de 38); accesibilidad en transporte público (88 %)"],
    ["Sostenibilidad", "Certificaciones de sostenibilidad; comunicación externa; transporte sostenible (5.5, A.6)", "Certificación FEV; auditoría de sostenibilidad comunicada en la web; distancia a estación y parada"],
]
tabla(s, MX, y, ANCHO, filas, [Inches(1.5), Inches(5.3), Inches(5.03)], size=10.5, alto_fila=Inches(0.55))
remate(s, "Anexo A.1: la ETI «debería reportar información al destino a través de una plataforma». ENOLYTICS es esa plataforma entre empresa y destino.",
       y=y + Inches(3.55))
cita_pie(s, "UNE 178510:2023, apartados 5.2 a 5.5 y anexo A (informativo). La correspondencia es una lectura del equipo, no una certificación.")
notas(s, """
Aclarar que el anexo A es informativo: la norma invita a cada empresa a fijar sus propios indicadores. La tabla
muestra que muchos de los que propone ya se calculan en la plataforma para las 42 bodegas del Marco sin que
ninguna haya tenido que aportar datos.
El apartado 5.3 h) y el anexo A.1 hablan de intercambio bidireccional de datos entre empresa y destino: es
exactamente la arquitectura de dos perfiles de ENOLYTICS.
Decir explícitamente que esto no es una certificación: es una lectura de correspondencia.
""")

# ---- II.16 Cobertura de la memoria ----
s, y = lamina("Lo prometido y lo construido", eyebrow="Parte II · Balance",
              subtitulo="Contraste entre los compromisos de la memoria y el estado del prototipo (auditoría interna de coherencia).")
filas = [
    ["Compromiso de la memoria", "Estado", "Observación"],
    ["Minería de textos y análisis de sentimiento", "Cumplido", "Léxico multilingüe + BERT multilingüe; 17.246 menciones anotadas"],
    ["IPA · IPCA · DIPA", "Cumplido", "Con importancia por impacto (PRCA) y bandas de indiferencia calibradas"],
    ["DIPCA", "Pendiente", "Requiere series competitivas por periodo con muestra suficiente"],
    ["Modelado de temas (LDA / BERT)", "Parcial", "Atributos por léxico; LDA explorado para gastronomía; pendiente como descubrimiento"],
    ["Recomendaciones accionables", "Cumplido", "Motor con 14 reglas de destino y reglas por bodega, umbrales declarados"],
    ["Simulaciones y proyecciones de escenarios", "Cumplido", "Simulador con cuatro palancas"],
    ["Capacidad predictiva", "Cumplido (valor añadido)", "Conectividad aérea de Dataestur: búsquedas y reservas por fecha futura"],
    ["Cuestionarios a bodegas y visitantes", "Pendiente", "Para indicadores sin fuente abierta (empleo, consumos, precios)"],
    ["TripAdvisor y redes sociales", "Pendiente", "Corpus actual solo de Google"],
    ["Power BI sobre Azure", "Sustituido", "Python + Streamlit, por reproducibilidad y coste; desviación documentada"],
]
tabla(s, MX, y, ANCHO, filas, [Inches(3.9), Inches(2.1), Inches(5.83)], size=11, alto_fila=Inches(0.36))
notas(s, "Diapositiva de honestidad: un proyecto a mitad de plazo que declara el 100 % cumplido no es creíble. Lo pendiente está identificado y priorizado.")

# ---- II.17 Limitaciones y líneas futuras ----
s, y = lamina("Limitaciones y líneas futuras", eyebrow="Parte II · Cierre")
cw2 = (ANCHO - Inches(0.5)) / 2
caja(s, MX, y, cw2, Inches(0.35), "LIMITACIONES", size=11, bold=True, color=ACENTO)
vinetas(s, MX, y + Inches(0.4), cw2, Inches(4.0), [
    "**Sesgo de autoselección:** quien escribe reseñas no representa a quien visita.",
    "**Efecto techo:** 75,9 % de puntuaciones máximas; limita Kano y cualquier método que necesite variación.",
    "**Proxies declarados:** afluencia mensual por volumen de reseñas; idioma como procedencia.",
    "**Fuente única de reseñas:** Google. TripAdvisor podría alterar resultados en el segmento internacional.",
    "**Indicadores de la Tabla 1 aún a cero** por falta de fuente abierta: empleo, consumos, precios verificados.",
], size=13, space=7)
caja(s, MX + cw2 + Inches(0.5), y, cw2, Inches(0.35), "LÍNEAS FUTURAS", size=11, bold=True, color=ACENTO)
vinetas(s, MX + cw2 + Inches(0.5), y + Inches(0.4), cw2, Inches(4.0), [
    "Implementar el **DIPCA** y completar el modelado de temas.",
    "Incorporar **TripAdvisor** y ampliar el léxico a portugués y neerlandés.",
    "**Cuestionarios** a bodegas y visitantes; verificación de precios con cada bodega.",
    "Cruzar IPA con **procedencia** (nacional / internacional) y análisis cross-cultural.",
    "**TFG y TFM** asociados: comparación con otras rutas, accesibilidad enoturística, Kano con fuentes de mayor varianza.",
], size=13, space=7)
notas(s, "Para el alumnado: la columna de limitaciones es un modelo de apartado de limitaciones de TFG; la de líneas futuras, una oferta real de temas.")

# ============================ CIERRE ============================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, W, H, PX)
filo(s, t=H - Inches(0.07))
caja(s, MX, Inches(2.0), ANCHO, Inches(1.0), "Gracias", size=48, bold=True, color=CREMA, font=TITULO_F)
caja(s, MX, Inches(3.1), Inches(10.5), Inches(1.2),
     "Lo difícil no es conseguir los datos. Es saber qué preguntarles, y decir con claridad qué se puede afirmar y qué no.",
     size=19, color=rgb("C9BEAC"))
caja(s, MX, Inches(4.7), ANCHO, Inches(0.4), "PLATAFORMA", size=10, bold=True, color=rgb("EBD98A"))
caja(s, MX, Inches(5.0), ANCHO, Inches(0.4), "enolytics-feder-uca.streamlit.app", size=16, color=CREMA)
caja(s, MX, Inches(5.5), ANCHO, Inches(0.4), "CONTACTO", size=10, bold=True, color=rgb("EBD98A"))
caja(s, MX, Inches(5.8), ANCHO, Inches(0.4), "inteligencia.turistica@gm.uca.es · Universidad de Cádiz · Proyecto FEDER Andalucía 2021-2027", size=14, color=CREMA)
pie(s, oscuro=True)
notas(s, """
Preguntas frecuentes:
· «¿Es espiar a los clientes?» → reseñas públicas escritas para ser leídas; se analizan textos agregados, no personas.
· «¿Quién lo mantiene al acabar el proyecto?» → software libre en servidor gratuito; el coste recurrente es actualizar
  el corpus (decenas de euros al año).
· «¿Sirve para otra denominación de origen?» → sí; diseño modular y replicable, objetivo declarado en la memoria.
· «¿Por qué Google y no TripAdvisor?» → volumen; TripAdvisor está en las líneas futuras.
""")

# ============================ GUARDAR ============================
import sys, pathlib
salida = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("ENOLYTICS_cursos_verano_2026.pptx")
salida.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(salida))
print(f"guardado: {salida} · {len(prs.slides)} diapositivas")
