"""Visita la plataforma publicada: la mantiene despierta y comprueba que funciona.

Para qué
--------
Streamlit Community Cloud suspende las aplicaciones que pasan días sin visitas. Quien entra
entonces no ve el cuadro de mando sino una pantalla de «Zzzz» con un botón, y tarda cerca de
un minuto en levantar. Para una plataforma cuyo enlace se pasa a bodegas y a la administración,
esa primera impresión es mala y además induce a pensar que está rota.

No basta con pedir la página por HTTP: Streamlit cuenta la actividad por sesiones abiertas, no
por peticiones, así que hay que cargarla en un navegador de verdad. De paso, al comprobar que
el contenido aparece, esto funciona como **canario**: si la plataforma deja de levantar, la
tarea falla y GitHub avisa por correo. Es la única vigilancia automática que tenemos.

Uso
---
    python3 scripts/visitar_plataforma.py
    python3 scripts/visitar_plataforma.py https://otra-direccion.streamlit.app
"""
from __future__ import annotations

import sys
import time

URL = "https://enolytics-feder-uca.streamlit.app"

# En Streamlit Cloud la aplicación NO vive en el documento principal: se sirve dentro de un
# iframe (`…/~/+/`), y por eso el texto del documento de arriba sale vacío. Comprobar por
# texto fue el primer intento y dio un falso negativo con la plataforma perfectamente en pie.
#
# La señal es un selector NUESTRO dentro de ese marco: `.eno-barra` es la barra superior que
# pinta `estilo.barra_superior()`. Si está, no solo responde Streamlit: ha pintado nuestra
# portada con nuestra hoja de estilo. Un código 200 no probaría nada, porque la pantalla de
# «Zzzz» también responde 200.
SEÑAL = ".eno-barra"
ESPERA_MAXIMA = 300          # segundos; levantar desde dormida ronda el minuto


def visitar(url: str) -> int:
    from playwright.sync_api import sync_playwright

    t0 = time.time()
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page(viewport={"width": 1400, "height": 900})
        pg.goto(url, wait_until="domcontentloaded", timeout=120_000)
        pg.wait_for_timeout(6_000)

        dormida = False
        try:
            boton = pg.get_by_text("get this app back up", exact=False).first
            boton.click(timeout=6_000)
            dormida = True
            print("Estaba dormida. Despertándola…", flush=True)
        except Exception:
            print("Estaba despierta.", flush=True)

        def ha_pintado() -> bool:
            """Busca la señal en cualquiera de los marcos de la página."""
            for marco in pg.frames:
                try:
                    if marco.evaluate(f"document.querySelectorAll('{SEÑAL}').length") > 0:
                        return True
                except Exception:
                    continue          # marco de otro dominio o aún sin cargar
            return False

        while time.time() - t0 < ESPERA_MAXIMA:
            try:
                if ha_pintado():
                    print(f"✓ En pie y pintando ({time.time() - t0:.0f} s"
                          f"{', tras despertarla' if dormida else ''}).")
                    nav.close()
                    return 0
            except Exception:
                pass
            pg.wait_for_timeout(5_000)

        print(f"✗ La plataforma no ha mostrado contenido en {ESPERA_MAXIMA} s. "
              f"Puede estar caída o el despliegue roto.", file=sys.stderr)
        nav.close()
        return 1


if __name__ == "__main__":
    sys.exit(visitar(sys.argv[1] if len(sys.argv) > 1 else URL))
