# Marca gráfica de ENOLYTICS

Generada por `scripts/generar_marca.py`. **Los colores no están escritos a mano**: se
importan de `enolytics/dashboard/estilo.py`, que es donde vive la identidad visual del
cuadro de mando. Si cambia la paleta de la plataforma, se vuelve a ejecutar el script y
la marca la sigue. No editar estos ficheros a mano: se regeneran.

```
python3 scripts/generar_marca.py
```

## El signo

Una **copita de catavinos** —el vaso del Marco de Jerez— cuyo contenido es un **gráfico
de barras ascendente**. Las dos mitades del nombre en una sola imagen: *eno* (el vino) y
*lytics* (el análisis). El recorte hace que las barras se corten con la silueta del
vaso, para que se lean como vino llenando la copa y no como un gráfico metido dentro de
un dibujo.

Las barras recorren la **escala de crianza del Marco**, de lo pálido a lo oscuro, que es
la misma gama que la interfaz usa para su cromo. La rampa se **desplaza un paso según el
fondo**: sobre blanco arranca en amontillado, porque el fino pajizo (`#EBD98A`) no tiene
contraste suficiente y la barra desaparecería; sobre el caoba oscuro pasa lo contrario
con el oloroso. Es la misma escala leída desde donde se ve.

## Ficheros

| Fichero | Qué es | Dónde se usa |
|---|---|---|
| `enolytics_logo.svg` | **Versión principal.** Signo + nombre + descriptor, horizontal | Documentos, presentaciones, cabeceras |
| `enolytics_logo_1600.png` | La misma, rasterizada a 1600 px de ancho (×2) | Cuando no se admite SVG |
| `enolytics_logo_oscuro.svg` / `_1600.png` | Para fondos oscuros, con su propio fondo caoba | Diapositivas oscuras, cubiertas |
| `enolytics_isotipo.svg` | Solo el signo, cuadrado | Avatar, marca de agua, favicon |
| `enolytics_isotipo_512.png` / `_128.png` | Rasterizado, fondo transparente | Iconos, redes |
| `enolytics_isotipo_oscuro.svg` / `_512.png` | Signo sobre pastilla caoba redondeada | Icono de aplicación |

Los SVG son vectoriales: sirven para imprenta y escalan sin pérdida. Los PNG salen con
**fondo transparente** y a doble densidad, para pantallas de retina.

## Cómo usarla

- **Aire alrededor**: dejar como mínimo la altura de la copa del isotipo por los cuatro
  lados. El encuadre de los ficheros ya incluye ese margen.
- **No deformar**: escalar siempre de forma proporcional.
- **No recolorear** ni añadir sombras, degradados o contornos.
- **Tamaño mínimo del logotipo horizontal**: 120 px de ancho. Por debajo, el descriptor
  deja de leerse y conviene usar el isotipo solo.
- **Sobre fotografía**: usar la versión oscura, que lleva su propio fondo.

## Relación con la marca institucional

Esta marca **no sustituye** a la banda de logos FEDER ni a la de la Universidad de
Cádiz, que son obligación de publicidad del proyecto y van en `datos/marca_feder/`.
ENOLYTICS es el nombre de la plataforma; la financiación y la institución se declaran
aparte, como exige la resolución. Ver `datos/marca_feder/LEEME.md`.
