"""Genera la marca gráfica de ENOLYTICS (SVG + PNG).

Por qué es un script y no un par de ficheros sueltos
----------------------------------------------------
Los colores NO se escriben aquí a mano: se importan de `enolytics.dashboard.estilo`,
que es donde vive la identidad visual del cuadro de mando. Así el logo no puede
desviarse de la paleta de la plataforma: si cambia el oloroso de la interfaz, se
vuelve a ejecutar esto y la marca lo sigue.

El concepto
-----------
Una **copita de catavinos** —el vaso del Marco de Jerez— cuyo contenido es un
**gráfico de barras ascendente**. Las dos mitades del nombre en un solo signo:
*eno* (el vino) + *lytics* (el análisis). Las barras recorren la **escala real de
crianza** del Marco, del fino pajizo al oloroso caoba, que es la misma gama que la
interfaz usa para su cromo.

Uso
---
    python3 scripts/generar_marca.py

Deja en `datos/marca/` el isotipo y el logotipo horizontal, en SVG (vectorial, para
imprenta y para escalar sin pérdida) y en PNG con fondo transparente a varios
tamaños, en versión clara y oscura.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from enolytics.dashboard import estilo  # noqa: E402

SALIDA = RAIZ / "datos" / "marca"
TAGLINE = "Inteligencia enoturística del Marco de Jerez"

# `estilo.TIPO` lleva comillas dobles ("Segoe UI"), que dentro de un atributo XML
# delimitado por comillas dobles lo cortarían por la mitad y la tipografía caería a
# la serif por defecto. En SVG se pasan con comillas simples.
TIPO_SVG = estilo.TIPO.replace('"', "'")

# Las barras recorren la escala de crianza del Marco. La rampa se DESPLAZA un paso
# según el fondo: sobre blanco, el fino pajizo (#EBD98A) no tiene contraste y la
# barra desaparece, así que la serie clara arranca en amontillado; sobre el caoba
# oscuro pasa lo contrario con el oloroso. Es la misma escala leída desde donde se
# ve, no cuatro colores elegidos a ojo.
CRIANZA_CLARO = [estilo.AMONTILLADO, estilo.PALO_CORTADO, estilo.OLOROSO, estilo.PX]
CRIANZA_OSCURO = [estilo.FINO, "#D8AE5C", estilo.AMONTILLADO, estilo.PALO_CORTADO]


def _copa(trazo: str, barras: list[str], ident: str) -> str:
    """Isotipo: la copita con el gráfico dentro, en un lienzo de 120x120.

    El recorte (`clipPath`) hace que las barras se corten con la silueta del vaso:
    es lo que da la lectura de «el vino es el dato», en vez de un gráfico metido
    dentro de un dibujo.
    """
    # Silueta de catavinos. Tres cosas la separan de un escudo, y las tres hacen
    # falta: el borde se cierra (la boca es más estrecha que el cuerpo), el cuenco
    # abomba de verdad hacia el tercio alto, y el fondo es REDONDO, no una punta.
    cuenco = ("M 39 18 "
              "C 32.5 31, 32.5 59, 47.5 72 "
              "C 52 76.5, 68 76.5, 72.5 72 "
              "C 87.5 59, 87.5 31, 81 18 Z")
    # (x, altura) de cada barra; la base está en y=74, sobre el fondo del cuenco.
    geo = [(42.75, 16), (51.75, 25), (60.75, 34), (69.75, 43)]
    rects = "\n".join(
        f'      <rect x="{x}" y="{74 - alto}" width="7.5" height="{alto}" '
        f'rx="1.6" fill="{color}"/>'
        for (x, alto), color in zip(geo, barras)
    )
    return f"""  <defs>
    <clipPath id="cuenco-{ident}">
      <path d="{cuenco}"/>
    </clipPath>
  </defs>
  <g clip-path="url(#cuenco-{ident})">
{rects}
  </g>
  <path d="{cuenco}" fill="none" stroke="{trazo}" stroke-width="3.2"
        stroke-linejoin="round"/>
  <path d="M 60 76 L 60 99" stroke="{trazo}" stroke-width="3.2"
        stroke-linecap="round"/>
  <path d="M 43 103 Q 60 97.5 77 103 Q 60 108.5 43 103 Z" fill="{trazo}"/>"""


def isotipo(oscuro: bool = False) -> str:
    """El signo solo, cuadrado. Para favicon, avatar y app icon."""
    trazo = estilo.FINO if oscuro else estilo.OLOROSO
    barras = CRIANZA_OSCURO if oscuro else CRIANZA_CLARO
    fondo = (f'  <rect width="120" height="120" rx="26" fill="{estilo.PX}"/>\n'
             if oscuro else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" '
            f'width="120" height="120" role="img" aria-label="ENOLYTICS">\n'
            f'{fondo}{_copa(trazo, barras, "iso")}\n</svg>\n')


def logotipo(oscuro: bool = False) -> str:
    """Isotipo + nombre + descriptor, en horizontal. Es la versión principal."""
    trazo = estilo.FINO if oscuro else estilo.OLOROSO
    barras = CRIANZA_OSCURO if oscuro else CRIANZA_CLARO
    tinta = estilo.SUPERFICIE if oscuro else estilo.INK
    tinta_suave = estilo.REJILLA if oscuro else estilo.INK_SUAVE
    # El encuadre NO está puesto a ojo: sale de medir las cajas reales en el
    # navegador (la copa y los dos textos) y dejar 22 de aire por los cuatro
    # lados. El desplazamiento vertical de la copa es lo que alinea su centro
    # óptico con el del bloque de texto, que si no queda montado hacia arriba.
    fondo = (f'  <rect width="453" height="132" fill="{estilo.PX}"/>\n'
             if oscuro else "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 453 132" \
width="453" height="132" role="img" aria-label="ENOLYTICS">
{fondo}  <g transform="translate(-12.9, 4)">
{_copa(trazo, barras, "logo")}
  </g>
  <text x="114.1" y="72" font-family="{TIPO_SVG}" font-size="46"
        font-weight="700" letter-spacing="2.4" fill="{tinta}">ENOLYTICS</text>
  <text x="116.1" y="100" font-family="{TIPO_SVG}" font-size="15.5"
        font-weight="400" letter-spacing="0.2" fill="{tinta_suave}">{TAGLINE}</text>
</svg>
"""


def _a_png(svg: Path, destinos: list[tuple[str, int]]) -> None:
    """Rasteriza el SVG con Chromium, respetando la transparencia."""
    from playwright.sync_api import sync_playwright

    texto = svg.read_text(encoding="utf-8")
    # El viewBox manda las proporciones; el alto se deduce del ancho pedido.
    vb = texto.split('viewBox="')[1].split('"')[0].split()
    prop = float(vb[3]) / float(vb[2])
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for nombre, ancho in destinos:
            alto = round(ancho * prop)
            pg = nav.new_page(viewport={"width": ancho, "height": alto},
                              device_scale_factor=2)
            pg.set_content(
                f'<style>html,body{{margin:0;padding:0;background:transparent}}'
                f'svg{{display:block;width:{ancho}px;height:{alto}px}}</style>{texto}')
            pg.wait_for_timeout(350)
            pg.screenshot(path=str(SALIDA / nombre), omit_background=True)
            pg.close()
            print(f"  {nombre}  {ancho}x{alto} (x2)")
        nav.close()


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    piezas = {
        "enolytics_isotipo.svg": isotipo(),
        "enolytics_isotipo_oscuro.svg": isotipo(oscuro=True),
        "enolytics_logo.svg": logotipo(),
        "enolytics_logo_oscuro.svg": logotipo(oscuro=True),
    }
    for nombre, contenido in piezas.items():
        (SALIDA / nombre).write_text(contenido, encoding="utf-8")
        print(f"  {nombre}")

    print("\nRasterizando:")
    _a_png(SALIDA / "enolytics_isotipo.svg",
           [("enolytics_isotipo_512.png", 512), ("enolytics_isotipo_128.png", 128)])
    _a_png(SALIDA / "enolytics_isotipo_oscuro.svg",
           [("enolytics_isotipo_oscuro_512.png", 512)])
    _a_png(SALIDA / "enolytics_logo.svg", [("enolytics_logo_1600.png", 1600)])
    _a_png(SALIDA / "enolytics_logo_oscuro.svg",
           [("enolytics_logo_oscuro_1600.png", 1600)])
    print(f"\nTodo en: {SALIDA}")


if __name__ == "__main__":
    main()
