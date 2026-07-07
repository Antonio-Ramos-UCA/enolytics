#!/usr/bin/env python3
"""Actualiza el catálogo de bodegas de la Ruta del Vino y Brandy de Jerez.

Descarga el listado, enriquece cada ficha y guarda el resultado en datos/catalogo/.

Uso:
    python3 scripts/actualizar_catalogo.py
"""
import sys
from pathlib import Path

# Permite ejecutar el script directamente sin instalar el paquete
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from enolytics.ingesta import ruta_jerez


if __name__ == "__main__":
    ruta_jerez.actualizar_catalogo_completo()
