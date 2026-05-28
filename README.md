# Página web — Adicción a videojuegos

Frontend de la landing cinematográfica para el proyecto de ciencia de datos sobre adicción al gaming y salud mental.

## Estructura

- `frontend/`: aplicación web con Vite.
- `Backend/`: API con FastAPI y modelo `.pkl`.

## Imagen de fondo

Coloca tu imagen en:

```
frontend/public/images/hero.jpg
```

También puedes usar `hero.webp` o `hero.png`; en ese caso actualiza la ruta en `frontend/src/styles.css` (clase `.wallpaper`).

Recomendaciones: orientación horizontal, al menos 1920×1080 px, buena compresión (JPG/WebP).

## Desarrollo

```bash
cd frontend
npm install
npm run dev
```

Abre la URL que muestra Vite (por defecto `http://localhost:5173`).

## Build

```bash
cd frontend
npm run build
npm run preview
```
