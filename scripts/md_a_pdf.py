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

Uso
---
    python3 scripts/md_a_pdf.py docs/tfg/daniela/plan_de_trabajo.md
    python3 scripts/md_a_pdf.py entrada.md salida.pdf
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


def convertir(origen: Path, destino: Path) -> None:
    from playwright.sync_api import sync_playwright

    cuerpo = markdown.markdown(
        origen.read_text(encoding="utf-8"),
        extensions=["tables", "sane_lists", "attr_list"],
    )
    html = (f'<!doctype html><html lang="es"><meta charset="utf-8">'
            f"<style>{CSS}</style><body>{cuerpo}</body></html>")

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page()
        pg.set_content(html, wait_until="load")
        pg.wait_for_timeout(400)
        pg.pdf(path=str(destino), format="A4", print_background=True,
               margin={"top": "19mm", "bottom": "17mm", "left": "17mm", "right": "17mm"},
               display_header_footer=True,
               header_template="<div></div>",
               footer_template=(
                   '<div style="width:100%;font-size:7.5pt;color:#8B877E;'
                   'font-family:system-ui,sans-serif;padding:0 17mm;">'
                   '<span style="float:right">'
                   '<span class="pageNumber"></span> / <span class="totalPages"></span>'
                   "</span></div>"))
        nav.close()


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    origen = Path(sys.argv[1])
    destino = Path(sys.argv[2]) if len(sys.argv) > 2 else origen.with_suffix(".pdf")
    convertir(origen, destino)
    kb = destino.stat().st_size / 1024
    print(f"{destino}  ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
