"""Descarga de páginas web con reintento en navegador real (Playwright).

Muchas webs de bodega no se dejan leer con una petición simple: tienen **verificación de edad**
("¿eres mayor de 18?"), avisos de cookies bloqueantes o cargan el contenido con JavaScript. El
lector rápido (`requests`) se queda en el muro y devuelve una página vacía.

El efecto es un **sesgo grave**: precisamente las bodegas grandes y con webs más avanzadas
(González Byass, Tradición...) salían con 0 en todos los índices, no por ser peores, sino por
bloquearnos. Esto **falseaba los indicadores a la baja**.

Estrategia (en dos pasos, para no gastar navegador sin necesidad):
  1. `requests` — rápido. Si devuelve una página válida y con contenido, se usa.
  2. Si falla o parece un muro, se abre **Chromium** con Playwright, se acepta la verificación
     de edad / cookies y se lee la página ya renderizada.

Uso:
    from enolytics.ingesta import navegador
    html = navegador.obtener_html("https://ejemplo.es")   # str vacío si no se pudo
"""
from __future__ import annotations

import re

import requests

from enolytics import config

# Señales de que la respuesta NO es la página real, sino un muro o un cascarón vacío
_SENALES_MURO = [
    "enable javascript", "habilitar javascript", "necesitas javascript",
    "verificación de edad", "age verification", "verify your age",
    "mayor de edad", "eres mayor", "confirma tu edad", "access denied",
    "just a moment", "checking your browser", "cf-browser-verification",
]

# Textos de botones que dan paso (edad, cookies). Se prueban en orden.
_BOTONES_ACEPTAR = [
    "Sí, soy mayor de edad", "Si, soy mayor de edad", "Soy mayor de edad",
    "Sí", "Si", "Entrar", "Acceder", "Confirmar", "Aceptar",
    "Aceptar todas", "Aceptar todas las cookies", "Aceptar cookies",
    "De acuerdo", "Estoy de acuerdo", "Continuar",
    "Yes", "I am over 18", "Enter", "Accept", "Accept all", "I agree", "Agree",
]

TIEMPO_ESPERA_MS = 20_000


def _parece_muro(html: str) -> bool:
    """True si el HTML es demasiado corto o contiene señales de bloqueo."""
    if not html:
        return True
    bajo = html.lower()
    # Un <body> con muy poco texto suele ser un cascarón de JavaScript
    texto = re.sub(r"<[^>]+>", " ", bajo)
    texto = re.sub(r"\s+", " ", texto).strip()
    if len(texto) < 400:
        return True
    return any(s in bajo for s in _SENALES_MURO)


def _con_requests(url: str, timeout: int = 12) -> str:
    """Intento rápido. Devuelve '' si falla."""
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return ""
        return r.text
    except requests.RequestException:
        return ""


def _con_navegador(url: str) -> str:
    """Abre Chromium real, salta la verificación de edad/cookies y devuelve el HTML."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ""

    html = ""
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(
                user_agent=config.USER_AGENT,
                locale="es-ES",
                viewport={"width": 1366, "height": 900},
            )
            pagina = contexto.new_page()
            try:
                pagina.goto(url, timeout=TIEMPO_ESPERA_MS, wait_until="domcontentloaded")

                # Aceptar verificación de edad / cookies si aparece algún botón conocido
                for texto in _BOTONES_ACEPTAR:
                    try:
                        boton = pagina.get_by_role(
                            "button", name=re.compile(rf"^\s*{re.escape(texto)}\s*$", re.I))
                        if boton.count() == 0:
                            boton = pagina.get_by_text(
                                re.compile(rf"^\s*{re.escape(texto)}\s*$", re.I))
                        if boton.count() > 0:
                            boton.first.click(timeout=2500)
                            pagina.wait_for_timeout(1200)
                            break
                    except Exception:
                        continue

                try:
                    pagina.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                html = pagina.content()
            finally:
                contexto.close()
                navegador.close()
    except Exception:
        return ""
    return html


def obtener_html(url: str, permitir_navegador: bool = True) -> tuple[str, str]:
    """Devuelve (html, metodo). `metodo` es 'requests', 'navegador' o '' si no se pudo.

    Primero prueba la vía rápida; si topa con un muro, abre el navegador real.
    """
    if not isinstance(url, str) or not url.startswith("http"):
        return "", ""

    html = _con_requests(url)
    if html and not _parece_muro(html):
        return html, "requests"

    if not permitir_navegador:
        return (html, "requests") if html else ("", "")

    html_nav = _con_navegador(url)
    if html_nav and not _parece_muro(html_nav):
        return html_nav, "navegador"

    # Si el navegador tampoco lo resolvió, devolvemos lo mejor que tengamos
    if html_nav:
        return html_nav, "navegador"
    return (html, "requests") if html else ("", "")
