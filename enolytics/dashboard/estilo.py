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


def figura(fig, alto: int = 320, leyenda: bool = True):
    """Aplica el estilo común a una figura de Plotly.

    Rejilla y ejes discretos, sin adornos, tipografía del sistema y superficie de la marca.
    """
    fig.update_layout(
        height=alto,
        margin=dict(l=8, r=24, t=30, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=TIPO, size=12, color=INK_SUAVE),
        title=dict(font=dict(size=13, color=INK, family=TIPO), x=0, xanchor="left"),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    title_text="", font=dict(size=11)),
        hoverlabel=dict(bgcolor="#fff", bordercolor=BORDE,
                        font=dict(family=TIPO, size=12, color=INK)),
    )
    fig.update_xaxes(showgrid=False, zeroline=False,
                     linecolor=REJILLA, tickfont=dict(color=INK_TENUE, size=11), title_text="")
    fig.update_yaxes(showgrid=True, gridcolor=REJILLA, gridwidth=1, zeroline=False,
                     linecolor="rgba(0,0,0,0)",
                     tickfont=dict(color=INK_TENUE, size=11), title_text="")
    return fig
