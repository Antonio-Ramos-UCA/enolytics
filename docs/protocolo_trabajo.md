# ENOLYTICS — Protocolo de trabajo en equipo

> Documento breve para coordinar el desarrollo de la plataforma entre los tres.
> Objetivo: trabajar **a la vez** sin pisarnos. Última actualización: 2026-07-10.

## 1. Quién hace qué (las 7 inteligencias)

Cada uno **profundiza en su bloque** y es su responsable. Nadie edita el bloque de otro.

| Persona | Bloque | Inteligencias |
|---|---|---|
| **Antonio** (Co-IP, integrador) | Demanda y mercado | 💶 Económica · 📈 Mercado |
| **Paula** | Cliente y competencia | 😊 Clientes · 🥊 Competidores |
| **Fernando** | Oferta y producto | 🏛️ Negocios · 🖥️ Tecnológica · 🌱 Sostenibilidad |

## 2. La regla de oro

> **Cada uno edita solo los archivos de SU bloque.**

Así, aunque trabajemos los tres a la vez, casi nunca hay conflictos. Antes de tocar
archivos comunes (catálogo de bodegas, configuración general), avisa al grupo.

## 3. Dónde vive el proyecto

- El proyecto está en **GitHub**: `Antonio-Ramos-UCA/enolytics`. Ese es nuestro punto común.
- El dashboard publicado está en: **https://enolytics-feder-uca.streamlit.app**
- ⚠️ **Nunca** nos pasamos la carpeta por Dropbox, correo o USB: se corrompe. Todo va por GitHub.

## 4. Cómo empezar (una sola vez por persona)

1. Crear una cuenta en **github.com** y decirle a Antonio tu usuario (te da acceso al repo).
2. Instalar **Claude Code** en tu ordenador.
3. Pedirle a Claude: *"clona el repositorio Antonio-Ramos-UCA/enolytics en una carpeta
   nueva (fuera de Dropbox)"*. Claude se encarga.

## 5. Cómo trabajar cada día

No hace falta saber Git: **Claude lo gestiona por ti**. Tu rutina es:

1. Al empezar: *"baja los últimos cambios y ponme en mi rama"* (tu rama: `mercado`,
   `clientes` o `negocios`, según tu bloque).
2. Trabajas en tus inteligencias con Claude (nuevas fuentes, análisis, mejoras de tu pestaña).
3. Para ver tu versión: *"arranca el dashboard en local"* → lo ves en tu navegador sin
   afectar al público.
4. Al terminar: *"sube mi trabajo y abre una Pull Request"*. Claude lo publica en GitHub.

## 6. Integración (lo hace Antonio)

- **Una vez por semana**, Antonio junta el trabajo de los tres en la versión oficial (`main`).
- El **dashboard público solo se actualiza al integrar**. Así, el trabajo a medias de cada
  uno nunca rompe lo que ve el equipo o las bodegas.
- Si hay algún choque, Claude lo resuelve al integrar.

> ⚠️ **Tras integrar, REINICIA la app.** Streamlit vuelve a ejecutar `app.py`, pero se queda con
> la versión **antigua en memoria** de los módulos importados (`config.py`, `ingesta/*.py`…).
> Si has tocado algo fuera de `app.py`, la app puede dar un `AttributeError` por quedarse a
> medio actualizar. **Solución:** en el dashboard → **"Manage app"** (abajo a la derecha) →
> menú **⋮** → **"Reboot app"**. Tarda ~30 s y arranca limpio.

## 7. Cómo dejamos las cosas para no perder el hilo

- Cada avance se anota en **`CONTEXTO.md`** (diario del proyecto) y las tareas en
  **`docs/pendientes.md`**. Así cualquiera retoma desde donde lo dejó otro.
- Cada indicador debe llevar **su fuente** (oficial / reseñas / estimado) para mantener el rigor.

## 8. Ritmo sugerido

- **Reunión corta semanal** (30 min): qué ha hecho cada uno, qué integra Antonio, próximos pasos.
- Dudas del día a día: por el canal del grupo.

---

**Resumen en una frase:** cada uno profundiza en su bloque, trabaja en su rama, sube por
GitHub, y Antonio integra una vez por semana. Claude se ocupa de la parte técnica.
