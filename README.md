# ENOLYTICS

**Plataforma digital de inteligencia competitiva integrada para la gestión enoturística del Marco de Jerez.**

Proyecto de investigación de la Universidad de Cádiz (financiación FEDER Andalucía 2021-2027). Transforma datos —reseñas online, indicadores económicos, sociales y de sostenibilidad— en inteligencia procesable, mediante minería de textos, análisis de sentimiento, modelado de temas y análisis de importancia-desempeño (IPA / IPCA / DIPA / DIPCA).

El entregable es un **cuadro de mando interactivo** (Streamlit) con dos vistas: bodega individual y gestor de destino.

## Estructura

```
PROTOTIPO ENOLYTICS/
├── enolytics/               # paquete principal
│   ├── config.py            # rutas, constantes y parámetros
│   ├── ingesta/             # descarga de datos
│   │   ├── ruta_jerez.py    #   catálogo de bodegas (Ruta del Vino de Jerez)
│   │   └── resenas.py       #   interfaz común de descarga de reseñas (Google/TripAdvisor)
│   ├── etl/                 # limpieza y normalización (pendiente)
│   ├── nlp/                 # sentimiento, LDA/BERT (pendiente)
│   ├── analitica/           # modelos IPA/IPCA/DIPA/DIPCA
│   │   └── ipa.py
│   └── dashboard/           # cuadro de mando Streamlit
│       └── app.py
├── datos/
│   ├── catalogo/            # catálogo de bodegas (CSV + JSON)
│   ├── crudo/               # datos sin procesar (reseñas descargadas) — no versionado
│   └── procesado/           # datasets limpios/derivados
├── scripts/                 # utilidades ejecutables
│   └── actualizar_catalogo.py
├── tests/
├── requirements.txt
└── MEMORIA/                 # memoria científico-técnica del proyecto
```

## Puesta en marcha

```bash
# 1. Instalar dependencias
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium   # para el scraper de reseñas (más adelante)

# 2. Generar/actualizar el catálogo de bodegas
python3 scripts/actualizar_catalogo.py

# 3. Lanzar el dashboard
python3 -m streamlit run enolytics/dashboard/app.py
```

## Estado actual

- [x] Catálogo de las 41 bodegas de la Ruta del Vino y Brandy de Jerez (nombre, localidad, dirección, teléfono, email, web, GPS, RRSS, servicios, descripción).
- [x] Dashboard inicial con mapa, directorio y ficha de bodega (vistas por rol).
- [ ] Descarga de reseñas (Google / TripAdvisor).
- [ ] NLP: sentimiento y modelado de temas.
- [ ] Módulos IPCA / DIPA / DIPCA.
- [ ] Indicadores de las 7 inteligencias y cuestionarios.

## Fuentes de datos

- **Catálogo de bodegas:** [Ruta del Vino y Brandy de Jerez](https://rutadelvinojerez.es/empresas-y-servicios/categoria/bodegas/).
- **Reseñas:** Google Reviews, TripAdvisor (pendiente).
- **Indicadores oficiales:** INE, Dataestur, ACEVIN, Google Trends (pendiente).
