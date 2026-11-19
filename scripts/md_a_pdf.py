"""Convierte un documento Markdown del proyecto en un PDF presentable.

Para qué
--------
Los documentos de `docs/` están en Markdown porque se versionan bien, pero un `.md` no se le
envía a nadie de fuera del proyecto: no se abre en un móvil ni se imprime. Esto los pasa a PDF
con la tipografía y los colores de ENOLYTICS (`dashboard/estilo.py`), para poder adjuntarlos.

Cómo
----
Markdown → HTML (biblioteca `markdown`) → PDF (motor de impresión de Chromium, vía Playwright).
No hace falta LaTeX ni pandoc.

Dos estilos
-----------
Por defecto se usa el estilo de la plataforma: tipografía de palo seco, epígrafes en color y
realces sombreados. Con `--sobrio` se compone en registro académico: tipografía con remates,
todo en negro, sin fondos ni filetes de color, tablas con reglas horizontales y citas marcadas
solo por la sangría. Es el que corresponde a lo que se entrega a un estudiante o a un tribunal.

Uso
---
    python3 scripts/md_a_pdf.py "docs/tfg/daniela/Plan de trabajo TFG - Daniela.md" --sobrio
    python3 scripts/md_a_pdf.py entrada.md salida.pdf
    python3 scripts/md_a_pdf.py entrada.md salida.pdf --sobrio
"""
from __future__ import annotations

import sys
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from enolytics.dashboard import estilo  # noqa: E402

CSS = f"""
@page {{ size: A4; margin: 19mm 17mm 17mm 17mm; }}
* {{ box-sizing: border-box; }}
body {{
  font-family: {estilo.TIPO};
  font-size: 10.4pt; line-height: 1.5;
  color: {estilo.INK}; margin: 0;
}}
h1 {{
  font-size: 19pt; line-height: 1.22; margin: 0 0 .15em;
  color: {estilo.INK}; letter-spacing: -.01em;
  border-bottom: 3px solid {estilo.OLOROSO}; padding-bottom: .3em;
}}
h2 {{
  font-size: 13.5pt; margin: 1.5em 0 .5em; color: {estilo.OLOROSO};
  page-break-after: avoid;
}}
h3 {{ font-size: 11.4pt; margin: 1.15em 0 .35em; page-break-after: avoid; }}
p, li {{ margin: .4em 0; }}
ul, ol {{ padding-left: 1.25em; }}
strong {{ color: {estilo.INK}; }}
em {{ color: {estilo.INK_SUAVE}; }}
code {{
  font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: .88em;
  background: {estilo.PLANO}; padding: .1em .3em; border-radius: 3px;
}}
table {{
  border-collapse: collapse; width: 100%; margin: .8em 0;
  font-size: 9.4pt; page-break-inside: avoid;
}}
th {{
  background: {estilo.PLANO}; text-align: left; font-weight: 700;
  border-bottom: 2px solid {estilo.OLOROSO};
}}
th, td {{ padding: .4em .55em; border-bottom: 1px solid {estilo.REJILLA}; vertical-align: top; }}
blockquote {{
  margin: .9em 0; padding: .6em .95em;
  background: {estilo.PLANO}; border-left: 3px solid {estilo.OLOROSO};
  page-break-inside: avoid;
}}
blockquote p {{ margin: .2em 0; }}
hr {{ border: none; border-top: 1px solid {estilo.REJILLA}; margin: 1.6em 0; }}
"""

CSS_SOBRIO = """
@page { size: A4; margin: 24mm 22mm 20mm 22mm; }
* { box-sizing: border-box; }
body {
  font-family: Georgia, "Times New Roman", Times, serif;
  font-size: 11pt; line-height: 1.52;
  color: #000; margin: 0;
}
h1 {
  font-size: 17pt; font-weight: 700; line-height: 1.25;
  margin: 0 0 .6em; padding: 0;
}
h2 {
  font-size: 12.5pt; font-weight: 700; color: #000;
  margin: 1.9em 0 .55em; page-break-after: avoid;
}
h3 {
  font-size: 11pt; font-weight: 400; font-style: italic;
  margin: 1.3em 0 .4em; page-break-after: avoid;
}
p, li { margin: .5em 0; }
ul, ol { padding-left: 1.4em; }
li { padding-left: .15em; }
strong { font-weight: 700; }
em { font-style: italic; }
a { color: #000; text-decoration: none; }
code { font-family: Georgia, "Times New Roman", Times, serif; font-size: 1em; }
table {
  border-collapse: collapse; width: 100%; margin: 1em 0;
  font-size: 10pt; page-break-inside: avoid;
  border-top: 1.1pt solid #000; border-bottom: 1.1pt solid #000;
}
th {
  text-align: left; font-weight: 700; background: none;
  border-bottom: .6pt solid #000;
}
th, td { padding: .42em .6em .42em 0; vertical-align: top; }
td { border: none; }
tbody tr:first-child td { padding-top: .6em; }
blockquote {
  margin: .9em 0 .9em 1.9em; padding: 0; background: none; border: none;
  page-break-inside: avoid;
}
blockquote p { margin: .3em 0; font-size: 10.3pt; }
hr { border: none; border-top: .6pt solid #000; margin: 1.8em 0; }
"""


def convertir(origen: Path, destino: Path, sobrio: bool = False) -> None:
    from playwright.sync_api import sync_playwright

    hoja = CSS_SOBRIO if sobrio else CSS

    cuerpo = markdown.markdown(
        origen.read_text(encoding="utf-8"),
        extensions=["tables", "sane_lists", "attr_list"],
    )
    html = (f'<!doctype html><html lang="es"><meta charset="utf-8">'
            f"<style>{hoja}</style><body>{cuerpo}</body></html>")

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page()
        pg.set_content(html, wait_until="load")
        pg.wait_for_timeout(400)
        m = ({"top": "24mm", "bottom": "20mm", "left": "22mm", "right": "22mm"} if sobrio
             else {"top": "19mm", "bottom": "17mm", "left": "17mm", "right": "17mm"})
        pg.pdf(path=str(destino), format="A4", print_background=True, margin=m,
               display_header_footer=True,
               header_template="<div></div>",
               footer_template=(
                   f'<div style="width:100%;font-size:8pt;'
                   f'color:{"#000" if sobrio else "#8B877E"};'
                   f'font-family:{"Georgia, serif" if sobrio else "system-ui, sans-serif"};'
                   f'padding:0 {"22mm" if sobrio else "17mm"};">'
                   '<span style="float:right">'
                   '<span class="pageNumber"></span> / <span class="totalPages"></span>'
                   "</span></div>"))
        nav.close()


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sobrio = "--sobrio" in sys.argv
    origen = Path(args[0])
    destino = Path(args[1]) if len(args) > 1 else origen.with_suffix(".pdf")
    convertir(origen, destino, sobrio=sobrio)
    kb = destino.stat().st_size / 1024
    print(f"{destino}  ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
