"""Identidad visual de ENOLYTICS: paleta, CSS y estilo de gráficos.

Dos capas que **no se mezclan**:

1. **Cromo de la interfaz** (cabecera, tarjetas, tipografía): aquí vive la identidad del Marco
   de Jerez — *albariza* (el blanco cálido de su tierra) y el tinto de Jerez como acento.

2. **Colores de los DATOS**: se toman de una paleta **ya validada** (contraste sobre la
   superficie y separación suficiente para daltonismo, ΔE ≥ 12 entre series contiguas).
   **No se inventan colores "de vino" para las series**: sería bonito y sería inaccesible.

Reglas que se siguen (estándar de visualización de datos):
  · Las series se asignan **en orden fijo**, nunca cíclico.
  · **Un solo eje**: jamás dos escalas Y en el mismo gráfico.
  · El color sigue a la **entidad**, no a su posición en el ranking.
  · Los colores de **estado** (semáforo) están reservados y **siempre van con icono + texto**,
    nunca solos: quien no distingue el color debe poder leerlo igual.
  · Rejilla y ejes discretos; sin adornos.
"""
from __future__ import annotations

# --- Escala de color del vino de Jerez (crianza: de lo pálido a lo oscuro) ---
# Es la gama de la INTERFAZ, no de los datos. Reproduce la escala real de color de los
# vinos del Marco, del fino pajizo al Pedro Ximénez casi ébano.
FINO = "#EBD98A"             # Fino / Manzanilla — amarillo pajizo pálido
AMONTILLADO = "#C6902F"      # Amontillado — ámbar / oro viejo (uso muy puntual: ver nota)
PALO_CORTADO = "#A45E2A"     # Palo Cortado — ámbar tostado
OLOROSO = "#7A3B1E"          # Oloroso — caoba
PX = "#3B1E12"               # Pedro Ximénez — caoba muy oscuro, casi ébano
# El ORO amontillado se reserva para adornos aislados y NUNCA junto a los colores de estado:
# está demasiado cerca del amarillo "mejorable" del semáforo y se confundiría.

# --- Superficies e ink (identidad del Marco) ---
SUPERFICIE = "#FBFAF7"       # albariza: blanco cálido, la tierra del Marco
PLANO = "#F3F0E9"            # fondo de tarjetas
TINTO = OLOROSO              # acento de la interfaz = caoba de oloroso (NO se usa para datos)
INK = "#1C1B19"              # texto principal
INK_SUAVE = "#57544E"        # texto secundario
INK_TENUE = "#8B877E"        # ejes y etiquetas
REJILLA = "#E4E0D6"          # rejilla, hairline
BORDE = "rgba(28,27,25,0.10)"

# --- Paleta CATEGÓRICA (validada: ΔE ≥ 12 entre contiguas, contraste comprobado) ---
# El orden es el mecanismo de seguridad para daltonismo, no un capricho estético.
SERIES = [
    "#2a78d6",  # 1 azul
    "#1baf7a",  # 2 aguamarina
    "#eda100",  # 3 amarillo
    "#008300",  # 4 verde
    "#4a3aa7",  # 5 violeta
    "#e34948",  # 6 rojo
    "#e87ba4",  # 7 magenta
    "#eb6834",  # 8 naranja
]

# Tono de CONTEXTO: para el patrón "foco + contexto". Las entidades que no son el foco se
# pintan en gris; así el ojo va directo al Marco de Jerez sin necesidad de buscarlo.
CONTEXTO = "#C9C5BA"

# --- Paleta de ESTADO (reservada: nunca se reutiliza como "serie 4") ---
ESTADO = {
    "ok": "#0ca30c",         # good
    "mejorable": "#fab219",  # warning
    "atencion": "#ec835a",   # serious
    "critico": "#d03b3b",    # critical
}

# Hue secuencial (magnitud continua): un solo tono, claro → oscuro. Nunca arcoíris.
SECUENCIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]

TIPO = ('system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif')


def css() -> str:
    """Hoja de estilos del cuadro de mando."""
    return f"""
<style>
  /* ---------- Tipografía y base ---------- */
  html, body, [class*="css"] {{ font-family: {TIPO}; }}
  .main .block-container {{ padding-top: 2.2rem; max-width: 1280px; }}

  h1 {{
    font-size: 1.9rem !important; font-weight: 700 !important;
    letter-spacing: -0.02em; color: {INK};
  }}
  h2 {{ font-size: 1.35rem !important; font-weight: 650 !important; color: {INK}; }}
  h3 {{ font-size: 1.1rem !important; font-weight: 650 !important; color: {INK}; }}
  h4 {{ font-size: .95rem !important; font-weight: 650 !important; color: {INK_SUAVE};
        text-transform: uppercase; letter-spacing: .06em; }}

  /* ---------- Cabecera de marca (Opción A · «filo de vino») ---------- */
  /* Fondo claro (albariza) para no comer aire; la escala del vino vive en un filo
     degradado de 6 px en el borde superior. La marca va discreta arriba; el título
     de sección manda, con una barra oloroso al lado. */
  .eno-hero {{
    position: relative; background: {SUPERFICIE};
    border: 1px solid {REJILLA}; border-radius: 14px;
    padding: 1.1rem 1.4rem 1.15rem; margin-bottom: 1.4rem; overflow: hidden;
    box-shadow: 0 1px 2px rgba(28,27,25,.05);
  }}
  .eno-hero::before {{  /* filo de la escala del vino: fino → Pedro Ximénez */
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 6px;
    background: linear-gradient(90deg, {FINO}, {AMONTILLADO}, {PALO_CORTADO}, {OLOROSO}, {PX});
  }}
  .eno-brandrow {{
    display: flex; align-items: baseline; justify-content: space-between;
    gap: .8rem; flex-wrap: wrap; margin-bottom: .7rem;
  }}
  .eno-brand {{ font-weight: 700; font-size: .95rem; color: {TINTO}; letter-spacing: .01em; }}
  .eno-tagline {{ font-size: .78rem; color: {INK_TENUE}; }}
  .eno-title {{ display: flex; align-items: stretch; gap: .8rem; }}
  .eno-title .bar {{ width: 4px; flex: none; border-radius: 2px; background: {OLOROSO}; }}
  .eno-hero h1 {{
    color: {INK} !important; margin: 0 0 .1rem 0;
    font-size: 1.6rem !important; line-height: 1.15;
  }}
  .eno-hero p {{ margin: 0; color: {INK_SUAVE}; font-size: .9rem; }}

  /* ---------- Tarjetas (KPI, semáforo, secciones) ---------- */
  [data-testid="stMetric"] {{
    background: #fff; border: 1px solid {BORDE}; border-radius: 12px;
    padding: .85rem 1rem .75rem 1rem;
    box-shadow: 0 1px 2px rgba(28,27,25,.04);
  }}
  [data-testid="stMetricLabel"] {{
    color: {INK_SUAVE} !important; font-size: .78rem !important; font-weight: 600 !important;
    letter-spacing: .01em;
  }}
  [data-testid="stMetricValue"] {{
    color: {INK} !important; font-size: 1.6rem !important; font-weight: 700 !important;
    letter-spacing: -0.02em;
  }}
  [data-testid="stMetricDelta"] {{ font-size: .78rem !important; }}

  /* Contenedores con borde: tarjeta blanca en vez de caja gris */
  [data-testid="stVerticalBlockBorderWrapper"] {{
    background: #fff; border-radius: 14px; border: 1px solid {BORDE} !important;
    box-shadow: 0 1px 2px rgba(28,27,25,.04);
  }}

  /* ---------- Pestañas ---------- */
  .stTabs [data-baseweb="tab-list"] {{ gap: .15rem; border-bottom: 1px solid {REJILLA}; }}
  .stTabs [data-baseweb="tab"] {{
    height: 42px; padding: 0 .95rem; border-radius: 9px 9px 0 0;
    font-weight: 600; font-size: .88rem; color: {INK_SUAVE};
  }}
  .stTabs [aria-selected="true"] {{
    color: {TINTO} !important; background: {PLANO};
    box-shadow: inset 0 -2px 0 0 {TINTO};
  }}

  /* ---------- Desplegables ---------- */
  [data-testid="stExpander"] details {{
    border: 1px solid {BORDE}; border-radius: 11px; background: #fff;
  }}
  [data-testid="stExpander"] summary {{ font-weight: 600; font-size: .9rem; color: {INK_SUAVE}; }}
  [data-testid="stExpander"] summary:hover {{ color: {TINTO}; }}

  /* ---------- Avisos ---------- */
  [data-testid="stAlert"] {{ border-radius: 11px; border: 1px solid {BORDE}; }}

  /* ---------- Barra lateral ---------- */
  [data-testid="stSidebar"] {{ background: {PLANO}; border-right: 1px solid {REJILLA}; }}
  [data-testid="stSidebar"] h2 {{ font-size: 1rem !important; }}

  /* ---------- Detalles ---------- */
  hr {{ border-color: {REJILLA}; }}
  [data-testid="stCaptionContainer"] {{ color: {INK_TENUE}; }}
</style>
"""


# Marca y descriptor, discretos, que acompañan a cada título de sección en la cabecera.
MARCA = "🍷 ENOLYTICS"
TAGLINE = "Inteligencia enoturística del Marco de Jerez"


def hero(titulo: str, subtitulo: str) -> str:
    """Cabecera «filo de vino» (Opción A): marca discreta + título de sección.

    Fondo claro (albariza) con un filo degradado de la escala del vino en el borde
    superior. Una sola cabecera por página: arriba la marca, debajo el título de
    sección grande con una barra oloroso al lado. Ligera, pero mantiene la identidad.
    """
    return (
        '<div class="eno-hero">'
        f'<div class="eno-brandrow"><span class="eno-brand">{MARCA}</span>'
        f'<span class="eno-tagline">{TAGLINE}</span></div>'
        f'<div class="eno-title"><div class="bar"></div>'
        f'<div><h1>{titulo}</h1><p>{subtitulo}</p></div></div>'
        '</div>'
    )


def figura(fig, alto: int = 320, leyenda: bool = True,
           titulo_leyenda: str | None = None, ejes: bool = False):
    """Aplica el estilo común a una figura de Plotly.

    Rejilla y ejes discretos, sin adornos, tipografía del sistema y superficie de la marca.

    **El «undefined» de la observación 8 de Paula salía de aquí**, y no era el título de
    la leyenda sino el **del gráfico**: esta función fijaba `title` con fuente y posición
    pero **sin texto**, y Streamlit pinta ese hueco como el texto literal «undefined»
    (comprobado en un navegador real: pasa con el objeto sin `text` y también con
    `text=None`; solo la cadena vacía lo evita). Por eso se conserva el título que traiga
    la figura y, si no trae ninguno, se dice explícitamente que está vacío.

    `titulo_leyenda`: título de la leyenda cuando aporta algo («Tipo de competidor»).
    Si no se pasa, la leyenda va sin título.

    `ejes`: deja los rótulos de los ejes que traiga la figura. Por defecto se quitan
    —la mayoría de los gráficos se explican con su encabezado y su pie—, pero hay
    gráficos, como el mapa de Kamensky, donde el eje ES la explicación.
    """
    fig.update_layout(
        height=alto,
        margin=dict(l=8, r=24, t=30, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=TIPO, size=12, color=INK_SUAVE),
        title=dict(text=fig.layout.title.text or "",
                   font=dict(size=13, color=INK, family=TIPO), x=0, xanchor="left"),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    title_text=titulo_leyenda or None, font=dict(size=11)),
        hoverlabel=dict(bgcolor="#fff", bordercolor=BORDE,
                        font=dict(family=TIPO, size=12, color=INK)),
    )
    rotulo = dict(title_font=dict(size=11, color=INK_TENUE)) if ejes else dict(title_text=None)
    fig.update_xaxes(showgrid=False, zeroline=False,
                     linecolor=REJILLA, tickfont=dict(color=INK_TENUE, size=11), **rotulo)
    fig.update_yaxes(showgrid=True, gridcolor=REJILLA, gridwidth=1, zeroline=False,
                     linecolor="rgba(0,0,0,0)",
                     tickfont=dict(color=INK_TENUE, size=11), **rotulo)
    return fig


# =========================================================================== #
# CAPA «PANEL» (25/11/2026)
#
# Segunda piel de la interfaz, elegida por Antonio sobre maqueta: barra superior
# oscura, carril de navegación, lienzo gris y tarjetas blancas con cabecera de color.
#
# Se AÑADE, no sustituye. `css()` sigue siendo la base —la usan las cinco vistas— y
# esto se inyecta después para redefinir solo el cromo. Así la portada puede llevar el
# lenguaje nuevo mientras el resto conserva el suyo, sin un día de pantalla rota por
# medio. Los colores de los DATOS (SERIES, ESTADO, SECUENCIAL) no se tocan: están
# validados y no dependen del aspecto.
# =========================================================================== #
PIZARRA = "#46525F"          # barra superior
PIZARRA_CLARA = "#6B7B8C"    # cabecera de tarjeta
CARRIL = "#3C4651"           # carril de navegación
LIENZO = "#EDF0F3"           # fondo de la página
TARJETA = "#FFFFFF"
BORDE_PANEL = "#DDE2E7"
TINTA = "#2C333A"
TINTA_MEDIA = "#5C6670"
TINTA_TENUE = "#8D959D"
AZUL = "#4A7EBB"             # acento de la interfaz en esta capa
VERDE_OK = "#2F8F36"
ROJO_MAL = "#C33A2E"


def css_panel() -> str:
    """Redefine el cromo: barra, carril, lienzo y tarjetas. Se inyecta tras `css()`."""
    return f"""
<style>
  /* ---------- Lienzo ---------- */
  [data-testid="stAppViewContainer"] {{ background: {LIENZO}; }}
  [data-testid="stHeader"] {{ background: transparent; }}
  .main .block-container {{ padding-top: 1rem; max-width: 1400px; }}

  /* ---------- Carril de navegación (barra lateral) ---------- */
  [data-testid="stSidebar"] {{ background: {CARRIL}; }}
  [data-testid="stSidebar"] * {{ color: #D5DCE3 !important; }}
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label p {{
    color: #FFFFFF !important; font-weight: 600 !important;
  }}
  [data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: .34rem .5rem; border-radius: 4px; border-left: 3px solid transparent;
  }}
  [data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: #FFFFFF14; }}
  [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
    background: #FFFFFF1A; border-left-color: {AZUL};
  }}
  [data-testid="stSidebar"] [data-baseweb="radio"] div[aria-checked="true"] {{
    background-color: {AZUL} !important; border-color: {AZUL} !important;
  }}

  /* ---------- Barra superior de marca ---------- */
  .eno-barra {{
    background: {PIZARRA}; color: #fff; border-radius: 4px;
    padding: .78rem 1.1rem; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
  }}
  .eno-barra .tit {{ font-size: 1.07rem; font-weight: 600; }}
  .eno-barra .tit span {{ font-weight: 300; opacity: .82; }}
  .eno-barra .dcha {{ margin-left: auto; font-size: .8rem; opacity: .92;
    display: flex; align-items: center; gap: .5rem; }}
  .eno-barra .punto {{ width: 8px; height: 8px; border-radius: 50%; background: #6FCF78; }}

  /* ---------- Tarjeta con cabecera ---------- */
  .eno-tarjeta {{
    background: {TARJETA}; border: 1px solid {BORDE_PANEL}; border-radius: 3px;
    box-shadow: 0 1px 3px rgba(0,0,0,.11); margin-bottom: .9rem; overflow: hidden;
  }}
  .eno-tarjeta > .cab {{
    background: {PIZARRA_CLARA}; color: #fff; font-size: .79rem; font-weight: 600;
    padding: .5rem .75rem; display: flex; align-items: center; gap: .6rem;
  }}
  .eno-tarjeta > .cab .pts {{ margin-left: auto; letter-spacing: 2px; opacity: .7; }}
  .eno-tarjeta > .cpo {{ padding: .85rem .9rem .4rem; }}
  .eno-tarjeta > .sello {{
    padding: .45rem .75rem .55rem; font-size: .69rem; color: {TINTA_TENUE};
    border-top: 1px solid {BORDE_PANEL};
  }}

  /* Mismo aspecto para los contenedores con borde de Streamlit, que son los que
     envuelven lo interactivo (pestañas, gráficos de Plotly). */
  [data-testid="stVerticalBlockBorderWrapper"] {{
    background: {TARJETA}; border: 1px solid {BORDE_PANEL} !important;
    border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,.11);
  }}

  /* ---------- Piezas de dentro de la tarjeta ---------- */
  .eno-cifra {{ display: flex; align-items: center; gap: 1.1rem; }}
  .eno-cifra .mitad {{ flex: 1; min-width: 0; text-align: center; }}
  .eno-cifra .grande {{ font-size: 3.05rem; font-weight: 300; line-height: 1; }}
  .eno-cifra .verde {{ color: {VERDE_OK}; }}
  .eno-cifra .rojo {{ color: {ROJO_MAL}; }}
  .eno-bajo {{ display: block; font-size: .78rem; color: {TINTA_MEDIA}; margin-top: .4rem; }}
  .eno-bajo b {{ display: block; color: {TINTA}; font-size: .85rem; }}

  .eno-ab .f {{ display: flex; align-items: center; gap: .55rem; padding: .22rem 0; }}
  .eno-ab .n {{ font-size: .79rem; flex: 1; min-width: 0; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap; }}
  .eno-ab .pista {{ width: 74px; height: 7px; border-radius: 4px; background: {BORDE_PANEL};
    flex: none; overflow: hidden; }}
  .eno-ab .relleno {{ height: 100%; border-radius: 4px; display: block; }}
  .eno-ab .v {{ font-size: .79rem; font-weight: 600; width: 2.6rem; text-align: right;
    flex: none; font-variant-numeric: tabular-nums; }}

  .eno-anillo {{ display: flex; flex-direction: column; align-items: center; gap: .1rem; }}
  .eno-anillo .pc {{ font-size: 2.3rem; font-weight: 300; color: {AZUL}; line-height: 1;
    font-variant-numeric: tabular-nums; }}
  .eno-anillo .et {{ font-size: .78rem; color: {TINTA_MEDIA}; }}
</style>
"""


def barra_superior(derecha: str = "") -> str:
    """Barra oscura de marca. `derecha` es HTML ya compuesto (la línea de frescura)."""
    return (f'<div class="eno-barra"><span class="tit">ENOLYTICS '
            f'<span>— {TAGLINE}</span></span>'
            f'<span class="dcha">{derecha}</span></div>')


def tarjeta(titulo: str, cuerpo: str, sello: str = "") -> str:
    """Tarjeta blanca con cabecera de color. `cuerpo` y `sello` son HTML."""
    pie = f'<div class="sello">{sello}</div>' if sello else ""
    return (f'<div class="eno-tarjeta"><div class="cab">{titulo}'
            f'<span class="pts">···</span></div>'
            f'<div class="cpo">{cuerpo}</div>{pie}</div>')


def chispa(serie: list[float], color: str, ancho: int = 150, alto: int = 46) -> str:
    """Minigráfico de línea, sin ejes. Para acompañar a una cifra grande."""
    if not serie or len(serie) < 2:
        return ""
    lo, hi = min(serie), max(serie)
    rango = (hi - lo) or 1
    px = lambda i: 2 + i * (ancho - 4) / (len(serie) - 1)
    py = lambda v: 5 + (alto - 10) * (1 - (v - lo) / rango)
    d = " ".join(f"{'L' if i else 'M'}{px(i):.1f},{py(v):.1f}" for i, v in enumerate(serie))
    return (f'<svg viewBox="0 0 {ancho} {alto}" style="width:100%;max-width:{ancho}px;'
            f'height:auto;display:block;margin:0 auto" aria-hidden="true">'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linejoin="round"/>'
            f'<circle cx="{px(len(serie)-1):.1f}" cy="{py(serie[-1]):.1f}" r="3.2" '
            f'fill="{color}"/></svg>')


def anillo(pct: float, etiqueta: str) -> str:
    """Anillo de progreso con el porcentaje en el centro."""
    r, circ = 52, 2 * 3.141592653589793 * 52
    texto = f"{pct:.1f}".rstrip("0").rstrip(".").replace(".", ",")
    return (f'<div class="eno-anillo">'
            f'<svg viewBox="0 0 130 130" style="width:100%;max-width:138px;height:auto" '
            f'role="img" aria-label="{etiqueta}: {texto} por ciento">'
            f'<circle cx="65" cy="65" r="{r}" fill="none" stroke="{BORDE_PANEL}" '
            f'stroke-width="13"/>'
            f'<circle cx="65" cy="65" r="{r}" fill="none" stroke="{AZUL}" stroke-width="13" '
            f'stroke-linecap="round" stroke-dasharray="{circ*pct/100:.1f} {circ:.1f}" '
            f'transform="rotate(-90 65 65)"/></svg>'
            f'<span class="pc">{texto} %</span><span class="et">{etiqueta}</span></div>')


def barras_atributo(filas: list[tuple[str, float]], media: float,
                    minimo: float = 3.3, maximo: float = 4.5) -> str:
    """Lista de atributos con barra de progreso, verde o roja según la media.

    El color va acompañado SIEMPRE del número, que es lo que de verdad se lee: quien no
    distingue verde de rojo tiene el valor y la posición en la lista.
    """
    out = ['<div class="eno-ab">']
    for nombre, valor in filas:
        col = VERDE_OK if valor >= media else ROJO_MAL
        ancho = max(2.0, min(100.0, (valor - minimo) / (maximo - minimo) * 100))
        out.append(
            f'<div class="f"><span class="n">{nombre}</span>'
            f'<span class="pista"><span class="relleno" style="width:{ancho:.1f}%;'
            f'background:{col}"></span></span>'
            f'<span class="v" style="color:{col}">{valor:.2f}</span></div>'.replace(
                f'{valor:.2f}', f'{valor:.2f}'.replace(".", ",")))
    out.append("</div>")
    return "".join(out)
